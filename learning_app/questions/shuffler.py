from __future__ import annotations

import random
from collections.abc import Sequence

from learning_app.core.models import Question


def shuffle_options(
    options: Sequence[str], seed: str | int | None = None
) -> list[str]:
    """Zwraca kopię listy opcji z losowo/deterministycznie wymieszaną kolejnością."""
    result = list(options)
    rng = random.Random(seed)
    rng.shuffle(result)
    return result


def place_correct_answer_at(
    correct_answer: str,
    distractors: Sequence[str],
    target_index: int,
    seed: str | int | None = None,
) -> list[str]:
    """Umieszcza poprawną odpowiedź na wskazanym indeksie (0-3), a dystraktory tasuje."""
    dist_list = [d for d in distractors if d != correct_answer]
    rng = random.Random(seed)
    rng.shuffle(dist_list)
    idx = max(0, min(3, target_index))
    return dist_list[:idx] + [correct_answer] + dist_list[idx:]


def balance_options_distribution(
    questions: Sequence[Question], seed: str | int | None = None
) -> list[Question]:
    """Zapewnia idealnie zbalansowany rozkład pozycji poprawnej odpowiedzi (A, B, C, D).

    Dla 20 pytań każda pozycja (A, B, C, D) przypada dokładnie 5 razy.
    """
    rng = random.Random(seed)
    n = len(questions)
    target_indices = [i % 4 for i in range(n)]
    rng.shuffle(target_indices)

    balanced: list[Question] = []
    for question, target_idx in zip(questions, target_indices):
        distractors = [opt for opt in question.options if opt != question.correct_answer]
        rng.shuffle(distractors)
        new_options = (
            distractors[:target_idx] + [question.correct_answer] + distractors[target_idx:]
        )
        balanced.append(question.model_copy(update={"options": new_options}))
    return balanced
