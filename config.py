import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR = BASE_DIR / "static" / "samples"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE, override=True)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "pixel2edit-secure-key-2025")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash").strip()
    MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", 10))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "jfif"}
    UPLOAD_FOLDER = str(UPLOAD_DIR)
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", os.environ.get("FLASK_PORT", 5000)))
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in (
        "true", "1", "yes"
    )

    @classmethod
    def get_gemini_model(cls) -> str:
        load_dotenv(ENV_FILE, override=True)
        model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash").strip()
        return model if model else "gemini-3.5-flash"

    @classmethod
    def get_gemini_api_key(cls) -> str:
        load_dotenv(ENV_FILE, override=True)
        return os.environ.get("GEMINI_API_KEY", "").strip()

    @classmethod
    def is_gemini_configured(cls) -> bool:
        key = cls.get_gemini_api_key()
        return bool(key and len(key) > 5 and not key.startswith("your_"))
