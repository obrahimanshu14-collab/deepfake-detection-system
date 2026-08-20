"""One-time script to download the training dataset from Kaggle."""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training import config

DATASET_KAGGLE_SLUG = "xhlulu/140k-real-and-fake-faces"


def main():
    if config.DATASET_ROOT_HINT.exists() and any(config.DATASET_ROOT_HINT.rglob("*.csv")):
        print(f"Dataset already present at: {config.DATASET_ROOT_HINT}")
        return

    print(f"Downloading '{DATASET_KAGGLE_SLUG}' via kagglehub...")
    try:
        import kagglehub
        downloaded_path = Path(kagglehub.dataset_download(DATASET_KAGGLE_SLUG))
        print(f"Downloaded to: {downloaded_path}")
        config.DATASET_ROOT_HINT.parent.mkdir(parents=True, exist_ok=True)
        if not config.DATASET_ROOT_HINT.exists():
            shutil.copytree(downloaded_path, config.DATASET_ROOT_HINT)
        print(f"Dataset ready at: {config.DATASET_ROOT_HINT}")
    except Exception as e:
        print(f"Download failed: {e}")
        print("Check that C:\\Users\\himan\\.kaggle\\kaggle.json exists and is valid.")
        sys.exit(1)


if __name__ == "__main__":
    main()