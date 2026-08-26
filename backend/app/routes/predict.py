import os
import tempfile
from pathlib import Path

import torch
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth_utils import get_current_user
from app.database.connection import get_db
from app.database.models import Prediction, User
from app.ml_model.audio_inference import predict_audio
from app.ml_model.audio_model import AudioDeepfakeDetector
from app.ml_model.inference import predict_image, predict_video
from app.ml_model.model import load_trained_model

router = APIRouter(prefix="/predict", tags=["Prediction"])

CHECKPOINT_PATH = "models/best_model.pt"
AUDIO_CHECKPOINT_PATH = "models/best_audio_model.pt"

MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_VIDEO_BYTES = 200 * 1024 * 1024
MAX_AUDIO_BYTES = 50 * 1024 * 1024

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}

_model = None
_audio_model = None


def get_model():
    global _model
    if _model is None:
        _model = load_trained_model(CHECKPOINT_PATH)
    return _model


def get_audio_model():
    global _audio_model
    if _audio_model is None:
        _audio_model = AudioDeepfakeDetector(pretrained=False)
        state_dict = torch.load(AUDIO_CHECKPOINT_PATH, map_location="cpu")
        _audio_model.load_state_dict(state_dict)
        _audio_model.eval()
    return _audio_model


async def _save_upload(file: UploadFile, allowed_extensions: set[str], max_bytes: int) -> tuple[str, str]:
    """Validate and stream an upload to a temporary file without loading it all into RAM."""
    original_name = file.filename or "upload"
    suffix = Path(original_name).suffix.lower()
    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed extensions: {', '.join(sorted(allowed_extensions))}",
        )

    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    total = 0
    try:
        with os.fdopen(fd, "wb") as tmp_file:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds the {max_bytes // (1024 * 1024)} MB upload limit.",
                    )
                tmp_file.write(chunk)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
    finally:
        await file.close()

    return tmp_path, original_name


@router.post("/image")
async def predict_image_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    model = get_model()
    tmp_path, original_name = await _save_upload(file, IMAGE_EXTENSIONS, MAX_IMAGE_BYTES)
    try:
        try:
            result = predict_image(tmp_path, model=model)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Image analysis failed: {exc}") from exc
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    new_prediction = Prediction(
        user_id=current_user.id,
        filename=original_name,
        file_type="image",
        predicted_label=result["label"],
        confidence=result["raw_fake_probability"],
    )
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)

    return {
        "prediction_id": new_prediction.id,
        "filename": original_name,
        "label": result["label"],
        "real_percent": result["real_percent"],
        "fake_percent": result["fake_percent"],
    }


@router.post("/video")
async def predict_video_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    model = get_model()
    tmp_path, original_name = await _save_upload(file, VIDEO_EXTENSIONS, MAX_VIDEO_BYTES)
    try:
        try:
            result = predict_video(tmp_path, model=model)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Video analysis failed: {exc}") from exc
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    new_prediction = Prediction(
        user_id=current_user.id,
        filename=original_name,
        file_type="video",
        predicted_label=result["label"],
        confidence=result["raw_fake_probability"],
    )
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)

    return {
        "prediction_id": new_prediction.id,
        "filename": original_name,
        "label": result["label"],
        "real_percent": result["real_percent"],
        "fake_percent": result["fake_percent"],
        "frames_analyzed": result.get("frames_analyzed", 0),
    }


@router.post("/audio")
async def predict_audio_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    model = get_audio_model()
    tmp_path, original_name = await _save_upload(file, AUDIO_EXTENSIONS, MAX_AUDIO_BYTES)
    try:
        try:
            result = predict_audio(tmp_path, model=model)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Audio analysis failed: {exc}") from exc
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    new_prediction = Prediction(
        user_id=current_user.id,
        filename=original_name,
        file_type="audio",
        predicted_label=result["label"],
        confidence=result["raw_fake_probability"],
    )
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)

    return {
        "prediction_id": new_prediction.id,
        "filename": original_name,
        "label": result["label"],
        "real_percent": result["real_percent"],
        "fake_percent": result["fake_percent"],
    }


@router.get("/history")
def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    predictions = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .all()
    )
    return [
        {
            "id": p.id,
            "filename": p.filename,
            "file_type": p.file_type,
            "label": p.predicted_label,
            "fake_probability": p.confidence,
            "created_at": p.created_at,
        }
        for p in predictions
    ]
