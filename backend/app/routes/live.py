"""Live webcam inference over a WebSocket."""
import base64
import binascii
import json

import cv2
import numpy as np
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.auth_utils import check_and_consume_trial, decode_access_token
from app.database.connection import SessionLocal
from app.database.models import User
from app.ml_model.inference import predict_frame
from app.routes.predict import get_model

router = APIRouter(prefix="/live", tags=["Live Detection"])
MAX_FRAME_BYTES = 2 * 1024 * 1024


def _get_user_from_token(token: str):
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            return None
    except Exception:
        return None

    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


@router.websocket("/webcam")
async def live_webcam(websocket: WebSocket, token: str = Query(...)):
    await websocket.accept()

    user = _get_user_from_token(token)
    if user is None:
        await websocket.send_json({"error": "Invalid or expired token"})
        await websocket.close(code=1008)
        return

    trial_db = SessionLocal()
    try:
        check_and_consume_trial(user, trial_db)
    except Exception as exc:
        detail = getattr(exc, "detail", "Free trial limit reached. Please upgrade to continue.")
        await websocket.send_json({"error": detail})
        await websocket.close(code=1008)
        return
    finally:
        trial_db.close()

    try:
        model = get_model()
    except Exception as exc:
        await websocket.send_json({"error": "Detection model is unavailable", "detail": str(exc)})
        await websocket.close(code=1011)
        return

    try:
        while True:
            raw = await websocket.receive_text()
            payload = json.loads(raw)
            b64_image = payload.get("image", "")
            if not isinstance(b64_image, str) or not b64_image:
                continue
            if "," in b64_image:
                b64_image = b64_image.split(",", 1)[1]
            if len(b64_image) > MAX_FRAME_BYTES * 2:
                await websocket.send_json({"error": "Frame is too large"})
                continue

            try:
                img_bytes = base64.b64decode(b64_image, validate=True)
            except (binascii.Error, ValueError):
                continue
            if len(img_bytes) > MAX_FRAME_BYTES:
                await websocket.send_json({"error": "Frame is too large"})
                continue

            frame_bgr = cv2.imdecode(np.frombuffer(img_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame_bgr is None:
                continue

            result = predict_frame(frame_bgr, model=model)
            await websocket.send_json(result)
    except WebSocketDisconnect:
        pass
    except Exception:
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
