# ImplementationPlan.md

## 1. Overview

This project will be built as a small Python automation utility that sends daily Vietnam stock signals to Telegram.

Version 1 will use a direct flow:

1. GitHub Actions runs the Python script on schedule.
2. Python script fetches stock data from `vnstock`.
3. Python calculates stock signals.
4. Python formats a Telegram message.
5. Python sends the message directly to Telegram.

Version 2 can add Make.com and Google Sheet:

1. Python calculates stock signals.
2. Python sends the result to Make.com Webhook.
3. Make.com formats and filters the message.
4. Make.com sends the message to Telegram.
5. Make.com saves the signal history to Google Sheet.

The reason for starting with Version 1 is to make the first automation simple and easier to test.

---

## 2. Tools

### Version 1

- Python
- vnstock
- Git
- GitHub
- GitHub Actions
- Telegram Bot
- GitHub Secrets
- `.env` file for local testing only

### Version 2 / Future

- Make.com
- Google Sheet
- Nvidia NIM / OpenRouter for AI summary

---

## 3. Project Folder Structure

```text
vn-stock-telegram-alert/
├── README.md
├── Requirements.md
├── ImplementationPlan.md
├── main.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── tests/
│   ├── test_signals.py
│   └── test_config.py
└── .github/
    └── workflows/
        └── daily-stock-alert.yml
```

---

## 4. Phases

### Phase 1: Project Setup & Configuration
- Create project structure and virtual environment
- Add `config.py` with watchlist grouped by sector and all signal thresholds
- Add `requirements.txt` (vnstock, python-dotenv, pandas, requests, pytest)
- Create `.env.example` and `.gitignore`
- Set up GitHub repository and GitHub Actions workflow skeleton

### Phase 2: Data Fetching & Core Calculations
- Implement `vnstock` data fetching for watchlist symbols
- Calculate MA20 and MA50 using rolling closing prices for each trading day. Only Vol20 should exclude the current trading day.
- Calculate Vol20 = average volume of previous 20 trading days (excluding current day)
- Calculate the recent 50-day high for drawdown context.
- Calculate the breakout high from the previous 20 trading days only, excluding the current day.
- Calculate 5-day average volume for Volume Dry-Up
- Handle missing data / holidays gracefully

### Phase 3: Signal Engine (Initial Version)
- Implement Trend/Price signals: MA20 Bounce, MA20 Breakout, MA50 Breakout, MA20 Breakdown
- Implement Volume signals: Volume Contraction (initial simpler version)
- Implement Base/Breakout signals: Sideways detection (5/10/20/30D), 20-Day Base Breakout
- Implement Context signals: 50D Drawdown, Daily Change, Distance from MA20
- Calculate watchlist breadth (stocks above MA20 / total processed)
- Format Telegram message with Watchlist Prices and Signal Alerts sections

### Phase 4: Signal Logic Refinement
**Objective:** Align signal logic with refined Requirements.md

#### 4.1 Volume Benchmark Correction
- Ensure Vol20 uses only the previous 20 completed trading days
- Current day's volume must not be included in its own benchmark
- Verify calculation with date-indexed dataframe slicing

#### 4.2 High-Volume Sell-Off Signal (New)
- Trigger: Daily close-to-close change ≤ -3% AND current volume ≥ 1.5 × Vol20
- Output: `🔴 High-Volume Sell-Off (X× Vol20)` with volume multiple
- Add threshold `HIGH_VOLUME_SELL_OFF_DROP = -0.03` and `HIGH_VOLUME_RATIO = 1.5` to config.py

#### 4.3 Volume Dry-Up (Replaces Volume Contraction)
- Trigger: Recent 5-day average volume ≤ 0.8 × Vol20 AND current volume ≤ 0.8 × Vol20
- Output: `🔇 Volume Dry-Up`
- Must NOT trigger when current volume is high, even if prior days had low volume
- Add threshold `VOLUME_DRY_UP_RATIO = 0.8` to config.py
- Remove old Volume Contraction logic

#### 4.4 MA20 Bounce - True Tolerance Logic
- Replace simple "low near MA20" check with true distance/tolerance
- Trigger: Low within ±1.5% of MA20 (i.e., `abs(low - MA20) / MA20 ≤ 0.015`), Close > MA20, Close > Previous Close, Volume ≥ 0.8 × Vol20
- Add threshold `MA20_TOUCH_TOLERANCE = 0.015` to config.py
- Output: `📈 MA20 Bounce`

#### 4.5 Separate MA20 Breakout and MA50 Breakout
- Both signals are independent and may trigger together
- MA20 Breakout: Previous close ≤ MA20, Current close > MA20, Volume ≥ 1.2 × Vol20
- MA50 Breakout: Previous close ≤ MA50, Current close > MA50, Volume ≥ 1.2 × Vol20
- Add threshold `MA_BREAKOUT_VOLUME_RATIO = 1.2` to config.py
- Outputs: `🚀 MA20 Breakout`, `🚀 MA50 Breakout`

#### 4.6 Stronger Volume Confirmation for Breakouts
- 20-Day Base Breakout: Volume ≥ 1.5 × Vol20 (was 1.2×)
- MA20/MA50 Breakout: Volume ≥ 1.2 × Vol20
- MA20 Breakdown: Volume ≥ 1.2 × Vol20
- MA20 Bounce: Volume ≥ 0.8 × Vol20
- High-Volume Sell-Off: Volume ≥ 1.5 × Vol20

#### 4.7 Longest Qualifying Sideways/Base Signal Only
- Check periods in priority order: 30D → 20D → 10D → 5D
- Show only the longest qualifying signal
- Thresholds: 5D ≤ 3%, 10D ≤ 6%, 20D ≤ 8%, 30D ≤ 10%
- Outputs: `↔️ Sideways Base (30D)`, `↔️ Sideways Base (20D)`, `↔️ Sideways Base (10D)`, `↔️ Sideways (5D)`

#### 4.8 Always Show Watchlist Breadth
- Display breadth every trading day regardless of value
- Format: `📊 Watchlist Breadth: XX% above MA20`
- No automatic market regime labels ("bullish", "bearish", etc.)

#### 4.9 Move Thresholds to config.py
- Centralize all signal thresholds in config.py
- Required variables:
  ```
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
- Import and use consistently in main.py and tests

#### 4.10 Regression Tests
- Create `tests/test_signals.py` with pytest
- Test each signal with synthetic data matching Requirements §17 cases:

**Case 1: High-Volume Sell-Off (SHB-type)**
```
Given: Daily Change = -6.7%, Current Volume = 1.8 × Vol20
Expected: ✅ High-Volume Sell-Off, ❌ Volume Dry-Up
```

**Case 2: Volume Dry-Up**
```
Given: Recent 5D Avg Volume = 0.65 × Vol20, Current Volume = 0.60 × Vol20
Expected: ✅ Volume Dry-Up, ❌ High-Volume Sell-Off
```

**Case 3: MA20 Bounce**
```
Given: Low within ±1.5% of MA20, Close > MA20, Close > Prev Close, Volume ≥ 0.8 × Vol20
Expected: ✅ MA20 Bounce
```

**Case 4: Sideways Priority**
```
Given: Qualifies for 5D, 10D, 20D, 30D
Expected: ✅ Sideways Base (30D) only
```

**Case 5: MA20 Breakdown**
```
Given: Previous Close >= Previous MA20, Current Close < Current MA20, Current Volume = 1.3 × Vol20
Expected: ✅ MA20 Breakdown
```

- Run tests with `pytest tests/` in CI and locally

### Phase 5: Telegram Integration & GitHub Actions
- Implement Telegram bot message sending with Markdown formatting
- Add error handling for network/API failures
- Configure GitHub Actions daily workflow (weekdays 3:30-5:00 PM Vietnam time)
- Store Telegram token and chat ID in GitHub Secrets
- Use latest available trading date from dataset (handles market holidays)

### Phase 6: Documentation & Polish
- Update README.md with setup, usage, and signal definitions
- Verify Requirements.md, ImplementationPlan.md, and code are consistent
- Add inline comments for complex signal logic
- Test end-to-end with GitHub Actions manual trigger

---

## 5. Testing Strategy

| Level | Tool | Scope |
|-------|------|-------|
| Unit | pytest | Signal logic with synthetic data (Phase 4.10) |
| Integration | Manual + GitHub Actions | Full flow with vnstock + Telegram |
| Config | pytest | Verify config.py values load correctly |

All core signal logic must be testable without external API calls.

---

## 6. Configuration Management

All user-adjustable parameters live in `config.py`:
- Watchlist (by sector)
- Moving average periods
- Signal thresholds (volume ratios, price tolerances, sideways/base ranges)
- Telegram formatting options

No hardcoded thresholds in `main.py` or signal modules.

---

## 7. Signal Conflict Rules (Implementation Checklist)

- [ ] High-Volume Sell-Off and Volume Dry-Up never trigger together
- [ ] Only longest sideways/base signal shown
- [ ] MA20 and MA50 breakouts can both trigger
- [ ] Context signals (drawdown, daily change, MA20 distance) always allowed with event signals
- [ ] Factual signal names only (no "panic selling", "selling climax")

---

## 8. Telegram Message Format

```
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

Every watchlist stock appears in Watchlist Prices section.