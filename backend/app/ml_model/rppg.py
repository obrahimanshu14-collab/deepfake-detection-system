"""
rPPG (remote photoplethysmography) using the POS (Plane-Orthogonal-to-Skin)
algorithm -- combines all three RGB channels to cancel out illumination and
compression noise, making it substantially more robust than naive
single-channel (green-only) approaches on compressed, real-world video
(e.g. WhatsApp/social-media exports).

Reference: Wang, den Brinker, Stuijk, de Haan (2017),
"Algorithmic Principles of Remote PPG"

Classical signal processing, not a trained model -- no dataset/training
required.
"""
import cv2
import numpy as np
from scipy.signal import butter, filtfilt

from app.ml_model.face_utils import detect_face_bbox

MIN_HR_HZ = 0.7   # 42 BPM
MAX_HR_HZ = 4.0   # 240 BPM
DEFAULT_FPS = 30.0


def _forehead_roi(bbox):
    x, y, w, h = bbox
    fx = x + int(w * 0.30)
    fy = y + int(h * 0.05)
    fw = int(w * 0.40)
    fh = int(h * 0.15)
    return fx, fy, fw, fh


def _sanitize_fps(fps: float) -> float:
    if fps is None or fps <= 1 or fps > 120:
        return DEFAULT_FPS
    return fps


def extract_rgb_signal(filepath: str, max_seconds: float = 10.0) -> tuple:
    """Returns an (N, 3) array of per-frame mean [R, G, B] values from the
    forehead region, plus the sanitized fps. All three channels are kept
    (not just green) because the POS algorithm needs all three to cancel
    illumination/compression noise."""
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video at: {filepath}")

    fps = _sanitize_fps(cap.get(cv2.CAP_PROP_FPS))
    max_frames = int(fps * max_seconds)

    rgb_means = []
    last_bbox = None

    for _ in range(max_frames):
        ret, frame_bgr = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        if last_bbox is None or len(rgb_means) % 5 == 0:
            bbox = detect_face_bbox(frame_rgb)
            if bbox is not None:
                last_bbox = bbox

        if last_bbox is None:
            continue

        fx, fy, fw, fh = _forehead_roi(last_bbox)
        roi = frame_rgb[fy:fy + fh, fx:fx + fw]
        if roi.size == 0:
            continue

        rgb_means.append(roi.reshape(-1, 3).mean(axis=0))

    cap.release()
    return np.array(rgb_means), fps


def _pos_algorithm(rgb_signal: np.ndarray) -> np.ndarray:
    """POS projection: temporally normalizes each RGB channel, then
    projects onto two chrominance-like axes designed so that illumination
    and motion artifacts (which affect all channels similarly) cancel
    out, while the blood-volume pulse (which affects channels
    differently, due to hemoglobin's wavelength-dependent absorption)
    survives.
    """
    mean_rgb = rgb_signal.mean(axis=0)
    mean_rgb[mean_rgb == 0] = 1e-8  # avoid divide-by-zero on degenerate ROIs
    normalized = rgb_signal / mean_rgb

    Rn, Gn, Bn = normalized[:, 0], normalized[:, 1], normalized[:, 2]

    S1 = Gn - Bn
    S2 = Gn + Bn - 2 * Rn

    std_s1, std_s2 = np.std(S1), np.std(S2)
    alpha = std_s1 / std_s2 if std_s2 > 1e-8 else 0.0

    pulse_signal = S1 + alpha * S2
    return pulse_signal


def _bandpass_filter(signal: np.ndarray, fps: float, low_hz: float, high_hz: float) -> np.ndarray:
    nyquist = fps / 2.0
    low = max(low_hz / nyquist, 0.01)
    high = min(high_hz / nyquist, 0.99)
    b, a = butter(N=3, Wn=[low, high], btype="band")
    return filtfilt(b, a, signal)


def compute_authenticity_score(rgb_signal: np.ndarray, fps: float) -> dict:
    min_required_samples = int(fps * 3)
    if len(rgb_signal) < min_required_samples:
        return {"authenticity_score": 0.5, "estimated_bpm": None, "note": "Insufficient frames for analysis"}

    pulse_signal = _pos_algorithm(rgb_signal)
    filtered = _bandpass_filter(pulse_signal, fps, MIN_HR_HZ, MAX_HR_HZ)

    fft_vals = np.abs(np.fft.rfft(filtered))
    freqs = np.fft.rfftfreq(len(filtered), d=1.0 / fps)

    band_mask = (freqs >= MIN_HR_HZ) & (freqs <= MAX_HR_HZ)
    if not np.any(band_mask):
        return {"authenticity_score": 0.3, "estimated_bpm": None, "note": "No usable frequency band"}

    band_power = fft_vals[band_mask]
    band_freqs = freqs[band_mask]

    peak_idx = np.argmax(band_power)
    peak_power = band_power[peak_idx]
    estimated_bpm = float(band_freqs[peak_idx] * 60)

    total_band_energy = band_power.sum() + 1e-8
    peak_ratio = float(peak_power / total_band_energy)
    authenticity_score = float(np.clip(peak_ratio / 0.25, 0.0, 1.0))

    edge_artifact = abs(estimated_bpm - MIN_HR_HZ * 60) < 1.0
    if edge_artifact:
        authenticity_score = min(authenticity_score, 0.3)

    return {
        "authenticity_score": round(authenticity_score, 4),
        "estimated_bpm": round(estimated_bpm, 1),
        "note": "Edge artifact -- likely no genuine peak" if edge_artifact else None,
    }


def analyze_video(filepath: str, max_seconds: float = 10.0) -> dict:
    rgb_signal, fps = extract_rgb_signal(filepath, max_seconds=max_seconds)
    return compute_authenticity_score(rgb_signal, fps)