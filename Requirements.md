# Requirements.md

## 1. Project Name

Stock Telegram Alert

## 2. Goal

Build a small automation utility that checks Vietnam stock data after each trading day and sends concise, useful technical signals to Telegram.

The project is mainly for personal learning, market monitoring, and automation practice.

The system should prioritize:
- Clear signal definitions
- Consistent logic
- Low-noise Telegram alerts
- Easy-to-maintain thresholds
- No contradictory signals for the same stock on the same day

## 3. Target User

Myself

## 4. Main Use Case

Every trading day after market close, the system should:

1. Read the configured stock watchlist.
2. Fetch daily price and volume data.
3. Calculate moving averages and volume benchmarks.
4. Detect selected technical signals.
5. Calculate watchlist breadth.
6. Generate a short Telegram message.
7. Send the message automatically through Telegram.

## 5. Watchlist

The watchlist should be maintained in `config.py` and grouped by sector.

Current watchlist:

### Securities
- HCM
- VND
- MBS
- VIX

### Banks
- MBB
- ACB
- SHB
- BVB
- TPB

### Real Estate
- DXG
- DIG

### Steel
- HPG
- NKG

### Consumer / Retail
- VNM
- MWG

### Technology
- FPT

The watchlist should be easy to update without changing the main signal logic.

## 6. Data Source

Use the `vnstock` Python library to get Vietnam stock market data.

Required daily fields:

- Trading date
- Open
- High
- Low
- Close
- Volume

The system should fetch enough historical data to calculate:

- MA20
- MA50
- Previous 20-day average volume
- 50-day recent high
- 20-day breakout range
- Sideways / base ranges

## 7. Signal Calculation Principles

### 7.1 Volume Benchmark

Volume-based signals should compare the current trading day with the average volume of the **previous 20 trading days**.

The current trading day's volume should not be included in its own benchmark.

Definition:

```text
Previous 20D Average Volume
= average volume of the 20 completed trading days before today
```

This benchmark is referred to as `Vol20` in the requirements below.

### 7.2 Signal Categories

Signals should be grouped conceptually into:

```text
Trend / Price Signals
Volume / Pressure Signals
Base / Breakout Signals
Context Signals
```

A stock may have more than one compatible signal, but contradictory signals should not be shown together.

Example:

```text
High-volume sell-off
and
Volume dry-up
```

should never be reported together for the same trading day.

## 8. Trend / Price Signals

### 8.1 MA20 Bounce

Purpose:

Detect a stock that tests MA20 and closes back above it with positive price action.

Trigger when:

- The day's low is within approximately ±1.5% of MA20.
- The closing price is above MA20.
- The closing price is higher than the previous close.
- Current volume is at least 0.8 × Vol20.

Suggested output:

```text
📈 MA20 Bounce
```

### 8.2 MA20 Breakout

Trigger when:

- Previous close was at or below MA20.
- Current close is above MA20.
- Current volume is at least 1.2 × Vol20.

Suggested output:

```text
🚀 MA20 Breakout
```

### 8.3 MA50 Breakout

Trigger when:

- Previous close was at or below MA50.
- Current close is above MA50.
- Current volume is at least 1.2 × Vol20.

Suggested output:

```text
🚀 MA50 Breakout
```

### 8.4 MA20 Breakdown

Trigger when:

- Previous close was at or above MA20.
- Current close is below MA20.
- Current volume is at least 1.2 × Vol20.

Suggested output:

```text
⚠️ MA20 Breakdown
```

## 9. Volume / Pressure Signals

### 9.1 High-Volume Sell-Off

Purpose:

Detect unusually strong selling pressure.

Trigger when:

- Daily close-to-close change is less than or equal to -3%.
- Current volume is at least 1.5 × Vol20.

Suggested output:

```text
🔴 High-Volume Sell-Off
```

The message may also display the volume multiple, for example:

```text
🔴 High-Volume Sell-Off (1.8× Vol20)
```

Do not label this automatically as "panic selling" or "selling climax" because those terms require additional interpretation.

### 9.2 Volume Dry-Up

Purpose:

Detect a genuine contraction in trading activity.

Trigger when:

- Recent 5-day average volume is less than or equal to 0.8 × Vol20.
- Current day's volume is also less than or equal to 0.8 × Vol20.

Suggested output:

```text
🔇 Volume Dry-Up
```

This replaces the older Volume Contraction rule that only checked whether the 5-day average was lower than the 20-day average.

The signal must not trigger when current volume is high, even if the previous few days had low volume.

## 10. Base / Breakout Signals

### 10.1 Sideways / Base Detection

Use the existing range thresholds:

- 5 days: within 3%
- 10 days: within 6%
- 20 days: within 8%
- 30 days: within 10%

If a stock qualifies for more than one sideways period, show only the **longest qualifying base**.

Priority:

```text
30D
→ else 20D
→ else 10D
→ else 5D
```

Suggested outputs:

```text
↔️ Sideways Base (30D)
↔️ Sideways Base (20D)
↔️ Sideways Base (10D)
↔️ Sideways (5D)
```

### 10.2 20-Day Base Breakout

Trigger when:

- Current close is above the highest high of the previous 20 trading days.
- Current close is above MA20.
- Current volume is at least 1.5 × Vol20.

Suggested output:

```text
🚀 20-Day Base Breakout
```

The current day must not be included when calculating the previous 20-day high.

## 11. Context Signals

### 11.1 50-Day Drawdown

Calculate the percentage decline from the recent 50-trading-day high.

Formula:

```text
(Recent 50D High - Current Close) / Recent 50D High
```

Show the context when drawdown is greater than 10%.

Suggested output:

```text
📉 50D Drawdown: 18.5%
```

This is a context / status indicator, not a buy or sell recommendation.

### 11.2 Daily Change

Display the close-to-close daily percentage change.

Example:

```text
Day: -6.7%
```

### 11.3 Distance from MA20

Display how far the current close is above or below MA20.

Formula:

```text
(Current Close - MA20) / MA20
```

Example:

```text
MA20: -10.8%
```

## 12. Watchlist Breadth

Calculate:

```text
Number of watchlist stocks above MA20
/
Number of stocks successfully processed
```

The Telegram message should show watchlist breadth every trading day, not only when breadth is above 50%.

Example:

```text
📊 Watchlist Breadth: 24% above MA20
```

The system should report the number without automatically labeling the market as "good", "bad", "bullish", or "bearish".

## 13. Signal Conflict Rules

The signal engine should avoid contradictory outputs.

Required rules:

1. `High-Volume Sell-Off` and `Volume Dry-Up` must not trigger together.
2. A stock should show only the longest qualifying sideways/base signal.
3. MA20 and MA50 breakout signals may both trigger if both conditions are genuinely met.
4. Context signals such as drawdown may appear together with event signals.
5. The system should prefer factual signal names over interpretive labels.

Example:

```text
SHB
Price: 11.8
Day: -6.7%
MA20: -10.8%

✅ 🔴 High-Volume Sell-Off
✅ 📉 50D Drawdown: 16.6%
❌ 🔇 Volume Dry-Up
```

## 14. Telegram Message Format

The Telegram message should be short and easy to scan.

Recommended structure:

```text
📊 VN Stock Daily Alert
Trading Date: YYYY-MM-DD
Run Date: YYYY-MM-DD

📊 Watchlist Breadth: XX% above MA20

📈 Watchlist Prices
• Securities: ...
• Banks: ...
• Real Estate: ...
• Steel: ...
• Consumer/Retail: ...
• Technology: ...

🔔 Signal Alerts

SHB
• Price: 11.8 | Day: -6.7% | MA20: -10.8%
• 🔴 High-Volume Sell-Off (1.8× Vol20)
• 📉 50D Drawdown: 16.6%
```

Every watchlist stock should still appear in the Watchlist Prices section even when no signal is triggered.

## 15. Schedule

The automation should run once per trading day after Vietnam market close.

Preferred time:

- Around 3:30 PM to 5:00 PM Vietnam time
- Monday to Friday

GitHub Actions may run on weekdays even when the Vietnam market is closed, so the script should use the latest available trading date from the dataset.

## 16. Configuration

Signal thresholds should be stored in `config.py` where practical so they can be adjusted without rewriting signal logic.

Recommended configurable values:

```text
MA_SHORT = 20
MA_LONG = 50

MA20_TOUCH_TOLERANCE = 0.015

MA_BREAKOUT_VOLUME_RATIO = 1.2
HIGH_VOLUME_RATIO = 1.5
VOLUME_DRY_UP_RATIO = 0.8
HIGH_VOLUME_SELL_OFF_DROP = -0.03

SIDEWAY_THRESHOLD = 0.03
SIDEWAY_DAYS = 5
BASE_THRESHOLD_10 = 0.06
BASE_THRESHOLD_20 = 0.08
BASE_THRESHOLD_30 = 0.10
```

Variable names should remain consistent across `config.py`, `main.py`, tests, documentation, and future versions.

## 17. Testing Requirements

Core signal logic should be testable separately from external APIs when practical.

Minimum regression cases:

### Case 1: High-Volume Sell-Off

Given:

```text
Daily Change = -6.7%
Current Volume = 1.8 × Vol20
```

Expected:

```text
✅ High-Volume Sell-Off
❌ Volume Dry-Up
```

### Case 2: Volume Dry-Up

Given:

```text
Recent 5D Avg Volume = 0.65 × Vol20
Current Volume = 0.60 × Vol20
```

Expected:

```text
✅ Volume Dry-Up
❌ High-Volume Sell-Off
```

### Case 3: MA20 Bounce

Given:

```text
Low is within ±1.5% of MA20
Close > MA20
Close > Previous Close
Volume >= 0.8 × Vol20
```

Expected:

```text
✅ MA20 Bounce
```

### Case 4: Sideways Priority

If a stock qualifies for 5D, 10D, 20D, and 30D sideways rules:

Expected:

```text
✅ Sideways Base (30D)
```

and the shorter sideways signals should not also be shown.

## 18. Output

The system should send the result to Telegram.

Optional later:

- Save signal history to Google Sheet
- Send messages through Make.com
- Add AI-generated summaries
- Add chart images
- Add sector-level breadth or rotation analysis

## 19. Current Scope

The current project includes:

- Python script
- Fixed sector-based watchlist
- `vnstock` data fetching
- MA20 / MA50 calculations
- Volume benchmark calculations
- Technical signal detection
- Watchlist breadth
- Telegram message sending
- GitHub Actions daily schedule
- GitHub Secrets for token security

## 20. Out of Scope

The current version will not include:

- Real-time intraday alerts
- Automatic buy / sell recommendations
- Portfolio position sizing
- Price targets
- Automatic trading
- Full web dashboard
- Advanced predictive AI models

## 21. Important Notes

This tool is for personal learning and market monitoring only.

Signals should describe observable price and volume conditions. They should not be presented as guaranteed trading outcomes or financial advice.
