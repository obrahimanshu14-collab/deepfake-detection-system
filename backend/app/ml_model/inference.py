"""
Reusable inference logic: image prediction, video prediction (CNN +
rPPG ensemble), single in-memory frame prediction (for live webcam),
and the 5-tier REAL/FAKE classification band mapping.
"""
import cv2
import numpy as np
import torch

from app.ml_model.face_utils import load_and_align, detect_and_align_face
from app.ml_model.transforms import eval_transform, IMG_SIZE
from app.ml_model.rppg import analyze_video

REAL_MAX = 0.15
POSSIBLY_REAL_MAX = 0.40
UNCERTAIN_MAX = 0.60
POSSIBLY_FAKE_MAX = 0.85

ENSEMBLE_WEIGHTS = {"cnn": 0.95, "rppg": 0.05}


def classify_probability(fake_prob: float) -> str:
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
    }


def predict_frame(frame_bgr: np.ndarray, model, device: str = "cpu") -> dict:
    """Same classification as predict_image, but on an in-memory frame
    (numpy array) -- used for live webcam streaming."""
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
    }


def predict_video(
    filepath: str, model, device: str = "cpu",
    frame_sample_rate: int = 15, max_frames: int = 30,
) -> dict:
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video at: {filepath}")

    frame_probs = []
    frame_idx = 0
    frames_processed = 0
    while frames_processed < max_frames:
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
                frames_processed += 1
        frame_idx += 1
    cap.release()

    if not frame_probs:
        return {
            "label": "Uncertain", "raw_fake_probability": 0.5,
            "real_percent": 50.0, "fake_percent": 50.0,
            "frames_analyzed": 0, "note": "No face detected in any sampled frame.",
        }

    cnn_fake_prob = float(np.mean(frame_probs))
    rppg_result = analyze_video(filepath)
    rppg_fake_signal = 1.0 - rppg_result["authenticity_score"]
    final_fake_prob = (
        ENSEMBLE_WEIGHTS["cnn"] * cnn_fake_prob + ENSEMBLE_WEIGHTS["rppg"] * rppg_fake_signal
    )

    return {
        "label": classify_probability(final_fake_prob),
        "raw_fake_probability": round(final_fake_prob, 4),
        "real_percent": round((1 - final_fake_prob) * 100, 1),
        "fake_percent": round(final_fake_prob * 100, 1),
        "frames_analyzed": len(frame_probs),
        "signals": {
            "cnn_fake_probability": round(cnn_fake_prob, 4),
            "rppg_authenticity_score": rppg_result["authenticity_score"],
            "rppg_estimated_bpm": rppg_result["estimated_bpm"],
        },
    }