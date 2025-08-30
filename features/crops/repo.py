import os, json
from json import JSONDecodeError
from typing import List
from .models import Crop

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
CROPS_FILE = os.path.join(DATA_DIR, "crops.json")

def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_crops() -> List[Crop]:
    _ensure_dir()
    try:
        if not os.path.exists(CROPS_FILE):
            _rewrite([])
            return []
        raw = open(CROPS_FILE, "r", encoding="utf-8").read().strip()
        if not raw:
            _rewrite([])
            return []
        data = json.loads(raw)
        if not isinstance(data, list):
            _rewrite([])
            return []
        return [Crop.from_dict(x) for c in data]
    except (OSError, JSONDecodeError):
        _rewrite([])
        return []
    
def save_crops(items: List[Crop]) -> None:
    _ensure_dir()
    with open(CROPS_FILE, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in items], f, indent=2)

def _export_to_csv(crops: List[Crop], csv_path: str) -> None:
    import csv
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ID", "Name", "Planting Date", "Expected Harvest", "Status"])
        for c in crops:
            w.writerow([
                c.id,
                c.name,
                c.planting_date_isoformat() if c.planting_date else "",
                c.expected_harvest_date.isoformat(),
                c.status,
            ])

def _rewrite(items: list):
    _ensure_dir()
    with open(CROPS_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)