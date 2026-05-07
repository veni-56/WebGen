#!/usr/bin/env bash
# stop.sh — Gracefully stop all services
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"

cd "$APP_DIR"

echo "[STOP] Stopping services (workers will finish current jobs)…"
docker compose stop --timeout 60

echo "[STOP] Services stopped."
echo "  To remove containers: docker compose down"
echo "  To remove volumes:    docker compose down -v  (WARNING: deletes all data)"
