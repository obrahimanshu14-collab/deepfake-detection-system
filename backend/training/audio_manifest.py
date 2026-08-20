"""Build, clean, and split the audio manifest (filepath -> label -> split)."""
import sys
from pathlib import Path

import librosa
import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training import config

AUDIO_DATASET_ROOT = config.RAW_DIR / "deepfake_audio_dataset" / "deepfake_audio_dataset_jay15k"
AUDIO_MANIFEST_PATH = config.PROCESSED_DIR / "audio_manifest.csv"
AUDIO_EXTENSIONS = (".wav", ".mp3")


def build_audio_manifest(dataset_root: Path) -> pd.DataFrame:
    rows = []
    for label_name in ["real", "fake"]:
        label_dir = dataset_root / label_name
        if not label_dir.exists():
            continue
        for fp in label_dir.iterdir():
            if fp.suffix.lower() in AUDIO_EXTENSIONS:
                rows.append({"filepath": str(fp), "label": label_name.upper()})
    return pd.DataFrame(rows)


def is_readable_audio(filepath: str) -> bool:
    try:
        librosa.load(filepath, sr=16000, duration=1.0)
        return True
    except Exception:
        return False


def clean_manifest(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    tqdm.pandas(desc="Checking audio readability")
    df = df.copy()
    df["is_readable"] = df["filepath"].progress_apply(is_readable_audio)
    n_corrupt = (~df["is_readable"]).sum()
    print(f"Corrupted/unreadable audio files removed: {n_corrupt}")
    df = df[df["is_readable"]].drop(columns=["is_readable"])
    return df.reset_index(drop=True)


def main():
    if not AUDIO_DATASET_ROOT.exists():
        print(f"Audio dataset not found at {AUDIO_DATASET_ROOT}.")
        sys.exit(1)

    manifest = build_audio_manifest(AUDIO_DATASET_ROOT)
    print(f"Raw audio manifest size: {len(manifest):,}")
    print(manifest["label"].value_counts())

    manifest = clean_manifest(manifest)
    print(f"Cleaned manifest size: {len(manifest):,}")

    subset_fraction = 0.5  # small dataset overall, so use a larger fraction
    if subset_fraction < 1.0 and len(manifest) > 0:
        working_df, _ = train_test_split(
            manifest, train_size=subset_fraction, stratify=manifest["label"], random_state=config.SEED,
        )
    else:
        working_df = manifest

    train_df, temp_df = train_test_split(
        working_df, test_size=0.30, stratify=working_df["label"], random_state=config.SEED,
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, stratify=temp_df["label"], random_state=config.SEED,
    )

    combined = pd.concat([
        train_df.assign(assigned_split="train"),
        val_df.assign(assigned_split="val"),
        test_df.assign(assigned_split="test"),
    ], ignore_index=True)

    combined.to_csv(AUDIO_MANIFEST_PATH, index=False)
    print(f"\nAudio manifest written to: {AUDIO_MANIFEST_PATH}")
    print(f"  train: {len(train_df):,}  val: {len(val_df):,}  test: {len(test_df):,}")


if __name__ == "__main__":
    main()