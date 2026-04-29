import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "healthy-habits-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'healthy_habits.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EXERCISE_API_BASE_URL = os.getenv(
        "EXERCISE_API_BASE_URL",
        "https://wger.de/api/v2",
    )
    EXERCISE_DEFAULT_LANGUAGE = int(os.getenv("EXERCISE_DEFAULT_LANGUAGE", "2"))
    EXERCISE_API_TIMEOUT = int(os.getenv("EXERCISE_API_TIMEOUT", "10"))
