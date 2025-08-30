from datetime import timedelta, date
from typing import Dict, List, Optional
from ds.min_heap import MinHeap
from features.crops.models import Crop

class HarvestScheduler:
    def __init__(self, crops: List[Crop], weather_delay_days: int = 0) -> None:
        self.weather_delay_days = int(weather_delay_days or 0)
        self.heap: MinHeap[date, str] = MinHeap()
        self._by_id: Dict[str, Crop] = {c.id: c for c in crops}
        self.rebuild()

    def set_weather_delay(self, days: int) -> None:
        self.weather_delay_days = int(days or 0)
        self.rebuild()

    def _adjusted(self, c:Crop) -> date:
        return c.expected_harvest_date + timedelta(days=self.weather_delay_days)
    
    def rebuild(self) -> None:
        self.heap = MinHeap()
        for c in self._by_id.values():
            if c.status != "Harvested":
                self.heap.push(self._adjusted(c), c.id)

    def add_crop(self, crop: Crop) -> None:
        self._by_id[crop.id] = crop
        if crop.status != "Harvested":
            self.heap.push(self._adjusted(crop), crop.id)

    def remove_crop(self, crop_id: str) -> None:
        if crop_id in self._by_id:
            self._by_id[crop_id].status = "Harvested"
        self.rebuild()

    def next_to_harvest(self) -> Optional[Crop]:
        cid = self._heap.peek_value()
        return self._by_id.get(cid) if cid else None
    
    def list_ordered(self) -> List[Crop]:
        #temp heap
        tmp = MiHeap[date, str]()
        for c in self._by_id.values():
            if c.status != "Harvested":
                tmp.push(self._adjusted(c), c.id)
            out: List[Crop] = []
            while len(tmp) > 0:
                pair = tmp.pop()
                if not pair:
                    break
                _, cid = pair
                cc = self._by_id.get(cid)
                if cc and cc.status != "Harvested":
                    out.append(cc)
                return out