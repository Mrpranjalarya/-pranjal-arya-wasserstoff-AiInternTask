# backend/app/config.py

import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

class Settings:
    # Core directories and paths
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    POPPLER_PATH: str = os.getenv("POPPLER_PATH", "")

    # Embedding model
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_MODEL_TYPE: str = os.getenv("EMBEDDING_MODEL_TYPE", "huggingface")

    # Optional DB config (if using SQLAlchemy elsewhere)
    SQLALCHEMY_DATABASE_URL: str = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./test.db")

settings = Settings()
