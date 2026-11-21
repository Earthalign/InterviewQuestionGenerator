# 🧠 Interview Question Generator

**Python Interview Lab** — polskojęzyczna platforma do nauki i przygotowania do rozmów kwalifikacyjnych na poziomie **Senior Python Developer**.

> Deployed on [Render.com](https://interview-question-generator.onrender.com) · Built with FastAPI + SQLite + Groq AI

---

## Co robi aplikacja?

Każdego dnia generuje zestaw **20 pytań rekrutacyjnych** (16 teorii + 4 praktyki) z:

- 🐍 Python (GIL, generatory, dekoratory, asyncio, typy)
- ⚡ FastAPI / Flask / Django
- 🗄️ SQL, REST API
- 🤖 AI / RAG (embeddingi, wektorowe bazy danych)
- 🐳 Docker, Kubernetes, CI/CD

Pytania i dystraktory są **edukacyjne** — czytanie każdej opcji uczy czegoś nowego. Wyjaśnienia mają minimum 3–5 zdań z analizą techniczną na poziomie seniora.

---

## Funkcje

| Funkcja | Opis |
|---|---|
| 📅 Dzienny zestaw | 20 pytań losowanych każdego dnia (16 teoria / 4 praktyka) |
| 🎲 Mieszanie opcji | Poprawna odpowiedź równomiernie na A/B/C/D (25% każda) |
| 🤖 Groq AI | Opcjonalne generowanie pytań przez LLM (OpenAI-kompatybilne) |
| 💾 Lokalna pula | 53 ręcznie napisane pytania jako fallback bez klucza API |
| 📊 Postęp | Licznik ukończonych pytań + streak dzienny |
| 🔁 Retry | Pytania praktyczne można powtarzać do uzyskania poprawnej odpowiedzi |
| 🏷️ Kategorie | Filtrowanie po tematyce (Teoria / Praktyka / Do zrobienia / Ukończone) |

---

## Architektura

```
interview_helper/
├── main.py                        # Punkt wejścia (FastAPI app factory)
├── Dockerfile                     # Multi-stage build (Python 3.12-slim)
├── render.yaml                    # Konfiguracja deploymentu Render.com
├── requirements.txt
│
└── learning_app/
    ├── api/           # Warstwa HTTP (FastAPI routes, dependencies, app factory)
    ├── core/          # Modele Pydantic + konfiguracja (dataclass Settings)
    ├── infrastructure/
    │   ├── ai/        # GroqQuestionProvider + CuratedQuestionProvider
    │   └── db/        # SQLiteLearningRepository
    ├── questions/     # Bank pytań (53 pyt.) + shuffler (balansowanie A/B/C/D)
    ├── services/      # LearningService (logika biznesowa)
    └── static/        # Frontend (Vanilla JS, modern CSS design system)
```

---

## Uruchomienie lokalne

```bash
git clone https://github.com/Earthalign/InterviewQuestionGenerator
cd InterviewQuestionGenerator

pip install -r requirements.txt
uvicorn main:app --reload
# Otwórz http://localhost:8000
```

### Z kluczem Groq (opcjonalnie)

```bash
# Ustaw zmienną środowiskową
export GROQ_API_KEY=gsk_...
uvicorn main:app --reload
```

---

## Deployment na Render.com

```bash
# 1. Utwórz nowe Web Service na render.com (Docker)
# 2. Podłącz repo GitHub
# 3. Render automatycznie wykryje render.yaml
# 4. Ustaw GROQ_API_KEY w dashboardzie (Settings → Environment)
```

> **Persistent disk** (`/data/learning.db`) jest automatycznie montowany przez render.yaml, dzięki czemu postępy i wygenerowane zestawy przeżywają restarty kontenera.

---

## Zmienne środowiskowe

| Zmienna | Opis | Domyślna |
|---|---|---|
| `GROQ_API_KEY` | Klucz API Groq (opcjonalny) | — |
| `GROQ_MODEL` | Model LLM | `openai/gpt-oss-20b` |
| `GROQ_BASE_URL` | URL API | `https://api.groq.com/openai/v1` |
| `DATABASE_PATH` | Ścieżka do pliku SQLite | `/data/learning.db` |

---

## Stack technologiczny

- **Backend**: Python 3.12, FastAPI, Pydantic v2, httpx, SQLite
- **Frontend**: Vanilla JS, CSS Custom Properties, Plus Jakarta Sans
- **AI**: Groq API (structured JSON output, 8192 token completion)
- **Deploy**: Docker (multi-stage), Render.com, persistent disk
- **Testy**: pytest (17 testów, 100% pass)
