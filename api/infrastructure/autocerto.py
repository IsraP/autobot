from typing import List, Dict
from playwright.async_api import BrowserContext, Page
from application.constants import BASE_URL, FETCH_LEADS_PATH, FETCH_INTERACTIONS_PATH
import requests


GET_LEADS_BY_PAGE = BASE_URL + FETCH_LEADS_PATH
GET_INTERACTIONS_BY_LEAD = BASE_URL + FETCH_INTERACTIONS_PATH


"""
Automates login flow via playwright and return a list of cookies on success.
Returns [] when login fails.
"""
async def login_and_get_cookies(username: str, password: str, ctx: BrowserContext) -> list[dict]:
    page = await ctx.new_page()

    success = await attempt_login(page, username, password)

    if not success:
        return []

    return await extract_autocerto_cookies(ctx)


"""
Attempts to login with given credentials.
"""
async def attempt_login(page: Page, username: str, password: str) -> bool:
    # Go to the login screen and wait for inputs to be present.
    await page.goto(f"{BASE_URL}/Auth/Login")
    await page.wait_for_selector('input[name="login"]', timeout=10_000)
    await page.wait_for_selector('input[name="senha"]', timeout=10_000)

    # Fill credentials and click the recaptcha/login button.
    await page.fill('input[name="login"]', username)
    await page.fill('input[name="senha"]', password)

    # This button exists in the target app; it triggers login after captcha validation
    await page.click('button.g-recaptcha')

    # Wait for a successful login redirect or network idle; return True if on Home/Main.
    try:
        await page.wait_for_url(f"{BASE_URL}/Home/Main", timeout=15_000)
    except Exception:
        # fallback: if slow, wait for network to settle and then check URL
        await page.wait_for_load_state('networkidle', timeout=20_000)

    return '/home/main' in page.url.lower()



"""
Return only cookies belonging to autocerto.com domains.
"""
async def extract_autocerto_cookies(ctx: BrowserContext) -> List[Dict]:
    cookies = await ctx.cookies()

    return [c for c in cookies if (c.get('domain') or '').endswith('autocerto.com')]



"""
Returns the HTML for all leads in a given page
"""
def get_leads_by_page(page: int, session: requests.Session):
    params = {'status': 1, 'midia': 0, 'page': page, 'usuario': 0, 'buscarapida': '', 'ordenacao': 0}

    request = session.get(GET_LEADS_BY_PAGE, params=params)

    return request.text


"""
Returns the HTML for all interactions in a given lead
"""
def get_interactions_by_lead(lead_id: str, session: requests.Session):
    request = session.get(GET_INTERACTIONS_BY_LEAD, params={'id': lead_id})

    return request.text