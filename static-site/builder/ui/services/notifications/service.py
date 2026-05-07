"""services/notifications/service.py — Notification domain service."""
from __future__ import annotations
from services.base import BaseService


class NotificationService(BaseService):
    service_name = "notifications"

    def send(self, user_id: str, notification_type: str,
             payload: dict, channels: list[str] | None = None) -> None:
        try:
            from notifications.dispatcher import dispatcher
            dispatcher.dispatch(user_id, notification_type, payload,
                                channels=channels or ["inapp"])
        except Exception as e:
            self._log("NOTIFICATION_FAIL", {"user_id": user_id, "type": notification_type, "error": str(e)}, "WARNING")

    def send_webhook(self, url: str, event_type: str, payload: dict) -> bool:
        try:
            from notifications.webhooks import WebhookSender
            return WebhookSender().send(url, event_type, payload)
        except Exception:
            return False
