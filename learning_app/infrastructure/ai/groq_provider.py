from __future__ import annotations

import json
from datetime import date

import httpx
from pydantic import ValidationError

from learning_app.core.config import Settings
from learning_app.core.models import DailySet, Question
from learning_app.infrastructure.ai.base import (
    CuratedQuestionProvider,
    QuestionProvider,
)
from learning_app.questions.shuffler import balance_options_distribution


def _groq_question_schema() -> dict[str, object]:
    properties: dict[str, object] = {
        "category": {"type": "string"},
        "title": {"type": "string"},
        "prompt": {"type": "string"},
        "options": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 4,
            "maxItems": 4,
        },
        "correct_answer": {"type": "string"},
        "explanation": {
            "type": "string",
            "description": (
                "Wyczerpujące wyjaśnienie składające się z minimum 3–5 pełnych zdań po polsku: "
                "zasada działania pod maską, dlaczego dana opcja jest poprawna, błędy w dystraktorach "
                "oraz wskazówki architektoniczne dla seniora."
            ),
        },
    }
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def _groq_response_format() -> dict[str, object]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "daily_interview_questions",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "theory_questions": {
                        "type": "array",
                        "items": _groq_question_schema(),
                        "minItems": 16,
                        "maxItems": 16,
                    },
                    "practice_questions": {
                        "type": "array",
                        "items": _groq_question_schema(),
                        "minItems": 4,
                        "maxItems": 4,
                    },
                },
                "required": ["theory_questions", "practice_questions"],
                "additionalProperties": False,
            },
        },
    }


class GroqQuestionProvider:
    """Generator zestawu pytań z wykorzystaniem API czatu Groq."""

    is_ai_enabled = True

    def __init__(self, api_key: str, model: str, base_url: str) -> None:
        self._api_key = api_key
        self._model = model
        self._url = f"{base_url.rstrip('/')}/chat/completions"

    async def create_daily_set(self, day: date) -> DailySet:
        prompt = (
            f"Przygotuj po polsku zestaw pytań na dzień {day.isoformat()} dla "
            "senior Python developera. Wybierz pytania rekrutacyjne z: "
            "Pythona, FastAPI, Django, Flask, SQL, REST, AI/RAG, CI/CD, Dockera "
            "i Kubernetes. Zestaw musi liczyć dokładnie 20 pytań jednokrotnego wyboru: "
            "dokładnie 16 pytań w 'theory_questions' i dokładnie 4 pytania w 'practice_questions'. "
            "Każde pytanie musi mieć dokładnie 4 odpowiedzi (options), z których dokładnie "
            "jedna jest poprawna (correct_answer). Zarówno poprawna odpowiedź, jak i błędne "
            "odpowiedzi (dystraktory) muszą być merytoryczne i edukacyjne — czytanie każdej "
            "opcji powinno uczyć kandydata i wyjaśniać rzeczywiste pojęcia lub powszechne mity. "
            "Pole 'explanation' (wyjaśnienie) musi być wyczerpujące i zawierać kilka pełnych zdań "
            "(minimum 3–5 zdań): szczegółowo wyjaśnij, dlaczego poprawna odpowiedź jest właściwa, "
            "jak ten mechanizm działa pod maską w Pythonie lub danym systemie, dlaczego pozostałe "
            "opcje są błędne oraz jaka jest rekomendacja architektoniczna dla Senior Developera. "
            "Zabrania się lakonicznych i 1-zdaniowych wyjaśnień — każde wyjaśnienie musi być "
            "pełnowymiarową analizą techniczną złożoną z co najmniej 3 pełnych zdań."
        )

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                self._url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self._model,
                    "temperature": 0.4,
                    "max_completion_tokens": 32768,
                    "response_format": _groq_response_format(),
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Jesteś doświadczonym rekruterem technicznym i głównym architektem Pythona. "
                                "Tworzysz głębokie merytorycznie, precyzyjne i wartościowe edukacyjnie "
                                "pytania rekrutacyjne po polsku. Każde wyjaśnienie pytania musi mieć charakter "
                                "mentorski i składać się z minimum 3–5 wyczerpujących zdań technicznych."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                },
            )
            response.raise_for_status()
            payload = response.json()

        try:
            grouped = json.loads(payload["choices"][0]["message"]["content"])
            raw_questions: list[Question] = []
            for kind in ("theory", "practice"):
                for index, raw_item in enumerate(
                    grouped[f"{kind}_questions"], start=1
                ):
                    raw = dict(raw_item)
                    q_id = f"groq-{kind}-{index:02d}"
                    raw["id"] = q_id
                    raw["kind"] = kind
                    raw_questions.append(Question.model_validate(raw))

            _validate_daily_set(raw_questions)

            # Równomiernie zbalansuj pozycje poprawnej odpowiedzi (A, B, C, D po 25%)
            questions = balance_options_distribution(
                raw_questions, seed=day.strftime("%Y%m%d")
            )
        except (
            KeyError,
            IndexError,
            TypeError,
            json.JSONDecodeError,
            ValidationError,
        ) as error:
            raise ValueError("Groq zwrócił nieprawidłowy zestaw pytań.") from error

        return DailySet(
            date=day.isoformat(),
            questions=questions,
            source=f"Groq · {self._model}",
        )


def build_question_provider(settings: Settings) -> QuestionProvider:
    """Fabryka dostawcy pytań zależnie od obecności klucza GROQ_API_KEY."""
    if settings.groq_api_key:
        return GroqQuestionProvider(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            base_url=settings.groq_base_url,
        )
    return CuratedQuestionProvider()


def describe_groq_error(error: Exception) -> str:
    """Formatuje błąd komunikacji z Groq do bezpiecznego i czytelnego komunikatu."""
    if isinstance(error, httpx.HTTPStatusError):
        status_code = error.response.status_code
        try:
            payload = error.response.json()
        except ValueError:
            payload = {}
        error_payload = payload.get("error") if isinstance(payload, dict) else None
        message = (
            error_payload.get("message") if isinstance(error_payload, dict) else None
        )
        failed_generation = (
            error_payload.get("failed_generation")
            if isinstance(error_payload, dict)
            else None
        )
        if not isinstance(failed_generation, str) and isinstance(payload, dict):
            failed_generation = payload.get("failed_generation")

        if isinstance(message, str) and message.strip():
            detail = f"Groq HTTP {status_code}: {message.strip()[:200]}"
            if isinstance(failed_generation, str) and failed_generation.strip():
                preview = " ".join(failed_generation.split())[:120]
                detail += f" Wygenerowany fragment: {preview}"
            return detail
        return f"Groq HTTP {status_code}."

    if isinstance(error, httpx.TimeoutException):
        return "Przekroczono limit czasu połączenia z Groq."
    if isinstance(error, httpx.RequestError):
        return "Nie udało się połączyć z Groq."
    if isinstance(error, ValueError):
        return str(error).strip()[:240] or "Nieprawidłowa odpowiedź Groq."
    return f"Nieoczekiwany błąd Groq ({type(error).__name__})."


def _validate_daily_set(questions: list[Question]) -> None:
    theory_count = sum(q.kind == "theory" for q in questions)
    practice_count = sum(q.kind == "practice" for q in questions)
    if len(questions) != 20 or theory_count != 16 or practice_count != 4:
        raise ValueError(
            "Zestaw musi zawierać 16 pytań teoretycznych i 4 praktyczne. "
            f"Otrzymano: {theory_count} teoretycznych i {practice_count} praktycznych."
        )
    if len({q.id for q in questions}) != 20:
        raise ValueError("Identyfikatory pytań muszą być unikalne.")
    if any(
        len(q.options) != 4 or q.correct_answer not in q.options
        for q in questions
    ):
        raise ValueError("Każde pytanie musi mieć 4 opcje i poprawną odpowiedź.")
