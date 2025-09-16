import json
import random
from datetime import datetime, time
from typing import Dict, Any

from langchain_community.chat_models import ChatOllama

from application.constants import BUY_QUESTIONS, TRADE_QUESTIONS, INTERACTION_PROMPT, INTENT_PROMPT, INTERACTION_PROMPT_ASK
from domain.context import load_context, save_context
from domain.schemas import Interaction, InteractionOrigin
from domain.store import load_store

def get_llm():
    return ChatOllama(
        model="gpt-oss:20b",
        model_kwargs={
            "thinking": False
        }
    )


def build_draft(lead_id: str):
    ctx = load_context(lead_id)
    store_config = load_store("Ellegance")

    #action = ctx.get("action", None) or must_answer(ctx)

    # answer_interaction = None
    # if action == "ANSWER":
    #     answer_interaction = answer(ctx)

    question_interaction = ask(ctx, store_config)
    return [question_interaction]



def must_answer(ctx: dict) -> str:
    interactions = ctx.get("interactions") or []
    if not interactions:
        return "ASK"

    last = interactions[-1]
    origin = (last.get("origin") or "").strip().upper()

    if origin == "CLIENT":
        return "ANSWER"

    return "ASK"



def answer(ctx: dict) -> Interaction:
    current_ctx = enrich_context(ctx)

    content = generate_message(current_ctx)

    message = build_interaction(content)

    return message



def define_next_question(ctx: dict, intent: str):
    if intent == "BUY":
        question_list = BUY_QUESTIONS
    else :
        question_list = TRADE_QUESTIONS

    answered_questions = ctx.get("answered_questions", [])
    possible_questions = list(set(question_list) - set(answered_questions))

    if not possible_questions:
        return False

    next_question = random.choice(possible_questions)

    answered_questions.append(next_question)
    ctx["answered_questions"] = answered_questions
    save_context(ctx["lead"]["id"], ctx)

    return next_question



def ask(ctx: dict, store_config: dict) -> Interaction:
    intent = ctx.get("intent")

    if intent is None:
        ctx["intent"] = intent = define_intent(ctx)

    question = define_next_question(ctx, intent)

    if not question:
        print("ACABOU")

    current_ctx = enrich_context(ctx)
    content = generate_message_ask(current_ctx,question)

    message = build_interaction(content)
    # message = policy_guardrail(message, store_config)

    return message


def enrich_context(ctx: dict):
    car = ctx.get("car") or {}
    ac = ctx.get("autocerto") or {}

    store_ctx = {
        "nome": "Ellegance Automoveis"
    }

    car_ctx = {
        "nome": car.get("name") or f"{ac.get('brand', '')} {ac.get('model', '')}".strip(),
        "versao": car.get("model") or ac.get("version"),
        "ano": car.get("year") or f"{ac.get('manufacture_year')}/{ac.get('model_year')}",
        "preco": car.get("price") or ac.get("price"),
        "km": ac.get("mileage"),
        "cambio": ac.get("transmission"),
        "combustivel": ac.get("fuel"),
        "cor": ac.get("color"),
        "placa": ac.get("plate") or car.get("plate"),
        "itens": [f.get("description") for f in (ac.get("features") or [])],
        "observacoes": ac.get("notes"),
        "loja": "Ellegance Automóveis"
    }

    interaction_ctx = ctx["interactions"]

    return { "loja": store_ctx, "carro desejado pelo cliente": car_ctx, "conversa": interaction_ctx }


def define_intent(ctx: dict) -> str:
    llm = get_llm()
    system_msg = INTENT_PROMPT.format(json.dumps(ctx["interactions"], ensure_ascii=False, indent=2))

    
    resposta = llm.invoke(system_msg)
    print(resposta)
    return (getattr(resposta, "content", "") or "").strip()



def generate_message(ctx: Dict[str, Any], question):
    llm = get_llm()

    system_msg = INTERACTION_PROMPT.format(ctx["loja"]["nome"],question, json.dumps(ctx, ensure_ascii=False, indent=2))

    resposta = llm.invoke(system_msg)

    return (getattr(resposta, "content", None) or "").strip()

def generate_message_ask(ctx: Dict[str, Any], question):
    llm = get_llm()

    system_msg = INTERACTION_PROMPT_ASK.format(ctx["loja"]["nome"],question, json.dumps(ctx, ensure_ascii=False, indent=2))

    resposta = llm.invoke(system_msg)

    return (getattr(resposta, "content", None) or "").strip()

def build_interaction(message: str):
    return Interaction(
                origin=InteractionOrigin.STORE,
                sent_at=datetime.now().time(),
                content=message,
            )