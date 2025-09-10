import random

from application.constants import BUY_QUESTIONS, TRADE_QUESTIONS
from domain.context import load_context, save_context
from domain.store import load_store
from infrastructure.autocerto import fetch_car_info


def build_draft(lead_id: str):
    ctx = load_context(lead_id)
    store_config = load_store("Ellegance")

    action = ctx.get("action", None) or must_answer()

    answer = None
    if action == "ANSWER":
        answer = generate_message(ctx)

    question = ask(ctx, store_config)
    return [answer, question]


def ask(ctx: dict, store_config: dict):
    intent = ctx["intent"]

    if intent is None:
        ctx["intent"] = intent = define_intent(ctx)

    question = define_next_question(ctx, intent)

    if not question:
        print("ACABOU")

    ctx = enrich_context(ctx)

    message = build_interaction(ctx, question)
    message = policy_guardrail(message, store_config)

    return message


def define_next_question(ctx: dict, intent: str):
    if intent == "BUY":
        question_list = BUY_QUESTIONS
    else:
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


def enrich_context(ctx: dict):
    if "car" in ctx:
        car = ctx["car"]

        if "autocerto" not in car:
            car["autocerto"] = fetch_car_info(car["plate"])
            save_context(ctx["lead"]["id"], car)

    return ctx

# avaliar, adicionar confianca, de modo que caso a confianca seja < 0.5, mandar pra um atendente de vdd?