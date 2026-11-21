from __future__ import annotations

import asyncio
import json
import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date

import httpx
from fastapi import FastAPI
from learning_app.api import create_app
from learning_app.core.config import Settings
from learning_app.core.models import DailySet
from learning_app.infrastructure.ai import (
    CuratedQuestionProvider,
    GroqQuestionProvider,
    QuestionProvider,
)
from learning_app.infrastructure.db import SQLiteLearningRepository
from learning_app.services import LearningService


@asynccontextmanager
async def _test_client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


class FakeGroqQuestionProvider(QuestionProvider):
    is_ai_enabled = True

    async def create_daily_set(self, day: date) -> DailySet:
        daily_set = await CuratedQuestionProvider().create_daily_set(day)
        return daily_set.model_copy(update={"source": "Groq · test-model"})


class UnavailableGroqQuestionProvider(QuestionProvider):
    is_ai_enabled = True

    async def create_daily_set(self, day: date) -> DailySet:
        raise httpx.ConnectError("Groq is unavailable")


class RejectedGroqQuestionProvider(QuestionProvider):
    is_ai_enabled = True

    async def create_daily_set(self, day: date) -> DailySet:
        request = httpx.Request(
            "POST", "https://api.groq.com/openai/v1/chat/completions"
        )
        response = httpx.Response(
            400,
            json={
                "error": {
                    "message": "Invalid test parameter.",
                    "failed_generation": '{"theory_questions":[]}',
                }
            },
            request=request,
        )
        raise httpx.HTTPStatusError("Bad request", request=request, response=response)


def test_daily_set_is_stable_and_balanced(tmp_path) -> None:
    repository = SQLiteLearningRepository(tmp_path / "learning.db")
    service = LearningService(repository, CuratedQuestionProvider())

    first = asyncio.run(service.get_daily_set(date(2026, 11, 21)))
    second = asyncio.run(service.get_daily_set(date(2026, 11, 21)))
    next_day = asyncio.run(service.get_daily_set(date(2026, 11, 22)))

    assert first.model_dump() == second.model_dump()
    assert len(first.questions) == 20
    assert sum(question.kind == "theory" for question in first.questions) == 16
    assert sum(question.kind == "practice" for question in first.questions) == 4
    assert all(len(question.options) == 4 for question in first.questions)
    theory_categories = {
        question.category for question in first.questions if question.kind == "theory"
    }
    practice_categories = {
        question.category for question in first.questions if question.kind == "practice"
    }
    assert len(theory_categories) == 10
    assert practice_categories.issubset(theory_categories)
    assert {question.id for question in first.questions} != {
        question.id for question in next_day.questions
    }


def test_settings_read_groq_environment(monkeypatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "local-test-key")
    monkeypatch.setenv("GROQ_MODEL", "openai/gpt-oss-20b")
    monkeypatch.setenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

    settings = Settings.from_environment()

    assert settings.groq_api_key == "local-test-key"
    assert settings.groq_model == "openai/gpt-oss-20b"
    assert settings.groq_base_url == "https://api.groq.com/openai/v1"


def test_groq_provider_uses_strict_schema_response_format(monkeypatch) -> None:
    day = date.today()
    curated_set = asyncio.run(CuratedQuestionProvider().create_daily_set(day))
    captured_request: dict[str, object] = {}
    original_async_client = httpx.AsyncClient

    def handle_request(request: httpx.Request) -> httpx.Response:
        captured_request.update(json.loads(request.content))
        content = json.dumps(
            {
                f"{kind}_questions": [
                    question.model_dump(exclude={"id", "kind"})
                    for question in curated_set.questions
                    if question.kind == kind
                ]
                for kind in ("theory", "practice")
            },
            ensure_ascii=False,
        )
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": content}}]},
        )

    transport = httpx.MockTransport(handle_request)
    monkeypatch.setattr(
        "learning_app.infrastructure.ai.groq_provider.httpx.AsyncClient",
        lambda *, timeout: original_async_client(
            transport=transport,
            timeout=timeout,
        ),
    )
    provider = GroqQuestionProvider(
        api_key="local-test-key",
        model="openai/gpt-oss-20b",
        base_url="https://api.groq.com/openai/v1",
    )

    generated = asyncio.run(provider.create_daily_set(day))

    assert captured_request.get("max_completion_tokens") == 8192
    response_format = captured_request["response_format"]
    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["strict"] is True
    schema = response_format["json_schema"]["schema"]
    assert set(schema["required"]) == {"theory_questions", "practice_questions"}
    theory_schema = schema["properties"]["theory_questions"]
    practice_schema = schema["properties"]["practice_questions"]
    assert theory_schema["minItems"] == theory_schema["maxItems"] == 16
    assert practice_schema["minItems"] == practice_schema["maxItems"] == 4
    question_schema = theory_schema["items"]
    assert set(question_schema["required"]) == {
        "category",
        "title",
        "prompt",
        "options",
        "correct_answer",
        "explanation",
    }
    assert question_schema["properties"]["options"]["minItems"] == 4
    assert question_schema["properties"]["options"]["maxItems"] == 4
    assert len(generated.questions) == 20
    assert sum(question.kind == "theory" for question in generated.questions) == 16
    assert sum(question.kind == "practice" for question in generated.questions) == 4
    assert generated.questions[0].id == "groq-theory-01"
    assert generated.questions[-1].id == "groq-practice-04"


def test_dashboard_hides_answers_and_attempts_persist(tmp_path) -> None:
    app = create_app(settings=Settings(database_path=tmp_path / "learning.db"))
    service: LearningService = app.state.learning_service
    daily_set = asyncio.run(service.get_daily_set(date.today()))
    theory = next(
        question for question in daily_set.questions if question.kind == "theory"
    )
    wrong_answer = next(
        option for option in theory.options if option != theory.correct_answer
    )

    async def exercise_api():
        async with _test_client(app) as client:
            page = await client.get("/")
            dashboard = await client.get("/api/today")
            wrong = await client.post(
                "/api/attempts",
                json={"question_id": theory.id, "answer": wrong_answer},
            )
            correct = await client.post(
                "/api/attempts",
                json={"question_id": theory.id, "answer": theory.correct_answer},
            )
            progress = await client.get("/api/progress")
            return page, dashboard, wrong, correct, progress

    page, dashboard, wrong, correct, progress = asyncio.run(exercise_api())

    assert page.status_code == 200
    assert 'lang="pl"' in page.text
    assert "Zestaw na dziś" in page.text
    assert dashboard.status_code == 200
    assert dashboard.json()["groq_available"] is False
    assert len(dashboard.json()["questions"]) == 20
    assert "correct_answer" not in dashboard.text
    assert wrong.status_code == 200
    assert wrong.json()["correct"] is False
    assert wrong.json()["completed_count"] == 0
    assert correct.status_code == 200
    assert correct.json()["correct"] is True
    assert correct.json()["completed_count"] == 1
    assert progress.json()["completed"] == 1


def test_groq_generation_replaces_cached_set_and_resets_progress(tmp_path) -> None:
    database_path = tmp_path / "learning.db"
    repository = SQLiteLearningRepository(database_path)
    day = date.today()
    curated_set = asyncio.run(CuratedQuestionProvider().create_daily_set(day))
    repository.store_daily_set(curated_set)
    completed_question = next(
        question for question in curated_set.questions if question.kind == "theory"
    )
    repository.save_attempt(
        day=day,
        question_id=completed_question.id,
        answer=completed_question.correct_answer,
        completed=True,
        correct=True,
    )
    app = create_app(
        settings=Settings(database_path=database_path),
        question_provider=FakeGroqQuestionProvider(),
    )

    async def exercise_api():
        async with _test_client(app) as client:
            before = await client.get("/api/today")
            generated = await client.post("/api/today/generate")
            after = await client.get("/api/today")
            return before, generated, after

    before, generated, after = asyncio.run(exercise_api())

    assert before.json()["source"] == "lokalna pula"
    assert before.json()["progress"]["completed"] == 1
    assert before.json()["groq_available"] is True
    assert generated.status_code == 200
    assert generated.json()["source"] == "Groq · test-model"
    assert generated.json()["progress"]["completed"] == 0
    assert after.json()["source"] == "Groq · test-model"
    assert after.json()["progress"]["completed"] == 0


def test_groq_generation_requires_a_configured_provider(tmp_path) -> None:
    app = create_app(settings=Settings(database_path=tmp_path / "learning.db"))

    async def generate():
        async with _test_client(app) as client:
            return await client.post("/api/today/generate")

    response = asyncio.run(generate())

    assert response.status_code == 409
    assert "GROQ_API_KEY" in response.json()["detail"]


def test_today_uses_curated_fallback_when_groq_is_unavailable(tmp_path) -> None:
    app = create_app(
        settings=Settings(database_path=tmp_path / "learning.db"),
        question_provider=UnavailableGroqQuestionProvider(),
    )

    async def load_today():
        async with _test_client(app) as client:
            return await client.get("/api/today")

    response = asyncio.run(load_today())

    assert response.status_code == 200
    assert len(response.json()["questions"]) == 20
    assert response.json()["source"] == (
        "Lokalna pula (awaryjnie): Nie udało się połączyć z Groq."
    )
    assert response.json()["groq_available"] is True


def test_groq_generation_shows_upstream_http_error(tmp_path) -> None:
    app = create_app(
        settings=Settings(database_path=tmp_path / "learning.db"),
        question_provider=RejectedGroqQuestionProvider(),
    )

    async def generate():
        async with _test_client(app) as client:
            return await client.post("/api/today/generate")

    response = asyncio.run(generate())

    assert response.status_code == 502
    assert "Groq HTTP 400" in response.json()["detail"]
    assert "Invalid test parameter." in response.json()["detail"]
    assert 'Wygenerowany fragment: {"theory_questions":[]}' in response.json()["detail"]


def test_practice_question_uses_multiple_choice_answers(tmp_path) -> None:
    app = create_app(settings=Settings(database_path=tmp_path / "learning.db"))
    service: LearningService = app.state.learning_service
    daily_set = asyncio.run(service.get_daily_set(date.today()))
    practice = next(
        question for question in daily_set.questions if question.kind == "practice"
    )

    async def exercise_api():
        async with _test_client(app) as client:
            wrong_answer = next(
                option
                for option in practice.options
                if option != practice.correct_answer
            )
            incorrect = await client.post(
                "/api/attempts",
                json={
                    "question_id": practice.id,
                    "answer": wrong_answer,
                },
            )
            correct = await client.post(
                "/api/attempts",
                json={
                    "question_id": practice.id,
                    "answer": practice.correct_answer,
                },
            )
            return incorrect, correct

    incorrect, correct = asyncio.run(exercise_api())

    assert incorrect.json()["completed"] is False
    assert incorrect.json()["completed_count"] == 0
    assert correct.json()["completed"] is True
    assert correct.json()["completed_count"] == 1


def test_old_daily_set_is_migrated_to_twenty_questions(tmp_path) -> None:
    repository = SQLiteLearningRepository(tmp_path / "learning.db")
    provider = CuratedQuestionProvider()
    day = date.today()
    full_set = asyncio.run(provider.create_daily_set(day))
    old_set = full_set.model_copy(update={"questions": full_set.questions[:6]})
    repository.store_daily_set(old_set)

    refreshed = asyncio.run(LearningService(repository, provider).get_daily_set(day))

    assert len(refreshed.questions) == 20
    assert refreshed.source == "lokalna pula"


def test_legacy_practice_questions_without_choices_are_migrated(tmp_path) -> None:
    database_path = tmp_path / "learning.db"
    repository = SQLiteLearningRepository(database_path)
    provider = CuratedQuestionProvider()
    day = date.today()
    daily_set = asyncio.run(provider.create_daily_set(day))
    legacy_questions = [
        next(
            question for question in daily_set.questions if question.kind == kind
        ).model_dump()
        for kind in ("theory", "practice")
    ]
    for question in legacy_questions:
        if question["kind"] == "practice":
            question["options"] = []

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "INSERT INTO daily_sets (day, content, source) VALUES (?, ?, ?)",
            (day.isoformat(), json.dumps(legacy_questions), "curated"),
        )

    refreshed = asyncio.run(LearningService(repository, provider).get_daily_set(day))

    assert len(refreshed.questions) == 20
    assert all(len(question.options) == 4 for question in refreshed.questions)


def test_daily_set_with_short_explanations_is_migrated(tmp_path) -> None:
    repository = SQLiteLearningRepository(tmp_path / "learning.db")
    provider = CuratedQuestionProvider()
    day = date.today()
    full_set = asyncio.run(provider.create_daily_set(day))
    short_questions = [
        q.model_copy(update={"explanation": "Krótkie wyjaśnienie."})
        for q in full_set.questions
    ]
    short_set = full_set.model_copy(update={"questions": short_questions})

    # Bezpośrednio zapisujemy do bazy przestarzały zestaw
    with sqlite3.connect(tmp_path / "learning.db") as connection:
        connection.execute(
            "INSERT OR REPLACE INTO daily_sets (day, content, source) VALUES (?, ?, ?)",
            (
                day.isoformat(),
                json.dumps([q.model_dump() for q in short_set.questions], ensure_ascii=False),
                "stale",
            ),
        )

    refreshed = asyncio.run(LearningService(repository, provider).get_daily_set(day))

    assert len(refreshed.questions) == 20
    assert all(
        len(
            [
                s.strip()
                for s in q.explanation.replace("!", ".").replace("?", ".").split(".")
                if len(s.strip()) > 5
            ]
        )
        >= 3
        for q in refreshed.questions
    )
