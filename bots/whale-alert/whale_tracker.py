"""
📡 Whale Alert Bot — 核心追蹤器
用 Etherscan/Arbiscan API 監察指定 whale address，偵測大額 transfer → Discord 通知
"""
from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone

import httpx

from config import WhaleAlertConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] whale-alert: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("whale-alert")

# ── Block Explorer API URLs ──
CHAIN_API_URLS = {
    "ethereum": "https://api.etherscan.io/api",
    "arbitrum": "https://api.arbiscan.io/api",
    "polygon": "https://api.polygonscan.com/api",
    "optimism": "https://api-optimistic.etherscan.io/api",
    "base": "https://api.basescan.org/api",
    "bsc": "https://api.bscscan.com/api",
}

# ── 已知 USDC 合約地址（by chain） ──
USDC_ADDRESSES = {
    "ethereum": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "arbitrum": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
}


class WhaleTracker:
    """Whale 交易追蹤器"""

    def __init__(self, config: WhaleAlertConfig):
        self.config = config
        self._client: httpx.AsyncClient | None = None
        self._last_tx_hashes: dict[str, set[str]] = {}  # address -> known tx hashes
        self._webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
        self._shutdown = False

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=15.0)
        return self._client

    # ═══════════════════════════════════════════════════════════
    #  API 查詢
    # ═══════════════════════════════════════════════════════════

    async def _fetch_tx_list(
        self, chain: str, address: str, count: int = 50
    ) -> list[dict]:
        """從 block explorer API 獲取指定 address 嘅最近交易"""
        api_url = CHAIN_API_URLS.get(chain)
        if not api_url:
            log.warning(f"Unsupported chain: {chain}")
            return []

        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "sort": "desc",
            "page": 1,
            "offset": count,
        }
        if self.config.etherscan_api_key:
            params["apikey"] = self.config.etherscan_api_key

        try:
            client = await self._get_client()
            resp = await client.get(api_url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "1":
                    return data.get("result", [])
            log.debug(f"API error {chain}: {resp.status_code}")
        except Exception as e:
            log.warning(f"Fetch tx failed {chain}/{address}: {e}")

        return []

    # ═══════════════════════════════════════════════════════════
    #  分析 + 通知
    # ═══════════════════════════════════════════════════════════

    def _is_large_transfer(self, tx: dict) -> tuple[bool, str, float]:
        """
        判斷交易係咪大額
        Returns: (is_large, type_str, amount_usd)
        """
        value_wei = int(tx.get("value", 0))
        value_eth = value_wei / 1e18
        value_usd = value_eth * self.config.eth_price_usd

        if value_usd >= self.config.eth_transfer_threshold_usd:
            return True, f"ETH Transfer", value_usd

        # TODO: 檢查 USDC transfer（需 call token tx API）
        return False, "", 0.0

    async def _send_discord_alert(
        self, chain: str, whale: str, tx: dict, amount_usd: float
    ):
        """發送 Discord Webhook 通知"""
        if not self._webhook_url:
            return

        chain_explorer_map = {
            "ethereum": "etherscan.io",
            "arbitrum": "arbiscan.io",
        }
        explorer = chain_explorer_map.get(chain, f"{chain}.etherscan.io")

        tx_hash = tx.get("hash", "")
        from_addr = tx.get("from", "")
        to_addr = tx.get("to", "")
        value_eth = int(tx.get("value", 0)) / 1e18
        block = tx.get("blockNumber", "?")

        embed = {
            "title": f"🐋 Whale Alert — {chain.upper()}",
            "description": f"大額轉賬偵測! **${amount_usd:,.0f}** ({value_eth:.2f} ETH)",
            "color": 0xE67E22,
            "fields": [
                {"name": "From", "value": f"`{from_addr[:10]}...{from_addr[-6:]}`", "inline": True},
                {"name": "To", "value": f"`{to_addr[:10]}...{to_addr[-6:]}`", "inline": True},
                {"name": "Tx Hash", "value": f"[{tx_hash[:16]}...](https://{explorer}/tx/{tx_hash})", "inline": False},
                {"name": "Block", "value": str(block), "inline": True},
                {"name": "Whale", "value": f"`{whale[:10]}...{whale[-6:]}`", "inline": True},
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        payload = {"username": "🐋 Whale Alert Bot", "embeds": [embed]}
        try:
            import requests
            requests.post(self._webhook_url, json=payload, timeout=10)
            log.info(f"📡 Discord alert sent: ${amount_usd:,.0f} from {from_addr[:10]}...")
        except Exception as e:
            log.error(f"Discord send failed: {e}")

    # ═══════════════════════════════════════════════════════════
    #  主掃描循環
    # ═══════════════════════════════════════════════════════════

    async def scan(self) -> None:
        """一次完整掃描"""
        for whale in self.config.whale_addresses:
            if self._shutdown:
                break

            whale_key = whale.lower()
            if whale_key not in self._last_tx_hashes:
                self._last_tx_hashes[whale_key] = set()

            for chain in self.config.chains:
                txs = await self._fetch_tx_list(chain, whale)
                if not txs:
                    continue

                known = self._last_tx_hashes[whale_key]
                for tx in txs:
                    tx_hash = tx.get("hash", "")
                    if tx_hash in known:
                        continue  # 已通知過

                    # 第一次 scan 只記錄，唔通知（避免洗版）
                    if known:
                        is_large, tx_type, amount_usd = self._is_large_transfer(tx)
                        if is_large:
                            await self._send_discord_alert(
                                chain, whale, tx, amount_usd
                            )
                    known.add(tx_hash)

    async def run(self):
        """主循環"""
        log.info(f"🐋 Whale Alert Bot 啟動 — 監察 {len(self.config.whale_addresses)} 個地址")

        if not self.config.whale_addresses:
            log.warning("⚠️ 未設定 WHALE_ADDRESSES，Bot 只會空轉")
            return

        # ── First scan: baseline（唔發通知） ──
        log.info("📸 Baseline scan...")
        await self.scan()

        while not self._shutdown:
            try:
                await self.scan()
            except Exception as e:
                log.error(f"Scan error: {e}")
            await asyncio.sleep(self.config.scan_interval_seconds)

    async def close(self):
        self._shutdown = True
        if self._client:
            await self._client.aclose()


# ═══════════════════════════════════════════════════════════════
#  Entry Point
# ═══════════════════════════════════════════════════════════════

async def main():
    config = WhaleAlertConfig()

    tracker = WhaleTracker(config)
    loop = asyncio.get_event_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: setattr(tracker, "_shutdown", True))
        except NotImplementedError:
            pass

    try:
        await tracker.run()
    finally:
        await tracker.close()


if __name__ == "__main__":
    asyncio.run(main())