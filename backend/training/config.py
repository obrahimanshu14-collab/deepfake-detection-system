"""Shared configuration for the training pipeline."""
import os
from pathlib import Path
import torch

TRAINING_DIR = Path(__file__).resolve().parent
BACKEND_DIR = TRAINING_DIR.parent

DATA_DIR = BACKEND_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = BACKEND_DIR / "models"
LOGS_DIR = BACKEND_DIR / "logs"

for d in [RAW_DIR, PROCESSED_DIR, MODELS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DATASET_ROOT_HINT = RAW_DIR / "140k_real_and_fake_faces"
MANIFEST_PATH = PROCESSED_DIR / "manifest.csv"
CHECKPOINT_PATH = MODELS_DIR / "best_model.pt"

SEED = 42
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NUM_WORKERS = min(4, os.cpu_count() or 1)

LABEL_TO_IDX = {"REAL": 0, "FAKE": 1}
IMG_EXTENSIONS = (".jpg", ".jpeg", ".png")

# Fraction of the full dataset used for a first, CPU-feasible training run.
SUBSET_FRACTION = float(os.environ.get("DEEPFAKE_SUBSET_FRACTION", 0.08))
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

IMG_SIZE = 160
BATCH_SIZE = int(os.environ.get("DEEPFAKE_BATCH_SIZE", 16))
NUM_EPOCHS = int(os.environ.get("DEEPFAKE_NUM_EPOCHS", 15))
LR_BACKBONE = 1e-4
LR_HEAD = 1e-3
EARLY_STOPPING_PATIENCE = 4
LR_SCHEDULER_FACTOR = 0.5
LR_SCHEDULER_PATIENCE = 2