"""Train the deepfake detector and evaluate the held-out test split."""
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
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
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training import config
from training.dataset import FaceDataset, train_transform, eval_transform
from app.ml_model.model import DeepfakeDetector


def set_seed(seed: int = config.SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def count_parameters(model):
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable


class EarlyStopping:
    def __init__(self, patience=config.EARLY_STOPPING_PATIENCE, min_delta=1e-4):
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss = float("inf")
        self.counter = 0
        self.should_stop = False

    def step(self, val_loss):
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True
        return self.should_stop


def run_epoch(model, loader, criterion, optimizer=None):
    is_training = optimizer is not None
    model.train() if is_training else model.eval()

    total_loss, correct, total = 0.0, 0, 0
    with torch.set_grad_enabled(is_training):
        for images, labels in tqdm(loader, desc="Train" if is_training else "Eval", leave=False):
            images, labels = images.to(config.DEVICE), labels.to(config.DEVICE)

            if is_training:
                optimizer.zero_grad()

            logits = model(images)
            loss = criterion(logits, labels)

            if is_training:
                loss.backward()
                optimizer.step()

            total_loss += loss.item() * images.size(0)
            preds = (torch.sigmoid(logits) > 0.5).float()
            correct += (preds == labels).sum().item()
            total += images.size(0)

    return total_loss / total, correct / total


def evaluate_test_set(model, loader, dataframe):
    """Evaluate the untouched test split and persist detailed baseline metrics."""
    model.eval()
    all_probs = []
    all_labels = []

    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Test", leave=False):
            images = images.to(config.DEVICE)
            logits = model(images)
            probs = torch.sigmoid(logits).detach().cpu().numpy().reshape(-1)
            all_probs.extend(probs.tolist())
            all_labels.extend(labels.numpy().reshape(-1).astype(int).tolist())

    y_true = np.asarray(all_labels, dtype=int)
    y_prob = np.asarray(all_probs, dtype=float)
    y_pred = (y_prob >= 0.5).astype(int)

    metrics = {
        "threshold": 0.5,
        "num_test_samples": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }

    if len(np.unique(y_true)) == 2:
        metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob))
    else:
        metrics["roc_auc"] = None

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    metrics["confusion_matrix"] = {
        "REAL": {"REAL": int(cm[0, 0]), "FAKE": int(cm[0, 1])},
        "FAKE": {"REAL": int(cm[1, 0]), "FAKE": int(cm[1, 1])},
    }

    report = classification_report(
        y_true,
        y_pred,
        labels=[0, 1],
        target_names=["REAL", "FAKE"],
        output_dict=True,
        zero_division=0,
    )
    metrics["classification_report"] = report

    predictions = dataframe.copy()
    predictions["fake_probability"] = y_prob
    predictions["predicted_label"] = np.where(y_pred == 1, "FAKE", "REAL")
    predictions.to_csv(config.LOGS_DIR / "test_predictions.csv", index=False)

    with open(config.LOGS_DIR / "test_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("\n===== HELD-OUT TEST RESULTS =====")
    print(f"Samples   : {metrics['num_test_samples']}")
    print(f"Accuracy  : {metrics['accuracy']:.4f}")
    print(f"Precision : {metrics['precision']:.4f}")
    print(f"Recall    : {metrics['recall']:.4f}")
    print(f"F1        : {metrics['f1']:.4f}")
    print(f"ROC-AUC   : {metrics['roc_auc'] if metrics['roc_auc'] is not None else 'N/A'}")
    print("Confusion matrix [REAL, FAKE]:")
    print(cm)
    print(f"\nDetailed metrics: {config.LOGS_DIR / 'test_metrics.json'}")
    print(f"Predictions     : {config.LOGS_DIR / 'test_predictions.csv'}")

    return metrics


def main():
    set_seed()

    if not config.MANIFEST_PATH.exists():
        print(f"Manifest not found at {config.MANIFEST_PATH}. Run data_menifest.py first.")
        sys.exit(1)

    df = pd.read_csv(config.MANIFEST_PATH)
    train_df = df[df["assigned_split"] == "train"].reset_index(drop=True)
    val_df = df[df["assigned_split"] == "val"].reset_index(drop=True)
    test_df = df[df["assigned_split"] == "test"].reset_index(drop=True)

    print(f"Train: {len(train_df)}  Val: {len(val_df)}  Test: {len(test_df)}")

    train_loader = DataLoader(
        FaceDataset(train_df, transform=train_transform), batch_size=config.BATCH_SIZE,
        shuffle=True, num_workers=config.NUM_WORKERS, drop_last=True,
    )
    val_loader = DataLoader(
        FaceDataset(val_df, transform=eval_transform), batch_size=config.BATCH_SIZE,
        shuffle=False, num_workers=config.NUM_WORKERS,
    )
    test_loader = DataLoader(
        FaceDataset(test_df, transform=eval_transform), batch_size=config.BATCH_SIZE,
        shuffle=False, num_workers=config.NUM_WORKERS,
    )

    model = DeepfakeDetector(pretrained=True).to(config.DEVICE)
    total, trainable = count_parameters(model)
    print(f"Total params: {total:,}  Trainable: {trainable:,} ({100*trainable/total:.1f}%)")

    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam([
        {"params": [p for p in model.features.parameters() if p.requires_grad], "lr": config.LR_BACKBONE},
        {"params": model.head.parameters(), "lr": config.LR_HEAD},
    ])
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=config.LR_SCHEDULER_FACTOR, patience=config.LR_SCHEDULER_PATIENCE,
    )
    early_stopping = EarlyStopping()

    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
    best_val_loss = float("inf")

    for epoch in range(1, config.NUM_EPOCHS + 1):
        train_loss, train_acc = run_epoch(model, train_loader, criterion, optimizer)
        val_loss, val_acc = run_epoch(model, val_loader, criterion, optimizer=None)
        scheduler.step(val_loss)

        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        print(f"Epoch {epoch:02d}/{config.NUM_EPOCHS} | "
              f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} | "
              f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), config.CHECKPOINT_PATH)
            print(f"  -> New best model saved (val_loss={val_loss:.4f})")

        if early_stopping.step(val_loss):
            print(f"Early stopping after epoch {epoch}.")
            break

    pd.DataFrame(history).to_csv(config.LOGS_DIR / "training_history.csv", index=False)

    # Evaluate the checkpoint selected using validation loss, never the test set.
    if not config.CHECKPOINT_PATH.exists():
        print(f"Best checkpoint not found at {config.CHECKPOINT_PATH}; skipping test evaluation.")
        sys.exit(1)

    model.load_state_dict(torch.load(config.CHECKPOINT_PATH, map_location=config.DEVICE))
    evaluate_test_set(model, test_loader, test_df)

    print(f"\nTraining complete. Best model at: {config.CHECKPOINT_PATH}")


if __name__ == "__main__":
    main()
