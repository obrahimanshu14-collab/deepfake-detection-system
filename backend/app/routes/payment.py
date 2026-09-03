import os
from datetime import timedelta

import razorpay
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth_utils import get_current_user, utc_now_naive
from app.database.connection import get_db
from app.database.models import User

load_dotenv()

router = APIRouter(prefix="/payment", tags=["Payment"])
KEY_ID = os.getenv("RAZORPAY_KEY_ID")
KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
client = razorpay.Client(auth=(KEY_ID, KEY_SECRET)) if KEY_ID and KEY_SECRET else None

PLANS = {
    "weekly": {"price_inr": 29, "days": 7, "label": "Weekly"},
    "monthly": {"price_inr": 99, "days": 30, "label": "Monthly"},
    "annual": {"price_inr": 899, "days": 365, "label": "Annual"},
}


class CreateOrderRequest(BaseModel):
    plan: str = Field(pattern="^(weekly|monthly|annual)$")


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str = Field(min_length=3, max_length=100)
    razorpay_payment_id: str = Field(min_length=3, max_length=100)
    razorpay_signature: str = Field(min_length=10, max_length=200)
    plan: str = Field(pattern="^(weekly|monthly|annual)$")


@router.get("/plans")
def get_plans():
    return PLANS


@router.post("/create-order")
def create_order(data: CreateOrderRequest, current_user: User = Depends(get_current_user)):
    if client is None:
        raise HTTPException(status_code=503, detail="Payments are not configured on this server")

    plan = PLANS[data.plan]
    try:
        order = client.order.create({
            "amount": plan["price_inr"] * 100,
            "currency": "INR",
            "payment_capture": 1,
            "notes": {"plan": data.plan, "user_id": str(current_user.id)},
        })
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to create payment order")

    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "key_id": KEY_ID,
        "plan_label": plan["label"],
    }


@router.post("/verify")
def verify_payment(
    data: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if client is None:
        raise HTTPException(status_code=503, detail="Payments are not configured on this server")

    try:
        order = client.order.fetch(data.razorpay_order_id)
        notes = order.get("notes") or {}
        if str(notes.get("user_id")) != str(current_user.id) or notes.get("plan") != data.plan:
            raise HTTPException(status_code=400, detail="Payment order does not match this account")
        expected_amount = PLANS[data.plan]["price_inr"] * 100
        if int(order.get("amount", 0)) != expected_amount:
            raise HTTPException(status_code=400, detail="Payment amount mismatch")

        client.utility.verify_payment_signature({
            "razorpay_order_id": data.razorpay_order_id,
            "razorpay_payment_id": data.razorpay_payment_id,
            "razorpay_signature": data.razorpay_signature,
        })
    except HTTPException:
        raise
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Payment verification failed")
    except Exception:
        raise HTTPException(status_code=400, detail="Payment verification failed")

    plan = PLANS[data.plan]
    current_user.has_premium = True
    current_user.premium_expires_at = utc_now_naive() + timedelta(days=plan["days"])
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {
        "status": "success",
        "has_premium": True,
        "expires_at": current_user.premium_expires_at,
    }
