from __future__ import annotations

from fastapi import Request

from learning_app.services.learning_service import LearningService


def get_learning_service(request: Request) -> LearningService:
    """Wstrzykuje instancję LearningService ze stanu aplikacji."""
    return request.app.state.learning_service
