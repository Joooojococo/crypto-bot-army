"""
🧠 AI 幣種分析 Bot — 核心掃描器
用 DeepSeek AI 每日掃描市場幣種潛力 → Discord Report
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import signal
import sys
from datetime import datetime, timezone
from dataclasses import dataclass

import httpx

from config import AICoinScannerConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] ai-scanner: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("ai-scanner")


@dataclass
class CoinPick:
    """AI 分析出嘅單一幣種推薦"""
    symbol: str
    name: str
    score: int
    rationale: str
    risk: str
    timeframe: str


class AICoinScanner:
    """AI 幣種分析掃描器"""

    _SYSTEM_PROMPT = """你係專業加密貨幣分析師。請分析市場搵出今日最具潛力嘅幣種。

評分準則:
1. 技術面 (30%): 價位結構、支撐阻力、成交量
2. 基本面 (30%): 項目進展、合作夥伴、生態發展
3. 市場情緒 (20%): 社群熱度、資金流向
4. 風險回報 (20%): 潛在升幅 vs 下跌風險

請嚴格用 JSON array 回應:
[
  {
    "symbol": "BTC",
    "name": "Bitcoin",
    "score": 8,
    "rationale": "brief reason in Chinese",
    "risk": "medium",
    "timeframe": "1-4 weeks"
  }
]
score 1-10, risk low/medium/high, 只回傳 JSON"""

    def __init__(self, config: AICoinScannerConfig):
        self.config = config
        self._client: httpx.AsyncClient | None = None
        self._webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
        self._shutdown = False

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=90.0)
        return self._client

    async def scan(self) -> list[CoinPick]:
        """Call DeepSeek API, parse response"""
        if not self.config.api_key:
            log.error("DEEPSEEK_API_KEY not set")
            return []

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        user_prompt = f"今日係 {today}。請掃描市場，列出頭 {self.config.top_n_coins} 個最有潛力嘅幣種（市值 $1M-$1B）。用繁體中文寫 rationale。"

        headers = {"Authorization": f"Bearer {self.config.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": self._SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        try:
            client = await self._get_client()
            resp = await client.post(self.config.base_url, headers=headers, json=payload)
            if resp.status_code != 200:
                log.error(f"API error: {resp.status_code}")
                return []

            content = resp.json()["choices"][0]["message"]["content"]

            # ── Parse JSON ──
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if not json_match:
                return []
            data = json.loads(json_match.group())

            picks = []
            for item in data:
                picks.append(CoinPick(
                    symbol=str(item.get("symbol", "?")),
                    name=str(item.get("name", "Unknown")),
                    score=max(1, min(10, int(item.get("score", 5)))),
                    rationale=str(item.get("rationale", "")),
                    risk=str(item.get("risk", "medium")),
                    timeframe=str(item.get("timeframe", "1-4 weeks")),
                ))
            return sorted(picks, key=lambda x: x.score, reverse=True)

        except Exception as e:
            log.error(f"Scan failed: {e}")
            return []

    async def _send_report(self, picks: list[CoinPick]):
        if not self._webhook_url or not picks:
            return

        fields = []
        for i, p in enumerate(picks[:10]):
            icon = "🔥" if p.score >= 9 else "⭐" if p.score >= 8 else "📌" if p.score >= 7 else "💡"
            fields.append({
                "name": f"{icon} #{p.score} {p.symbol} — {p.name}",
                "value": f"**理由**: {p.rationale[:150]}\n**風險**: {p.risk} | **時間**: {p.timeframe}",
                "inline": False,
            })

        import requests
        embed = {
            "title": f"🧠 AI 幣種分析 — Top {len(picks)} 潛力幣",
            "color": 0x3498DB,
            "fields": fields,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "footer": {"text": "🤖 Powered by DeepSeek AI"},
        }
        requests.post(self._webhook_url, json={
            "username": "🧠 AI Coin Scanner", "embeds": [embed]
        }, timeout=10)

    async def run(self):
        log.info("🧠 AI Coin Scanner 啟動")
        scan_seconds = self.config.scan_interval_hours * 3600

        while not self._shutdown:
            try:
                log.info("🔍 掃描幣種...")
                picks = await self.scan()
                if picks:
                    log.info(f"📊 Top 3: {', '.join(p.symbol for p in picks[:3])}")
                    await self._send_report(picks)
                else:
                    log.warning("無結果")
            except Exception as e:
                log.error(f"Error: {e}")

            for _ in range(scan_seconds // 60):
                if self._shutdown: break
                await asyncio.sleep(60)

    async def close(self):
        self._shutdown = True
        if self._client:
            await self._client.aclose()


async def main():
    config = AICoinScannerConfig()
    scanner = AICoinScanner(config)
    try:
        await scanner.run()
    finally:
        await scanner.close()

if __name__ == "__main__":
    asyncio.run(main())