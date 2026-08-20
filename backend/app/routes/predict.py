import os
import shutil
import tempfile
from pathlib import Path

import torch
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Prediction, User
from app.auth_utils import get_current_user
from app.ml_model.inference import predict_image, predict_video
from app.ml_model.model import load_trained_model
from app.ml_model.audio_model import AudioDeepfakeDetector
from app.ml_model.audio_inference import predict_audio

router = APIRouter(prefix="/predict", tags=["Prediction"])

CHECKPOINT_PATH = "models/best_model.pt"
AUDIO_CHECKPOINT_PATH = "models/best_audio_model.pt"

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


@router.post("/image")
async def predict_image_endpoint(
    file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    model = get_model()
    suffix = Path(file.filename).suffix or ".jpg"
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
        try:
            result = predict_image(tmp_path, model=model)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.remove(tmp_path)

    new_prediction = Prediction(
        user_id=current_user.id, filename=file.filename, file_type="image",
        predicted_label=result["label"], confidence=result["raw_fake_probability"],
    )
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)

    return {
        "prediction_id": new_prediction.id, "filename": file.filename,
        "label": result["label"], "real_percent": result["real_percent"], "fake_percent": result["fake_percent"],
    }


@router.post("/video")
async def predict_video_endpoint(
    file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    model = get_model()
    suffix = Path(file.filename).suffix or ".mp4"
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
        try:
            result = predict_video(tmp_path, model=model)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.remove(tmp_path)

    new_prediction = Prediction(
        user_id=current_user.id, filename=file.filename, file_type="video",
        predicted_label=result["label"], confidence=result["raw_fake_probability"],
    )
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)

    return {
        "prediction_id": new_prediction.id, "filename": file.filename,
        "label": result["label"], "real_percent": result["real_percent"], "fake_percent": result["fake_percent"],
        "frames_analyzed": result.get("frames_analyzed", 0),
    }


@router.post("/audio")
async def predict_audio_endpoint(
    file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    model = get_audio_model()
    suffix = Path(file.filename).suffix or ".wav"
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
        try:
            result = predict_audio(tmp_path, model=model)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    finally:
        os.remove(tmp_path)

    new_prediction = Prediction(
        user_id=current_user.id, filename=file.filename, file_type="audio",
        predicted_label=result["label"], confidence=result["raw_fake_probability"],
    )
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)

    return {
        "prediction_id": new_prediction.id, "filename": file.filename,
        "label": result["label"], "real_percent": result["real_percent"], "fake_percent": result["fake_percent"],
    }


@router.get("/history")
def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    predictions = (
        db.query(Prediction).filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc()).all()
    )
    return [
        {
            "id": p.id, "filename": p.filename, "file_type": p.file_type,
            "label": p.predicted_label, "fake_probability": p.confidence, "created_at": p.created_at,
        }
        for p in predictions
    ]