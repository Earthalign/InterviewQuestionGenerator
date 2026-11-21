from __future__ import annotations

import random
from collections.abc import Iterable
from datetime import date
from typing import Protocol

from learning_app.core.models import DailySet, Question
from learning_app.questions.bank import build_question_bank
from learning_app.questions.shuffler import balance_options_distribution


class QuestionProvider(Protocol):
    """Protokół dostawcy pytań rekrutacyjnych."""

    is_ai_enabled: bool

    async def create_daily_set(self, day: date) -> DailySet: ...


class CuratedQuestionProvider:
    """Tworzy zbalansowany zestaw pytań z lokalnej puli (16 teorii + 4 praktyki)."""

    is_ai_enabled = False

    def __init__(self) -> None:
        self._questions = build_question_bank()

    async def create_daily_set(self, day: date) -> DailySet:
        theory_by_cat = _group_by_category(
            q for q in self._questions if q.kind == "theory"
        )
        practice_by_cat = _group_by_category(
            q for q in self._questions if q.kind == "practice"
        )

        all_categories = sorted(theory_by_cat.keys())
        if len(all_categories) != 10:
            raise RuntimeError("Lokalna pula teorii musi obejmować 10 kategorii.")

        rng = random.Random(day.strftime("%Y%m%d"))

        # 1. Wybierz 16 pytań teoretycznych:
        # Najpierw po jednym z każdej z 10 kategorii, aby zagwarantować pełne pokrycie
        chosen_theory: list[Question] = [
            rng.choice(theory_by_cat[cat]) for cat in all_categories
        ]
        chosen_theory_ids = {q.id for q in chosen_theory}

        # Następnie dopełnij 6 pytań z pozostałej puli teorii
        remaining_theory = [
            q for q in self._questions
            if q.kind == "theory" and q.id not in chosen_theory_ids
        ]
        rng.shuffle(remaining_theory)
        chosen_theory.extend(remaining_theory[:6])

        # 2. Wybierz 4 pytania praktyczne z różnych kategorii
        practice_categories = sorted(practice_by_cat.keys())
        rng.shuffle(practice_categories)
        chosen_practice: list[Question] = []
        for cat in practice_categories[:4]:
            chosen_practice.append(rng.choice(practice_by_cat[cat]))

        combined = chosen_theory + chosen_practice

        # 3. Zbalansuj pozycje odpowiedzi (A, B, C, D) równomiernie (po 5 z każdej litery)
        balanced_questions = balance_options_distribution(
            combined, seed=day.strftime("%Y%m%d")
        )

        # 4. Wymieszaj kolejność pytań w zestawie dziennym
        rng.shuffle(balanced_questions)

        return DailySet(
            date=day.isoformat(),
            questions=balanced_questions,
            source="lokalna pula",
        )


def _group_by_category(
    questions: Iterable[Question],
) -> dict[str, list[Question]]:
    grouped: dict[str, list[Question]] = {}
    for question in questions:
        grouped.setdefault(question.category, []).append(question)
    return grouped
