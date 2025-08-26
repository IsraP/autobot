from __future__ import annotations

import requests
from bs4 import BeautifulSoup, Tag
from datetime import datetime, date, time
from typing import List, Optional, Tuple

from application.constants import TZ_SP
from domain.context import persist_leads
from domain.schemas import Lead, Car
from infrastructure.autocerto import get_leads_by_page


# ==============================
# High-level API
# ==============================

"""
Fetch HTML for a page of leads and return the parsed Lead objects.
"""
def fetch_leads(page: int, session: requests.Session) -> list[Lead]:
    page_html = get_leads_by_page(page, session)

    leads = parse_page(page_html)
    persist_leads(leads)

    return leads


"""
Parse all leads from a single HTML page.
"""
def parse_page(page_html: str) -> list[Lead]:
    soup = BeautifulSoup(page_html, "html.parser")
    base_day = parse_base_day(soup)

    leads: List[Lead] = []
    for block in soup.select('div.view-message[data-id]'):
        leads.append(extract_lead(block, base_day))
    return leads


# ==============================
# Lead extraction
# ==============================

"""
Extract one Lead from a 'view-message' block, handling both vehicle and birthday rows.
"""
def extract_lead(block: Tag, base_day: date) -> Lead:
    lead_id = block.get("data-id", "")

    client = extract_text(block, ".nomeClienteLead") or ""
    last_msg = extract_text(block, ".teorMensagem") or ""
    received_at, updated_at = extract_times(block, base_day)

    birthday = is_birthday_lead(block, last_msg)
    car: Optional[Car] = None if birthday else extract_car(block)

    return Lead(
        id=lead_id,
        client=client,
        last_client_message=last_msg,
        car=car,
        is_birthday=birthday,
        received_at=received_at or datetime.now(TZ_SP),
        updated_at=updated_at or (received_at or datetime.now(TZ_SP)),
    )


"""
Heuristics to decide if a lead row is actually a birthday reminder (no vehicle).
"""
def is_birthday_lead(block: Tag, last_msg: Optional[str]) -> bool:
    title   = extract_text(block, 'div[style*="padding: 3px 0"] .col-md-7 span[style*="font-weight"]')
    version = extract_text(block, ".VersaoVeiculoLead")
    midia   = extract_text(block, ".midiaLeadItem")
    msg     = (last_msg or "")

    tl = safe_lower(title)
    vl = safe_lower(version)
    ml = safe_lower(midia)
    ml_has_post_venda = "pós venda" in ml or "pos venda" in ml

    # Explicit signals only.
    if ("anivers" in tl) or ("anivers" in vl) or ("aniversário" in msg.lower()) or ("aniversario" in msg.lower()):
        return True

    # Common UI pattern: Pós Venda + 'Aniversariante'/'do dia'
    if ml_has_post_venda and (("anivers" in tl) or ("anivers" in vl) or ("do dia" in vl)):
        return True



"""
Extract the Car info inside a lead block. Returns None if we cannot find a valid car.
"""
def extract_car(block: Tag) -> Optional[Car]:
    name = extract_text_any(block, [
        'div[style*="padding: 3px 0"] .col-md-7 span[style*="font-weight"]',  # classic layout
        'div[style*="padding: 3px 0"] span[style*="font-weight"]',            # no .col-md-7 (e.g., "Seminovos")
    ])

    model = extract_text(block, ".VersaoVeiculoLead")

    if not (name or model):
        return None

    ln = (name or "").lower()
    lm = (model or "").lower()
    if any(term in ln for term in ("aniversáriante", "aniversariante")) or lm == "do dia":
        return None

    plate, year, price_opt = extract_extra(block)

    return Car(
        name=name or "",
        model=model or "",
        year=year,
        plate=plate,
        price=price_opt,
    )


"""
Extract (plate, year, price) from the right column within the vehicle row.
"""
def extract_extra(block: Tag) -> Tuple[Optional[str], Optional[str], Optional[float]]:
    right = block.select_one('div[style*="padding: 3px 0"] .col-md-5')
    if not right:
        return None, None, None

    items = right.select("small.itemVeiculoLead")
    plate_tag = items[0] if len(items) >= 1 else None
    year_tag = items[1] if len(items) >= 2 else None
    price_tag = right.select_one("small.precoVeiculoLead")

    plate = plate_tag.get_text(strip=True) if plate_tag else None
    year = year_tag.get_text(strip=True) if year_tag else None
    price = parse_price(price_tag.get_text(strip=True)) if price_tag else None

    return plate, year, price


"""
Extract (received_at, updated_at) from the footer row (.dataLead spans).
"""
def extract_times(block: Tag, base_day: date) -> Tuple[Optional[datetime], Optional[datetime]]:
    spans = block.select("span.dataLead")
    received = parse_dt(spans[0].get_text(strip=True), base_day) if len(spans) >= 1 else None
    updated = parse_dt(spans[1].get_text(strip=True), base_day) if len(spans) >= 2 else None
    return received, updated


# ==============================
# Tiny utilities
# ==============================

"""
Return normalized text from the first element matched by a given set of selectors (or default None).
"""
def extract_text_any(block: Tag, selectors: list[str]) -> Optional[str]:
    for sel in selectors:
        txt = extract_text(block, sel)
        if txt:
            return txt
    return None

"""
Return normalized text from the first element matched by selector (or default None).
"""
def extract_text(block: Tag, selector: str, join_with: str = " ") -> Optional[str]:
    element = block.select_one(selector)
    if not element:
        return None
    return " ".join(element.get_text(join_with, strip=True).split())



def safe_lower(s: Optional[str]) -> str:
    return s.lower() if isinstance(s, str) else ""


# ==============================
# Parsing helpers (dates, price)
# ==============================

"""
Read 'Leads recebidos no dia: DD/MM/YYYY' (inside #tabDia .actions) and return that date.
Fallback to 'today' in São Paulo if not present.
"""
def parse_base_day(soup: BeautifulSoup) -> date:
    actions = soup.select_one('#tabDia .actions')
    if actions:
        txt = actions.get_text(strip=True)
        for fmt in ("%d/%m/%Y", "%d/%m/%y"):
            try:
                return datetime.strptime(txt, fmt).date()
            except ValueError:
                pass
    return datetime.now(TZ_SP).date()


"""
Convert 'R$ 54.900,00' -> 54900.0 (or None if unparseable).
"""
def parse_price(brl_text: str) -> Optional[float]:
    if not brl_text:
        return None
    s = (
        brl_text.replace("R$", "")
        .replace(".", "")
        .replace(" ", "")
        .replace("\xa0", "")
        .replace(",", ".")
    )
    try:
        return float(s)
    except ValueError:
        return None


"""
Parse date/time strings like:
  - 'HOJE HH:MM'
  - 'DD/MM HH:MM'   (year injected from base_day)
  - 'DD/MM/YYYY HH:MM' (or YY)
Return timezone-aware datetime in America/Sao_Paulo (or None).
"""
def parse_dt(text: str, base_day: date) -> Optional[datetime]:
    if not text:
        return None

    t = text.strip().upper()

    if t.startswith("HOJE"):
        parts = t.split()
        if len(parts) >= 2:
            try:
                hh, mm = parts[1].split(":")
                return datetime.combine(base_day, time(int(hh), int(mm), tzinfo=TZ_SP))
            except Exception:
                return None
        return None

    try:
        partial = datetime.strptime(t, "%d/%m %H:%M")
        return datetime(
            base_day.year, partial.month, partial.day,
            partial.hour, partial.minute, tzinfo=TZ_SP
        )
    except ValueError:
        pass

    for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%y %H:%M"):
        try:
            dt = datetime.strptime(t, fmt)
            return dt.replace(tzinfo=TZ_SP)
        except ValueError:
            continue

    return None
