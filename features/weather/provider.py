from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import datetime as dt

try:
    import requests
except Exception:
    requests = None

@dataclass
class WeatherResult:
    delay_days: int
    reason: None

class WeatherProvider:
    def compute_delay(self) -> WeatherResult:
        raise NotImplementedError
    
class OfflineHeuristicProvider(WeatherProvider):
    def compute_delay(self) -> WeatherResult:
        m = dt.date.today().month
        heavy = {5, 10, 11}
        moderate = {4, 9, 12}
        if m in heavy:
            return WeatherResult(3, f"offline rule: heavy rain month {m}")
        if m in moderate:
            return WeatherResult(2, f"offline rule: moderate rain month {m}")
        return WeatherResult(0, f"offline rule: fair month {m}")
    
class OpenMeteoProvider(WeatherProvider):
    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon

    def compute_delay(self) -> WeatherResult:
        if requests is None:
            return WeatherResult(0, "requests not available")
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={self.lon}&longitude={self.lon}"
            "&daily=precipitation_sum"
            "&timezone=auto"
        )
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            data = r.json()
            sums = data.get("daily", {}).get("precipitation_sum", [])
            total = sum(x for x in sums if isinstance(x, (int, float)))
            if total > 60:
                return WeatherResult(4, f"precip over 5d = {total: .1f}mm")
            if total > 30:
                return WeatherResult(2, f"precip over 5d = {total: .1f}mm")
            return WeatherResult(0, f"precip over 5d = {total: .1f}mm")
        except Exception as e:
            return WeatherResult(0, f"fetch failed: {e.__class__.__name__}")
        