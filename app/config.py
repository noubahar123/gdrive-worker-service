# worker-service/app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    PROJECT_NAME: str = "Image Import Worker"

    # Point to the SAME SQLite file as api-service
    # ../api-service/image_import.db
    db_path = (BASE_DIR.parent / "api-service" / "image_import.db").resolve()
    DATABASE_URL: str = f"sqlite:///{db_path.as_posix()}"

settings = Settings()
