import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api_key_utils import generate_api_key, get_api_key_record
from app.auth_utils import get_current_user, utc_now_naive
from app.database.connection import get_db
from app.database.models import ApiKey, Organization, Prediction, UsageLog, User
from app.ml_model.audio_inference import predict_audio
from app.ml_model.inference import predict_image, predict_video
from app.routes.predict import _save_upload, get_audio_model, get_model

router = APIRouter(prefix="/v1", tags=["Developer API"])


class ApiKeyCreateRequest(BaseModel):
    organization_name: str = Field(min_length=2, max_length=120)
    name: str = Field(default="Production", min_length=2, max_length=80)


@router.get("/")
def api_overview():
    return {
        "service": "Veritas Deepfake Detection API",
        "version": "v1",
        "authentication": "Bearer token for provisioning; X-API-Key for developer inference",
        "endpoints": [
            "/v1/api-keys",
            "/v1/predict/image",
            "/v1/predict/video",
            "/v1/predict/audio",
            "/v1/usage",
        ],
    }


@router.post("/api-keys")
def create_api_key(
    data: ApiKeyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    organization = Organization(name=data.organization_name.strip(), plan="api")
    db.add(organization)
    db.flush()

    raw_key, key_hash = generate_api_key()
    record = ApiKey(
        organization_id=organization.id,
        key_hash=key_hash,
        is_active=True,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "organization_id": organization.id,
        "organization": organization.name,
        "name": data.name,
        "api_key": raw_key,
        "warning": "Store this key securely. It is shown only once.",
    }


def _record_usage(db: Session, api_key_id: int, endpoint: str) -> None:
    db.add(UsageLog(api_key_id=api_key_id, endpoint=endpoint, called_at=utc_now_naive()))
    db.commit()


def _save_api_prediction(
    db: Session,
    api_key: ApiKey,
    file: UploadFile,
    file_type: str,
    result: dict,
    duration=None,
):
    # Developer API calls intentionally do not retain the raw uploaded media.
    prediction = Prediction(
        user_id=None,
        api_key_id=api_key.id,
        filename=file.filename,
        file_type=file_type,
        predicted_label=result["label"],
        confidence=float(result.get("raw_fake_probability", 0.5)),
        file_path=None,
        duration_seconds=duration,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def _payload(prediction: Prediction, result: dict, filename: str) -> dict:
    return {
        "prediction_id": prediction.id,
        "filename": filename,
        "label": result["label"],
        "real_percent": result["real_percent"],
        "fake_percent": result["fake_percent"],
        "raw_fake_probability": result.get("raw_fake_probability"),
        "model": "veritas-mobilenetv2",
    }


@router.post("/predict/image")
async def api_predict_image(
    file: UploadFile = File(...),
    api_key: ApiKey = Depends(get_api_key_record),
    db: Session = Depends(get_db),
):
    dest = _save_upload(file, "image", api_key.organization_id or 0)
    try:
        result = predict_image(str(dest), model=get_model())
        prediction = _save_api_prediction(db, api_key, file, "image", result)
        _record_usage(db, api_key.id, "/v1/predict/image")
        dest.unlink(missing_ok=True)
        return _payload(prediction, result, file.filename)
    except HTTPException:
        dest.unlink(missing_ok=True)
        raise
    except Exception:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Image could not be analyzed")


@router.post("/predict/video")
async def api_predict_video(
    file: UploadFile = File(...),
    api_key: ApiKey = Depends(get_api_key_record),
    db: Session = Depends(get_db),
):
    dest = _save_upload(file, "video", api_key.organization_id or 0)
    try:
        result = predict_video(str(dest), model=get_model())
        prediction = _save_api_prediction(db, api_key, file, "video", result)
        _record_usage(db, api_key.id, "/v1/predict/video")
        dest.unlink(missing_ok=True)
        payload = _payload(prediction, result, file.filename)
        payload.update({
            "frames_analyzed": result.get("frames_analyzed", 0),
            "signals": result.get("signals"),
        })
        return payload
    except HTTPException:
        dest.unlink(missing_ok=True)
        raise
    except Exception:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Video could not be analyzed")


@router.post("/predict/audio")
async def api_predict_audio(
    file: UploadFile = File(...),
    api_key: ApiKey = Depends(get_api_key_record),
    db: Session = Depends(get_db),
):
    dest = _save_upload(file, "audio", api_key.organization_id or 0)
    try:
        result = predict_audio(str(dest), model=get_audio_model())
        prediction = _save_api_prediction(db, api_key, file, "audio", result)
        _record_usage(db, api_key.id, "/v1/predict/audio")
        dest.unlink(missing_ok=True)
        return _payload(prediction, result, file.filename)
    except HTTPException:
        dest.unlink(missing_ok=True)
        raise
    except Exception:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Audio could not be analyzed")


@router.get("/usage")
def api_usage(api_key: ApiKey = Depends(get_api_key_record), db: Session = Depends(get_db)):
    total = db.query(UsageLog).filter(UsageLog.api_key_id == api_key.id).count()
    return {
        "api_key_id": api_key.id,
        "total_requests": total,
        "daily_limit": int(os.getenv("API_DAILY_LIMIT", "100")),
    }
