"""
Face detection and alignment utilities.

Primary backend: MediaPipe FaceMesh. Falls back to OpenCV's bundled Haar
Cascade detector automatically if MediaPipe's legacy API is unavailable,
so this works regardless of which MediaPipe build ends up installed.
"""
from __future__ import annotations
from pathlib import Path

import cv2
import numpy as np

_BACKEND = None
_mp_face_mesh = None
_LEFT_EYE_IDX = 33
_RIGHT_EYE_IDX = 263

try:
    import mediapipe as mp
    _mp_face_mesh = mp.solutions.face_mesh
    _BACKEND = "mediapipe"
except Exception:
    _BACKEND = "haar"

if _BACKEND == "haar":
    _CASCADE_DIR = Path(__file__).resolve().parent / "cascades"
    _face_cascade = cv2.CascadeClassifier(
        str(_CASCADE_DIR / "haarcascade_frontalface_default.xml")
    )
    _eye_cascade = cv2.CascadeClassifier(
        str(_CASCADE_DIR / "haarcascade_eye.xml")
    )

print(f"[face_utils] Using face detection backend: {_BACKEND}")


def _detect_align_mediapipe(image_rgb: np.ndarray, output_size: int) -> np.ndarray | None:
    h, w = image_rgb.shape[:2]
    with _mp_face_mesh.FaceMesh(
        static_image_mode=True, max_num_faces=1, refine_landmarks=False,
        min_detection_confidence=0.5,
    ) as face_mesh:
        result = face_mesh.process(image_rgb)

    if not result.multi_face_landmarks:
        return None

    landmarks = result.multi_face_landmarks[0].landmark
    left_eye = np.array([landmarks[_LEFT_EYE_IDX].x * w, landmarks[_LEFT_EYE_IDX].y * h])
    right_eye = np.array([landmarks[_RIGHT_EYE_IDX].x * w, landmarks[_RIGHT_EYE_IDX].y * h])

    dy, dx = right_eye[1] - left_eye[1], right_eye[0] - left_eye[0]
    angle = np.degrees(np.arctan2(dy, dx))
    eyes_center = tuple(((left_eye + right_eye) / 2).astype(int).tolist())
    rotation_matrix = cv2.getRotationMatrix2D(eyes_center, angle, scale=1.0)
    aligned = cv2.warpAffine(image_rgb, rotation_matrix, (w, h))

    xs = [lm.x * w for lm in landmarks]
    ys = [lm.y * h for lm in landmarks]
    margin = 0.25
    x_min, x_max = max(0, min(xs) - margin * w), min(w, max(xs) + margin * w)
    y_min, y_max = max(0, min(ys) - margin * h), min(h, max(ys) + margin * h)

    face_crop = aligned[int(y_min):int(y_max), int(x_min):int(x_max)]
    if face_crop.size == 0:
        return None
    return cv2.resize(face_crop, (output_size, output_size), interpolation=cv2.INTER_AREA)


def _detect_align_haar(image_rgb: np.ndarray, output_size: int) -> np.ndarray | None:
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    faces = _face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
    if len(faces) == 0:
        return None

    x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])

    face_roi_gray = gray[y:y + fh, x:x + fw]
    eyes = _eye_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.1, minNeighbors=5)

    working_image = image_rgb
    if len(eyes) >= 2:
        eyes_sorted = sorted(eyes, key=lambda e: e[0])[:2]
        (ex1, ey1, ew1, eh1), (ex2, ey2, ew2, eh2) = eyes_sorted
        left_eye = np.array([x + ex1 + ew1 / 2, y + ey1 + eh1 / 2])
        right_eye = np.array([x + ex2 + ew2 / 2, y + ey2 + eh2 / 2])
        dy, dx = right_eye[1] - left_eye[1], right_eye[0] - left_eye[0]
        angle = np.degrees(np.arctan2(dy, dx))
        eyes_center = tuple(((left_eye + right_eye) / 2).astype(int).tolist())
        h, w = image_rgb.shape[:2]
        rotation_matrix = cv2.getRotationMatrix2D(eyes_center, angle, scale=1.0)
        working_image = cv2.warpAffine(image_rgb, rotation_matrix, (w, h))
        gray2 = cv2.cvtColor(working_image, cv2.COLOR_RGB2GRAY)
        faces2 = _face_cascade.detectMultiScale(gray2, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
        if len(faces2) > 0:
            x, y, fw, fh = max(faces2, key=lambda f: f[2] * f[3])

    margin = 0.25
    x_min = max(0, int(x - margin * fw))
    y_min = max(0, int(y - margin * fh))
    x_max = min(working_image.shape[1], int(x + fw + margin * fw))
    y_max = min(working_image.shape[0], int(y + fh + margin * fh))

    face_crop = working_image[y_min:y_max, x_min:x_max]
    if face_crop.size == 0:
        return None
    return cv2.resize(face_crop, (output_size, output_size), interpolation=cv2.INTER_AREA)


def detect_and_align_face(image_rgb: np.ndarray, output_size: int = 160) -> np.ndarray | None:
    if _BACKEND == "mediapipe":
        return _detect_align_mediapipe(image_rgb, output_size)
    return _detect_align_haar(image_rgb, output_size)


def load_and_align(filepath: str, output_size: int = 160) -> np.ndarray:
    img_bgr = cv2.imread(filepath)
    if img_bgr is None:
        raise FileNotFoundError(f"Could not read image at: {filepath}")
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    face = detect_and_align_face(img_rgb, output_size=output_size)
    if face is None:
        face = cv2.resize(img_rgb, (output_size, output_size), interpolation=cv2.INTER_AREA)
    return face

def detect_face_bbox(image_rgb: np.ndarray):
    """Return (x, y, w, h) of the largest detected face, or None.

    Unlike detect_and_align_face (which returns a cropped, rotated face
    image), this returns raw bounding-box coordinates in the ORIGINAL
    frame -- needed for rPPG, which must sample color values directly
    from unprocessed camera pixels, not a rotated/normalized crop.
    """
    if _BACKEND == "haar":
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        faces = _face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        if len(faces) == 0:
            return None
        return tuple(max(faces, key=lambda f: f[2] * f[3]))

    with _mp_face_mesh.FaceMesh(
        static_image_mode=True, max_num_faces=1, refine_landmarks=False,
        min_detection_confidence=0.5,
    ) as face_mesh:
        result = face_mesh.process(image_rgb)
    if not result.multi_face_landmarks:
        return None
    h, w = image_rgb.shape[:2]
    xs = [lm.x * w for lm in result.multi_face_landmarks[0].landmark]
    ys = [lm.y * h for lm in result.multi_face_landmarks[0].landmark]
    x_min, x_max, y_min, y_max = min(xs), max(xs), min(ys), max(ys)
    return (int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min))