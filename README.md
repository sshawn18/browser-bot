# Browser Bot

Control your Chrome browser remotely via Telegram. Send tasks in plain English, get screenshots and results back — even when you're away from your PC.

## How it works

1. You send a task to your Telegram bot: *"Check the price of iPhone 15 on Amazon"*
2. The bot asks you to confirm, then Claude AI takes over
3. Claude controls your existing Chrome browser step-by-step
4. If it needs input (login, CAPTCHA, ambiguous choice), it asks you on Telegram
5. When done, you get a screenshot + summary

Your existing Chrome logins and sessions are preserved — no need to log in again.

---

## Setup

### Step 1: Install Python 3.11+

Download from [python.org](https://python.org). During install, check **"Add Python to PATH"**.

Verify:
```
python --version
```

### Step 2: Run setup.bat

Double-click `setup.bat` in this folder. It will:
- Create a Python virtual environment
- Install all dependencies
- Install the Chromium browser for Playwright
- Create your `.env` file from the template

### Step 3: Fill in `.env` with your credentials

Open the `.env` file (created by setup.bat) and fill in:

```
TELEGRAM_BOT_TOKEN=    ← from Step 4
TELEGRAM_CHAT_ID=      ← from Step 5
ANTHROPIC_API_KEY=     ← from anthropic.com
CHROME_DEBUG_PORT=9222
CHROME_PROFILE_PATH=C:\Users\YOUR_USERNAME\AppData\Local\Google\Chrome\User Data
BROWSER_HEADLESS=false
MAX_TASK_TIMEOUT=300
```

### Step 4: Get your Telegram bot token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow the prompts — choose a name and username for your bot
4. Copy the token (looks like `123456789:ABCdefGHI...`) into `.env`

### Step 5: Get your Telegram chat ID

1. Open Telegram and search for **@userinfobot**
2. Send `/start`
3. Copy the **Id** number into `.env` as `TELEGRAM_CHAT_ID`

### Step 6: Launch Chrome with remote debugging

Double-click `start_chrome.bat`. This opens Chrome with remote debugging enabled on port 9222, using your existing profile (all logins preserved).

> **Important:** Chrome must be running via `start_chrome.bat` every time you use the bot. Normal Chrome shortcuts will not work for remote control.

### Step 7: Start the bot

Open a terminal in this folder and run:

```
venv\Scripts\python.exe bot.py
```

You should see: `Bot is running. Press Ctrl+C to stop.`

### Step 8: Send /start on Telegram

Open Telegram, find your bot, and send `/start`. It will respond with a welcome message.

### Step 9: Test it

Send this message to your bot:

```
Go to google.com and tell me the page title
```

You should see:
1. A confirmation keyboard: **Yes, proceed** / **Cancel**
2. After confirming — a progress update
3. A final screenshot + result

---

## Usage Tips

- **Tasks are queued** — if a task is running, new tasks wait in line
- **The bot only responds to you** — your `TELEGRAM_CHAT_ID` is the only one authorized
- **The bot asks when unsure** — login walls, CAPTCHAs, or ambiguous choices trigger a question back to you
- **Watch it work** — with `BROWSER_HEADLESS=false`, you can watch Chrome being controlled in real time

## Example tasks

```
Check the score of today's IPL match
Search Amazon for "mechanical keyboard" under ₹3000 and list top 3
Go to my Gmail and check if I have any unread emails from HR
Check what's trending on YouTube India right now
Go to irctc.co.in and check trains from Mumbai to Delhi on June 10
```

## Troubleshooting

**"Connection refused" error**  
Chrome isn't running with remote debugging. Run `start_chrome.bat` first.

**Bot doesn't respond**  
Check that `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are correct in `.env`.

**Chrome closes existing windows**  
This is normal when connecting — Chrome will use your existing profile and windows.

**Task times out**  
Increase `MAX_TASK_TIMEOUT` in `.env` (default is 300 seconds).
