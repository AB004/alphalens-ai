"""Application settings loaded once at process startup."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True, slots=True)
class Settings:
    """Environment-backed settings shared by infrastructure adapters."""

    database_url: str
    gemini_api_key: str | None
    gemini_model: str
    embedding_model: str


def load_settings() -> Settings:
    """Build immutable settings, retaining safe local-development defaults."""

    default_database = PROJECT_ROOT / "backend" / "alphalens.db"
    return Settings(
        database_url=os.getenv(
            "DATABASE_URL", f"sqlite:///{default_database.as_posix()}"
        ),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
    )


settings = load_settings()
