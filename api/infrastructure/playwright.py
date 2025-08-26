from contextlib import asynccontextmanager
from fastapi import Request
from typing import AsyncIterator
from playwright.async_api import async_playwright, Browser, BrowserContext

from application.constants import ARGS, VIEWPORT, USER_AGENT

"""
Sets up the API's lifespan, setting up a browser context at startup to be reutilized as long as the app is running.
"""
@asynccontextmanager
async def lifespan(app):
    pw = await async_playwright().start()
    browser: Browser = await pw.chromium.launch(headless=False, args=ARGS)

    app.state.pw = pw
    app.state.browser = browser

    try:
        yield
    finally:
        if app.state.browser and app.state.browser.is_connected():
            await app.state.browser.close()
        await app.state.pw.stop()



"""
Fetches the browser context defined in the API's lifespan function
"""
async def fetch_browser_context(request: Request) -> AsyncIterator[BrowserContext]:
    browser: Browser = request.app.state.browser

    ctx = await browser.new_context(viewport=VIEWPORT, user_agent=USER_AGENT)
    await ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

    try:
        yield ctx
    finally:
        await ctx.close()
