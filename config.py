import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    telegram_chat_id: int
    anthropic_api_key: str
    chrome_debug_port: int
    chrome_profile_path: str
    browser_headless: bool
    max_task_timeout: int


def load_config() -> Config:
    missing = []

    def require(key: str) -> str:
        val = os.getenv(key)
        if not val:
            missing.append(key)
        return val or ""

    token = require("TELEGRAM_BOT_TOKEN")
    chat_id_str = require("TELEGRAM_CHAT_ID")
    api_key = require("ANTHROPIC_API_KEY")

    if missing:
        raise ValueError(f"Missing required env vars: {', '.join(missing)}")

    return Config(
        telegram_bot_token=token,
        telegram_chat_id=int(chat_id_str),
        anthropic_api_key=api_key,
        chrome_debug_port=int(os.getenv("CHROME_DEBUG_PORT", "9222")),
        chrome_profile_path=os.getenv(
            "CHROME_PROFILE_PATH",
            r"C:\Users\USERNAME\AppData\Local\Google\Chrome\User Data",
        ),
        browser_headless=os.getenv("BROWSER_HEADLESS", "false").lower() == "true",
        max_task_timeout=int(os.getenv("MAX_TASK_TIMEOUT", "300")),
    )


config = load_config()
