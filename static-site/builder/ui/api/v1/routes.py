"""
api/v1/routes.py — API v1 Blueprint.

Registers all /api/v1/ routes as a Flask Blueprint.
Wraps existing server.py logic via the repository layer.
Backward-compatible with /api/ routes (server.py still handles those).

New in v1:
  - Multi-tenant: org_id + workspace_id on all resources
  - Repository pattern (no raw SQL)
  - Consistent { success, data, error } envelope
  - Request validation via schemas
  - Deprecation headers
  - Collab endpoints
  - Plugin marketplace endpoints
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from flask import Blueprint, g, jsonify, request, session

# Ensure parent dirs are on path
_UI = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_UI))

from db.connection import get_conn, transaction
from db.repositories import (
    UserRepository, OrgRepository, WorkspaceRepository,
    ProjectRepository, AuditRepository,
)
from security.rbac import require_role, require_permission, has_role

v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")


# ── Response helpers ──────────────────────────────────────────────────────────

def ok(data=None, status=200):
    return jsonify({"success": True, "data": data or {}, "error": "",
                    "api_version": "v1"}), status

def err(msg: str, status=400):
    return jsonify({"success": False, "data": {}, "error": msg,
                    "api_version": "v1"}), status


# ── Tenant middleware ─────────────────────────────────────────────────────────

@v1.before_request
def _resolve_tenant():
    """
    Resolve org + workspace from request.
    Sets g.org_id, g.workspace_id, g.member_role.
    """
    g.user_id     = session.get("user_id")
    g.org_id      = request.headers.get("X-Org-ID")      or request.args.get("org_id")
    g.workspace_id = request.headers.get("X-Workspace-ID") or request.args.get("workspace_id")
    g.member_role = None

    if g.user_id and g.org_id:
        conn = get_conn()
        repo = OrgRepository(conn)
        member = repo.get_member(g.org_id, g.user_id)
        if member:
            g.member_role = member["role"]


# ── Auth ──────────────────────────────────────────────────────────────────────

@v1.route("/auth/me", methods=["GET"])
def v1_me():
    if not g.user_id:
        return err("Not authenticated", 401)
    conn = get_conn()
    user = UserRepository(conn).find_by_id(g.user_id)
    if not user:
        return err("User not found", 404)
    return ok({"id": user["id"], "email": user["email"]})


# ── Organizations ─────────────────────────────────────────────────────────────

@v1.route("/orgs", methods=["GET"])
def list_orgs():
    if not g.user_id:
        return err("Not authenticated", 401)
    conn  = get_conn()
    orgs  = OrgRepository(conn).list_for_user(g.user_id)
    return ok({"orgs": orgs})


@v1.route("/orgs", methods=["POST"])
def create_org():
    if not g.user_id:
        return err("Not authenticated", 401)
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    slug = (data.get("slug") or name.lower().replace(" ", "-")).strip()
    if not name:
        return err('"name" is required')
    conn   = get_conn()
    repo   = OrgRepository(conn)
    if repo.find_by_slug(slug):
        return err(f'Slug "{slug}" is already taken')
    with transaction(conn):
        org_id = repo.create(name, slug)
        repo.add_member(org_id, g.user_id, "owner")
        AuditRepository(conn).log(org_id, g.user_id, "org.create", "org", org_id)
    return ok({"id": org_id, "name": name, "slug": slug}, 201)


@v1.route("/orgs/<org_id>/members", methods=["GET"])
@require_role("viewer")
def list_members(org_id):
    conn    = get_conn()
    members = OrgRepository(conn).list_members(org_id)
    return ok({"members": members})


@v1.route("/orgs/<org_id>/members", methods=["POST"])
@require_role("admin")
def add_member(org_id):
    data    = request.get_json(silent=True) or {}
    user_id = data.get("user_id", "").strip()
    role    = data.get("role", "viewer")
    if not user_id:
        return err('"user_id" is required')
    if role not in ("owner", "admin", "editor", "viewer"):
        return err('role must be owner|admin|editor|viewer')
    conn = get_conn()
    with transaction(conn):
        OrgRepository(conn).add_member(org_id, user_id, role)
        AuditRepository(conn).log(org_id, g.user_id, "member.add",
                                   "user", user_id, {"role": role})
    return ok({}, 201)


# ── Workspaces ────────────────────────────────────────────────────────────────

@v1.route("/orgs/<org_id>/workspaces", methods=["GET"])
@require_role("viewer")
def list_workspaces(org_id):
    conn = get_conn()
    wss  = WorkspaceRepository(conn).list_for_org(org_id)
    return ok({"workspaces": wss})


@v1.route("/orgs/<org_id>/workspaces", methods=["POST"])
@require_role("admin")
def create_workspace(org_id):
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    slug = (data.get("slug") or name.lower().replace(" ", "-")).strip()
    if not name:
        return err('"name" is required')
    conn = get_conn()
    with transaction(conn):
        ws_id = WorkspaceRepository(conn).create(org_id, name, slug)
        AuditRepository(conn).log(org_id, g.user_id, "workspace.create",
                                   "workspace", ws_id)
    return ok({"id": ws_id, "name": name, "slug": slug}, 201)


# ── Projects ──────────────────────────────────────────────────────────────────

@v1.route("/orgs/<org_id>/projects", methods=["GET"])
@require_role("viewer")
def list_projects_v1(org_id):
    conn  = get_conn()
    ws_id = g.workspace_id
    if ws_id:
        projects = ProjectRepository(conn).list_for_workspace(ws_id)
    else:
        projects = ProjectRepository(conn).list_for_user(g.user_id)
    # Strip config from list (too large)
    for p in projects:
        p.pop("config", None)
    return ok({"projects": projects})


@v1.route("/orgs/<org_id>/projects", methods=["POST"])
@require_permission("projects", "write")
def create_project_v1(org_id):
    data   = request.get_json(silent=True) or {}
    name   = (data.get("name") or "").strip()
    config = data.get("config") or {}
    if not name:
        return err('"name" is required')
    slug   = name.lower().replace(" ", "-")
    ws_id  = g.workspace_id
    conn   = get_conn()
    with transaction(conn):
        pid = ProjectRepository(conn).create(
            g.user_id, org_id, ws_id, name, slug, config
        )
        AuditRepository(conn).log(org_id, g.user_id, "project.create",
                                   "project", pid, {"name": name})
    return ok({"id": pid, "name": name, "slug": slug}, 201)


@v1.route("/projects/<pid>", methods=["GET"])
def get_project_v1(pid):
    if not g.user_id:
        return err("Not authenticated", 401)
    conn    = get_conn()
    project = ProjectRepository(conn).find_by_id(pid)
    if not project:
        return err("Project not found", 404)
    # Check org membership
    member = OrgRepository(conn).get_member(project["org_id"], g.user_id)
    if not member:
        return err("Access denied", 403)
    return ok(project)


@v1.route("/projects/<pid>", methods=["PUT"])
def update_project_v1(pid):
    if not g.user_id:
        return err("Not authenticated", 401)
    conn    = get_conn()
    project = ProjectRepository(conn).find_by_id(pid)
    if not project:
        return err("Project not found", 404)
    member = OrgRepository(conn).get_member(project["org_id"], g.user_id)
    if not member or not has_role(member["role"], "editor"):
        return err("Insufficient permissions", 403)
    data    = request.get_json(silent=True) or {}
    updates = {}
    if "config" in data: updates["config"] = data["config"]
    if "name"   in data: updates["name"]   = data["name"]
    changed = ProjectRepository(conn).update(pid, **updates)
    if changed:
        AuditRepository(conn).log(project["org_id"], g.user_id,
                                   "project.update", "project", pid)
    return ok({"skipped": not changed})


@v1.route("/projects/<pid>", methods=["DELETE"])
def delete_project_v1(pid):
    if not g.user_id:
        return err("Not authenticated", 401)
    conn    = get_conn()
    project = ProjectRepository(conn).find_by_id(pid)
    if not project:
        return err("Project not found", 404)
    member = OrgRepository(conn).get_member(project["org_id"], g.user_id)
    if not member or not has_role(member["role"], "admin"):
        return err("Insufficient permissions", 403)
    with transaction(conn):
        ProjectRepository(conn).delete(pid)
        AuditRepository(conn).log(project["org_id"], g.user_id,
                                   "project.delete", "project", pid)
    return ok({})


# ── Collaboration ─────────────────────────────────────────────────────────────

@v1.route("/collab/<doc_id>/session", methods=["POST"])
def collab_open(doc_id):
    if not g.user_id:
        return err("Not authenticated", 401)
    from collab.sync import open_session
    conn  = get_conn()
    user  = UserRepository(conn).find_by_id(g.user_id)
    email = user["email"] if user else ""
    sess  = open_session(doc_id, g.user_id, g.org_id or "", email)
    return ok(sess, 201)


@v1.route("/collab/<doc_id>/session/<sid>", methods=["DELETE"])
def collab_close(doc_id, sid):
    if not g.user_id:
        return err("Not authenticated", 401)
    from collab.sync import close_session
    close_session(sid, doc_id, g.user_id)
    return ok({})


@v1.route("/collab/<doc_id>/ops", methods=["POST"])
def collab_submit(doc_id):
    if not g.user_id:
        return err("Not authenticated", 401)
    from collab.sync import submit_ops
    data       = request.get_json(silent=True) or {}
    ops        = data.get("ops", [])
    client_seq = data.get("seq", 0)
    result     = submit_ops(doc_id, g.user_id, ops, client_seq)
    return ok(result)


@v1.route("/collab/<doc_id>/ops", methods=["GET"])
def collab_poll(doc_id):
    if not g.user_id:
        return err("Not authenticated", 401)
    from collab.sync import get_ops_since
    seq    = int(request.args.get("since", 0))
    result = get_ops_since(doc_id, seq)
    return ok(result)


@v1.route("/collab/<doc_id>/presence", methods=["GET"])
def collab_presence(doc_id):
    if not g.user_id:
        return err("Not authenticated", 401)
    from collab.sync import get_presence
    return ok({"presence": get_presence(doc_id)})


@v1.route("/collab/<doc_id>/ping", methods=["POST"])
def collab_ping(doc_id):
    if not g.user_id:
        return err("Not authenticated", 401)
    from collab.sync import ping_session
    data = request.get_json(silent=True) or {}
    ok_  = ping_session(
        data.get("session_id", ""), doc_id, g.user_id,
        seq=data.get("seq"), cursor_block=data.get("cursor_block",""),
        cursor_page=data.get("cursor_page","")
    )
    return ok({"alive": ok_})


# ── Plugin marketplace ────────────────────────────────────────────────────────

@v1.route("/plugins", methods=["GET"])
def list_plugins():
    conn = get_conn()
    from marketplace.registry import PluginRegistry
    reg  = PluginRegistry(conn)
    return ok({"plugins": reg.list_all()})


@v1.route("/plugins/install", methods=["POST"])
@require_role("admin")
def install_plugin():
    data     = request.get_json(silent=True) or {}
    manifest = data.get("manifest")
    sig      = data.get("signature")
    if not manifest:
        return err('"manifest" is required')
    conn = get_conn()
    from marketplace.installer import PluginInstaller
    result = PluginInstaller(conn).install_from_manifest(manifest, sig)
    if not result["ok"]:
        return err(str(result.get("errors", "Install failed")), 400)
    return ok(result, 201)


@v1.route("/plugins/<slug>/uninstall", methods=["POST"])
@require_role("admin")
def uninstall_plugin(slug):
    conn = get_conn()
    from marketplace.installer import PluginInstaller
    result = PluginInstaller(conn).uninstall(slug)
    return ok(result) if result["ok"] else err(str(result.get("errors")))


# ── Audit logs ────────────────────────────────────────────────────────────────

@v1.route("/orgs/<org_id>/audit", methods=["GET"])
@require_role("admin")
def audit_logs(org_id):
    conn  = get_conn()
    limit = min(int(request.args.get("limit", 100)), 500)
    logs  = AuditRepository(conn).list_for_org(org_id, limit)
    return ok({"logs": logs})


# ── OpenAPI spec ──────────────────────────────────────────────────────────────

@v1.route("/openapi.json", methods=["GET"])
def openapi_spec():
    """Return a minimal OpenAPI 3.0 spec for v1 endpoints."""
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title":   "WebGen Builder API",
            "version": "1.0.0",
            "description": "Multi-tenant website builder API",
        },
        "servers": [{"url": "/api/v1"}],
        "paths": {
            "/auth/me":                    {"get":    {"summary": "Get current user"}},
            "/orgs":                       {"get":    {"summary": "List orgs"},
                                            "post":   {"summary": "Create org"}},
            "/orgs/{org_id}/members":      {"get":    {"summary": "List members"},
                                            "post":   {"summary": "Add member"}},
            "/orgs/{org_id}/workspaces":   {"get":    {"summary": "List workspaces"},
                                            "post":   {"summary": "Create workspace"}},
            "/orgs/{org_id}/projects":     {"get":    {"summary": "List projects"},
                                            "post":   {"summary": "Create project"}},
            "/projects/{pid}":             {"get":    {"summary": "Get project"},
                                            "put":    {"summary": "Update project"},
                                            "delete": {"summary": "Delete project"}},
            "/collab/{doc_id}/session":    {"post":   {"summary": "Open collab session"}},
            "/collab/{doc_id}/ops":        {"post":   {"summary": "Submit ops"},
                                            "get":    {"summary": "Poll ops"}},
            "/collab/{doc_id}/presence":   {"get":    {"summary": "Get presence"}},
            "/plugins":                    {"get":    {"summary": "List plugins"}},
            "/plugins/install":            {"post":   {"summary": "Install plugin"}},
            "/orgs/{org_id}/audit":        {"get":    {"summary": "Audit logs"}},
        },
        "components": {
            "securitySchemes": {
                "session": {"type": "apiKey", "in": "cookie", "name": "session"},
                "apiKey":  {"type": "apiKey", "in": "header", "name": "X-API-Key"},
            }
        },
    }
    return jsonify(spec)


@v1.route("/docs", methods=["GET"])
def api_docs():
    """Redirect to OpenAPI spec viewer."""
    return f"""<!DOCTYPE html>
<html><head><title>API v1 Docs</title>
<meta http-equiv="refresh" content="0;url=https://petstore.swagger.io/?url=/api/v1/openapi.json">
</head><body>Redirecting to API docs...</body></html>"""
