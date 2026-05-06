#!/usr/bin/env python3
"""Send a one-way Telegram notification.

Usage:
    python telegram_notify.py "Your message here"
"""
import sys
import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("ERROR: Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in browser-bot/.env")
    sys.exit(1)

message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "(no message)"

resp = requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    json={"chat_id": CHAT_ID, "text": message},
    timeout=10,
)

if not resp.ok:
    print(f"ERROR: {resp.text}")
    sys.exit(1)

print("Sent.")
