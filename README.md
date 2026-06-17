# 🪖 Crypto Bot Army

> Web3 全自動化 Bot 軍團 — 一個 repo，5 個賺錢機器人

## 📦 Projects

| # | Bot | 目的 | 風險 | 預期收益 |
|---|-----|------|------|----------|
| 1 | 💱 **DEX 做市 Bot** | Uniswap V3 / PancakeSwap 自動提供流動性賺交易費 | 中 | APR 15-50% |
| 2 | 📡 **Whale Alert Bot** | 監察大戶 on-chain 動作 → Discord 通知 | 低 | 跟買跟賣 |
| 3 | 🧠 **AI 幣種分析 Bot** | DeepSeek AI 每日掃描幣種潛力，出 report | 低 | 資訊優勢 |
| 4 | 🎮 **GameFi 掛機 Bot** | 自動玩 Web3 game 賺 token | 低-中 | Token rewards |
| 5 | ✍️ **自動交互 Bot** | 自動同大量新協議互動，批量刷潛在 airdrop | 低 | Airdrop 回報 |

## 🏗️ Project Structure

```
crypto-bot-army/
├── README.md                         # 呢個 file
├── shared/                           # 共享模組（config / reporter / utils）
│   ├── config.py                     # 通用 dataclass config pattern
│   └── reporter.py                   # Discord Webhook 通知模組
├── bots/
│   ├── dex-market-maker/             # 💱 DEX 做市 Bot
│   │   ├── README.md
│   │   ├── config.py
│   │   ├── market_maker.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── whale-alert/                  # 📡 Whale Alert Bot
│   │   ├── README.md
│   │   ├── config.py
│   │   ├── whale_tracker.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── ai-coin-scanner/              # 🧠 AI 幣種分析 Bot
│   │   ├── README.md
│   │   ├── config.py
│   │   ├── ai_scanner.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── gamefi-grinder/               # 🎮 GameFi 掛機 Bot
│   │   ├── README.md
│   │   ├── config.py
│   │   ├── gamefi_bot.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── auto-interactor/              # ✍️ 自動交互 Bot
│       ├── README.md
│       ├── config.py
│       ├── interactor.py
│       ├── requirements.txt
│       └── Dockerfile
└── docker-compose.yml                # 一鍵啟動所有 Bot
```

## 🚀 快速開始

```bash
git clone https://github.com/Joooojococo/crypto-bot-army.git
cd crypto-bot-army

# 設定環境變數
cp .env.example .env
vim .env  # 填 DeepSeek API Key + Discord Webhook

# 全部啟動
docker-compose up -d

# 或只啟動某個 bot
docker-compose up -d whale-alert
```

## 🔧 共通設定（.env）

```bash
DEEPSEEK_API_KEY=sk-xxx
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx
WALLET_PRIVATE_KEY=0x_xxx  # 需要做市/交互時用
```

## 📋 開發路線圖

- [x] Repo scaffold
- [ ] DEX 做市 Bot v1
- [ ] Whale Alert Bot v1
- [ ] AI 幣種分析 Bot v1
- [ ] GameFi 掛機 Bot v1
- [ ] 自動交互 Bot v1