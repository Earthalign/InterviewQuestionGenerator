# ── Stage 1: build deps ──────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # domyślna ścieżka bazy – nadpisywalna przez DATABASE_PATH
    DATABASE_PATH=/data/learning.db

WORKDIR /app

# Skopiuj zainstalowane paczki ze stage'a build
COPY --from=builder /install /usr/local

# Skopiuj kod aplikacji
COPY learning_app/ learning_app/
COPY main.py .

# Volumen na persystencję SQLite
VOLUME ["/data"]

EXPOSE 8000

# Render.com nadpisuje CMD przez startCommand; zostawiamy sensowny default.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
