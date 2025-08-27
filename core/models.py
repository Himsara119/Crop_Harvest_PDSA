from dataclasses import dataclass, asdict
from datetime import date
from typing import Optional

@dataclass
class Crop:
    id: str #Unique string.
    name: str
    planting_date: Optional[date] #can be unknown sometimes
    expected_harvest_date: date
    status: str = "Planted"

def to_dict(self):
    d = asdict(self)
    d["planting_date"] = (self.planting_date.isoformat()
                          if self.planting_date else None)
    d["expected_harvest_date"] = self.expected_harvest_date.isoformat()
    return d

@staticmethod
def from_dict(d: dict) -> "Crop":
    from datetime import date
    pd = date.fromisoformat(d["planting_date"]) if d.get("planting_date") else None
    hd = date.fromisoformat(d["expected_harvest_date"])
    return Crop(
        id=d["id"],
        name=d["name"],
        planting_date=pd,
        expected_harvest_date=hd,
        status=d.get("status", "Planted")
    )  