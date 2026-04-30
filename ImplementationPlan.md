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
└── .github/
    └── workflows/
        └── daily-stock-alert.yml