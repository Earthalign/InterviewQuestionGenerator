from __future__ import annotations

import logging
from datetime import date

import httpx

from learning_app.core.models import (
    AttemptRequest,
    AttemptResult,
    DailySet,
    DashboardResponse,
    Progress,
    Question,
    QuestionView,
)
from learning_app.infrastructure.ai.base import (
    CuratedQuestionProvider,
    QuestionProvider,
)
from learning_app.infrastructure.ai.groq_provider import describe_groq_error
from learning_app.infrastructure.db.repository import SQLiteLearningRepository

logger = logging.getLogger(__name__)


class GroqProviderNotConfiguredError(RuntimeError):
    """Zgłaszany, gdy wywołano generowanie Groq bez skonfigurowanego klucza API."""


class LearningService:
    """Serwis koordynujący logikę nauki, sprawdzanie odpowiedzi i postępy."""

    def __init__(
        self, repository: SQLiteLearningRepository, provider: QuestionProvider
    ) -> None:
        self._repository = repository
        self._provider = provider
        self._fallback = CuratedQuestionProvider() if provider.is_ai_enabled else None

    async def get_daily_set(self, day: date) -> DailySet:
        """Pobiera zestaw z bazy lub generuje nowy przy użyciu dostawcy."""
        cached = self._repository.get_daily_set(day)
        if cached is not None:
            return cached

        try:
            daily_set = await self._provider.create_daily_set(day)
        except (httpx.HTTPError, ValueError) as error:
            if self._fallback is None:
                raise
            logger.warning(
                "Nie udało się pobrać pytań z Groq; użycie lokalnej puli awaryjnej: %s",
                describe_groq_error(error),
            )
            fallback_set = await self._fallback.create_daily_set(day)
            daily_set = fallback_set.model_copy(
                update={"source": f"Lokalna pula (awaryjnie): {describe_groq_error(error)}"}
            )

        return self._repository.store_daily_set(daily_set)

    async def get_dashboard(self, day: date) -> DashboardResponse:
        """Tworzy pełny model pulpitu dla wskazanego dnia."""
        daily_set = await self.get_daily_set(day)
        return self._build_dashboard(day, daily_set)

    async def generate_groq_dashboard(self, day: date) -> DashboardResponse:
        """Wymusza wygenerowanie nowego zestawu pytań z Groq i resetuje dzisiejszy postęp."""
        if not self._provider.is_ai_enabled:
            raise GroqProviderNotConfiguredError

        daily_set = await self._provider.create_daily_set(day)
        self._repository.replace_daily_set(daily_set)
        return self._build_dashboard(day, daily_set)

    async def submit_attempt(self, day: date, attempt: AttemptRequest) -> AttemptResult:
        """Weryfikuje odpowiedź kandydata, zapisuje próbę i zwraca wynik."""
        daily_set = await self.get_daily_set(day)
        question = next(
            (q for q in daily_set.questions if q.id == attempt.question_id),
            None,
        )
        if question is None:
            raise KeyError(attempt.question_id)

        is_correct = attempt.answer.strip().casefold() == question.correct_answer.casefold()
        feedback = (
            "Świetnie! Poprawna odpowiedź."
            if is_correct
            else "Niestety, to nie jest poprawna odpowiedź. Zapoznaj się z wyjaśnieniem poniżej."
        )
        solution = f"Prawidłowa odpowiedź: {question.correct_answer}\n\nWyjaśnienie: {question.explanation}"

        self._repository.save_attempt(
            day=day,
            question_id=question.id,
            answer=attempt.answer,
            completed=is_correct,
            correct=is_correct,
        )

        progress = self._repository.get_progress(day, total=len(daily_set.questions))
        return AttemptResult(
            question_id=question.id,
            completed=is_correct,
            correct=is_correct,
            feedback=feedback,
            solution=solution,
            completed_count=progress.completed,
            total_count=progress.total,
        )

    def get_progress(self, day: date) -> Progress:
        """Zwraca stan postępów użytkownika na dany dzień."""
        daily_set = self._repository.get_daily_set(day)
        total = len(daily_set.questions) if daily_set else 20
        return self._repository.get_progress(day, total=total)

    def _build_dashboard(self, day: date, daily_set: DailySet) -> DashboardResponse:
        progress = self._repository.get_progress(day, total=len(daily_set.questions))
        return DashboardResponse(
            date=day.isoformat(),
            questions=[self._to_view(q) for q in daily_set.questions],
            progress=progress,
            source=daily_set.source,
            groq_available=self._provider.is_ai_enabled,
        )

    @staticmethod
    def _to_view(question: Question) -> QuestionView:
        return QuestionView(
            id=question.id,
            category=question.category,
            kind=question.kind,
            title=question.title,
            prompt=question.prompt,
            options=question.options,
        )
