# Stock Telegram Alert

This project is a small Python automation utility that sends daily Vietnam stock signals to Telegram.

## Goal

The goal of this project is for personal learning and practice in automation.

Through this project, I want to learn how to:

1. Use Gemini CLI to help create and improve a small utility.
2. Use Git and GitHub to manage project files and version history.
3. Use GitHub Actions to run a Python script automatically on a schedule.
4. Use Python to fetch and process Vietnam stock market data.
5. Use environment variables and GitHub Secrets to keep tokens safe.
6. Send automated messages to Telegram.
7. Gradually improve the project by adding Make.com, Google Sheet, and AI summary in future versions.

The stock alert use case is used as a practical example to learn how automation works from end to end.

## Version 1 Scope

Version 1 will use a direct flow:

1. GitHub Actions runs the Python script on schedule.
2. Python fetches stock data from `vnstock`.
3. Python calculates basic stock signals.
4. Python formats a Telegram message.
5. Python sends the message directly to Telegram.

Version 1 includes:

- Fixed stock watchlist
- Basic stock data fetching
- Basic signal calculation
- Direct Telegram message sending
- GitHub Actions schedule
- GitHub Secrets for token security

Version 1 does not include:

- Make.com
- Google Sheet signal journal
- AI-generated summary


## Tools Used

- Gemini CLI
- vnstock
- Github Destop
- GitHub
- GitHub Actions
- Telegram Bot
- GitHub Secrets
- `.env` file for local testing only

## Project Flow

```text
GitHub Actions
↓
Python script
↓
vnstock data
↓
Signal calculation
↓
Telegram message
↓
Telegram app


## Version 2 Improvements

The stock daily alert system has been upgraded with the following improvements:

1. **Daily Watchlist Prices**: The daily alert message now reports the closing price of every stock in your watchlist (grouped by sector) every day, regardless of whether a technical signal was triggered.
2. **Dedicated Signal Alerts Section**: Alerts triggering specific technical signals are kept in a separate, dedicated section.
3. **1 Decimal Place Precision**: Stock prices are formatted with exactly 1 decimal place (e.g., `18.2` or `125.6`).
4. **FPT added**: FPT Corporation (`FPT`) is monitored under a new `Technology` sector in `config.py`.
5. **Base Formation Detection**:
   - **Sideways 10 days**: Price range is within 6% (`BASE_THRESHOLD_10`) over the last 10 trading days.
   - **Sideways 20 days**: Price range is within 8% (`BASE_THRESHOLD_20`) over the last 20 trading days.
   - **Sideways 30 days**: Price range is within 10% (`BASE_THRESHOLD_30`) over the last 30 trading days.
6. **20-Day Base Breakout Signal**:
   - Close price breaks above the highest high of the previous 20 trading days.
   - Volume is higher than the 20-day average volume.
   - Price is above the 20-day Moving Average (MA20).
7. Volume Contraction Signal:
   - The recent 5-day average volume is lower than the 20-day average volume.
8. Daily Change % & MA20 Diff % Format: Displays the close-to-close daily change and the distance from MA20 side-by-side (e.g., `BVB: 13.8 | Day: -2.1% | MA20: +6.1%`).
9. Dynamic Latest Trading Date: Parses the actual trading date from the dataset (e.g. `Trading Date: YYYY-MM-DD`) and prints it alongside the script's run date to avoid timing confusion.

### Local Testing

To test this project locally, run the script using Python 3.10+ (which is required by the `vnstock` library to import `Quote`):

1. **Create and Activate a Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Script**:
   ```bash
   python main.py
   ```

### Pre-Commit Checklist (GitHub Desktop)

Before committing your changes in GitHub Desktop, verify the following:
1. **No Sensitive Data**: Ensure `.env` is listed in `.gitignore` and is **not** staged for commit (do not commit bot tokens or chat IDs).
2. **Changes Checked**: Check the diffs for `config.py`, `main.py`, and `README.md` to ensure only the requested changes are included.
3. **Python Version**: Ensure your local interpreter and environment match the Python 3.10 configuration in your GitHub Actions workflow.