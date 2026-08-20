from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User, Prediction
from app.auth_utils import get_current_admin_user

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
def get_stats(admin: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_predictions = db.query(Prediction).count()

    label_counts = (
        db.query(Prediction.predicted_label, func.count(Prediction.id))
        .group_by(Prediction.predicted_label).all()
    )
    type_counts = (
        db.query(Prediction.file_type, func.count(Prediction.id))
        .group_by(Prediction.file_type).all()
    )

    return {
        "total_users": total_users,
        "total_predictions": total_predictions,
        "label_breakdown": {label: count for label, count in label_counts},
        "type_breakdown": {file_type: count for file_type, count in type_counts},
    }


@router.get("/users")
def get_all_users(admin: User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        prediction_count = db.query(Prediction).filter(Prediction.user_id == u.id).count()
        result.append({
            "id": u.id, "email": u.email, "is_admin": u.is_admin,
            "created_at": u.created_at, "prediction_count": prediction_count,
        })
    return result