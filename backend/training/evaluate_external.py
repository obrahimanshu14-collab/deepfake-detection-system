"""
Evaluate the trained model on a hand-curated, out-of-distribution test set
-- images NOT from the training dataset -- to get an honest read on
real-world generalization, separate from the train/val/test split.
"""
import sys
from pathlib import Path

import pandas as pd
import torch
from sklearn.metrics import confusion_matrix

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training import config
from app.ml_model.model import DeepfakeDetector
from app.ml_model.inference import predict_image

EXTERNAL_TEST_DIR = config.BACKEND_DIR / "data" / "external_test"


def load_model():
    model = DeepfakeDetector(pretrained=False).to(config.DEVICE)
    state_dict = torch.load(config.CHECKPOINT_PATH, map_location=config.DEVICE)
    model.load_state_dict(state_dict)
    model.eval()
    return model


def collapse(label: str) -> str:
    """Collapse the 5-tier label into REAL/FAKE/Uncertain for a simple accuracy readout."""
    if label in ("REAL", "Possibly Real"):
        return "REAL"
    if label in ("FAKE", "Possibly Fake"):
        return "FAKE"
    return "Uncertain"


def main():
    if not EXTERNAL_TEST_DIR.exists():
        print(f"Create {EXTERNAL_TEST_DIR}\\real and \\fake, add images, then re-run.")
        sys.exit(1)

    model = load_model()
    rows = []

    for true_label, folder in [("REAL", "real"), ("FAKE", "fake")]:
        folder_path = EXTERNAL_TEST_DIR / folder
        if not folder_path.exists():
            continue
        for filepath in folder_path.iterdir():
            if filepath.suffix.lower() not in config.IMG_EXTENSIONS:
                continue
            result = predict_image(str(filepath), model=model, device=str(config.DEVICE))
            rows.append({
                "filename": filepath.name,
                "true_label": true_label,
                "predicted_label": result["label"],
                "fake_probability": result["raw_fake_probability"],
            })

    if not rows:
        print("No images found in external_test/real or external_test/fake.")
        sys.exit(1)

    df = pd.DataFrame(rows)
    print(df.to_string(index=False))

    df["collapsed"] = df["predicted_label"].apply(collapse)
    certain = df[df["collapsed"] != "Uncertain"]

    if len(certain) > 0:
        accuracy = (certain["collapsed"] == certain["true_label"]).mean()
        print(f"\nAccuracy (excluding Uncertain cases): {accuracy:.2%}")
    print(f"Uncertain cases: {len(df) - len(certain)} / {len(df)}")

    if len(certain) > 0:
        print("\nConfusion matrix (REAL/FAKE, certain cases only):")
        print(confusion_matrix(certain["true_label"], certain["collapsed"], labels=["REAL", "FAKE"]))


if __name__ == "__main__":
    main()