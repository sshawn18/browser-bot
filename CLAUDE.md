# Browser Bot — Claude Instructions

This repo turns Claude Code into a remote-controlled browser agent. Tasks arrive via Telegram,
Claude executes them in Chrome using the Claude in Chrome extension, and sends a screenshot
of the result back to Telegram.

---

## ON EVERY SESSION START: Check setup status

Run this immediately — before doing anything else:

```bash
test -f .env && echo "READY" || echo "FIRST_RUN"
```

- Output is `READY` → skip to **Normal Operation** below
- Output is `FIRST_RUN` → run the **First-Time Setup** flow below

---

## FIRST-TIME SETUP

Walk the user through each step conversationally. Do one step at a time — wait for their
response before moving to the next. Never dump all steps at once.

### Step 1 — Install dependencies

Run this first so it's done while the user reads instructions:

```bash
python -m venv venv && venv/Scripts/pip install -r requirements.txt -q
```

Tell the user: *"Installing dependencies in the background — while that runs, let's get your Telegram bot set up."*

### Step 2 — Create a Telegram bot

Tell the user:

> Open Telegram and message **@BotFather**.
> Send `/newbot`, choose a name and username, and it will give you a token like:
> `1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ`
> Paste that token here.

Wait for them to paste the token. Save it — you'll write it to `.env` in Step 4.

### Step 3 — Get their Chat ID

Tell the user:

> Now message **@userinfobot** on Telegram (just send it anything).
> It replies instantly with your info. Paste the **Id** number here.

Wait for them to paste the ID. Save it.

### Step 4 — Create .env

Create a `.env` file in the current directory:

```
TELEGRAM_BOT_TOKEN=<token from Step 2>
TELEGRAM_CHAT_ID=<id from Step 3>
```

### Step 5 — Verify the connection

Start the poller in the background:

```bash
start /B venv\Scripts\python telegram_poller.py
```

Tell the user:

> Send any message to your bot on Telegram now (e.g. "hello").

Wait about 10 seconds then check:

```bash
cat inbox.txt
```

- If it has text → connection works. Clear it: `echo -n "" > inbox.txt`
- If empty → tell the user to double-check they messaged the right bot and try again

### Step 6 — Done

Tell the user:

> You're all set! I'm now watching for tasks from Telegram.
> Send me a task like *"search Google for Tokyo weather"* and I'll get to work.

Then immediately begin **Normal Operation** below.

---

## NORMAL OPERATION

### Start monitoring

Run this /loop command at the start of every session after setup is complete:

```
/loop Check inbox.txt for a pending Telegram task by running: ./venv/Scripts/python telegram_listener.py from the browser-bot directory. If a task is printed, execute it using the Claude in Chrome extension (mcp__Claude_in_Chrome__* tools). After completing the task, send a screenshot back using: venv\Scripts\python send_chrome_screenshot.py "result caption". If no task is pending, do nothing and wait.
```

### Also start the poller if it's not running

Check if `telegram_poller.py` is already running:

```bash
tasklist | grep -i python
```

If not running, start it:

```bash
start /B venv\Scripts\python telegram_poller.py
```

---

## TASK EXECUTION — Step by step

When a task arrives in `inbox.txt`:

1. **Read the task** — run `./venv/Scripts/python telegram_listener.py` (prints task and clears inbox)
2. **Acknowledge** — run `venv\Scripts\python telegram_notify.py "⏳ On it: <task>"` so the user knows you got it
3. **Execute in Chrome** — use `mcp__Claude_in_Chrome__*` tools to complete the task
4. **Take an extension screenshot** — use `mcp__Claude_in_Chrome__computer` (this activates the correct Chrome tab)
5. **Send screenshot to Telegram** — run `venv\Scripts\python send_chrome_screenshot.py "<what you did>"`
6. **Done** — go back to watching inbox.txt

### Rules
- **Always use the Claude in Chrome extension** — never Playwright, never a headless browser
- The extension screenshot in step 4 is required before `send_chrome_screenshot.py` — it forces Chrome to show the right tab
- `send_chrome_screenshot.py` minimizes terminals, maximizes Chrome, captures full screen via DXGI (GPU-rendered), and sends directly to Telegram — no upload needed

---

## ERROR REPORTING

If something goes wrong mid-task and the user needs to see what's on screen:

1. Take an extension screenshot of the error state: `mcp__Claude_in_Chrome__computer`
2. Run: `venv\Scripts\python send_chrome_screenshot.py "Error: <description>"`
3. Send a text explanation: `venv\Scripts\python telegram_notify.py "❌ <what went wrong>"`

---

## SCRIPTS REFERENCE

| Script | What it does |
|---|---|
| `telegram_poller.py` | Background process — polls Telegram every 5s, writes new tasks to `inbox.txt`, sends instant ack |
| `telegram_listener.py` | Reads and clears `inbox.txt` — prints the task or nothing if empty |
| `send_chrome_screenshot.py` | Minimizes terminals → maximizes Chrome → DXGI capture → sends JPEG to Telegram |
| `telegram_notify.py` | Sends a plain text message to Telegram |

---

## FILE STRUCTURE

All paths below are relative to this repo root:

```
browser-bot/
├── .env                    ← your credentials (never commit this)
├── .env.example            ← template
├── inbox.txt               ← task queue (one task at a time)
├── telegram_poller.py      ← run in background, always
├── telegram_listener.py    ← called by Claude to read inbox
├── send_chrome_screenshot.py
├── telegram_notify.py
└── requirements.txt
```
