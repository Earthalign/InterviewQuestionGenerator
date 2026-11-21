from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from pydantic import ValidationError

from learning_app.core.models import DailySet, Progress, Question


class SQLiteLearningRepository:
    """Repozytorium SQLite do trwałego zapisu zestawów pytań i postępów."""

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS daily_sets (
                    day TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS attempts (
                    day TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    completed INTEGER NOT NULL,
                    correct INTEGER,
                    PRIMARY KEY (day, question_id),
                    FOREIGN KEY (day) REFERENCES daily_sets(day)
                );
                """
            )

    def get_daily_set(self, day: date) -> DailySet | None:
        """Pobiera zestaw pytań dla wskazanego dnia lub None."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT content, source FROM daily_sets WHERE day = ?",
                (day.isoformat(),),
            ).fetchone()

        if row is None:
            return None

        daily_set = self._deserialize_daily_set(day, row)
        if daily_set is None or not self._is_valid_set(daily_set):
            return None
        return daily_set

    def store_daily_set(self, daily_set: DailySet) -> DailySet:
        """Zapisuje zestaw pytań, jeśli nie istnieje poprawny zestaw na dany dzień."""
        day = date.fromisoformat(daily_set.date)
        content = json.dumps(
            [q.model_dump() for q in daily_set.questions],
            ensure_ascii=False,
        )

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT content, source FROM daily_sets WHERE day = ?",
                (daily_set.date,),
            ).fetchone()

            if row is not None:
                existing = self._deserialize_daily_set(day, row)
                if existing is not None and self._is_valid_set(existing):
                    return existing
                connection.execute(
                    "DELETE FROM attempts WHERE day = ?", (daily_set.date,)
                )

            connection.execute(
                """
                INSERT INTO daily_sets (day, content, source) VALUES (?, ?, ?)
                ON CONFLICT(day) DO UPDATE SET
                    content = excluded.content,
                    source = excluded.source
                """,
                (daily_set.date, content, daily_set.source),
            )
        return daily_set

    def replace_daily_set(self, daily_set: DailySet) -> None:
        """Zastępuje zestaw na dany dzień i zeruje powiązane próby."""
        content = json.dumps(
            [q.model_dump() for q in daily_set.questions],
            ensure_ascii=False,
        )
        with self._connect() as connection:
            connection.execute("DELETE FROM attempts WHERE day = ?", (daily_set.date,))
            connection.execute(
                """
                INSERT INTO daily_sets (day, content, source)
                VALUES (?, ?, ?)
                ON CONFLICT(day) DO UPDATE SET
                    content = excluded.content,
                    source = excluded.source
                """,
                (daily_set.date, content, daily_set.source),
            )

    def save_attempt(
        self,
        day: date,
        question_id: str,
        answer: str,
        completed: bool = True,
        correct: bool | None = None,
    ) -> None:
        """Zapisuje odpowiedź użytkownika na dane pytanie."""
        is_correct = completed if correct is None else correct
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO attempts (day, question_id, answer, completed, correct)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(day, question_id) DO UPDATE SET
                    answer = excluded.answer,
                    completed = excluded.completed,
                    correct = excluded.correct
                """,
                (
                    day.isoformat(),
                    question_id,
                    answer,
                    int(completed),
                    int(is_correct),
                ),
            )

    def get_progress(self, day: date, total: int = 20) -> Progress:
        """Oblicza bieżący postęp użytkownika i passę (streak)."""
        day_key = day.isoformat()
        with self._connect() as connection:
            completed_rows = connection.execute(
                "SELECT question_id FROM attempts WHERE day = ? AND completed = 1",
                (day_key,),
            ).fetchall()
            completed_days = connection.execute(
                """
                SELECT daily_sets.day, COUNT(attempts.question_id) AS completed_count
                FROM daily_sets
                LEFT JOIN attempts ON attempts.day = daily_sets.day AND attempts.completed = 1
                GROUP BY daily_sets.day
                ORDER BY daily_sets.day DESC
                """
            ).fetchall()

        completed_ids = [row["question_id"] for row in completed_rows]
        completed_count = len(completed_ids)
        percentage = round((completed_count / total) * 100) if total else 0
        streak = self._calculate_streak(completed_days, day, total)

        return Progress(
            completed=completed_count,
            total=total,
            percentage=percentage,
            streak=streak,
            completed_ids=completed_ids,
        )

    def _calculate_streak(
        self, rows: list[sqlite3.Row], day: date, total: int
    ) -> int:
        completed_by_day = {row["day"]: row["completed_count"] for row in rows}
        cursor = (
            day
            if completed_by_day.get(day.isoformat(), 0) >= total
            else day - timedelta(days=1)
        )
        streak = 0
        while completed_by_day.get(cursor.isoformat(), 0) >= total:
            streak += 1
            cursor -= timedelta(days=1)
        return streak

    @staticmethod
    def _deserialize_daily_set(day: date, row: sqlite3.Row) -> DailySet | None:
        try:
            return DailySet(
                date=day.isoformat(),
                questions=json.loads(row["content"]),
                source=row["source"],
            )
        except (ValidationError, json.JSONDecodeError, KeyError):
            return None

    @staticmethod
    def _is_valid_set(daily_set: DailySet) -> bool:
        questions = daily_set.questions
        return (
            len(questions) == 20
            and sum(q.kind == "theory" for q in questions) == 16
            and sum(q.kind == "practice" for q in questions) == 4
            and all(
                len(q.options) == 4 and q.correct_answer in q.options
                for q in questions
            )
            and all(
                len(
                    [
                        s.strip()
                        for s in q.explanation.replace("!", ".").replace("?", ".").split(".")
                        if len(s.strip()) > 5
                    ]
                )
                >= 3
                for q in questions
            )
        )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
