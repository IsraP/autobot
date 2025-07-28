#!/usr/bin/env python3
import argparse
import asyncio
import getpass
import json
import sys
import time
from pathlib import Path

import requests
from playwright.async_api import async_playwright
from constants import CONFIG_FILE, PROFILE_DIR, BASE_URL, DUMP_LOGIN_FILE, PROJECT_DIR


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Autobot CLI for session login and API access")
    parser.add_argument(
        "--headful", action="store_true",
        help="Run browser with UI (not headless)"
    )
    return parser.parse_args()


def load_saved_cookies() -> dict[str, dict]:
    """
    Load cookies from CONFIG_FILE if they exist, are not expired,
    and the user confirms reuse.
    """
    if not CONFIG_FILE.exists():
        return {}

    data = json.loads(CONFIG_FILE.read_text())
    email = data.get("email", "<unknown>")
    cookies = data.get("cookies", {})

    # Check for expiration
    now = time.time()
    if any(info.get("expires", 0) < now for info in cookies.values()):
        print(f"⌛ Saved session for {email} has expired.")
        return {}

    choice = input(f"🔑 Found saved session for {email}. Use it? (Y/n): ").strip().lower()
    return cookies if choice in ("", "y", "yes") else {}


async def _perform_login(
    username: str,
    password: str,
    headless: bool
) -> list[dict]:
    """
    Automate Playwright login flow and return a list of cookies on success.
    """
    async with async_playwright() as p:
        args = [
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
        ]
        viewport = {'width': 1280, 'height': 800}
        user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/115.0.0.0 Safari/537.36'
        )

        # Choose persistent context when profile exists or headful mode
        if PROFILE_DIR.exists() or not headless:
            browser_context = await p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR), headless=headless,
                args=args, viewport=viewport, user_agent=user_agent
            )
        else:
            browser = await p.chromium.launch(headless=headless, args=args)
            browser_context = await browser.new_context(
                viewport=viewport, user_agent=user_agent
            )

        # Stealth: disable webdriver flag
        await browser_context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )

        page = await browser_context.new_page()
        await page.goto(f"{BASE_URL}/Auth/Login")
        await page.wait_for_selector('input[name="login"]', timeout=10000)
        await page.wait_for_selector('input[name="senha"]', timeout=10000)

        await page.fill('input[name="login"]', username)
        await page.fill('input[name="senha"]', password)
        await page.click('button.g-recaptcha')

        # Wait for redirect
        try:
            await page.wait_for_url(f"{BASE_URL}/Home/Main", timeout=15000)
        except Exception:
            await page.wait_for_load_state('networkidle', timeout=20000)

        # Verify login success
        if '/home/main' not in page.url.lower():
            # Dump HTML for debugging
            DUMP_LOGIN_FILE.write_text(await page.content(), encoding='utf-8')
            await browser_context.close()
            return []

        # Filter for target domain cookies
        cookies = await browser_context.cookies()
        app_cookies = [
            c for c in cookies if c.get('domain', '').endswith('autocerto.com')
        ]
        await browser_context.close()
        return app_cookies


def save_session(username: str, cookies_list: list[dict]) -> None:
    """Save the session cookies to CONFIG_FILE."""
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        'email': username,
        'cookies': {
            c['name']: {'value': c['value'], 'expires': c.get('expires')}
            for c in cookies_list
        }
    }
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding='utf-8')
    print(f"✅ Session saved to {CONFIG_FILE}")


def login_and_retrieve_cookies(headful: bool) -> dict[str, dict]:
    """
    Prompt user credentials, perform login loop until success,
    and optionally save session.
    Returns a dictionary of cookies.
    """
    while True:
        user = input('Email: ').strip()
        pw = getpass.getpass('Password: ')
        print('\n🔐 Logging in…')

        cookies = asyncio.run(_perform_login(user, pw, not headful))
        if cookies:
            print('✅ Login successful!')
            if input('Save session? (y/N): ').strip().lower() in ('y', 'yes'):
                save_session(user, cookies)
            return {c['name']: {'value': c['value'], 'expires': c.get('expires')} for c in cookies}

        print(f"❌ Login blocked or failed; HTML dumped to {DUMP_LOGIN_FILE}\n")


def create_api_session(cookies_dict: dict[str, dict]) -> requests.Session:
    """Create a requests.Session using stored cookies."""
    session = requests.Session()
    for name, info in cookies_dict.items():
        session.cookies.set(name, info['value'], domain='sistema.autocerto.com', path='/')
    return session


def get_api_session(args: argparse.Namespace) -> requests.Session:
    """
    Retrieve an API session either by loading saved cookies or logging in anew.
    """
    cookies = load_saved_cookies()
    if not cookies:
        cookies = login_and_retrieve_cookies(headful=args.headful)
    return create_api_session(cookies)