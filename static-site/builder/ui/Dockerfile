# ── Stage 1: dependency builder ───────────────────────────────────────────────
FROM python:3.12-slim AS deps

WORKDIR /deps

# Install build tools needed for bcrypt + Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev libjpeg-dev zlib1g-dev libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Security: run as non-root
RUN groupadd -r wbs && useradd -r -g wbs -d /app -s /sbin/nologin wbs

# Copy installed packages from deps stage
COPY --from=deps /install /usr/local

WORKDIR /app

# Copy application source
# builder/ui  → /app/ui
# builder/     → /app  (for build.py, engine.py, etc.)
COPY . /app/ui/
COPY ../  /app/

# Ensure data directories exist (will be overridden by volume mounts)
RUN mkdir -p /data/db /data/uploads /data/published /data/logs \
    && chown -R wbs:wbs /app /data

# Tell server.py where to find data via env vars
ENV DB_PATH=/data/db/projects.db \
    UPLOADS_DIR=/data/uploads \
    PUBLISH_DIR=/data/published \
    LOG_DIR=/data/logs \
    PORT=4000 \
    FLASK_DEBUG=0 \
    WORKER_COUNT=2 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app/ui

USER wbs

EXPOSE 4000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:4000/health')" || exit 1

# Default: run web server
CMD ["gunicorn", "-c", "gunicorn.conf.py", "server:app"]
