from __future__ import annotations

import json
import os
from datetime import datetime, date, time
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from domain.schemas import Interaction, Lead

# ==============================
# High-level API
# ==============================

"""
Initiates or complements all lead contexts for a list of leads
"""
def persist_leads(leads: List[Lead]):
    for lead in leads:
        lead_ctx = load_context(lead.id)

        if not should_process(lead.updated_at, lead_ctx.get("updated_at")):
            continue

        if lead.is_birthday:
            lead_ctx["is_birthday"] = True
        else:
            lead_ctx["car"] = lead.car.model_dump(mode="json")

        lead_ctx["client"] = lead.client
        lead_ctx["updated_at"] = lead.updated_at

        save_context(lead.id, lead_ctx)

"""
Persist the interactions array under the "interactions" key.
"""
def persist_interactions(lead_id: str, interactions: List[Interaction]) -> None:
    ctx = load_context(lead_id)

    ctx["interactions"] = [it.model_dump(mode="json") for it in interactions]

    save_context(lead_id, ctx)


# ==============================
# Paths & I/O
# ==============================

"""
Return the JSON file path for a lead's context.
"""
def context_path(lead_id: str) -> Path:
    base = Path("api/_context")
    base.mkdir(parents=True, exist_ok=True)

    return base / f"{lead_id}.json"


"""
Read and parse a lead's context JSON.
Returns an empty dict if the file doesn't exist or is invalid.
"""
def load_context(lead_id: str) -> Dict[str, Any]:
    path = context_path(lead_id)

    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return {}


"""
Write a context dict atomically to disk.
"""
def save_context(lead_id: str, data: Dict[str, Any]) -> None:
    path = context_path(lead_id)
    tmp_path = path.with_suffix(".json.tmp")

    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=default_encoder)

    os.replace(tmp_path, path)



# ==============================
# Generic key operations
# ==============================

"""
Get a key from the context, with optional default.
"""
def get_context_key(lead_id: str, key: str, default: Any = None) -> Any:
    ctx = load_context(lead_id)

    return ctx.get(key, default)


"""
Add or replace a single key in the context.
"""
def set_context_key(lead_id: str, key: str, value: Any) -> None:
    ctx = load_context(lead_id)
    ctx[key] = value

    save_context(lead_id, ctx)


"""
Update multiple keys at once (merge).
"""
def update_context(lead_id: str, **kwargs: Any) -> None:
    ctx = load_context(lead_id)
    ctx.update(kwargs)

    save_context(lead_id, ctx)


"""
Delete a key from the context (no-op if missing).
"""
def delete_context_key(lead_id: str, key: str) -> None:
    ctx = load_context(lead_id)
    if key in ctx:
        del ctx[key]
        save_context(lead_id, ctx)


# ==============================
# Optional helpers
# ==============================


def should_process(lead_updated_at: datetime, persisted_updated_at: str) -> bool:
    return str(persisted_updated_at) != str(lead_updated_at)

"""
Append new interactions to the context (dedup by `id` if present).
"""
def append_interactions(lead_id: str, interactions: List[Interaction]) -> None:
    ctx = load_context(lead_id)
    existing = ctx.get("interactions", [])

    existing_ids = {i.get("id") for i in existing if isinstance(i, dict) and "id" in i}

    new_serialized = []
    for it in interactions:
        d = it.model_dump(mode="json")
        if d.get("id") not in existing_ids:
            new_serialized.append(d)

    if new_serialized:
        ctx["interactions"] = existing + new_serialized
        save_context(lead_id, ctx)



"""
Helps with encoding non primitive data types
"""
def default_encoder(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, time):
        return obj.strftime("%H:%M")   # if you want time-only like “08:11”
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, Path):
        return str(obj)
    # Let json raise if it truly can't handle something else:
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")