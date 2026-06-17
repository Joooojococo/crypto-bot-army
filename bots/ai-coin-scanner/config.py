"""
🧠 AI 幣種分析 Bot — 配置
用 DeepSeek AI 分析幣種潛力 → 輸出 Top 10 Report → Discord 通知
"""
import os
from dataclasses import dataclass, field


@dataclass
class AICoinScannerConfig:
    """
    AI 幣種掃描器設定
    """

    # ── DeepSeek API ──
    api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    base_url: str = "https://api.deepseek.com/v1/chat/completions"
    model: str = "deepseek-chat"
    temperature: float = 0.3
    max_tokens: int = 6000

    # ── 掃描頻率 ──
    scan_interval_hours: int = int(os.getenv("COIN_SCAN_INTERVAL_HOURS", "24"))

    # ── AI 分析參數 ──
    top_n_coins: int = 10  # 輸出頭幾名
    min_market_cap: int = 1_000_000  # 最少市值過濾（1M）
    max_market_cap: int = 1_000_000_000  # 最大市值（1B，專注中小幣）

    # ── 風險偏好 ──
    risk_levels: list[str] = field(default_factory=lambda: ["low", "medium", "high"])