from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _default_database_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "learning.db"


@dataclass(frozen=True, slots=True)
class Settings:
    """Konfiguracja aplikacji ładowana ze zmiennych środowiskowych."""

    database_path: Path = field(default_factory=_default_database_path)
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-20b"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    @classmethod
    def from_environment(cls) -> Settings:
        db_env = os.getenv("DATABASE_PATH")
        db_path = Path(db_env).expanduser() if db_env else _default_database_path()
        return cls(
            database_path=db_path,
            groq_api_key=os.getenv("GROQ_API_KEY", "").strip() or None,
            groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            groq_base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        )
