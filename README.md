# Stock Telegram Alert

A small Python automation utility that fetches Vietnam stock market data, calculates technical signals, and sends a daily watchlist summary to Telegram.

## Goal

This project is mainly for personal learning and automation practice.

Through this project, I want to learn how to:

1. Use AI coding tools to help improve a small utility.
2. Use Git and GitHub to manage project files and version history.
3. Use GitHub Actions to run Python automation on a schedule.
4. Use Python to fetch and process Vietnam stock market data.
5. Use environment variables and GitHub Secrets to keep tokens safe.
6. Send automated Telegram messages.
7. Write repeatable tests for stock signal logic.
8. Gradually improve the project with logging, retries, history tracking, and AI summaries.

The stock alert use case is a practical example for learning an end-to-end automation workflow.

---

## Current Project Flow

```text
GitHub Actions / Local Run
        ↓
Python
        ↓
vnstock / VCI market data
        ↓
Signal calculation
        ↓
Watchlist summary
        ↓
Telegram Bot API
        ↓
Telegram
```

The signal engine is separated from the external data-fetching layer so it can be tested with synthetic pandas DataFrames without calling `vnstock`.

---

## Current Watchlist

The watchlist is maintained in `config.py` and grouped by sector.

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

---

## Signal Logic

### Volume Benchmark

Volume-based signals use:

```text
Vol20 = average volume of the previous 20 completed trading days
```

The current trading day's volume is excluded from its own Vol20 benchmark.

MA20 and MA50 remain normal rolling price averages that include the current day's close.

### Trend / Price Signals

#### MA20 Bounce

Triggers when:

- The day's low is within ±1.5% of MA20.
- Current close is above MA20.
- Current close is above the previous close.
- Current volume is at least `0.8 × Vol20`.

Output:

```text
📈 MA20 Bounce
```

#### MA20 Breakout

Triggers when:

- Previous close was at or below previous MA20.
- Current close is above current MA20.
- Current volume is at least `1.2 × Vol20`.

Output:

```text
🚀 MA20 Breakout
```

#### MA50 Breakout

Triggers when:

- Previous close was at or below previous MA50.
- Current close is above current MA50.
- Current volume is at least `1.2 × Vol20`.

Output:

```text
🚀 MA50 Breakout
```

MA20 and MA50 Breakout may both trigger on the same day.

#### MA20 Breakdown

Triggers when:

- Previous close was at or above previous MA20.
- Current close is below current MA20.
- Current volume is at least `1.2 × Vol20`.

Output:

```text
⚠️ MA20 Breakdown
```

### Volume / Pressure Signals

#### High-Volume Sell-Off

Triggers when:

- Daily close-to-close change is `<= -3%`.
- Current volume is at least `1.5 × Vol20`.

Output example:

```text
🔴 High-Volume Sell-Off (1.8× Vol20)
```

The project intentionally uses the factual label **High-Volume Sell-Off** instead of interpretive terms such as "panic selling" or "selling climax".

#### Volume Dry-Up

This replaces the older Volume Contraction rule.

Triggers when:

- Recent 5-day average volume is `<= 0.8 × Vol20`.
- Current volume is also `<= 0.8 × Vol20`.

Output:

```text
🔇 Volume Dry-Up
```

A High-Volume Sell-Off and Volume Dry-Up must not be reported together.

### Base / Breakout Signals

#### Sideways / Base Detection

Current thresholds:

- 5 trading days: range `<= 3%`
- 10 trading days: range `<= 6%`
- 20 trading days: range `<= 8%`
- 30 trading days: range `<= 10%`

If more than one period qualifies, only the longest qualifying base is shown.

Priority:

```text
30D → 20D → 10D → 5D
```

Possible outputs:

```text
↔️ Sideways Base (30D)
↔️ Sideways Base (20D)
↔️ Sideways Base (10D)
↔️ Sideways (5 days)
```

#### 20-Day Base Breakout

Triggers when:

- Current close is above the highest high of the previous 20 trading days.
- The current day is excluded from the previous 20-day breakout range.
- Current close is above MA20.
- Current volume is at least `1.5 × Vol20`.

Output:

```text
🚀 20-Day Base Breakout
```

### Context Signals

#### 50-Day Drawdown

Shows the decline from the recent 50-trading-day high when drawdown is greater than 10%.

Output example:

```text
📉 50D Drawdown: 16.6%
```

This is contextual information, not a buy/sell recommendation.

The daily Telegram summary also displays:

- Daily close-to-close change %
- Distance from MA20 %
- Watchlist breadth

---

## Watchlist Breadth

Watchlist breadth is calculated as:

```text
Stocks above MA20
÷
Stocks successfully processed
```

It is always shown in the Telegram message.

Example:

```text
📊 Watchlist Breadth: 24% above MA20
```

The bot does not automatically label breadth as bullish, bearish, good, or bad.

---

## Telegram Message Format

Example:

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

Every watchlist stock appears in the Watchlist Prices section even when no technical signal is triggered.

---

## Project Structure

```text
stock-telegram-alert/
├── .github/
│   └── workflows/
│       └── daily-stock-alert.yml
├── tests/
│   └── test_signals.py
├── .env
├── .env.example
├── .gitignore
├── config.py
├── ImplementationPlan.md
├── main.py
├── README.md
├── Requirements.md
└── requirements.txt
```

`.env` and `.venv/` must not be committed to GitHub.

---

## Tools Used

- Python
- pandas
- vnstock
- requests
- python-dotenv
- pytest
- Git
- GitHub
- GitHub Desktop
- GitHub Actions
- Telegram Bot
- GitHub Secrets
- VS Code / AI coding assistant

---

## Local Development

### 1. Use Python 3.11

The current local development environment uses Python 3.11.

Check:

```bash
python3.11 --version
```

### 2. Create a Virtual Environment

From the project folder:

```bash
python3.11 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

When active, the terminal prompt should begin with:

```text
(.venv)
```

To leave the environment:

```bash
deactivate
```

### 3. Install Dependencies

With `.venv` active:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Environment Variables

Create a local `.env` file containing:

```text
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Never commit `.env` to GitHub.

### 5. Run Unit Tests

```bash
python -m pytest tests/
```

Current regression suite includes five core signal cases:

1. SHB-type High-Volume Sell-Off
2. Volume Dry-Up
3. MA20 Bounce
4. Longest Sideways/Base priority
5. MA20 Breakdown

Expected result:

```text
5 passed
```

These tests use synthetic pandas DataFrames and do not call `vnstock`.

### 6. Run the Bot Locally

```bash
python main.py
```

The script will:

1. Fetch market data for every symbol in the watchlist.
2. Calculate signals.
3. Calculate watchlist breadth.
4. Format the Telegram message.
5. Send the result to Telegram.

---

## Signal Engine Design

The project separates data fetching from signal calculation.

```text
calculate_signals(symbol)
        ↓
fetch data from vnstock
        ↓
analyze_stock_data(symbol, df)
        ↓
calculate technical signals
```

`analyze_stock_data()` can accept a synthetic DataFrame directly, which makes regression testing possible without external API calls.

---

## External API Reliability

Market data is fetched from an external provider through `vnstock`.

External API requests may occasionally time out or fail temporarily. For example, a VCI/Vietcap request may hit a read timeout even when the rest of the script continues running.

A future reliability improvement is to add:

- Per-symbol error logging
- Retry with a small backoff
- Clear reporting of symbols that failed to fetch

This is separate from the core signal logic.

---

## GitHub Actions

The bot is intended to run automatically on trading weekdays after the Vietnam market closes.

GitHub Actions stores sensitive Telegram credentials in GitHub Secrets rather than in committed source files.

The script uses the latest available trading date from the dataset so weekend or holiday runs do not rely only on the calendar date.

---

## Pre-Commit Checklist

Before committing changes:

1. Confirm `.env` is ignored and not staged.
2. Confirm `.venv/` is ignored and not staged.
3. Run:

   ```bash
   python -m pytest tests/
   ```

4. Review the Git diff.
5. Confirm only intended files are included.
6. Commit using a descriptive message.
7. Push to GitHub.

---

## Current Scope

The project currently includes:

- Sector-based watchlist
- Vietnam stock data fetching
- MA20 and MA50 calculations
- Previous-20-day volume benchmark
- Technical signal detection
- Watchlist breadth
- Telegram message sending
- GitHub Actions scheduling
- Unit/regression tests
- GitHub Secrets
- Local virtual environment workflow

---

## Future Improvements

Possible later improvements:

- Retry logic for temporary market data API failures
- Better per-symbol fetch/error logging
- Save signal history to Google Sheets
- Make.com integration
- AI-generated market summary
- Sector-level breadth / rotation analysis
- Chart images
- More regression tests
- Refactor signal logic into a separate module if the project grows

---

## Important Notes

This tool is for personal learning and market monitoring only.

Signals describe observable price and volume conditions. They are not guaranteed trading outcomes, automatic buy/sell recommendations, or financial advice.
