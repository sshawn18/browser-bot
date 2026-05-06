import asyncio
import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from config import config
from browser import BrowserController
from agent import TaskAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Inline keyboard callback prefixes ────────────────────────────────────────
CB_CONFIRM_YES = "confirm:yes"
CB_CONFIRM_NO  = "confirm:no"
CB_CHOICE_PFX  = "choice:"


class BrowserBot:
    def __init__(self):
        self._app: Application = None

        # Task queue — one task executes at a time
        self._task_queue: asyncio.Queue[str] = asyncio.Queue()

        # Q&A bridge — used when agent needs user input mid-task
        self._answer_event: asyncio.Event = asyncio.Event()
        self._pending_answer: Optional[str] = None

        # Pending confirmation state
        self._pending_task: Optional[str] = None

        # Whether a task is currently running (for routing text messages)
        self._task_running: bool = False
        self._waiting_for_answer: bool = False

    # ── Security ─────────────────────────────────────────────────────────────

    def _authorized(self, update: Update) -> bool:
        return update.effective_chat and update.effective_chat.id == config.telegram_chat_id

    # ── /start ────────────────────────────────────────────────────────────────

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            await update.message.reply_text("Unauthorized.")
            return
        await update.message.reply_text(
            "Browser bot ready!\n\n"
            "Send me any task in plain English. Examples:\n"
            "• Check the price of iPhone 15 on Amazon\n"
            "• Open Gmail and check unread emails\n"
            "• Search Flipkart for USB-C cables under ₹500\n"
            "• Go to youtube.com and find trending videos\n\n"
            f"Your chat ID: `{update.effective_chat.id}`",
            parse_mode="Markdown",
        )

    # ── Incoming task message ─────────────────────────────────────────────────

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._authorized(update):
            await update.message.reply_text("Unauthorized.")
            return

        text = update.message.text.strip()

        # Route: if we're waiting for a user answer to a mid-task question
        if self._waiting_for_answer:
            self._pending_answer = text
            self._answer_event.set()
            await update.message.reply_text(f"Got it. Resuming task...")
            return

        # Otherwise treat as a new task
        self._pending_task = text
        queue_pos = self._task_queue.qsize() + (1 if self._task_running else 0)

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("Yes, proceed", callback_data=CB_CONFIRM_YES),
            InlineKeyboardButton("Cancel", callback_data=CB_CONFIRM_NO),
        ]])

        position_note = f" (will queue — {queue_pos} task(s) ahead)" if queue_pos > 0 else ""
        await update.message.reply_text(
            f"Task{position_note}:\n\n_{text}_\n\nShall I proceed?",
            reply_markup=keyboard,
            parse_mode="Markdown",
        )

    # ── Confirmation callbacks ────────────────────────────────────────────────

    async def handle_confirm_yes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        if not self._authorized(update):
            return
        task = self._pending_task
        self._pending_task = None
        if not task:
            await query.edit_message_text("No pending task found.")
            return
        await self._task_queue.put(task)
        queued = self._task_queue.qsize()
        if self._task_running:
            await query.edit_message_text(f"Queued! (position {queued})")
        else:
            await query.edit_message_text("Starting task...")

    async def handle_confirm_no(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        if not self._authorized(update):
            return
        self._pending_task = None
        await query.edit_message_text("Cancelled.")

    # ── Mid-task inline-keyboard choice ──────────────────────────────────────

    async def handle_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        if not self._authorized(update):
            return
        choice = query.data[len(CB_CHOICE_PFX):]
        self._pending_answer = choice
        self._answer_event.set()
        await query.edit_message_text(f"Selected: *{choice}*. Resuming...", parse_mode="Markdown")

    # ── Q&A bridge (called by agent) ─────────────────────────────────────────

    async def ask_user_fn(self, question: str, options: list[str] | None) -> str:
        self._waiting_for_answer = True
        self._answer_event.clear()
        self._pending_answer = None

        if options:
            rows = []
            for i in range(0, len(options), 2):
                rows.append([
                    InlineKeyboardButton(opt, callback_data=f"{CB_CHOICE_PFX}{opt}")
                    for opt in options[i:i+2]
                ])
            keyboard = InlineKeyboardMarkup(rows)
            await self._send_message(question, reply_markup=keyboard)
        else:
            await self._send_message(f"Question:\n\n{question}\n\nPlease reply with your answer.")

        try:
            await asyncio.wait_for(self._answer_event.wait(), timeout=300)
        except asyncio.TimeoutError:
            self._waiting_for_answer = False
            raise TimeoutError("User did not reply within 5 minutes.")

        self._waiting_for_answer = False
        return self._pending_answer or ""

    # ── Progress/screenshot sender (called by agent) ──────────────────────────

    async def send_progress_fn(self, message: str = None, screenshot: bytes = None):
        if screenshot:
            await self._send_message(message or "Screenshot:", photo_bytes=screenshot)
        elif message:
            await self._send_message(f"⏳ {message}")

    # ── Telegram send helper ──────────────────────────────────────────────────

    async def _send_message(self, text: str, reply_markup=None, photo_bytes: bytes = None):
        if photo_bytes:
            caption = (text or "")[:1024]
            await self._app.bot.send_photo(
                chat_id=config.telegram_chat_id,
                photo=photo_bytes,
                caption=caption,
            )
        else:
            for chunk in _split(text, 4000):
                await self._app.bot.send_message(
                    chat_id=config.telegram_chat_id,
                    text=chunk,
                    reply_markup=reply_markup,
                    parse_mode="Markdown",
                )

    async def _notify_fn(self, message: str, screenshot: bytes | None):
        await self._send_message(f"Browser error:\n`{message}`", photo_bytes=screenshot)

    # ── Task worker ───────────────────────────────────────────────────────────

    async def _task_worker(self):
        while True:
            task_text = await self._task_queue.get()
            self._task_running = True
            await self._send_message(f"Starting:\n_{task_text}_", )

            try:
                async with BrowserController(
                    debug_port=config.chrome_debug_port,
                    notify_fn=self._notify_fn,
                ) as browser:
                    agent = TaskAgent(
                        browser=browser,
                        ask_user_fn=self.ask_user_fn,
                        send_progress_fn=self.send_progress_fn,
                        anthropic_api_key=config.anthropic_api_key,
                    )
                    summary = await asyncio.wait_for(
                        agent.execute_task(task_text),
                        timeout=config.max_task_timeout,
                    )
                    screenshot = await browser.screenshot()
                    await self._send_message(
                        f"Task complete!\n\n{summary}",
                        photo_bytes=screenshot,
                    )

            except asyncio.TimeoutError:
                await self._send_message(
                    f"Task timed out after {config.max_task_timeout}s.\n_{task_text}_"
                )
            except Exception as e:
                await self._send_message(
                    f"Task failed:\n`{type(e).__name__}: {e}`\n\n_{task_text}_"
                )
            finally:
                self._task_running = False
                self._task_queue.task_done()

    # ── Build & run ───────────────────────────────────────────────────────────

    def _build(self) -> Application:
        self._app = Application.builder().token(config.telegram_bot_token).build()

        self._app.add_handler(CommandHandler("start", self.cmd_start))
        self._app.add_handler(
            CallbackQueryHandler(self.handle_confirm_yes, pattern=f"^{CB_CONFIRM_YES}$")
        )
        self._app.add_handler(
            CallbackQueryHandler(self.handle_confirm_no, pattern=f"^{CB_CONFIRM_NO}$")
        )
        self._app.add_handler(
            CallbackQueryHandler(self.handle_choice, pattern=f"^{CB_CHOICE_PFX}")
        )
        self._app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        return self._app

    async def run(self):
        self._build()
        asyncio.create_task(self._task_worker())
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling(drop_pending_updates=True)
        logger.info("Bot is running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()  # run forever


def _split(text: str, limit: int) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        chunk = text[:limit]
        cut = chunk.rfind("\n")
        cut = cut if cut > 0 else limit
        chunks.append(text[:cut])
        text = text[cut:].lstrip("\n")
    return chunks


if __name__ == "__main__":
    import signal

    bot = BrowserBot()

    async def main():
        await bot.run()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped.")
