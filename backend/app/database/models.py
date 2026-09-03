from sqlalchemy import Column, Integer, String, Boolean, Float, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    free_trials_used = Column(Integer, default=0)
    has_premium = Column(Boolean, default=False)
    premium_expires_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    plan = Column(String(50), default="free")
    created_at = Column(TIMESTAMP, server_default=func.now())


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    key_hash = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=True)
    filename = Column(String(255))
    file_type = Column(String(20))
    predicted_label = Column(String(20))
    confidence = Column(Float)
    file_path = Column(String(500), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class AdminLog(Base):
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(255))
    performed_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"))
    endpoint = Column(String(255))
    called_at = Column(TIMESTAMP, server_default=func.now())