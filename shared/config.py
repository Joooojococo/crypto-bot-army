"""
Crypto Bot Army — 共享配置模組
所有 Bot 通用嘅 dataclass config pattern
參考 ITA-Refine / Airdrop Farmer 嘅 config 設計
"""
import os
from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    """DeepSeek AI LLM 設定"""
    provider: str = "deepseek"
    api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    base_url: str = "https://api.deepseek.com/v1/chat/completions"
    model: str = "deepseek-chat"
    temperature: float = 0.3
    max_tokens: int = 4000
    max_retries: int = 3


@dataclass
class DiscordConfig:
    """Discord Webhook 通知設定"""
    webhook_url: str = field(default_factory=lambda: os.getenv("DISCORD_WEBHOOK_URL", ""))
    username: str = "🪖 Crypto Bot Army"
    notify_on_scan: bool = True
    notify_on_alert: bool = True


@dataclass
class WalletConfig:
    """EVM Wallet 設定"""
    private_key: str = field(default_factory=lambda: os.getenv("WALLET_PRIVATE_KEY", ""))
    rpc_url_eth: str = field(default_factory=lambda: os.getenv("RPC_ETHEREUM", "https://1rpc.io/eth"))
    rpc_url_arb: str = field(default_factory=lambda: os.getenv("RPC_ARBITRUM", "https://arb1.arbitrum.io/rpc"))


@dataclass
class BaseBotConfig:
    """每個 Bot 嘅基礎 config（各自 extend）"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    discord: DiscordConfig = field(default_factory=DiscordConfig)
    wallet: WalletConfig = field(default_factory=WalletConfig)
    scan_interval_hours: int = 6