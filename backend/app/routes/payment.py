"""Razorpay test-mode payment integration: create an order, then verify
the signature after checkout completes, and mark the user as premium."""
import os

import razorpay
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth_utils import get_current_user
from app.database.connection import get_db
from app.database.models import User

router = APIRouter(prefix="/payment", tags=["Payment"])

client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET")))

PREMIUM_PRICE_INR = 99  # test-mode amount, in rupees


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


@router.post("/create-order")
def create_order(current_user: User = Depends(get_current_user)):
    order = client.order.create({
        "amount": PREMIUM_PRICE_INR * 100,  # Razorpay expects paise, not rupees
        "currency": "INR",
        "payment_capture": 1,
    })
    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "key_id": os.getenv("RAZORPAY_KEY_ID"),
    }


@router.post("/verify")
def verify_payment(
    data: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": data.razorpay_order_id,
            "razorpay_payment_id": data.razorpay_payment_id,
            "razorpay_signature": data.razorpay_signature,
        })
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Payment verification failed")

    current_user.has_premium = True
    db.add(current_user)
    db.commit()
    return {"status": "success", "has_premium": True}