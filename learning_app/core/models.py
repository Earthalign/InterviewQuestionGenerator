from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

QuestionKind = Literal["theory", "practice"]


class Question(BaseModel):
    """Reprezentacja pojedynczego pytania rekrutacyjnego."""

    id: str
    category: str
    kind: QuestionKind
    title: str
    prompt: str
    options: list[str] = Field(min_length=4, max_length=4)
    correct_answer: str
    explanation: str


class DailySet(BaseModel):
    """Zestaw pytań na dany dzień."""

    date: str
    questions: list[Question]
    source: str


class QuestionView(BaseModel):
    """Widok pytania dla klienta (bez ujawniania poprawnej odpowiedzi)."""

    id: str
    category: str
    kind: QuestionKind
    title: str
    prompt: str
    options: list[str]


class AttemptRequest(BaseModel):
    """Żądanie weryfikacji wybranej odpowiedzi."""

    question_id: str = Field(min_length=1)
    answer: str = Field(min_length=1, max_length=1000)


class AttemptResult(BaseModel):
    """Wynik sprawdzenia odpowiedzi użytkownika."""

    question_id: str
    completed: bool
    correct: bool
    feedback: str
    solution: str
    completed_count: int
    total_count: int


class Progress(BaseModel):
    """Stan postępu użytkownika w danym dniu."""

    completed: int
    total: int
    percentage: int
    streak: int
    completed_ids: list[str]


class DashboardResponse(BaseModel):
    """Główna odpowiedź pulpitu aplikacji."""

    date: str
    questions: list[QuestionView]
    progress: Progress
    source: str
    groq_available: bool
