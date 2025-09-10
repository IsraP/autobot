import sys, asyncio, anyio, requests
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext

from domain.schemas import Token, Lead, Interaction
from application.security import get_user_session
from domain.session import authenticate_user
from domain.leads import fetch_leads
from domain.interactions import fetch_interactions, publish_interactions
from infrastructure.playwright import lifespan, fetch_browser_context

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(title="Auto-API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou restrinja para ["http://localhost:3000", ...]
    allow_credentials=True,
    allow_methods=["*"],   # inclui OPTIONS
    allow_headers=["*"],
)

@app.post("/token", response_model=Token, summary="Login and get an access token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), ctx = Depends(fetch_browser_context)):
    user = await authenticate_user(form_data.username, form_data.password, ctx)

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")


    return {"access_token": user.token.access_token, "token_type": user.token.token_type}


@app.get("/leads", response_model=List[Lead], response_model_exclude_none=True)
async def list_leads(page: int = 1, session: requests.Session = Depends(get_user_session)):
    return await anyio.to_thread.run_sync(fetch_leads, page, session)


@app.get("/leads/{lead_id}/interactions", response_model=List[Interaction])
async def list_interactions(lead_id: str, session: requests.Session = Depends(get_user_session)):
    return await anyio.to_thread.run_sync(fetch_interactions, lead_id, session)


@app.post("/leads/{lead_id}/interactions/draft", response_model=List[Interaction])
async def build_draft(lead_id: str, session: requests.Session = Depends(get_user_session)):
    return await anyio.to_thread.run_sync(build_draft, lead_id, session)


@app.post("/leads/{lead_id}/interactions/draft", response_model=List[Interaction])
async def post_interactions(lead_id: str, interactions: List[Interaction] = Body(...), session: requests.Session = Depends(get_user_session)):
    return await anyio.to_thread.run_sync(publish_interactions, lead_id, interactions, session)


# FAZER BUSCA DE CARRO NA API DOS CARAS
# FAZER ROTA DE DRAFT DE RESPOSTA
# FAZER ROTA DE ENVIO DE RESPOSTA
# ACOPLAR COM IA
# TALVEZ POR NA AWS