from pathlib import Path
import json
from typing import Dict, Any

"""
Loads a store confirguration by its name
"""
def load_store(store: str) -> Dict[str, Any]:
    path = store_path(store)

    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return {}

"""
Builds a request store's file path
"""
def store_path(store: str) -> Path:
    base = Path("api/_store")
    base.mkdir(parents=True, exist_ok=True)

    return base / f"{store}.json"