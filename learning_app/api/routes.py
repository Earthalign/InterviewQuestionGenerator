from __future__ import annotations

import logging
from datetime import date

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from learning_app.api.dependencies import get_learning_service
from learning_app.core.models import (
    AttemptRequest,
    AttemptResult,
    DashboardResponse,
    Progress,
)
from learning_app.infrastructure.ai.groq_provider import describe_groq_error
from learning_app.services.learning_service import (
    GroqProviderNotConfiguredError,
    LearningService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Quiz"])


@router.get("/today", response_model=DashboardResponse)
async def get_today_dashboard(
    service: LearningService = Depends(get_learning_service),
) -> DashboardResponse:
    """Zwraca dzisiejszy zestaw pytań oraz aktualny postęp."""
    try:
        return await service.get_dashboard(date.today())
    except (httpx.HTTPError, ValueError) as error:
        logger.exception("Nie udało się pobrać dzisiejszych pytań")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Nie udało się wczytać pytań. Spróbuj ponownie.",
        ) from error


@router.post("/today/generate", response_model=DashboardResponse)
async def generate_today_dashboard(
    service: LearningService = Depends(get_learning_service),
) -> DashboardResponse:
    """Generuje nowy zestaw pytań przy użyciu Groq AI i resetuje dzisiejszy postęp."""
    try:
        return await service.generate_groq_dashboard(date.today())
    except GroqProviderNotConfiguredError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ustaw GROQ_API_KEY i zrestartuj aplikację, aby generować pytania.",
        ) from error
    except (httpx.HTTPError, ValueError) as error:
        logger.exception("Nie udało się wygenerować pytań przez Groq")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Nie udało się wygenerować pytań. {describe_groq_error(error)}",
        ) from error


@router.post("/attempts", response_model=AttemptResult)
async def submit_attempt(
    attempt: AttemptRequest,
    service: LearningService = Depends(get_learning_service),
) -> AttemptResult:
    """Weryfikuje odpowiedź kandydata na wybrane pytanie."""
    try:
        return await service.submit_attempt(date.today(), attempt)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tego pytania nie ma w dzisiejszym zestawie.",
        ) from error
    except (httpx.HTTPError, ValueError) as error:
        logger.exception("Nie udało się przetworzyć próby odpowiedzi")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Nie udało się sprawdzić odpowiedzi. Spróbuj ponownie.",
        ) from error


@router.get("/progress", response_model=Progress)
async def get_progress(
    service: LearningService = Depends(get_learning_service),
) -> Progress:
    """Zwraca postęp i liczbę dni regularnej nauki (streak)."""
    return service.get_progress(date.today())
