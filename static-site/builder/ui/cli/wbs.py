#!/usr/bin/env python3
"""
cli/wbs.py — WebGen Builder CLI tool.

Commands:
    wbs dev          Start local dev server
    wbs doctor       Check system health
    wbs migrate      Run DB migrations
    wbs create-plugin <name>  Scaffold a new plugin
    wbs deploy <provider>     Deploy to a provider
    wbs backup       Create a backup

Usage:
    python -m cli.wbs <command> [options]
    # or after pip install: wbs <command>
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

UI_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(UI_DIR))
sys.path.insert(0, str(UI_DIR.parent))


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_dev(args):
    """Start the local development server."""
    port  = args.port or int(os.environ.get("PORT", "4000"))
    print(f"[WBS] Starting dev server on http://localhost:{port}")
    os.environ["FLASK_DEBUG"] = "1"
    os.environ["PORT"]        = str(port)
    os.chdir(UI_DIR)
    os.execvp(sys.executable, [sys.executable, "server.py"])


def cmd_doctor(args):
    """Check system health and dependencies."""
    import importlib
    print("[WBS Doctor] Checking system...\n")
    checks = [
        ("flask",          "Flask web framework"),
        ("bcrypt",         "Password hashing"),
        ("dotenv",         "Environment config"),
        ("PIL",            "Image optimization (Pillow)"),
        ("gevent",         "Async workers"),
    ]
    all_ok = True
    for mod, desc in checks:
        try:
            importlib.import_module(mod)
            print(f"  ✓ {desc} ({mod})")
        except ImportError:
            print(f"  ✗ {desc} ({mod}) — run: pip install {mod}")
            all_ok = False

    # Check DB
    db_path = Path(os.environ.get("DB_PATH", str(UI_DIR / "projects.db")))
    if db_path.exists():
        print(f"\n  ✓ Database found: {db_path}")
    else:
        print(f"\n  ⚠ Database not found: {db_path} (will be created on first run)")

    # Check .env
    env_file = UI_DIR / ".env"
    if env_file.exists():
        print(f"  ✓ .env file found")
    else:
        print(f"  ⚠ .env not found — copy .env.example to .env")

    print(f"\n{'✓ All checks passed' if all_ok else '✗ Some checks failed — see above'}")


def cmd_migrate(args):
    """Run database migrations."""
    import sqlite3
    sys.path.insert(0, str(UI_DIR))
    from db.migrations import run_migrations
    db_path = Path(os.environ.get("DB_PATH", str(UI_DIR / "projects.db")))
    print(f"[WBS Migrate] Running migrations on {db_path}...")
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    run_migrations(conn)
    conn.close()
    print("[WBS Migrate] Done.")


def cmd_create_plugin(args):
    """Scaffold a new plugin."""
    name     = args.name
    slug     = name.lower().replace(" ", "_").replace("-", "_")
    dest     = UI_DIR / "plugins" / slug
    if dest.exists():
        print(f"[WBS] Plugin '{slug}' already exists at {dest}")
        sys.exit(1)
    dest.mkdir(parents=True)
    (dest / "__init__.py").write_text("")
    (dest / "index.js").write_text(f"""/**
 * plugins/{slug}/index.js — {name} plugin.
 */
'use strict';

const {slug.title()}Plugin = {{
  id:      '{slug}',
  name:    '{name}',
  version: '1.0.0',
  settings: {{}},
  hooks: {{}},
  render()   {{ return null; }},
  validate() {{ return []; }},
  onEnable(s)  {{ console.info('[{name}] enabled'); }},
  onDisable()  {{ console.info('[{name}] disabled'); }},
}};

if (typeof WBS_SDK !== 'undefined') {{
  WBS_SDK.registerPlugin({slug.title()}Plugin);
}}
""")
    (dest / "manifest.json").write_text(f"""{{\n  "id": "{slug}",\n  "name": "{name}",\n  "version": "1.0.0",\n  "author": "",\n  "description": ""\n}}\n""")
    print(f"[WBS] Plugin scaffolded at {dest}")
    print(f"  Edit: {dest}/index.js")


def cmd_deploy(args):
    """Deploy to a provider."""
    from deploy.providers import get_provider
    from pathlib import Path
    provider_name = args.provider
    build_dir     = Path(args.dir) if args.dir else UI_DIR / "published" / "default" / "latest"
    print(f"[WBS Deploy] Deploying to {provider_name} from {build_dir}...")
    provider = get_provider(provider_name)
    errors   = provider.validate(build_dir)
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    result = provider.deploy(build_dir, args.name or "wbs-site")
    if result.get("ok"):
        print(f"  ✓ Deployed: {result.get('url')}")
    else:
        print(f"  ✗ Deploy failed: {result.get('error') or result.get('errors')}")
        sys.exit(1)


def cmd_backup(args):
    """Create a backup archive."""
    import subprocess
    script = UI_DIR / "deploy" / "backup.sh"
    if script.exists():
        subprocess.run(["bash", str(script)], check=True)
    else:
        print("[WBS Backup] backup.sh not found. Run from the deploy/ directory.")


# ── CLI entry point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(prog="wbs", description="WebGen Builder CLI")
    sub    = parser.add_subparsers(dest="command")

    p_dev = sub.add_parser("dev", help="Start local dev server")
    p_dev.add_argument("--port", type=int, default=None)

    sub.add_parser("doctor", help="Check system health")
    sub.add_parser("migrate", help="Run DB migrations")

    p_plugin = sub.add_parser("create-plugin", help="Scaffold a new plugin")
    p_plugin.add_argument("name", help="Plugin name")

    p_deploy = sub.add_parser("deploy", help="Deploy to a provider")
    p_deploy.add_argument("provider", choices=["vercel", "netlify", "docker"])
    p_deploy.add_argument("--dir",  default=None, help="Build directory")
    p_deploy.add_argument("--name", default="wbs-site", help="Project name")

    sub.add_parser("backup", help="Create a backup")

    args = parser.parse_args()
    cmds = {
        "dev":           cmd_dev,
        "doctor":        cmd_doctor,
        "migrate":       cmd_migrate,
        "create-plugin": cmd_create_plugin,
        "deploy":        cmd_deploy,
        "backup":        cmd_backup,
    }
    fn = cmds.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
