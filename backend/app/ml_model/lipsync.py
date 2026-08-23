"""
Lip-sync mismatch detection: extracts a lip-opening signal from video
frames (via MediaPipe face-mesh landmarks) and an audio energy envelope
from the same video's audio track, then measures how well they
correlate. A real speaking video has lips opening/closing in sync with
loudness; an AI-generated or dubbed-over video often does not.

Classical signal processing, not a trained model -- no dataset/training
required, consistent with the rPPG module's approach.
"""
import numpy as np
import cv2

try:
    import mediapipe as mp
    _mp_face_mesh = mp.solutions.face_mesh
    _BACKEND = "mediapipe"
except Exception:
    _BACKEND = "unavailable"

# MediaPipe face-mesh landmark indices for the upper and lower lip
# midpoints (fixed topology, documented in MediaPipe's landmark map).
_UPPER_LIP_IDX = 13
_LOWER_LIP_IDX = 14


def _extract_lip_openness_signal(filepath: str, max_seconds: float = 8.0) -> tuple:
    """Returns (lip_openness_per_frame, fps). Measures vertical distance
    between upper and lower lip landmarks in each frame -- a simple,
    interpretable proxy for how open the mouth is."""
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video at: {filepath}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    max_frames = int(fps * max_seconds)
    openness = []

    if _BACKEND != "mediapipe":
        cap.release()
        return np.array([]), fps

    with _mp_face_mesh.FaceMesh(
        static_image_mode=False, max_num_faces=1, refine_landmarks=True,
        min_detection_confidence=0.5,
    ) as face_mesh:
        for _ in range(max_frames):
            ret, frame_bgr = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            h, w = frame_rgb.shape[:2]
            result = face_mesh.process(frame_rgb)

            if result.multi_face_landmarks:
                landmarks = result.multi_face_landmarks[0].landmark
                upper = landmarks[_UPPER_LIP_IDX]
                lower = landmarks[_LOWER_LIP_IDX]
                dist = abs((lower.y - upper.y) * h)
                openness.append(dist)
            else:
                openness.append(np.nan)

    cap.release()
    return np.array(openness), fps


def _extract_audio_energy_envelope(filepath: str, target_fps: float, num_frames: int) -> np.ndarray:
    """Extracts the audio track and returns a loudness value per video
    frame, resampled to match the video's frame rate so the two signals
    can be directly compared."""
    from moviepy.editor import VideoFileClip
    import librosa

    clip = VideoFileClip(filepath)
    if clip.audio is None:
        return np.array([])

    audio_array = clip.audio.to_soundarray(fps=16000)
    if audio_array.ndim > 1:
        audio_array = audio_array.mean(axis=1)  # collapse to mono

    hop_length = int(16000 / target_fps)
    energy = np.array([
        np.sqrt(np.mean(audio_array[i:i + hop_length] ** 2))
        for i in range(0, len(audio_array), hop_length)
    ])
    clip.close()
    return energy[:num_frames]


def analyze_lipsync(filepath: str, max_seconds: float = 8.0) -> dict:
    """Returns a sync_score (0-1, higher = better audio-lip correlation)
    and a note explaining any failure mode."""
    lip_signal, fps = _extract_lip_openness_signal(filepath, max_seconds=max_seconds)

    if len(lip_signal) < fps * 2:
        return {"sync_score": 0.5, "note": "Insufficient frames with a detected face"}

    valid_mask = ~np.isnan(lip_signal)
    if valid_mask.sum() < len(lip_signal) * 0.5:
        return {"sync_score": 0.5, "note": "Face/lips not consistently detected"}

    audio_energy = _extract_audio_energy_envelope(filepath, fps, len(lip_signal))
    if len(audio_energy) < len(lip_signal) * 0.5:
        return {"sync_score": 0.5, "note": "No usable audio track found"}

    n = min(len(lip_signal), len(audio_energy))
    lip_clean = np.nan_to_num(lip_signal[:n], nan=np.nanmean(lip_signal))
    audio_clean = audio_energy[:n]

    if np.std(lip_clean) < 1e-6 or np.std(audio_clean) < 1e-6:
        return {"sync_score": 0.4, "note": "No variation detected in lip movement or audio"}

    correlation = np.corrcoef(lip_clean, audio_clean)[0, 1]
    # Correlation ranges -1 to 1; map to a 0-1 "sync score" where higher
    # is more natural (positive correlation = mouth opens when louder).
    sync_score = float(np.clip((correlation + 1) / 2, 0.0, 1.0))

    return {"sync_score": round(sync_score, 4), "correlation": round(float(correlation), 4), "note": None}