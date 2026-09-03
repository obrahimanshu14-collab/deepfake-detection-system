from app.database.connection import engine
from sqlalchemy import text

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
except Exception as e:
    print("❌ Connection fail hua:", e)