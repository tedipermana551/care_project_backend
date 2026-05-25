# ── Base image ────────────────────────────────────────────────────────────────
FROM python:3.14-slim

# ── System deps ───────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ── Create non-root user (HuggingFace requires UID 1000) ─────────────────────
RUN useradd -m -u 1000 appuser

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Install Python deps ───────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project ──────────────────────────────────────────────────────────────
COPY . .

# ── Collect static files ──────────────────────────────────────────────────────
RUN python manage.py collectstatic --noinput

# ── Permissions ───────────────────────────────────────────────────────────────
RUN mkdir -p /app/media && chown -R appuser:appuser /app

USER appuser

# ── HuggingFace Spaces expects port 7860 ─────────────────────────────────────
EXPOSE 7860

# ── Entrypoint: migrate then start gunicorn ───────────────────────────────────
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn core.wsgi --workers 2 --timeout 120 --bind 0.0.0.0:7860"]