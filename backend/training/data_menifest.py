"""Build, clean, and split the image manifest (filepath -> label -> split)."""
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training import config


def build_manifest(dataset_root: Path) -> pd.DataFrame:
    rows = []
    for split in ["train", "valid", "test"]:
        split_dir = dataset_root / split
        if not split_dir.exists():
            continue
        for label_name in ["real", "fake"]:
            label_dir = split_dir / label_name
            if not label_dir.exists():
                continue
            for fp in label_dir.iterdir():
                if fp.suffix.lower() in config.IMG_EXTENSIONS:
                    rows.append({
                        "filepath": str(fp),
                        "label": label_name.upper(),
                        "split": split,
                    })
    return pd.DataFrame(rows)


def locate_dataset_root(search_root: Path) -> Path:
    for candidate in search_root.rglob("train"):
        if (candidate / "real").exists() and (candidate / "fake").exists():
            return candidate.parent
    raise FileNotFoundError(f"Could not locate a train/real,fake structure under {search_root}")


def is_readable_image(filepath: str) -> bool:
    return cv2.imread(filepath) is not None


def clean_manifest(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    tqdm.pandas(desc="Checking image readability")
    df = df.copy()
    df["is_readable"] = df["filepath"].progress_apply(is_readable_image)
    n_corrupt = (~df["is_readable"]).sum()
    print(f"Corrupted/unreadable images removed: {n_corrupt}")
    df = df[df["is_readable"]].drop(columns=["is_readable"])
    return df.reset_index(drop=True)


def build_splits(df: pd.DataFrame):
    if df.empty:
        empty = pd.DataFrame(columns=["filepath", "label", "split"])
        return empty, empty, empty

    if config.SUBSET_FRACTION < 1.0:
        working_df, _ = train_test_split(
            df, train_size=config.SUBSET_FRACTION,
            stratify=df["label"], random_state=config.SEED,
        )
    else:
        working_df = df.copy()

    train_df, temp_df = train_test_split(
        working_df, test_size=(config.VAL_RATIO + config.TEST_RATIO),
        stratify=working_df["label"], random_state=config.SEED,
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=config.TEST_RATIO / (config.VAL_RATIO + config.TEST_RATIO),
        stratify=temp_df["label"], random_state=config.SEED,
    )
    return (train_df.reset_index(drop=True), val_df.reset_index(drop=True),
            test_df.reset_index(drop=True))


def main():
    if not config.DATASET_ROOT_HINT.exists():
        print(f"Dataset not found at {config.DATASET_ROOT_HINT}")
        sys.exit(1)

    dataset_root = locate_dataset_root(config.DATASET_ROOT_HINT)
    print(f"Dataset root: {dataset_root}")

    manifest = build_manifest(dataset_root)
    print(f"Raw manifest size: {len(manifest):,}")

    manifest = clean_manifest(manifest)
    print(f"Cleaned manifest size: {len(manifest):,}")

    train_df, val_df, test_df = build_splits(manifest)
    combined = pd.concat([
        train_df.assign(assigned_split="train"),
        val_df.assign(assigned_split="val"),
        test_df.assign(assigned_split="test"),
    ], ignore_index=True)

    combined.to_csv(config.MANIFEST_PATH, index=False)
    print(f"\nManifest written to: {config.MANIFEST_PATH}")
    print(f"  train: {len(train_df):,}  val: {len(val_df):,}  test: {len(test_df):,}")


if __name__ == "__main__":
    main()