from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from learning_app.api.routes import router
from learning_app.core.config import Settings
from learning_app.infrastructure.ai.base import QuestionProvider
from learning_app.infrastructure.ai.groq_provider import build_question_provider
from learning_app.infrastructure.db.repository import SQLiteLearningRepository
from learning_app.services.learning_service import LearningService


def create_app(
    settings: Settings | None = None,
    question_provider: QuestionProvider | None = None,
) -> FastAPI:
    """Fabryka aplikacji FastAPI w architekturze czystej."""
    app_settings = settings or Settings.from_environment()
    repo = SQLiteLearningRepository(app_settings.database_path)
    provider = question_provider or build_question_provider(app_settings)
    learning_service = LearningService(repo, provider)

    app = FastAPI(
        title="Python Interview Lab — Trening Rekrutacyjny",
        description="Polsko języczna platforma przygotowująca programistów do rozmów technicznych na poziomie Senior Python Developer.",
        version="2.0.0",
    )

    app.state.learning_service = learning_service

    static_dir = Path(__file__).resolve().parents[1] / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    async def home() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    app.include_router(router)

    return app
