import asyncio
from typing import Callable, Awaitable, Optional
from playwright.async_api import async_playwright, Page, Browser, Playwright

NotifyFn = Callable[[str, Optional[bytes]], Awaitable[None]]


class BrowserController:
    def __init__(self, debug_port: int = 9222, notify_fn: NotifyFn = None):
        self._debug_port = debug_port
        self.notify_fn = notify_fn
        self._playwright: Playwright = None
        self._browser: Browser = None
        self._page: Page = None

    async def __aenter__(self) -> "BrowserController":
        self._playwright = await async_playwright().start()
        cdp_url = f"http://localhost:{self._debug_port}"
        self._browser = await self._playwright.chromium.connect_over_cdp(cdp_url)

        # Use the first existing page, or open a new one
        contexts = self._browser.contexts
        if contexts and contexts[0].pages:
            self._page = contexts[0].pages[0]
        else:
            context = await self._browser.new_context()
            self._page = await context.new_page()

        return self

    async def __aexit__(self, *_):
        # Disconnect only — do NOT close the user's Chrome
        try:
            await self._playwright.stop()
        except Exception:
            pass

    # ── Core actions ───────────────────────────────────────────────────────

    async def navigate(self, url: str) -> None:
        await self._page.goto(url, wait_until="domcontentloaded", timeout=30_000)

    async def click(self, selector: str) -> None:
        await self._page.click(selector, timeout=10_000)

    async def type_text(self, selector: str, text: str, clear_first: bool = True) -> None:
        if clear_first:
            await self._page.fill(selector, "")
        await self._page.type(selector, text, delay=50)

    async def screenshot(self) -> bytes:
        return await self._page.screenshot(full_page=False)

    async def get_page_content(self) -> str:
        return await self._page.evaluate("document.body.innerText")

    async def get_page_html(self) -> str:
        return await self._page.content()

    async def wait_for_selector(self, selector: str, timeout: int = 10_000) -> None:
        await self._page.wait_for_selector(selector, timeout=timeout)

    async def scroll_to_bottom(self) -> None:
        await self._page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    async def get_element_text(self, selector: str) -> str:
        el = await self._page.query_selector(selector)
        return await el.inner_text() if el else ""

    async def current_url(self) -> str:
        return self._page.url

    async def select_option(self, selector: str, value: str) -> None:
        await self._page.select_option(selector, value)

    # ── Error-safe wrapper ────────────────────────────────────────────────

    async def safe_action(self, coro, description: str):
        try:
            return await coro
        except Exception as e:
            screenshot_bytes = None
            try:
                screenshot_bytes = await self.screenshot()
            except Exception:
                pass
            if self.notify_fn:
                await self.notify_fn(
                    f"Browser error during: {description}\n{type(e).__name__}: {e}",
                    screenshot_bytes,
                )
            raise
