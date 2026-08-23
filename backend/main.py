from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import engine, Base
from app.routes import auth, predict, admin, live, payment

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Deepfake Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(admin.router)
app.include_router(live.router)
app.include_router(payment.router)


@app.get("/")
def root():
    return {"message": "Deepfake Detection API is running"}