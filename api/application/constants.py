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
PUBLISH_INTERACTION_PATH = "/Lead/SalvarInteracao"

API_BASE_URL = "https://integracao.autocerto.com"
API_OAUTH_PATH = "/oauth/token"
API_CAR_PATH = "/api/veiculo/obterEstoque"

API_USERNAME = "elleganceautomoveis@api.com"
API_PASSWORD = "yxlit*7ktTv"


BUY_QUESTIONS = [
    "Qual veículo você tem interesse em comprar?",
    "Você procura um carro 0km ou seminovo?",
    "Qual faixa de preço você está buscando?",
    "Prefere pagamento à vista, financiamento ou consórcio?",
    "Você já tem algum valor de entrada disponível?",
    "Qual a sua urgência para fechar a compra?",
    "Você gostaria de agendar uma visita ou test drive?",
    "Tem alguma cor ou versão específica em mente?",
    "Deseja receber fotos, vídeos ou a ficha técnica do veículo?",
    "Você gostaria que eu simulasse parcelas para o financiamento?",
]

TRADE_QUESTIONS = [
    "Você pretende dar um carro como parte do pagamento?",
    "Qual o modelo, ano e versão do seu veículo atual?",
    "Qual é a quilometragem aproximada?",
    "O carro já está quitado ou possui financiamento ativo?",
    "O documento (CRLV) está em dia?",
    "Qual é o estado geral do carro (pintura, pneus, motor)?",
    "Você já fez todas as revisões regulares?",
    "O veículo possui algum sinistro ou restrição?",
    "Qual valor você imagina receber nele?",
    "Gostaria de enviar fotos do seu carro para análise?",
]

