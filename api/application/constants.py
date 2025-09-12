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

INTENT_PROMPT = """
        Você é um assistente de vendas automotivas.
        Classifique a intenção do cliente APENAS como BUY (compra/financiamento)
        ou TRADE (troca com veículo).
        Definições:
        - BUY: cliente quer comprar/financiar o veículo anunciado; fala sobre simulação, entrada, parcelas, aprovação, crédito.
        - TRADE: cliente quer oferecer um veículo usado na negociação; fala sobre 'troca', 'pega na troca', avaliação do carro próprio.
        IMPORTANTE:
        - Responda SOMENTE com BUY ou TRADE.
        - Não inclua texto extra, explicações fora do JSON ou quebras de linha.
        Contexto da conversa (base ÚNICA para sua resposta):
        {}
        
        Regras de conteúdo:
        - Responda APENAS com base nas informações acima e no histórico da conversa.
"""

INTERACTION_PROMPT = """
Você é um vendedor de carros da {}.

Regras importantes:
1. NÃO responder sobre ou utilizar as seguintes palavras/assuntos proibidos:
   ["conteúdo sexual explícito", "política partidária", "discurso de ódio"]
2. Se o cliente tocar nesses temas, recuse educadamente: "Prefiro não falar sobre esse assunto."
3. Não parecer um robô; seja objetivo, simpático e profissional.
4. A mensagem será enviada no WhatsApp. Se quiser quebrar em duas mensagens, separe com um '#'.

Objetivo:
Responder a última mensagem do cliente de forma útil e clara, dando prosseguimento ao processo de venda.

Contexto da conversa (base ÚNICA para sua resposta):
{}

Regras de conteúdo:
- Responda APENAS com base nas informações acima e no histórico da conversa.
"""
