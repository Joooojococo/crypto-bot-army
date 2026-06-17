"""
📡 Whale Alert Bot — 配置
監察區塊鏈大戶動作，Discord 即時通知
"""
import os
from dataclasses import dataclass, field


@dataclass
class WhaleAlertConfig:
    """
    Whale Alert 設定
    監察指定 whale address 嘅 on-chain 活動
    """

    # ── 要監察嘅 whale address 列表 ──
    # 可以經 env var WHALE_ADDRESSES 用逗號分隔（例如: 0xabc...,0xdef...）
    whale_addresses: list[str] = field(default_factory=lambda: [
        addr.strip()
        for addr in os.getenv("WHALE_ADDRESSES", "").split(",")
        if addr.strip()
    ])

    # ── 大額 transfer 門檻（USD） ──
    eth_transfer_threshold_usd: float = float(os.getenv("WHALE_ETH_THRESHOLD", "50000"))
    usdc_transfer_threshold: float = float(os.getenv("WHALE_USDC_THRESHOLD", "100000"))

    # ── 掃描間隔（秒） ──
    scan_interval_seconds: int = int(os.getenv("WHALE_SCAN_INTERVAL", "60"))

    # ── Etherscan API keys（免費 tier 夠用） ──
    etherscan_api_key: str = os.getenv("ETHERSCAN_API_KEY", "")

    # ── 要監察嘅鏈 ──
    chains: list[str] = field(default_factory=lambda: [
        c.strip() for c in os.getenv("WHALE_CHAINS", "ethereum,arbitrum").split(",") if c.strip()
    ])

    # ── ETH 價格（USD） ──
    eth_price_usd: float = float(os.getenv("ETH_PRICE_USD", "1800"))