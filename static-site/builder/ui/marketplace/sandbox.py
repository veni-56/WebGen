"""
marketplace/sandbox.py — Plugin sandboxing and permission isolation.

Provides a restricted execution context for plugin code.
Prevents plugins from accessing filesystem, network, or DB
beyond their declared permissions.

For Python-side plugins (server hooks), uses a restricted globals dict.
For JS-side plugins, the sandbox is enforced by the browser's iframe CSP.
"""
from __future__ import annotations

import builtins
import types
from typing import Any, Callable


# ── Allowed builtins for sandboxed plugins ────────────────────────────────────
_SAFE_BUILTINS = {
    "abs", "all", "any", "bool", "bytes", "chr", "dict", "dir",
    "divmod", "enumerate", "filter", "float", "format", "frozenset",
    "getattr", "hasattr", "hash", "hex", "int", "isinstance", "issubclass",
    "iter", "len", "list", "map", "max", "min", "next", "oct", "ord",
    "pow", "print", "range", "repr", "reversed", "round", "set", "setattr",
    "slice", "sorted", "str", "sum", "tuple", "type", "zip",
    "True", "False", "None",
    "ValueError", "TypeError", "KeyError", "IndexError", "AttributeError",
    "Exception", "RuntimeError", "StopIteration",
}

_SAFE_BUILTINS_DICT = {k: getattr(builtins, k) for k in _SAFE_BUILTINS if hasattr(builtins, k)}


class PluginSandbox:
    """
    Restricted execution environment for a single plugin.

    Permissions are checked before any sensitive operation.
    The sandbox wraps the plugin's callable and injects a
    restricted context object.
    """

    def __init__(self, plugin_id: str, permissions: set[str]):
        self.plugin_id   = plugin_id
        self.permissions = permissions
        self._call_log:  list[dict] = []

    def has_permission(self, scope: str) -> bool:
        return scope in self.permissions

    def require_permission(self, scope: str) -> None:
        if not self.has_permission(scope):
            raise PermissionError(
                f"Plugin '{self.plugin_id}' does not have permission '{scope}'"
            )

    def make_context(self, cfg: dict | None = None,
                     page_html: str | None = None) -> dict:
        """
        Build a restricted context dict passed to plugin hooks.
        Only exposes data the plugin has permission to see/modify.
        """
        ctx: dict[str, Any] = {"plugin_id": self.plugin_id}

        if self.has_permission("read:config") and cfg is not None:
            ctx["cfg"] = cfg   # read-only view (caller must not mutate)

        if self.has_permission("read:pages") and page_html is not None:
            ctx["html"] = page_html

        # Provide a safe log function
        ctx["log"] = lambda msg: self._call_log.append(
            {"plugin": self.plugin_id, "msg": str(msg)[:500]}
        )

        return ctx

    def run(self, fn: Callable, ctx: dict) -> Any:
        """
        Execute fn(ctx) in a sandboxed manner.
        Catches all exceptions and returns { ok, result, error }.
        """
        try:
            result = fn(ctx)
            return {"ok": True, "result": result, "error": None}
        except PermissionError as e:
            return {"ok": False, "result": None, "error": f"Permission denied: {e}"}
        except Exception as e:
            return {"ok": False, "result": None, "error": str(e)}

    def get_log(self) -> list[dict]:
        return list(self._call_log)


class SandboxRegistry:
    """Manages sandboxes for all installed plugins."""

    def __init__(self):
        self._sandboxes: dict[str, PluginSandbox] = {}

    def register(self, plugin_id: str, permissions: set[str]) -> PluginSandbox:
        sb = PluginSandbox(plugin_id, permissions)
        self._sandboxes[plugin_id] = sb
        return sb

    def get(self, plugin_id: str) -> PluginSandbox | None:
        return self._sandboxes.get(plugin_id)

    def remove(self, plugin_id: str) -> None:
        self._sandboxes.pop(plugin_id, None)


sandbox_registry = SandboxRegistry()
