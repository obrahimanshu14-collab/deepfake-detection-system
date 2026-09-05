"""
Reusable inference logic for image, video, live-frame detection and the
five-tier verdict system used by the product and developer API.
"""
import os

import cv2
import numpy as np
import torch
from app.ml_model.lipsync import analyze_lipsync

from app.ml_model.face_utils import detect_and_align_face, load_and_align
from app.ml_model.rppg import analyze_video
from app.ml_model.transforms import IMG_SIZE, eval_transform

REAL_MAX = float(os.getenv("VERDICT_REAL_MAX", "0.15"))
POSSIBLY_REAL_MAX = float(os.getenv("VERDICT_POSSIBLY_REAL_MAX", "0.40"))
UNCERTAIN_MAX = float(os.getenv("VERDICT_UNCERTAIN_MAX", "0.60"))
POSSIBLY_FAKE_MAX = float(os.getenv("VERDICT_POSSIBLY_FAKE_MAX", "0.85"))


def _weights() -> dict[str, float]:
    raw = {
        "cnn": float(os.getenv("ENSEMBLE_CNN_WEIGHT", "0.90")),
        "rppg": float(os.getenv("ENSEMBLE_RPPG_WEIGHT", "0.05")),
        "lipsync": float(os.getenv("ENSEMBLE_LIPSYNC_WEIGHT", "0.05")),
    }
    total = sum(max(v, 0.0) for v in raw.values()) or 1.0
    return {key: max(value, 0.0) / total for key, value in raw.items()}


ENSEMBLE_WEIGHTS = _weights()
MODEL_VERSION = os.getenv("MODEL_VERSION", "veritas-mobilenetv2-1.0")


def classify_probability(fake_prob: float) -> str:
    fake_prob = float(np.clip(fake_prob, 0.0, 1.0))
    if fake_prob < REAL_MAX:
        return "REAL"
    if fake_prob < POSSIBLY_REAL_MAX:
        return "Possibly Real"
    if fake_prob < UNCERTAIN_MAX:
        return "Uncertain"
    if fake_prob < POSSIBLY_FAKE_MAX:
        return "Possibly Fake"
    return "FAKE"


def predict_image(filepath: str, model, device: str = "cpu") -> dict:
    face = load_and_align(filepath, output_size=IMG_SIZE)
    tensor = eval_transform(image=face)["image"].unsqueeze(0).to(device)
    with torch.no_grad():
        logit = model(tensor)
        fake_prob = torch.sigmoid(logit).item()
    return {
        "label": classify_probability(fake_prob),
        "raw_fake_probability": round(fake_prob, 4),
        "real_percent": round((1 - fake_prob) * 100, 1),
        "fake_percent": round(fake_prob * 100, 1),
        "model_version": MODEL_VERSION,
    }


def predict_frame(frame_bgr: np.ndarray, model, device: str = "cpu") -> dict:
    """Run image-model inference on an in-memory webcam frame."""
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    face = detect_and_align_face(frame_rgb, output_size=IMG_SIZE)
    if face is None:
        return {"label": "No Face", "real_percent": None, "fake_percent": None}
    tensor = eval_transform(image=face)["image"].unsqueeze(0).to(device)
    with torch.no_grad():
        logit = model(tensor)
        fake_prob = torch.sigmoid(logit).item()
    return {
        "label": classify_probability(fake_prob),
        "real_percent": round((1 - fake_prob) * 100, 1),
        "fake_percent": round(fake_prob * 100, 1),
        "model_version": MODEL_VERSION,
    }


def predict_video(
    filepath: str,
    model,
    device: str = "cpu",
    frame_sample_rate: int | None = None,
    max_frames: int | None = None,
) -> dict:
    frame_sample_rate = frame_sample_rate or int(os.getenv("VIDEO_FRAME_SAMPLE_RATE", "15"))
    max_frames = max_frames or int(os.getenv("VIDEO_MAX_FRAMES", "30"))
    frame_sample_rate = max(1, frame_sample_rate)
    max_frames = max(1, max_frames)

    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video at: {filepath}")

    frame_probs = []
    frame_idx = 0
    try:
        while len(frame_probs) < max_frames:
            ret, frame_bgr = cap.read()
            if not ret:
                break
            if frame_idx % frame_sample_rate == 0:
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                face = detect_and_align_face(frame_rgb, output_size=IMG_SIZE)
                if face is not None:
                    tensor = eval_transform(image=face)["image"].unsqueeze(0).to(device)
                    with torch.no_grad():
                        logit = model(tensor)
                        fake_prob = torch.sigmoid(logit).item()
                    frame_probs.append(fake_prob)
            frame_idx += 1
    finally:
        cap.release()

    if not frame_probs:
        return {
            "label": "Uncertain",
            "raw_fake_probability": 0.5,
            "real_percent": 50.0,
            "fake_percent": 50.0,
            "frames_analyzed": 0,
            "model_version": MODEL_VERSION,
            "note": "No face detected in any sampled frame.",
        }

    cnn_fake_prob = float(np.mean(frame_probs))

    # Auxiliary signals are advisory. A failure in one signal must not take
    # down the entire video detector; neutral 0.5 keeps that signal from
    # dominating the final probability.
    try:
        rppg_result = analyze_video(filepath)
        rppg_fake_signal = float(np.clip(1.0 - rppg_result["authenticity_score"], 0.0, 1.0))
    except Exception:
        rppg_result = {"authenticity_score": 0.5, "estimated_bpm": None}
        rppg_fake_signal = 0.5

    try:
        lipsync_result = analyze_lipsync(filepath)
        lipsync_fake_signal = float(np.clip(1.0 - lipsync_result["sync_score"], 0.0, 1.0))
    except Exception:
        lipsync_result = {"sync_score": 0.5}
        lipsync_fake_signal = 0.5

    final_fake_prob = (
        ENSEMBLE_WEIGHTS["cnn"] * cnn_fake_prob
        + ENSEMBLE_WEIGHTS["rppg"] * rppg_fake_signal
        + ENSEMBLE_WEIGHTS["lipsync"] * lipsync_fake_signal
    )

    return {
        "label": classify_probability(final_fake_prob),
        "raw_fake_probability": round(final_fake_prob, 4),
        "real_percent": round((1 - final_fake_prob) * 100, 1),
        "fake_percent": round(final_fake_prob * 100, 1),
        "frames_analyzed": len(frame_probs),
        "model_version": MODEL_VERSION,
        "signals": {
            "cnn_fake_probability": round(cnn_fake_prob, 4),
            "rppg_authenticity_score": rppg_result["authenticity_score"],
            "rppg_estimated_bpm": rppg_result["estimated_bpm"],
            "lipsync_score": lipsync_result["sync_score"],
        },
    }
