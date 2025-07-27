#!/usr/bin/env python3
import asyncio
import json
import getpass
import time
import sys
import requests
from playwright.async_api import async_playwright
from constants import CONFIG_FILE, PROFILE_DIR, BASE_URL, DUMP_LOGIN_FILE, PROJECT_DIR


# ─ Session Persistence ─────────────────────────────────────────────────────────
def load_session():
    if not CONFIG_FILE.exists():
        return None
    data = json.loads(CONFIG_FILE.read_text())
    email = data.get("email")
    cookies = data.get("cookies", {})
    now = time.time()
    for name, info in cookies.items():
        exp = info.get("expires")
        if exp and exp < now:
            print(f"⌛ Saved session for {email} has expired.")
            return None
    ans = input(f"🔑 Found saved session for {email}. Use it? (Y/n): ").strip().lower()
    if ans in ("y", "", "yes"):
        return cookies
    return None

async def do_login(username: str, password: str, headless: bool):
    async with async_playwright() as p:
        if PROFILE_DIR.exists() or not headless:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR), headless=headless,
                args=['--disable-blink-features=AutomationControlled','--no-sandbox'],
                viewport={'width':1280,'height':800},
                user_agent=(
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/115.0.0.0 Safari/537.36'
                ),
            )
        else:
            browser = await p.chromium.launch(
                headless=headless,
                args=['--disable-blink-features=AutomationControlled','--no-sandbox']
            )
            context = await browser.new_context(
                viewport={'width':1280,'height':800},
                user_agent=(
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/115.0.0.0 Safari/537.36'
                ),
            )
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        page = await context.new_page()
        login_url = f"{BASE_URL}/Auth/Login"
        await page.goto(login_url)
        await page.wait_for_load_state('domcontentloaded')
        if '/auth/login' not in page.url.lower():
            await page.goto(login_url)
            await page.wait_for_load_state('domcontentloaded')
        try:
            await page.wait_for_selector('input[name=\"login\"]', timeout=10000)
            await page.wait_for_selector('input[name=\"senha\"]', timeout=10000)
        except Exception:
            DUMP_LOGIN_FILE.write_text(await page.content(), encoding='utf-8')
            print(f"⚠️ Login form not found. HTML dumped to {DUMP_LOGIN_FILE}")
            await context.close()
            return None
        await page.fill('input[name=\"login\"]', username)
        await page.fill('input[name=\"senha\"]', password)
        await page.click('button.g-recaptcha')
        try:
            await page.wait_for_url(f"{BASE_URL}/Home/Main", timeout=15000)
        except Exception:
            try:
                await page.wait_for_load_state('networkidle', timeout=20000)
            except:
                pass
        if '/home/main' not in page.url.lower():
            await context.close()
            return None
        all_cookies = await context.cookies()
        app_cookies = [c for c in all_cookies if c.get('domain','').endswith('autocerto.com')]
        await context.close()
        return app_cookies

# ─ Session Saving ────────────────────────────────────────────────────────────────
def save_session(username, cookies_list):
    data = {
        'email': username,
        'cookies': {c['name']:{'value':c['value'],'expires':c.get('expires')} for c in cookies_list}
    }
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2))
    print(f"\n✅ Session saved to {CONFIG_FILE}\n")

# ─ API Session ──────────────────────────────────────────────────────────────────
def create_api_session(cookies_dict):
    s = requests.Session()
    for name, info in cookies_dict.items():
        s.cookies.set(name, info['value'], domain='sistema.autocerto.com', path='/')
    return s

def create_new_session(args):
    while True:
        user = input('Email: ').strip()
        try:
            pw = getpass.getpass('Password: ')
        except:
            sys.stdout.write('Password: ')
            pw = sys.stdin.readline().strip()
        print('\n🔐 Logging in…')
        cookies_list = asyncio.run(do_login(user, pw, not args.headful))
        if cookies_list:
            print('✅ Login successful!')
            if input('Save session? (y/N): ').strip().lower() in ('y','yes'):
                save_session(user, cookies_list)
            cookies_dict = {c['name']:{'value':c['value'],'expires':c.get('expires')} for c in cookies_list}
            break
        print('❌ Login blocked or failed; HTML dumped to', DUMP_LOGIN_FILE, '\n')
    return create_api_session(cookies_dict)