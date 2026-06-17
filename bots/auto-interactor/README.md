# ✍️ 自動交互 Bot

自動同大量新協議互動 → 批量刷潛在 airdrop（盲目撒網策略）

## 策略
- 自動 scan 新 deploy 嘅合約
- 自動 mint NFT / swap / bridge / stake
- 每日同 10-50 個協議互動
- 反女巫 random delay + random amount
- 唔靠 AI，純自動批量操作

## 成本分析

| | Airdrop Farmer | 自動交互 Bot |
|------|------|------|
| 每 tx 成本 | $0.01-0.05 | $0.10-0.50 |
| 每日 tx 量 | 5-10 次 | 10-50 次 |
| 每日成本 | ~$0.50 | ~$5-25 |
| 每月成本 | ~$5-20 | ~$150-750 |
| 需要本金 | 只係 gas | gas + token（swap 要有錢 swap） |

## ⚠️ 風險
- 會同大量未知合約互動 → scam contract 風險
- 無常損失風險（swap / LP）
- 需要較多本金

## 開發狀態
🚧 已評估 — 成本過高，等 Airdrop Farmer 收到第一筆回報後再啟動