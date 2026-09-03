import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database.connection import Base, engine
from app.routes import admin, auth, live, payment, predict

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Veritas Deepfake Detection API",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

cors_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(admin.router)
app.include_router(live.router)
app.include_router(payment.router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Veritas Deepfake Detection API",
        "version": app.version,
    }


@app.get("/healthz")
def healthz():
    return {"status": "healthy"}


@app.get("/readyz")
def readyz():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}
