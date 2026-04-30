# Requirements.md

## 1. Project Name

Stock Telegram Alert

## 2. Goal

Build a small automation utility that checks Vietnam stock data daily and sends important signals to my Telegram.

## 3. Target User

Myself

## 4. Main Use Case

Every trading day after market close, the system should:
1. Read my stock watchlist.
2. Fetch daily price and volume data.
3. Calculate selected technical signals.
4. Generate a short alert message.
5. Send the message to Telegram.

## 5. Watchlist

The first version should support a fixed watchlist in the code or a config file.

Example:

- FPT
- MWG
- VND
- HPG
- MBS

## 6. Data Source

Use the `vnstock` Python library to get Vietnam stock market data.

## 7. Signals for Version 1

The system should calculate:

### 7.1 MA20 Bounce

Trigger when:
- Current price is above MA20
- Previous close was near or below MA20
- Volume is higher than recent average volume

### 7.2 MA20 Breakdown

Trigger when:
- Current price closes below MA20
- Volume is higher than recent average volume

### 7.3 MA20 / MA50 Breakout

Trigger when:
- Current price breaks above MA20 or MA50
- Volume increases compared with average volume

### 7.4 Drawdown from Recent High

Calculate:

(Current High - Current Price) / Current High

Show the drawdown percentage from the recent peak.

## 8. Telegram Message Format

The Telegram message should be short and easy to read.

Example:

📊 VN Stock Daily Alert

Date: 2026-04-29

FPT
- Signal: Break above MA20
- Price: 120,000
- Volume: Higher than average
- Note: Watch for continuation

PVT
- Signal: Drawdown 18% from recent high
- Note: In discount zone, monitor base formation

## 9. Schedule

The automation should run once per trading day after Vietnam market close.

Preferred time:
- Around 3:30 PM to 5:00 PM Vietnam time

## 10. Output

The system should send the result to Telegram.

Optional later:
- Save signal history to Google Sheet
- Send message through Make.com
- Use AI to summarize signals

## 11. Version 1 Scope

Version 1 includes:
- Python script
- Fixed watchlist
- vnstock data fetching
- Basic signal calculation
- Telegram message sending
- GitHub Actions daily schedule

## 12. Not in Version 1

Version 1 will not include:
- Real-time intraday alerts
- Buy/sell recommendation
- Portfolio position sizing
- Advanced AI analysis
- Full web dashboard
- Automatic trading

## 13. Important Notes

This tool is for personal learning and monitoring only. It does not provide financial advice.