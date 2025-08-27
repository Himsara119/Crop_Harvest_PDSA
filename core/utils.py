#helpers for coding

from datetime import date

def iso_to_date(s: str):  #Y-M-D into date object
    return date.fromisoformat(s)
    
def date_to_iso(d:date) -> str: # data object into Y-M-D
    return d.isoformat()

def days_until(target: date, today: date | None = None) -> int:
    #today to target date count of days
    if today is None:
        today = date.today()
    return (target - today).days