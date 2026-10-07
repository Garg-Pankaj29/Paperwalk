import json
import threading
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "data" / "state.json"
_lock = threading.Lock()


def _load() -> dict:
    if PATH.exists():
        try:
            return json.loads(PATH.read_text())
        except json.JSONDecodeError:
            pass
    return {"cards": {}}


def save_card(card: dict) -> None:
    with _lock:
        s = _load()
        s["cards"][card["id"]] = card
        PATH.parent.mkdir(exist_ok=True)
        PATH.write_text(json.dumps(s, indent=2))


def get_card(card_id: str) -> dict | None:
    with _lock:
        return _load()["cards"].get(card_id)
