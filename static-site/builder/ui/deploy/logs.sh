#!/usr/bin/env bash
# logs.sh — Tail logs from all services or a specific one.
# Usage: ./deploy/logs.sh [web|worker|nginx] [--lines N]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
SERVICE="${1:-}"
LINES="${2:-100}"

cd "$APP_DIR"

if [ -n "$SERVICE" ]; then
  docker compose logs -f --tail="$LINES" "$SERVICE"
else
  docker compose logs -f --tail="$LINES"
fi
