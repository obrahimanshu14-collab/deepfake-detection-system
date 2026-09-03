"""
Calibration utility: measures the rPPG peak_ratio distribution over a
set of KNOWN-REAL videos, so the authenticity_score normalization
constant (currently a guessed 0.25) can be replaced with a value
derived from actual data.

Run this whenever new real/fake videos are added to the external test
sets, to keep the calibration current.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training import config
from app.ml_model.rppg import extract_rgb_signal, _pos_algorithm, _bandpass_filter, MIN_HR_HZ, MAX_HR_HZ

REAL_DIR = config.BACKEND_DIR / "data" / "external_test_video" / "real"
FAKE_DIR = config.BACKEND_DIR / "data" / "external_test_video" / "fake"
VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".mkv")


def measure_peak_ratio(filepath: str) -> float:
    rgb_signal, fps = extract_rgb_signal(filepath)
    if len(rgb_signal) < fps * 3:
        return None
    pulse_signal = _pos_algorithm(rgb_signal)
    filtered = _bandpass_filter(pulse_signal, fps, MIN_HR_HZ, MAX_HR_HZ)
    fft_vals = np.abs(np.fft.rfft(filtered))
    freqs = np.fft.rfftfreq(len(filtered), d=1.0 / fps)
    band_mask = (freqs >= MIN_HR_HZ) & (freqs <= MAX_HR_HZ)
    band_power = fft_vals[band_mask]
    if len(band_power) == 0:
        return None
    return float(band_power.max() / (band_power.sum() + 1e-8))


def main():
    real_ratios, fake_ratios = [], []

    for label, folder, bucket in [("REAL", REAL_DIR, real_ratios), ("FAKE", FAKE_DIR, fake_ratios)]:
        if not folder.exists():
            continue
        for filepath in folder.iterdir():
            if filepath.suffix.lower() not in VIDEO_EXTENSIONS:
                continue
            ratio = measure_peak_ratio(str(filepath))
            if ratio is not None:
                print(f"{label}: {filepath.name} -> peak_ratio = {ratio:.4f}")
                bucket.append(ratio)

    print("\n--- Summary ---")
    if real_ratios:
        print(f"REAL videos  -- mean: {np.mean(real_ratios):.4f}, std: {np.std(real_ratios):.4f}, "
              f"min: {min(real_ratios):.4f}, max: {max(real_ratios):.4f}")
    if fake_ratios:
        print(f"FAKE videos  -- mean: {np.mean(fake_ratios):.4f}, std: {np.std(fake_ratios):.4f}, "
              f"min: {min(fake_ratios):.4f}, max: {max(fake_ratios):.4f}")

    if real_ratios and fake_ratios:
        separation = np.mean(real_ratios) - np.mean(fake_ratios)
        print(f"\nMean separation (real - fake): {separation:.4f}")
        if abs(separation) < 0.02:
            print("WARNING: minimal separation -- rPPG signal may not be reliable "
                  "on this data (likely due to heavy compression). Consider "
                  "collecting more/less-compressed samples before trusting this signal.")


if __name__ == "__main__":
    main()