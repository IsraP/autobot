import os
from datetime import timezone, timedelta

SECRET_KEY = "autobot"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
ARGS = ['--disable-blink-features=AutomationControlled', '--no-sandbox']
VIEWPORT = {'width': 1280, 'height': 800}
USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
              'AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/115.0.0.0 Safari/537.36')
TZ_SP = timezone(timedelta(hours=-3))

BASE_URL = "https://sistema.autocerto.com"
FETCH_LEADS_PATH = "/Lead/ObterleadsAjax"
FETCH_INTERACTIONS_PATH = "/Lead/ObterInteracoesAjax"

