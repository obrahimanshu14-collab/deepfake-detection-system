"""One-off utility: extract still frames from AI-avatar-style fake
videos and add them as additional FAKE training images, so the CNN
learns this generation method's artifacts too, not just StyleGAN's
(which the original 140k dataset exclusively represents)."""
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training import config

AVATAR_VIDEOS_DIR = config.RAW_DIR / "avatar_fake_videos"
OUTPUT_DIR = config.RAW_DIR / "140k_real_and_fake_faces" / "real_vs_fake" / "real-vs-fake" / "train" / "fake"


def main():
    if not AVATAR_VIDEOS_DIR.exists():
        print(f"Put avatar-style fake videos in: {AVATAR_VIDEOS_DIR}")
        sys.exit(1)

    if not OUTPUT_DIR.exists():
        print(f"Expected training fake-folder not found at: {OUTPUT_DIR}")
        print("Check your dataset path structure with: dir data\\raw\\140k_real_and_fake_faces")
        sys.exit(1)

    frame_count = 0
    for video_path in AVATAR_VIDEOS_DIR.iterdir():
        if video_path.suffix.lower() not in (".mp4", ".mov", ".avi", ".mkv"):
            continue
        cap = cv2.VideoCapture(str(video_path))
        idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if idx % 30 == 0:  # roughly one frame per second
                out_path = OUTPUT_DIR / f"avatar_{video_path.stem}_{idx}.jpg"
                cv2.imwrite(str(out_path), frame)
                frame_count += 1
            idx += 1
        cap.release()

    print(f"Extracted {frame_count} avatar-fake frames into {OUTPUT_DIR}")


if __name__ == "__main__":
    main()