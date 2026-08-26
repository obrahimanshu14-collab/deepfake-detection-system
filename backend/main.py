import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import Base, engine
from app.routes import admin, auth, live, predict

# Keep the current lightweight development setup, but use one FastAPI app
# instance and register every router exactly once.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Deepfake Detection API",
    version="1.0.0",
    description="AI-powered image, video, audio and live deepfake analysis API.",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(admin.router)
app.include_router(live.router)


@app.get("/", tags=["System"])
def root():
    return {
        "status": "ok",
        "service": "Deepfake Detection API",
        "version": "1.0.0",
    }


@app.get("/health", tags=["System"])
def health():
    return {"status": "healthy"}
