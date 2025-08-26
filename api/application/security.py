from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import requests
from domain.session import get_session_by_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_user_session(token: str = Depends(oauth2_scheme)) -> requests.Session:
    session = get_session_by_token(token)

    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    return session
