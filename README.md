# Claude Browser Bot — Remote Control via Telegram

Control your PC's browser remotely using Telegram. Send a task from your phone → Claude executes it in Chrome → you get a screenshot of the result back on Telegram.

## How it works

```
You (Telegram) ──► inbox.txt ──► Claude Code ──► Chrome browser ──► screenshot back to you
```

1. You send a message to your Telegram bot ("Search for flights to Tokyo")
2. `telegram_poller.py` picks it up and writes it to `inbox.txt`
3. Claude Code (running on your PC) detects the task and executes it using the **Claude in Chrome** extension
4. Claude sends a screenshot of the result back to your Telegram

---

## Requirements

- Windows PC (always-on)
- [Claude Code](https://claude.ai/code) installed
- [Claude in Chrome extension](https://chromewebstore.google.com/detail/claude-extension/...) installed in Chrome
- Python 3.10+

---

## One-time setup

### Step 1 — Clone the repo
```bat
git clone https://github.com/YOUR_USERNAME/browser-bot.git
cd browser-bot
```

### Step 2 — Create your Telegram bot
1. Open Telegram and message **@BotFather**
2. Send `/newbot` and follow the steps
3. Copy the **bot token** (looks like `1234567890:ABCdef...`)

### Step 3 — Get your Telegram Chat ID
1. Message **@userinfobot** on Telegram
2. Copy the **Id** number it gives you

### Step 4 — Configure `.env`
Copy `.env.example` to `.env` and fill it in:
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdef...
TELEGRAM_CHAT_ID=987654321
```

### Step 5 — Install dependencies
```bat
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

### Step 6 — Start the Telegram poller (background)
Open a terminal and run — keep it running in the background:
```bat
venv\Scripts\python telegram_poller.py
```

### Step 7 — Tell Claude Code to start monitoring
Open Claude Code and say:
> **"Start the Telegram bot"**

Claude will start watching `inbox.txt` and execute tasks as they arrive.

---

## Usage

Once set up, just message your bot on Telegram:

| You send | Claude does |
|---|---|
| "Search Google for Tokyo weather" | Opens Chrome, searches, sends screenshot |
| "Go to amazon.com and find AirPods price" | Navigates, finds price, sends screenshot |
| "What's on my Gmail inbox?" | Opens Gmail, reads subjects, sends screenshot |

---

## Scripts

| Script | Purpose |
|---|---|
| `telegram_poller.py` | Polls Telegram every 5s, writes tasks to `inbox.txt` |
| `telegram_listener.py` | Read + clear `inbox.txt` (used by Claude internally) |
| `send_chrome_screenshot.py` | Screenshots Chrome via DXGI and sends to Telegram |
| `telegram_notify.py` | Sends a plain text message to Telegram |
| `start_chrome.bat` | Launches Chrome with remote debugging (optional) |

---

## How Claude knows what to do

Add this snippet to your Claude Code project's `CLAUDE.md`:

```markdown
## Telegram Bot Remote Control System
All scripts live at C:\path\to\browser-bot\

### Key Files
- `inbox.txt` — incoming tasks written here by telegram_poller.py
- `send_chrome_screenshot.py` — screenshots Chrome and sends to Telegram
- `telegram_notify.py` — sends plain text to Telegram
- `.env` — TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID

### To start monitoring (say "start the Telegram bot")
Run: /loop Check inbox.txt for a pending task by running: cd /path/to/browser-bot && ./venv/Scripts/python telegram_listener.py. If a task is printed, execute it using the Claude in Chrome extension tools. Then send a screenshot using: venv\Scripts\python send_chrome_screenshot.py "result caption". Clear inbox.txt after each task.

### Screenshot pipeline
1. Take a Chrome extension screenshot (activates the correct tab)
2. Run: venv\Scripts\python send_chrome_screenshot.py "caption"
3. Always use Claude in Chrome extension — NOT Playwright
```

---

## Troubleshooting

**Telegram messages not arriving**
- Make sure you sent at least one message to your bot first (Telegram requires this)
- Double-check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`

**Screenshot is black or wrong tab**
- The `send_chrome_screenshot.py` script will minimize other windows and maximize Chrome automatically
- Make sure Chrome is open before running tasks

**`telegram_poller.py` crashes**
- Check your bot token is valid
- Run it from the `browser-bot` folder, not elsewhere
