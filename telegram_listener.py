"""
Reads the latest task from inbox.txt, prints it, then clears the file.
Prints nothing if no pending task.
"""
from pathlib import Path

INBOX = Path(__file__).parent / "inbox.txt"
if INBOX.exists():
    task = INBOX.read_text(encoding="utf-8").strip()
    INBOX.write_text("", encoding="utf-8")
    if task:
        print(task)
