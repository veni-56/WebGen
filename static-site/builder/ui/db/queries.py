"""
Named read-only SQL query constants for the Website Builder SaaS platform.

All entries in ``QUERIES`` are plain SELECT statements intended to be used
with parameterized execution, e.g.::

    from db.queries import QUERIES
    rows = conn.execute(QUERIES["GET_WORKSPACE_PROJECTS"], (ws_id, limit)).fetchall()

Role hierarchy (lowest → highest privilege):
    viewer < editor < admin < owner

The CHECK_PERMISSION query uses a CASE expression to map role names to
integer weights so callers can compare against a required minimum level.
"""

from __future__ import annotations

QUERIES: dict[str, str] = {
    # ------------------------------------------------------------------
    # GET_PROJECT_WITH_ORG
    # Returns a single project row joined with its parent organization.
    # Bind: (project_id,)
    # ------------------------------------------------------------------
    "GET_PROJECT_WITH_ORG": """
        SELECT
            p.id              AS project_id,
            p.name            AS project_name,
            p.slug            AS project_slug,
            p.config          AS project_config,
            p.config_hash,
            p.published,
            p.publish_url,
            p.created_at      AS project_created_at,
            p.updated_at      AS project_updated_at,
            o.id              AS org_id,
            o.name            AS org_name,
            o.slug            AS org_slug,
            o.plan            AS org_plan
        FROM projects p
        JOIN organizations o ON o.id = p.org_id
        WHERE p.id = ?
    """,

    # ------------------------------------------------------------------
    # GET_USER_ORGS
    # All organizations a user belongs to, including their role.
    # Bind: (user_id,)
    # ------------------------------------------------------------------
    "GET_USER_ORGS": """
        SELECT
            o.id         AS org_id,
            o.name       AS org_name,
            o.slug       AS org_slug,
            o.plan       AS org_plan,
            o.created_at AS org_created_at,
            m.role       AS member_role,
            m.created_at AS joined_at
        FROM organizations o
        JOIN org_members m ON m.org_id = o.id
        WHERE m.user_id = ?
        ORDER BY o.name ASC
    """,

    # ------------------------------------------------------------------
    # GET_WORKSPACE_PROJECTS
    # All projects in a workspace, newest first.
    # Bind: (workspace_id, limit)
    # ------------------------------------------------------------------
    "GET_WORKSPACE_PROJECTS": """
        SELECT
            p.id,
            p.name,
            p.slug,
            p.config_hash,
            p.published,
            p.publish_url,
            p.created_at,
            p.updated_at,
            p.user_id
        FROM projects p
        WHERE p.workspace_id = ?
        ORDER BY p.updated_at DESC
        LIMIT ?
    """,

    # ------------------------------------------------------------------
    # GET_RECENT_AUDIT
    # Recent audit log entries for an org, enriched with the actor's email.
    # Bind: (org_id, limit)
    # ------------------------------------------------------------------
    "GET_RECENT_AUDIT": """
        SELECT
            al.id,
            al.action,
            al.resource_type,
            al.resource_id,
            al.metadata,
            al.ip,
            al.created_at,
            al.user_id,
            u.email AS user_email
        FROM audit_logs al
        LEFT JOIN users u ON u.id = al.user_id
        WHERE al.org_id = ?
        ORDER BY al.created_at DESC
        LIMIT ?
    """,

    # ------------------------------------------------------------------
    # GET_JOB_STATS
    # Count of jobs grouped by status.
    # Bind: ()  — no parameters
    # ------------------------------------------------------------------
    "GET_JOB_STATS": """
        SELECT
            status,
            COUNT(*) AS total
        FROM jobs
        GROUP BY status
        ORDER BY status
    """,

    # ------------------------------------------------------------------
    # CHECK_PERMISSION
    # Returns a single row with ``has_permission`` = 1 when the user's
    # role weight is >= the required role weight, 0 otherwise.
    #
    # Role weights: viewer=1, editor=2, admin=3, owner=4
    #
    # Bind: (org_id, user_id, required_role)
    # where required_role is one of 'viewer', 'editor', 'admin', 'owner'.
    # ------------------------------------------------------------------
    "CHECK_PERMISSION": """
        SELECT
            CASE
                WHEN CASE m.role
                         WHEN 'viewer' THEN 1
                         WHEN 'editor' THEN 2
                         WHEN 'admin'  THEN 3
                         WHEN 'owner'  THEN 4
                         ELSE 0
                     END
                     >=
                     CASE ?
                         WHEN 'viewer' THEN 1
                         WHEN 'editor' THEN 2
                         WHEN 'admin'  THEN 3
                         WHEN 'owner'  THEN 4
                         ELSE 99
                     END
                THEN 1
                ELSE 0
            END AS has_permission,
            m.role AS actual_role
        FROM org_members m
        WHERE m.org_id = ?
          AND m.user_id = ?
    """,
}
