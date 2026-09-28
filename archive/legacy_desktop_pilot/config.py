"""
config.py — Centralised configuration for DesktopPilot AI.
Reads from environment variables / .env file.
"""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Force load .env over system environment variables
load_dotenv(Path(__file__).parent / ".env", override=True)

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Groq ──────────────────────────────────────────────────────────────────
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # ── Ollama ────────────────────────────────────────────────────────────────
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # ── FastAPI ───────────────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # ── Memory / SQLite ───────────────────────────────────────────────────────
    db_path: str = "./data/desktoppilot.db"

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level: str = "INFO"

    # ── Connectivity check timeouts (seconds) ────────────────────────────────
    groq_ping_timeout: float = 5.0
    ollama_ping_timeout: float = 3.0


config = Settings()


def get_db_path() -> Path:
    """Return the absolute path to the SQLite database, creating parent dirs."""
    p = Path(config.db_path)
    if not p.is_absolute():
        p = Path(__file__).parent / p
    p.parent.mkdir(parents=True, exist_ok=True)
    return p
