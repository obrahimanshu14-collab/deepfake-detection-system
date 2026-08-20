"""One-time script to download the audio deepfake dataset from Kaggle."""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training import config

AUDIO_DATASET_KAGGLE_SLUG = "jayjoshi37/deepfake-audio-dataset-fake-vs-real-speech"
AUDIO_DATASET_ROOT_HINT = config.RAW_DIR / "deepfake_audio_dataset"

def main():
    if AUDIO_DATASET_ROOT_HINT.exists() and any(AUDIO_DATASET_ROOT_HINT.rglob("*.wav")):
        print(f"Audio dataset already present at: {AUDIO_DATASET_ROOT_HINT}")
        return

    print(f"Downloading '{AUDIO_DATASET_KAGGLE_SLUG}' via kagglehub...")
    try:
        import kagglehub
        downloaded_path = Path(kagglehub.dataset_download(AUDIO_DATASET_KAGGLE_SLUG))
        print(f"Downloaded to: {downloaded_path}")
        AUDIO_DATASET_ROOT_HINT.parent.mkdir(parents=True, exist_ok=True)
        if not AUDIO_DATASET_ROOT_HINT.exists():
            shutil.copytree(downloaded_path, AUDIO_DATASET_ROOT_HINT)
        print(f"Audio dataset ready at: {AUDIO_DATASET_ROOT_HINT}")
    except Exception as e:
        print(f"Download failed: {e}")
        print("Check that C:\\Users\\himan\\.kaggle\\kaggle.json exists and is valid.")
        sys.exit(1)


if __name__ == "__main__":
    main()