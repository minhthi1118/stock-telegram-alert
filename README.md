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