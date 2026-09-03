"""One-off utility: extract still frames from genuine (non-AI-generated)
talking-head videos and add them as additional REAL training images,
to balance the new avatar-fake frames added via extract_avatar_frames.py."""
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training import config

REAL_VIDEOS_DIR = config.RAW_DIR / "real_talking_videos"
OUTPUT_DIR = config.RAW_DIR / "140k_real_and_fake_faces" / "real_vs_fake" / "real-vs-fake" / "train" / "real"


def main():
    if not REAL_VIDEOS_DIR.exists():
        print(f"Put genuine talking-head videos in: {REAL_VIDEOS_DIR}")
        sys.exit(1)

    if not OUTPUT_DIR.exists():
        print(f"Expected training real-folder not found at: {OUTPUT_DIR}")
        sys.exit(1)

    frame_count = 0
    for video_path in REAL_VIDEOS_DIR.iterdir():
        if video_path.suffix.lower() not in (".mp4", ".mov", ".avi", ".mkv"):
            continue
        cap = cv2.VideoCapture(str(video_path))
        idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if idx % 30 == 0:
                out_path = OUTPUT_DIR / f"realvid_{video_path.stem}_{idx}.jpg"
                cv2.imwrite(str(out_path), frame)
                frame_count += 1
            idx += 1
        cap.release()

    print(f"Extracted {frame_count} real-video frames into {OUTPUT_DIR}")


if __name__ == "__main__":
    main()