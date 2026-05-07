#!/usr/bin/env bash
# start.sh — Build and start all services
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"

cd "$APP_DIR"

# ── Ensure .env exists ────────────────────────────────────────────────────────
if [ ! -f .env ]; then
  echo "[ERROR] .env file not found. Copy .env.example to .env and fill in values."
  exit 1
fi

# ── Create ssl directory if missing ──────────────────────────────────────────
mkdir -p nginx_ssl

# ── Pull latest images ────────────────────────────────────────────────────────
echo "[START] Pulling base images…"
docker compose pull nginx 2>/dev/null || true

# ── Build app images ──────────────────────────────────────────────────────────
echo "[START] Building images…"
docker compose build --no-cache

# ── Start services ────────────────────────────────────────────────────────────
echo "[START] Starting services…"
docker compose up -d

# ── Wait for health checks ────────────────────────────────────────────────────
echo "[START] Waiting for web service to be healthy…"
for i in $(seq 1 30); do
  STATUS=$(docker inspect --format='{{.State.Health.Status}}' wbs_web 2>/dev/null || echo "starting")
  if [ "$STATUS" = "healthy" ]; then
    echo "[START] Web service is healthy."
    break
  fi
  echo "  … waiting ($i/30) — status: $STATUS"
  sleep 3
done

echo ""
echo "✓ WebGen Builder is running."
echo "  Web:    http://localhost:${NGINX_HTTP_PORT:-80}"
echo "  Health: http://localhost:${NGINX_HTTP_PORT:-80}/health"
echo ""
echo "  Logs:   docker compose logs -f"
echo "  Stop:   ./deploy/stop.sh"
