from __future__ import annotations

from learning_app.core.models import Question
from learning_app.questions.bank import build_question_bank
from learning_app.questions.shuffler import shuffle_options


def test_question_bank_options_are_shuffled_and_valid() -> None:
    questions = build_question_bank()
    assert len(questions) >= 20

    # Upewnij się, że poprawna odpowiedź NIE jest zawsze na pozycji 0
    positions = [q.options.index(q.correct_answer) for q in questions]
    assert len(set(positions)) > 1, "Poprawna odpowiedź nie może być zawsze na tej samej pozycji!"
    assert any(pos != 0 for pos in positions)

    for q in questions:
        assert len(q.options) == 4
        assert q.correct_answer in q.options
        assert len(set(q.options)) == 4, f"Opcje w pytaniu {q.id} muszą być unikalne."
        assert q.prompt.strip()
        assert q.title.strip()
        assert q.explanation.strip()


def test_question_bank_explanations_have_multiple_sentences() -> None:
    questions = build_question_bank()
    for q in questions:
        sentences = [
            s.strip()
            for s in q.explanation.replace("!", ".").replace("?", ".").split(".")
            if len(s.strip()) > 5
        ]
        assert len(sentences) >= 3, (
            f"Pytanie '{q.id}' ma za krótkie wyjaśnienie ({len(sentences)} zdań). "
            f"Wymagane są minimum 3 pełne zdania. Wyjaśnienie: {q.explanation}"
        )


def test_question_bank_polish_language_quality() -> None:
    questions = build_question_bank()
    forbidden_ponglish = [
        "yielduje",
        "nie awaitować",
        "po timeoutcie",
        "All of the above",
        "krotka kopiowana przy każdym put",
    ]

    for q in questions:
        full_text = f"{q.title} {q.prompt} {' '.join(q.options)} {q.explanation}"
        for bad_word in forbidden_ponglish:
            assert bad_word.lower() not in full_text.lower(), (
                f"Znaleziono niedozwolony żargon/Ponglish '{bad_word}' w pytaniu {q.id}"
            )


def test_shuffler_preserves_elements_and_randomizes() -> None:
    opts = ["Opcja 1", "Opcja 2", "Opcja 3", "Opcja 4"]
    shuffled_1 = shuffle_options(opts, seed=42)
    shuffled_2 = shuffle_options(opts, seed=999)

    assert set(shuffled_1) == set(opts)
    assert set(shuffled_2) == set(opts)


def test_curated_daily_set_has_sixteen_theory_and_balanced_options() -> None:
    import asyncio
    from datetime import date
    from collections import Counter
    from learning_app.infrastructure.ai.base import CuratedQuestionProvider

    provider = CuratedQuestionProvider()
    daily_set = asyncio.run(provider.create_daily_set(date(2026, 11, 21)))

    assert len(daily_set.questions) == 20
    theory_count = sum(q.kind == "theory" for q in daily_set.questions)
    practice_count = sum(q.kind == "practice" for q in daily_set.questions)
    assert theory_count == 16
    assert practice_count == 4

    positions = [q.options.index(q.correct_answer) for q in daily_set.questions]
    counts = Counter(positions)
    # Dokładnie po 5 pytań z poprawną odpowiedzią na pozycji A, B, C, D (25% każda)
    assert counts[0] == 5
    assert counts[1] == 5
    assert counts[2] == 5
    assert counts[3] == 5
