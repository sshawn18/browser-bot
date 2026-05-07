## Telegram Remote Control Bot

This repo lets you control your PC's Chrome browser remotely by sending tasks via Telegram.
Claude executes them and sends a screenshot of the result back to you.

---

## FIRST: Run this check at the start of EVERY session

Check if `.env` exists in this directory:
- **Does NOT exist** → run the Onboarding Flow below
- **Exists** → jump straight to "Start Monitoring"

---

## Onboarding Flow (only if no .env)

Walk the user through these steps conversationally, one at a time. Do not dump all steps at once.

### Step 1 — Create a Telegram bot
Tell the user:
> "Open Telegram and message **@BotFather**. Send `/newbot`, pick a name, and follow the steps. Once you have the bot token (looks like `1234567890:ABCdef...`), paste it here."

Wait for them to paste the token.

### Step 2 — Get your Chat ID
Tell the user:
> "Now message **@userinfobot** on Telegram. It will instantly reply with your info — paste the **Id** number here."

Wait for them to paste the ID.

### Step 3 — Create .env
Create a `.env` file in this directory with:
```
TELEGRAM_BOT_TOKEN=<their token>
TELEGRAM_CHAT_ID=<their chat id>
```

### Step 4 — Install dependencies
Run this command:
```
python -m venv venv && venv\Scripts\pip install -r requirements.txt
```
Tell the user you're installing and wait for it to finish.

### Step 5 — Update this CLAUDE.md with the correct path
Find the absolute path to this repo directory on the user's machine (e.g. `C:\Users\Bob\browser-bot`).
Replace every occurrence of `REPO_PATH` in this file with that absolute path.
This makes future sessions work without re-onboarding.

### Step 6 — Send a test message
Tell the user:
> "Send any message to your bot on Telegram to make sure it's working."

Start `telegram_poller.py` in the background:
```
start /B venv\Scripts\python telegram_poller.py
```
Wait ~10 seconds and check `inbox.txt` — if it contains text, the connection works.

### Step 7 — Done! Start monitoring
Tell the user:
> "You're all set! I'm now watching for tasks. Send me a message on Telegram and I'll get to work."

Then proceed to Start Monitoring below.

---

## Start Monitoring

Run this command to begin watching for tasks:

```
/loop Check REPO_PATH\inbox.txt for a pending Telegram task. Run: cd REPO_PATH && venv\Scripts\python telegram_listener.py. If a task is printed, execute it using the Claude in Chrome extension (mcp__Claude_in_Chrome__* tools — NOT Playwright). After completing the task, send a screenshot back: cd REPO_PATH && venv\Scripts\python send_chrome_screenshot.py "task result caption". If no task, do nothing.
```

---

## Task Execution Rules

- **Always use the Claude in Chrome extension** (`mcp__Claude_in_Chrome__*`) for browser control — never Playwright
- After every task: take an extension screenshot first (activates the correct Chrome tab), then run `send_chrome_screenshot.py`
- Clear `inbox.txt` after reading (write empty string) so the monitor doesn't re-trigger

## Screenshot Pipeline

1. Use `mcp__Claude_in_Chrome__computer` to take a screenshot (forces Chrome to show the working tab)
2. Run: `venv\Scripts\python send_chrome_screenshot.py "caption"` from REPO_PATH
3. This minimizes terminal windows, maximizes Chrome, captures full screen via DXGI, and sends the JPEG directly to Telegram

## Error Reporting

If something goes wrong and you need the user to see what's on screen:
1. Take an extension screenshot of the error state
2. Run: `venv\Scripts\python send_chrome_screenshot.py "Error: <description>"`

## Scripts Reference

| Script | Purpose |
|---|---|
| `telegram_poller.py` | Background process — polls Telegram every 5s, writes tasks to inbox.txt |
| `telegram_listener.py` | Read + clear inbox.txt (Claude calls this to get the current task) |
| `send_chrome_screenshot.py` | Screenshot Chrome via DXGI → send photo to Telegram |
| `telegram_notify.py` | Send plain text message to Telegram |
