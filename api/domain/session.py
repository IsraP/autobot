import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict

import requests
from application.constants import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from domain.schemas import LoggedUser, Token
from infrastructure.autocerto import login_and_get_cookies

current_sessions = dict()


"""
Attempts to authenticate a user with given credentials.
"""
async def authenticate_user(username: str, password: str, ctx) -> Optional[LoggedUser]:
    user_cookies = await login_and_get_cookies(username, password, ctx)

    if user_cookies:
        user_access_token = build_access_token(username)

        user_session = build_session(user_cookies)
        save_session(user_session, user_access_token)

        return LoggedUser(username=username, token=Token(access_token=user_access_token))

    return None


"""
Builds an auto-api token for streamlining requests.
"""
def build_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": username,
        "exp": expire
    }

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


"""
Creates a requests.Session() with user cookies
"""
def build_session(user_cookies: List[Dict]) -> requests.Session:
    session = requests.Session()

    for cookie in user_cookies:
        name = cookie.get("name")
        value = cookie.get("value")
        domain = cookie.get("domain", "sistema.autocerto.com")
        path = cookie.get("path", "/")

        if name and value:
            session.cookies.set(name, value, domain=domain, path=path)

    return session


"""
Saves a session to the api context to be reused on subsequent requests.
"""
def save_session(session: requests.Session, user_token: str) -> None:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    current_sessions[user_token] = (session, expire)


"""
Given a token, return the associated requests.Session if still valid.
If the token is missing or expired, return None and remove the entry.
"""
def get_session_by_token(token: str) -> Optional[requests.Session]:
    rec = current_sessions.get(token)
    if not rec:
        return None

    session_obj, expires_at = rec

    if datetime.now(timezone.utc) >= expires_at:
        current_sessions.pop(token, None)
        return None

    return session_obj