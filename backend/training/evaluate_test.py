"""Evaluate the held-out image test split without retraining."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training import config
from training.dataset import FaceDataset, eval_transform
from app.ml_model.model import load_trained_model


def main():
    if not config.MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found: {config.MANIFEST_PATH}")
    if not config.CHECKPOINT_PATH.exists():
        raise FileNotFoundError(f"Checkpoint not found: {config.CHECKPOINT_PATH}")

    df = pd.read_csv(config.MANIFEST_PATH)
    test_df = df[df["assigned_split"] == "test"].reset_index(drop=True)
    if test_df.empty:
        raise ValueError("No rows assigned to the test split.")

    loader = DataLoader(
        FaceDataset(test_df, transform=eval_transform),
        batch_size=config.BATCH_SIZE,
        shuffle=False,
        num_workers=config.NUM_WORKERS,
    )

    model = load_trained_model(str(config.CHECKPOINT_PATH), device=str(config.DEVICE))
    probabilities = []
    labels = []

    with torch.no_grad():
        for images, batch_labels in loader:
            logits = model(images.to(config.DEVICE))
            probabilities.extend(torch.sigmoid(logits).cpu().numpy().tolist())
            labels.extend(batch_labels.numpy().tolist())

    y_true = np.asarray(labels, dtype=int)
    y_prob = np.asarray(probabilities, dtype=float)
    y_pred = (y_prob >= 0.5).astype(int)

    metrics = {
        "samples": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) == 2 else None,
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }

    report = classification_report(
        y_true,
        y_pred,
        target_names=["REAL", "FAKE"],
        output_dict=True,
        zero_division=0,
    )

    output_dir = config.LOGS_DIR / "evaluation"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "test_metrics.json").write_text(json.dumps(metrics, indent=2))
    (output_dir / "classification_report.json").write_text(json.dumps(report, indent=2))
    pd.DataFrame({"label": y_true, "fake_probability": y_prob, "prediction": y_pred}).to_csv(
        output_dir / "test_predictions.csv", index=False
    )

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
