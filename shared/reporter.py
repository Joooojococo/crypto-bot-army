"""
Crypto Bot Army — 共享 Discord Webhook 通知模組
"""
import logging
import requests
from datetime import datetime, timezone
from typing import Any, Optional

log = logging.getLogger("army.reporter")

COLOR_GREEN = 0x00FF00
COLOR_BLUE = 0x3498DB
COLOR_ORANGE = 0xE67E22
COLOR_RED = 0xFF0000
COLOR_GOLD = 0xF1C40F


class DiscordReporter:
    """通用 Discord Webhook 通知器"""

    def __init__(self, webhook_url: str, username: str = "🪖 Crypto Bot Army"):
        self._webhook_url = webhook_url
        self._username = username

    def _is_enabled(self) -> bool:
        return bool(self._webhook_url)

    def send(self, title: str, description: str = "", fields: list = None,
             color: int = COLOR_BLUE, footer: str = "") -> bool:
        if not self._is_enabled():
            return False
        embed = {"title": title, "description": description, "color": color,
                 "timestamp": datetime.now(timezone.utc).isoformat()}
        if fields: embed["fields"] = fields
        if footer: embed["footer"] = {"text": footer}
        payload = {"username": self._username, "embeds": [embed]}
        try:
            resp = requests.post(self._webhook_url, json=payload, timeout=10)
            return resp.status_code == 204
        except Exception as e:
            log.error(f"Discord send failed: {e}")
            return False

    def send_alert(self, message: str) -> bool:
        if not self._is_enabled(): return False
        try:
            requests.post(self._webhook_url, json={
                "username": self._username, "content": f"⚠️ {message}"
            }, timeout=10)
            return True
        except Exception:
            return False