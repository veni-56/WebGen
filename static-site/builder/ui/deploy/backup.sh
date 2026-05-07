#!/usr/bin/env bash
# backup.sh — Backup database, uploads, and published sites to a timestamped archive.
# Usage: ./deploy/backup.sh [output_dir]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${1:-$APP_DIR/backups}"
TS=$(date -u +"%Y%m%d_%H%M%S")
ARCHIVE="$BACKUP_DIR/wbs_backup_$TS.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "[BACKUP] Starting backup → $ARCHIVE"

# ── Option A: backup from Docker volumes (preferred in production) ────────────
if docker compose -f "$APP_DIR/docker-compose.yml" ps --quiet web 2>/dev/null | grep -q .; then
  echo "[BACKUP] Backing up via running container…"
  docker compose -f "$APP_DIR/docker-compose.yml" exec -T web \
    python -c "
import sys; sys.path.insert(0,'/app/ui')
from server import admin_backup
" 2>/dev/null || true

  # Use docker cp to extract volumes
  TMP=$(mktemp -d)
  docker run --rm \
    -v wbs_db_data:/data/db:ro \
    -v wbs_uploads_data:/data/uploads:ro \
    -v wbs_published_data:/data/published:ro \
    -v "$TMP:/backup" \
    alpine sh -c "
      cp -r /data/db      /backup/db
      cp -r /data/uploads /backup/uploads
      cp -r /data/published /backup/published
    "
  tar -czf "$ARCHIVE" -C "$TMP" .
  rm -rf "$TMP"

# ── Option B: backup from local filesystem (dev mode) ────────────────────────
else
  echo "[BACKUP] Backing up from local filesystem…"
  cd "$APP_DIR"
  tar -czf "$ARCHIVE" \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    projects.db uploads/ published/ logs/ 2>/dev/null || true
fi

SIZE=$(du -sh "$ARCHIVE" 2>/dev/null | cut -f1)
echo "[BACKUP] Done — $ARCHIVE ($SIZE)"

# ── Prune old backups (keep last 7) ──────────────────────────────────────────
ls -t "$BACKUP_DIR"/wbs_backup_*.tar.gz 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null || true
echo "[BACKUP] Old backups pruned (keeping last 7)."
