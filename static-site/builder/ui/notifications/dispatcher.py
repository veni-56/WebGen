"""
notifications/dispatcher.py — Async notification dispatcher.

Routes notifications to the correct channel (email, webhook, in-app).
Subscribes to the event bus to trigger notifications automatically.
"""
from __future__ import annotations

import queue
import threading
import time
from typing import Any


# ── Notification templates ────────────────────────────────────────────────────

TEMPLATES: dict[str, dict] = {
    "project.created":    {"subject": "Project created",    "body": "Your project '{name}' was created."},
    "build.completed":    {"subject": "Build complete",     "body": "Build for project '{project_id}' finished."},
    "deployment.finished":{"subject": "Deployment done",    "body": "Your site is live at {url}."},
    "plugin.installed":   {"subject": "Plugin installed",   "body": "Plugin '{slug}' was installed."},
    "user.invited":       {"subject": "You're invited",     "body": "You've been invited to join {org_name}."},
}


class NotificationDispatcher:
    MAX_QUEUE = 1000

    def __init__(self):
        self._queue   = queue.Queue(maxsize=self.MAX_QUEUE)
        self._stop    = threading.Event()
        self._thread: threading.Thread | None = None
        self._providers: dict[str, Any] = {}

    def register_provider(self, channel: str, provider: Any) -> None:
        self._providers[channel] = provider

    def start(self) -> None:
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._worker, daemon=True, name="notification-dispatcher"
        )
        self._thread.start()
        # Subscribe to event bus
        try:
            from core.event_bus import bus
            for event_type in TEMPLATES:
                bus.subscribe(event_type, self._on_event, group="notifications")
        except Exception:
            pass

    def stop(self) -> None:
        self._stop.set()

    def dispatch(self, user_id: str, notification_type: str,
                 payload: dict, channels: list[str] | None = None) -> None:
        item = {
            "user_id":           user_id,
            "notification_type": notification_type,
            "payload":           payload,
            "channels":          channels or ["inapp"],
            "ts":                time.time(),
        }
        try:
            self._queue.put_nowait(item)
        except queue.Full:
            pass

    def _on_event(self, event: dict) -> None:
        """Auto-dispatch notifications for subscribed events."""
        event_type = event.get("type", "")
        payload    = event.get("payload", {})
        user_id    = payload.get("user_id", "")
        if user_id and event_type in TEMPLATES:
            self.dispatch(user_id, event_type, payload)

    def _worker(self) -> None:
        while not self._stop.is_set():
            try:
                item = self._queue.get(timeout=1.0)
                self._send(item)
                self._queue.task_done()
            except queue.Empty:
                continue

    def _send(self, item: dict) -> None:
        for channel in item.get("channels", ["inapp"]):
            provider = self._providers.get(channel)
            if provider:
                try:
                    provider.send(item["user_id"], item["notification_type"],
                                  item["payload"])
                except Exception:
                    pass
            elif channel == "inapp":
                # Default: store in-app notification
                try:
                    from notifications.inapp import inapp_store
                    tpl  = TEMPLATES.get(item["notification_type"], {})
                    body = tpl.get("body", "").format(**item["payload"])
                    inapp_store.push(item["user_id"], item["notification_type"], body)
                except Exception:
                    pass


dispatcher = NotificationDispatcher()
