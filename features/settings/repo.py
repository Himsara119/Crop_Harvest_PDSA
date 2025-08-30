import os, json
from json import JSONDecodeError

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
DEFAULTS = {"weather_delay_days": 0}

def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_settings() -> dict:
    _ensure_dir()
    try:
        if not os.path.exists(SETTINGS_FILE):
            save_settings(DEFAULTS)
            return dict(DEFAULTS)
        raw = open(SETTINGS_FILE, "r", encoding="utf-8").read().strip()
        if not raw:
            save_settings(DEFAULTS)
            return dict(DEFAULTS)
        data = json.loads(raw)
        if not isinstance(data, dict):
            save_settings(DEFAULTS)
            return dict(DEFAULTS)
        healed = {**DEFAULTS, **data}
        save_settings(healed)
        return healed
    except (OSError, JSONDecodeError):
        save_settings(DEFAULTS)
        return dict(DEFAULTS)
    
def save_settings(obj: dict) -> None:
    _ensure_dir()
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)