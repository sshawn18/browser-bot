# Browser Bot — Remote Control Chrome via Telegram

Send a task from your phone → Claude executes it in your browser → you get a screenshot back on Telegram.

```
You (Telegram) ──► inbox.txt ──► Claude Code ──► Chrome ──► screenshot back to you
```

**Example:** You send *"search Google for flights to Tokyo"* on Telegram.
Claude opens Chrome, runs the search, and sends you a photo of the results — all while you're away from your PC.

---

## What you need

| Requirement | Notes |
|---|---|
| Windows PC | Must be on when you want to send tasks |
| [Claude Code](https://claude.ai/code) | The AI that executes your tasks |
| [Claude in Chrome extension](https://chromewebstore.google.com/search/claude) | Installed in Chrome — gives Claude browser control |
| Python 3.10+ | For the Telegram scripts |
| Telegram account | Free — you'll create a bot in 2 minutes |

---

## Setup

```bash
git clone https://github.com/sshawn18/browser-bot.git
cd browser-bot
```

Then open the `browser-bot` folder in **Claude Code** and say:

> **"Set this up for me"**

Claude will guide you through the rest — creating your Telegram bot, getting your chat ID,
installing dependencies, and starting the monitor. **You don't need to follow any manual steps.**

---

## How it works (after setup)

1. You send a message to your Telegram bot
2. `telegram_poller.py` (running in the background) picks it up and writes it to `inbox.txt`
3. Claude Code detects the new task
4. Claude executes it in Chrome using the **Claude in Chrome** extension
5. Claude sends a screenshot of the result back to your Telegram

---

## Usage examples

| You send on Telegram | Claude does |
|---|---|
| Search Google for Tokyo weather | Opens Chrome, searches, sends screenshot |
| Go to amazon.com and find AirPods price | Navigates, finds the price, sends screenshot |
| What's on my Gmail inbox? | Opens Gmail, reads subjects, sends screenshot |
| Open YouTube and find a Python tutorial | Finds and opens the video, sends screenshot |

---

## Starting a new session

Each time you open Claude Code in this folder, just say:

> **"Start the Telegram bot"**

Claude will check if setup is already done and jump straight to monitoring.

---

## Troubleshooting

**Messages not arriving in Telegram**
Make sure you've sent at least one message to your bot first — Telegram requires this before a bot can message you.

**Screenshot shows the wrong tab or is black**
The screenshot script handles this automatically by maximizing Chrome and minimizing other windows. Make sure Chrome is open.

**`telegram_poller.py` isn't running**
Claude will start it automatically, but you can also run it manually:
```bash
venv\Scripts\python telegram_poller.py
```

**Want to use your own bot token?**
Message `@BotFather` on Telegram → `/newbot` → follow the steps → update `.env` with the new token.
