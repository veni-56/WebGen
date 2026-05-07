"""notifications/webhooks.py — Signed webhook delivery."""
from __future__ import annotations
import hashlib
import hmac
import json
import os
import time
import urllib.request
import urllib.error


_WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "wbs-webhook-secret").encode()


def sign_payload(payload: bytes, secret: bytes = _WEBHOOK_SECRET) -> str:
    return "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()


class WebhookSender:
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self._timeout     = timeout
        self._max_retries = max_retries

    def send(self, url: str, event_type: str, payload: dict,
             secret: bytes | None = None) -> bool:
        body = json.dumps({"event": event_type, "payload": payload,
                           "ts": int(time.time())}).encode()
        sig  = sign_payload(body, secret or _WEBHOOK_SECRET)
        for attempt in range(self._max_retries):
            try:
                req = urllib.request.Request(
                    url, data=body, method="POST",
                    headers={
                        "Content-Type":    "application/json",
                        "X-WBS-Signature": sig,
                        "X-WBS-Event":     event_type,
                    }
                )
                with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                    return resp.status < 300
            except urllib.error.HTTPError as e:
                if e.code < 500:
                    return False   # client error — don't retry
                if attempt < self._max_retries - 1:
                    time.sleep(2 ** attempt)
            except Exception:
                if attempt < self._max_retries - 1:
                    time.sleep(2 ** attempt)
        return False
