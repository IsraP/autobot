import re
from typing import List, Optional

import requests
from bs4 import BeautifulSoup, Tag
from datetime import time

from application.constants import TZ_SP
from domain.context import persist_interactions
from domain.schemas import Interaction, InteractionOrigin
from infrastructure.autocerto import get_interactions_by_lead

tz = TZ_SP

"""
Fetch HTML for a page of leads and return the parsed Lead objects.
"""
def fetch_interactions(lead_id: str, session: requests.Session):
    page_html = get_interactions_by_lead(lead_id, session)

    interactions = parse_interactions(page_html)
    persist_interactions(lead_id, interactions)

    return interactions


"""
Parse all user-facing interactions (client/store) from a lead details HTML.
"""
def parse_interactions(html: str) -> List[Interaction]:
    soup = BeautifulSoup(html, "html.parser")
    interactions: List[Interaction] = []

    for block in find_message_blocks(soup):

        origin = classify_origin(block)
        content = extract_text(block, ".interacaoTeor") or ""
        sent_at = extract_time(block)

        interactions.append(
            Interaction(
                origin=origin,
                sent_at=sent_at,
                content=content,
            )
        )

    return interactions


# ==============================
# Extraction helpers
# ==============================

"""
Return all message blocks that belong to client or store.
"""
def find_message_blocks(soup: BeautifulSoup) -> List[Tag]:
    return list(soup.select(".interacaoClienteMessenger, .interacaoLojaMessenger"))



"""
Classify a message block as CLIENT or STORE based on its class.
"""
def classify_origin(block) -> InteractionOrigin:
    classes = set(block.get("class", []))
    return InteractionOrigin.CLIENT if "interacaoClienteMessenger" in classes else InteractionOrigin.STORE




"""
Extract normalized text from the first element matching selector.
"""
def extract_text(root, selector: str) -> Optional[str]:
    el = root.select_one(selector)
    if not el:
        return None
    return normalize_whitespace(el.get_text(" ", strip=True))




"""
Extract a timezone-aware datetime from a block using the displayed HH:MM.
Falls back to midnight if HH:MM is missing.
"""
def extract_time(block) -> Optional[time]:
    txt = extract_text(block, ".interacaoHorario")
    if not txt:
        return None

    m = re.search(r"(\d{2}):(\d{2})", txt)
    if not m:
        return None

    hh, mm = int(m.group(1)), int(m.group(2))
    return time(hh, mm)


# ==============================
# Tiny utilities
# ==============================

"""
Collapse internal whitespace to single spaces.
"""
def normalize_whitespace(s: str) -> str:
    return " ".join(s.split())