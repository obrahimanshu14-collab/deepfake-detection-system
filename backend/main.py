import os
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database.connection import Base, engine
from app.routes import admin, auth, integration, live, payment, predict

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Veritas Deepfake Detection API",
    version="1.2.0",
    description=(
        "Multimodal deepfake detection service for image, video, audio, "
        "live inference, dashboard access, and organization API integrations."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


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
app.include_router(integration.router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Veritas Deepfake Detection API",
        "version": app.version,
        "docs": "/docs",
        "developer_api": "/v1/",
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "veritas"}


@app.get("/healthz")
def healthz():
    return {"status": "healthy"}


@app.get("/readyz")
def readyz():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}
