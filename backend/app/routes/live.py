"""Live webcam detection via WebSocket -- keeps one connection open and
streams a result back for every frame the browser sends."""
import base64
import json

import cv2
import numpy as np
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.auth_utils import decode_access_token
from app.database.connection import SessionLocal
from app.database.models import User
from app.ml_model.inference import predict_frame
from app.routes.predict import get_model

router = APIRouter(prefix="/live", tags=["Live Detection"])


def _get_user_from_token(token: str):
    try:
        payload = decode_access_token(token)
    except Exception as e:
        print(f"[live] Token decode failed: {e}")  # visible in backend terminal now
        return None

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == payload.get("user_id")).first()
        if user is None:
            print(f"[live] No user found for user_id={payload.get('user_id')}")
        return user
    finally:
        db.close()


@router.websocket("/webcam")
async def live_webcam(websocket: WebSocket, token: str = Query(...)):
    # Accept the connection FIRST, then verify -- this way, an invalid
    # token produces a clean post-accept close (visible to the frontend
    # as a normal disconnect) rather than a raw 403 that hides the real
    # reason in server logs.
    await websocket.accept()

    user = _get_user_from_token(token)
    if user is None:
        await websocket.send_json({"error": "Invalid or expired token"})
        await websocket.close(code=1008)
        return

    model = get_model()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            b64_image = payload.get("image", "")
            if "," in b64_image:
                b64_image = b64_image.split(",", 1)[1]

            img_bytes = base64.b64decode(b64_image)
            np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
            frame_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame_bgr is None:
                continue

            result = predict_frame(frame_bgr, model=model)
            await websocket.send_json(result)
    except WebSocketDisconnect:
        pass