#!/usr/bin/env bash
# build.sh — Render.com build script
set -euo pipefail

echo "[BUILD] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[BUILD] Creating data directories..."
mkdir -p /opt/render/project/data/uploads
mkdir -p /opt/render/project/data/published
mkdir -p /opt/render/project/data/logs

echo "[BUILD] Running DB migrations..."
python -c "
import sys, os
sys.path.insert(0, '.')
os.environ.setdefault('DB_PATH', '/opt/render/project/data/projects.db')
import sqlite3
from db.migrations import run_migrations
conn = sqlite3.connect(os.environ['DB_PATH'])
conn.execute('PRAGMA journal_mode=WAL')
run_migrations(conn)
conn.close()
print('Migrations done.')
" || echo "[WARN] Migration skipped (first deploy)"

echo "[BUILD] Done."
