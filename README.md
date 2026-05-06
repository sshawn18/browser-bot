# Browser Bot — Telegram Notifications for Claude Code

Claude Code controls your browser directly. These two scripts let Claude ping you on Telegram when it needs input or hits a problem — and wait for your reply before continuing.

## How it works

1. You give Claude Code a task in chat
2. Claude uses the Playwright MCP to control your Chrome browser
3. When Claude gets stuck or needs a decision, it runs:
   ```
   python telegram_ask.py "Login wall on Amazon — skip or try Flipkart instead?"
   ```
4. You get the message on Telegram, reply, and Claude reads your answer and continues

---

## One-time setup (on your Windows PC)

### Step 1: Clone this repo
```
git clone https://github.com/sshawn18/browser-bot.git
cd browser-bot
```

### Step 2: Run setup.bat
Double-click `setup.bat` — creates a virtual environment and installs `requests` and `python-dotenv`.

### Step 3: Create your Telegram bot
- Message **@BotFather** on Telegram → send `/newbot` → follow the steps → copy the token

### Step 4: Get your Telegram chat ID
- Message **@userinfobot** on Telegram → copy the **Id** number

### Step 5: Fill in .env
```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### Step 6: Add the Playwright MCP to Claude Code
Run this once in your terminal:
```
claude mcp add playwright -- npx @playwright/mcp@latest --cdp-endpoint http://localhost:9222
```
This gives Claude Code the ability to control your Chrome browser.

### Step 7: Start Chrome with remote debugging
Double-click `start_chrome.bat` — opens Chrome using your existing profile (all logins preserved).

---

## Every time you use it

1. Double-click `start_chrome.bat`
2. Open Claude Code and give it a task, e.g.:
   > *"Go to Amazon and check the price of iPhone 15 128GB"*
3. Claude does the work. If it gets stuck, your phone buzzes on Telegram.
4. Reply on Telegram — Claude reads your answer and continues.

---

## What the scripts do

**`telegram_notify.py`** — Claude sends you a one-way update:
```bash
python telegram_notify.py "Done! Found iPhone 15 at ₹69,999"
```

**`telegram_ask.py`** — Claude asks a question and waits for your reply:
```bash
python telegram_ask.py "Hit a CAPTCHA — should I try a different site?"
# blocks until you reply on Telegram
# prints your reply so Claude can read it
```

Claude calls these via its Bash tool during tasks.

---

## Troubleshooting

**"Connection refused" when Claude tries to use the browser**
Chrome isn't running with remote debugging. Run `start_chrome.bat` first.

**Telegram messages not arriving**
Check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`. Make sure you've started a chat with your bot on Telegram first (send it any message).

**`telegram_ask.py` times out**
You have 5 minutes to reply by default. Change `TELEGRAM_REPLY_TIMEOUT=300` in `.env` to extend it.
