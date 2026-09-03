"""
Evaluate the video pipeline (CNN + rPPG ensemble) on hand-curated
real and AI-generated videos -- never seen during training, and
specifically chosen to include the "talking avatar" category the
image-only model was found to miss.
"""
import sys
from pathlib import Path

import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training import config
from app.ml_model.model import DeepfakeDetector
from app.ml_model.inference import predict_video

EXTERNAL_TEST_DIR = config.BACKEND_DIR / "data" / "external_test_video"
VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".mkv")


def load_model():
    model = DeepfakeDetector(pretrained=False).to(config.DEVICE)
    state_dict = torch.load(config.CHECKPOINT_PATH, map_location=config.DEVICE)
    model.load_state_dict(state_dict)
    model.eval()
    return model


def collapse(label: str) -> str:
    if label in ("REAL", "Possibly Real"):
        return "REAL"
    if label in ("FAKE", "Possibly Fake"):
        return "FAKE"
    return "Uncertain"


def main():
    if not EXTERNAL_TEST_DIR.exists():
        print(f"Create {EXTERNAL_TEST_DIR}\\real and \\fake, add videos, then re-run.")
        sys.exit(1)

    model = load_model()
    rows = []

    for true_label, folder in [("REAL", "real"), ("FAKE", "fake")]:
        folder_path = EXTERNAL_TEST_DIR / folder
        if not folder_path.exists():
            continue
        for filepath in folder_path.iterdir():
            if filepath.suffix.lower() not in VIDEO_EXTENSIONS:
                continue
            print(f"Analyzing: {filepath.name} ...")
            result = predict_video(str(filepath), model=model, device=str(config.DEVICE))
            signals = result.get("signals", {})
            rows.append({
                "filename": filepath.name,
                "true_label": true_label,
                "predicted_label": result["label"],
                "real_percent": result["real_percent"],
                "fake_percent": result["fake_percent"],
                "cnn_fake_probability": signals.get("cnn_fake_probability"),
                "rppg_authenticity": signals.get("rppg_authenticity_score"),
                "rppg_bpm": signals.get("rppg_estimated_bpm"),
                "frames_analyzed": result.get("frames_analyzed"),
            })

    if not rows:
        print("No videos found in external_test_video/real or /fake.")
        sys.exit(1)

    df = pd.DataFrame(rows)
    print("\n" + df.to_string(index=False))

    df["collapsed"] = df["predicted_label"].apply(collapse)
    certain = df[df["collapsed"] != "Uncertain"]
    if len(certain) > 0:
        accuracy = (certain["collapsed"] == certain["true_label"]).mean()
        print(f"\nAccuracy (excluding Uncertain): {accuracy:.2%}")
    print(f"Uncertain cases: {len(df) - len(certain)} / {len(df)}")


if __name__ == "__main__":
    main()