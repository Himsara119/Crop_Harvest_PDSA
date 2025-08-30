#Min-Heap to adjust harvest dates
#adjust = expected harvest date +  weather delays

import heapq
from datetime import timedelta, date
from typing import List, Tuple
from .models import Crop

class HarvestScheduler:

    #min heap adjusted
    #heap adjusted with weather delays
    #add/remove crops in order MIN _ HEAP
    #ordered min heap view for table

    def __init__(self, crops: List[Crop], weather_delay_days: int = 0):
        self.weather_delay_days = int(weather_delay_days or 0)
        self.heap: List[Tuple[date, str]] = [] # (adjusted_harvest_date, crop_name)
        self._id_to_crop = {c.id: c for c in crops}
        self.rebuild_heap()

    def set_weather_delay(self, days: int):
        #update delay and rebuild heap
        self.weather_delay_days = int(days or 0)
        self.rebuild_heap()

    def rebuild_heap(self):
        #since simple heap, we clear re push all non harvested crops with fresh adjusted dates.
        self.heap.clear()
        for c in self._id_to_crop.values():
            if c.status != "Harvested":
                adj = c.expected_harvest_date + timedelta(days=self.weather_delay_days)
                heapq.heappush(self.heap, (adj, crop.id))

    def add_crop(self, crop: Crop):
        #insert new crop and push to heap
        self._id_to_crop[crop.id] = crop
        adj = crop.expected_harvest_date + timedelta(days=self.weather_delay_days)
        heapq.heappush(self.heap, (adj, crop.id))

    def remove_crop(self, crop_id: str):
        #soft delet to harvested crops
        #easiest to avoid tricky heap deletions

        if crop_id in self._id_to_crop:
            self._id_to_crop[crop_id].status = "Harvested"
        self.rebuild_heap()

    def next_to_harvest(self) -> Crop | None:
        #peek at next crop to harvest
        while self.heap:
            adj, cid = heapq.heappop(self.heap)
            c = self._id_to_crop.get(cid)
            if c and c.status != "Harvested":
                #push it back
                heapq.heappush(self.heap, (adj, cid))
                return c
        return None
    
    def list_ordered(self) -> List[Crop]:
        #ordered heap with adjusted date is taken
        #create a temporary heap so the ui can render a stable view

        tmp = list(self.heap)
        heapq.heapify(tmp)
        ordered =  []
        seen = set()
        while tmp:
            adj, cid = heapq.heappop(tmp)
            if cid in seen:
                continue
            c = self._id_to_crop.get(cid)
            if c and c.status != "Harvested":
                ordered.append(c)
                seen.add(cid)
            return ordered