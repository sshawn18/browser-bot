#!/usr/bin/env python3
"""Send a Telegram message and wait for the user's reply.

Prints the reply text to stdout so Claude Code can read it.

Usage:
    python telegram_ask.py "Which storage size — 128GB or 256GB?"
"""
import sys
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))
TIMEOUT = int(os.getenv("TELEGRAM_REPLY_TIMEOUT", "300"))  # 5 minutes


def api(method: str, **kwargs):
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/{method}",
        json=kwargs,
        timeout=35,
    )
    r.raise_for_status()
    return r.json()


if not TOKEN or not CHAT_ID:
    print("ERROR: Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in browser-bot/.env")
    sys.exit(1)

question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "(no question)"

# Remember the latest update_id so we only catch NEW replies (not old messages)
resp = api("getUpdates", offset=-1, timeout=0)
updates = resp.get("result", [])
offset = (updates[-1]["update_id"] + 1) if updates else 0

# Send the question
api("sendMessage", chat_id=CHAT_ID, text=f"Claude needs your input:\n\n{question}")

# Poll for a reply
deadline = time.time() + TIMEOUT
while time.time() < deadline:
    wait = min(30, int(deadline - time.time()))
    resp = api("getUpdates", offset=offset, timeout=wait)
    for update in resp.get("result", []):
        offset = update["update_id"] + 1
        msg = update.get("message", {})
        if msg.get("chat", {}).get("id") == CHAT_ID and "text" in msg:
            print(msg["text"])
            sys.exit(0)

print("TIMEOUT: No reply received within the time limit.")
sys.exit(1)
