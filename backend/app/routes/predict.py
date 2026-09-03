import mimetypes
import os
import uuid
from pathlib import Path

import torch
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.auth_utils import check_and_consume_trial, get_current_user
from app.database.connection import get_db
from app.database.models import Prediction, User
from app.ml_model.audio_inference import predict_audio
from app.ml_model.audio_model import AudioDeepfakeDetector
from app.ml_model.inference import predict_image, predict_video
from app.ml_model.model import load_trained_model

router = APIRouter(prefix="/predict", tags=["Prediction"])

BASE_DIR = Path(__file__).resolve().parents[2]
CHECKPOINT_PATH = Path(os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "best_model.pt")))
AUDIO_CHECKPOINT_PATH = Path(os.getenv("AUDIO_MODEL_PATH", str(BASE_DIR / "models" / "best_audio_model.pt")))
UPLOADS_DIR = Path(os.getenv("UPLOADS_DIR", str(BASE_DIR / "data" / "uploads")))
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZES = {
    "image": int(os.getenv("MAX_IMAGE_MB", "15")) * 1024 * 1024,
    "video": int(os.getenv("MAX_VIDEO_MB", "100")) * 1024 * 1024,
    "audio": int(os.getenv("MAX_AUDIO_MB", "30")) * 1024 * 1024,
}
ALLOWED_EXTENSIONS = {
    "image": {".jpg", ".jpeg", ".png", ".webp"},
    "video": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "audio": {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"},
}

_model = None
_audio_model = None


def get_model():
    global _model
    if _model is None:
        if not CHECKPOINT_PATH.exists():
            raise RuntimeError(f"Image/video model checkpoint not found: {CHECKPOINT_PATH}")
        _model = load_trained_model(str(CHECKPOINT_PATH))
    return _model


def get_audio_model():
    global _audio_model
    if _audio_model is None:
        if not AUDIO_CHECKPOINT_PATH.exists():
            raise RuntimeError(f"Audio model checkpoint not found: {AUDIO_CHECKPOINT_PATH}")
        _audio_model = AudioDeepfakeDetector(pretrained=False)
        state_dict = torch.load(str(AUDIO_CHECKPOINT_PATH), map_location="cpu")
        _audio_model.load_state_dict(state_dict)
        _audio_model.eval()
    return _audio_model



def _save_upload(file: UploadFile, kind: str, user_id: int) -> Path:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A filename is required")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS[kind]:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS[kind]))
        raise HTTPException(status_code=415, detail=f"Unsupported {kind} format. Allowed: {allowed}")

    user_dir = UPLOADS_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    dest_path = user_dir / f"{uuid.uuid4().hex}{suffix}"
    limit = MAX_FILE_SIZES[kind]
    total = 0
    try:
        with open(dest_path, "wb") as out_file:
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > limit:
                    raise HTTPException(status_code=413, detail=f"{kind.title()} file is too large")
                out_file.write(chunk)
    except HTTPException:
        dest_path.unlink(missing_ok=True)
        raise
    except Exception:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Could not save uploaded file")
    return dest_path


def _store_prediction(db: Session, user: User, file: UploadFile, file_type: str, result: dict, path: Path, duration=None):
    prediction = Prediction(
        user_id=user.id,
        filename=file.filename,
        file_type=file_type,
        predicted_label=result["label"],
        confidence=float(result.get("raw_fake_probability", 0.5)),
        file_path=str(path),
        duration_seconds=duration,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


@router.post("/image")
async def predict_image_endpoint(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    model = get_model()
    dest_path = _save_upload(file, "image", current_user.id)
    try:
        result = predict_image(str(dest_path), model=model)
        check_and_consume_trial(current_user, db)
        prediction = _store_prediction(db, current_user, file, "image", result, dest_path)
    except HTTPException:
        dest_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "prediction_id": prediction.id,
        "filename": file.filename,
        "label": result["label"],
        "real_percent": result["real_percent"],
        "fake_percent": result["fake_percent"],
    }


@router.post("/video")
async def predict_video_endpoint(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    model = get_model()
    dest_path = _save_upload(file, "video", current_user.id)
    try:
        result = predict_video(str(dest_path), model=model)
        check_and_consume_trial(current_user, db)
        prediction = _store_prediction(db, current_user, file, "video", result, dest_path)
    except HTTPException:
        dest_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "prediction_id": prediction.id,
        "filename": file.filename,
        "label": result["label"],
        "real_percent": result["real_percent"],
        "fake_percent": result["fake_percent"],
        "frames_analyzed": result.get("frames_analyzed", 0),
        "signals": result.get("signals"),
    }


@router.post("/audio")
async def predict_audio_endpoint(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    model = get_audio_model()
    dest_path = _save_upload(file, "audio", current_user.id)
    try:
        result = predict_audio(str(dest_path), model=model)
        check_and_consume_trial(current_user, db)
        prediction = _store_prediction(db, current_user, file, "audio", result, dest_path)
    except HTTPException:
        dest_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "prediction_id": prediction.id,
        "filename": file.filename,
        "label": result["label"],
        "real_percent": result["real_percent"],
        "fake_percent": result["fake_percent"],
    }


@router.post("/live/save")
async def save_live_session(
    file: UploadFile = File(...),
    label: str = Form(...),
    real_percent: float = Form(...),
    fake_percent: float = Form(...),
    duration_seconds: float = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if label not in {"REAL", "Possibly Real", "Uncertain", "Possibly Fake", "FAKE"}:
        raise HTTPException(status_code=400, detail="Invalid live verdict")
    if not 0 <= real_percent <= 100 or not 0 <= fake_percent <= 100:
        raise HTTPException(status_code=400, detail="Invalid confidence values")
    if duration_seconds < 0 or duration_seconds > 3600:
        raise HTTPException(status_code=400, detail="Invalid live session duration")

    dest_path = _save_upload(file, "video", current_user.id)
    try:
        prediction = Prediction(
            user_id=current_user.id,
            filename=f"Live session ({round(duration_seconds)}s)",
            file_type="live",
            predicted_label=label,
            confidence=fake_percent / 100.0,
            file_path=str(dest_path),
            duration_seconds=duration_seconds,
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
    except Exception:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Could not save live session")

    return {"prediction_id": prediction.id, "status": "saved"}


@router.get("/file/{prediction_id}")
def get_prediction_file(prediction_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    if prediction.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this file")
    if not prediction.file_path or not os.path.exists(prediction.file_path):
        raise HTTPException(status_code=404, detail="File no longer available")
    media_type, _ = mimetypes.guess_type(prediction.file_path)
    return FileResponse(prediction.file_path, media_type=media_type or "application/octet-stream")


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
            "real_percent": round((1 - p.confidence) * 100, 1),
            "fake_percent": round(p.confidence * 100, 1),
            "duration_seconds": p.duration_seconds,
            "created_at": p.created_at,
        }
        for p in predictions
    ]
