import json, os
from typing import List
from .models import Crop

#project relative paths.
DATA.DIR = os.path(os.path.dirname(os.path.dirname(__file__)), "data")
CROPS.FILE = os.path.join(DATA_DIR, "crops.json")
Settings.FILE = os.path.join(DATA_DIR, "settings.json")

#Default settings
DEFAULT_SETTINGS = {
    "weather_delay_days": 0
}

def ensure_files():
    #Ensure data directory and base files exist

    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CROPS_FILE): 
        with open(CROPS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
    if not os.path.exists(SETINGS_FILE): 
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=2)

def load_crops() -> List[Crop]:
    ensure_files()
    with open(CROPS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Crop.from_dict(x) for x in data]

def save_crops(crops: List[Crop]):
    ensure_files()
    with open(CROPS_FILE, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in crops], f, indent=2)

def load_settings() -> dict:
    ensure_files()
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    
def save_settings(settings: dict):
    ensure_files()
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

def export_to_csv(crops: List[Crop], csv_path: str):
    import csv
    with open(csv_path, "w", newline='', encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ID", "Name", "Planting Date", "Expected Harvest Date", "Status"])
        for c in crops:
            w.writerow([
                c.id,
                c.name,
                c.planting_date.isoformat() if c.planting_date else "",
                c.expected_harvest_date.isoformat(),
                c.status
            ])