from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()  # .env file se DATABASE_URL padhega

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Har API request ke liye ek fresh database session deta hai,
    aur request khatam hone pe automatically close kar deta hai."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()