import asyncio
from typing import Callable, Awaitable, Optional
import anthropic
from browser import BrowserController

AskUserFn = Callable[[str, Optional[list[str]]], Awaitable[str]]
SendProgressFn = Callable[[str], Awaitable[None]]

TOOLS = [
    {
        "name": "navigate",
        "description": "Navigate the browser to a URL.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Full URL including https://"}
            },
            "required": ["url"],
        },
    },
    {
        "name": "click",
        "description": "Click an element on the page using a CSS selector or Playwright locator.",
        "input_schema": {
            "type": "object",
            "properties": {"selector": {"type": "string"}},
            "required": ["selector"],
        },
    },
    {
        "name": "type_text",
        "description": "Type text into an input field. Clears existing content first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string"},
                "text": {"type": "string"},
            },
            "required": ["selector", "text"],
        },
    },
    {
        "name": "get_page_content",
        "description": "Get the visible text content of the current page for analysis.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_page_html",
        "description": "Get the full HTML of the current page to identify selectors and structure.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "screenshot",
        "description": "Take a screenshot of the current page and send it to the user via Telegram.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "wait_for_selector",
        "description": "Wait for an element to appear on the page before continuing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string"},
                "timeout_ms": {"type": "integer", "default": 10000},
            },
            "required": ["selector"],
        },
    },
    {
        "name": "scroll_to_bottom",
        "description": "Scroll to the bottom of the page to reveal lazy-loaded content.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "select_option",
        "description": "Select an option in a <select> dropdown element.",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string"},
                "value": {"type": "string"},
            },
            "required": ["selector", "value"],
        },
    },
    {
        "name": "send_progress",
        "description": (
            "Send a progress update message to the user via Telegram. "
            "Use this every 3-4 tool steps to keep the user informed."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"message": {"type": "string"}},
            "required": ["message"],
        },
    },
    {
        "name": "ask_user",
        "description": (
            "Ask the user a question via Telegram and wait for their reply. "
            "Use when you need clarification, hit a login wall, or encounter a CAPTCHA. "
            "Provide 'options' for multiple-choice (max 6 items) or omit for free-text reply."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of choices to present as buttons",
                },
            },
            "required": ["question"],
        },
    },
    {
        "name": "task_complete",
        "description": "Signal that the task has been completed. Provide a clear summary of what was accomplished.",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"}
            },
            "required": ["summary"],
        },
    },
]

SYSTEM_PROMPT = """You are an expert browser automation agent controlling a real Chrome browser on behalf of the user.

## Rules
- **Before clicking anything**, call get_page_html to find reliable selectors (prefer id, data-testid, aria-label over fragile nth-child selectors).
- **After every navigation**, always take a screenshot to confirm the page loaded correctly.
- **When blocked** by a login wall, CAPTCHA, cookie consent popup, or any ambiguity about what the user wants — immediately call ask_user. Never guess.
- **Every 3-4 tool calls**, call send_progress with a short status update so the user knows you're working.
- **Never guess at selectors**. Read the HTML first, then act.
- **On task_complete**, always include a clear, human-readable summary of what was found or done.
- If a page has large amounts of HTML, scan for key identifiers rather than reading everything.
- Prefer get_page_content (inner text) for reading prices/text; use get_page_html when you need to identify click targets.
"""

MAX_TURNS = 20


class TaskAgent:
    def __init__(
        self,
        browser: BrowserController,
        ask_user_fn: AskUserFn,
        send_progress_fn: SendProgressFn,
        anthropic_api_key: str,
    ):
        self._browser = browser
        self._ask_user_fn = ask_user_fn
        self._send_progress_fn = send_progress_fn
        self._client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)
        self._messages: list = []

    async def execute_task(self, task_description: str) -> str:
        self._messages = [{"role": "user", "content": task_description}]

        for _ in range(MAX_TURNS):
            response = await self._client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=self._messages,
            )
            self._messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                return "Task finished."

            if response.stop_reason != "tool_use":
                return f"Unexpected stop: {response.stop_reason}"

            tool_results = []
            final_summary = None

            for block in response.content:
                if block.type != "tool_use":
                    continue
                result_text, is_terminal = await self._dispatch(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_text,
                })
                if is_terminal:
                    final_summary = result_text
                    break

            self._messages.append({"role": "user", "content": tool_results})

            if final_summary is not None:
                return final_summary

        return "Reached maximum turn limit without completing."

    async def _dispatch(self, name: str, inputs: dict) -> tuple[str, bool]:
        try:
            if name == "navigate":
                await self._browser.navigate(inputs["url"])
                return f"Navigated to {inputs['url']}", False

            elif name == "click":
                await self._browser.click(inputs["selector"])
                return f"Clicked '{inputs['selector']}'", False

            elif name == "type_text":
                await self._browser.type_text(inputs["selector"], inputs["text"])
                return f"Typed into '{inputs['selector']}'", False

            elif name == "get_page_content":
                content = await self._browser.get_page_content()
                return content[:8000], False

            elif name == "get_page_html":
                html = await self._browser.get_page_html()
                return html[:12000], False

            elif name == "screenshot":
                img = await self._browser.screenshot()
                await self._send_progress_fn(None, screenshot=img)
                return f"Screenshot taken ({len(img)} bytes) and sent to Telegram.", False

            elif name == "wait_for_selector":
                timeout = inputs.get("timeout_ms", 10000)
                await self._browser.wait_for_selector(inputs["selector"], timeout=timeout)
                return f"Element '{inputs['selector']}' appeared.", False

            elif name == "scroll_to_bottom":
                await self._browser.scroll_to_bottom()
                return "Scrolled to bottom.", False

            elif name == "select_option":
                await self._browser.select_option(inputs["selector"], inputs["value"])
                return f"Selected '{inputs['value']}' in '{inputs['selector']}'.", False

            elif name == "send_progress":
                await self._send_progress_fn(inputs["message"])
                return "Progress update sent.", False

            elif name == "ask_user":
                options = inputs.get("options")
                answer = await self._ask_user_fn(inputs["question"], options)
                return f"User replied: {answer}", False

            elif name == "task_complete":
                return inputs["summary"], True

            else:
                return f"Unknown tool: {name}", False

        except Exception as e:
            return f"Error in {name}: {type(e).__name__}: {e}", False
