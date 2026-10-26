"""Download WINDFOR (forecasts) and FUELHH WIND (actuals) from Elexon
and save the raw JSON to backend/data/raw so we only hit the API once.

Run from the backend folder: python scripts/fetch_data.py"""
import json
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

BASE = "https://data.elexon.co.uk/bmrs/api/v1/datasets"
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def get_json(url, params):
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()  # stops with a clear error on 400/429/500
    return resp.json()


def fetch_actuals(start, end):
    """FUELHH, wind only, filtered by settlement date (both ends inclusive)."""
    path = RAW_DIR / f"fuelhh_wind_{start}_{end}.json"
    if path.exists():
        print("skip", path.name)
        return
    params = {
        "settlementDateFrom": start.isoformat(),
        "settlementDateTo": end.isoformat(),
        "fuelType": "WIND",
    }
    rows = get_json(f"{BASE}/FUELHH/stream", params)
    path.write_text(json.dumps(rows))
    print("saved", path.name, len(rows), "rows")


def fetch_forecasts_for_day(day):
    """WINDFOR, all forecast runs published during one UTC day."""
    path = RAW_DIR / f"windfor_{day}.json"
    if path.exists():
        print("skip", path.name)
        return
    start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    params = {
        "publishDateTimeFrom": start.strftime(fmt),
        "publishDateTimeTo": end.strftime(fmt),
    }
    rows = get_json(f"{BASE}/WINDFOR/stream", params)
    path.write_text(json.dumps(rows))
    print("saved", path.name, len(rows), "rows")
    time.sleep(0.5)  # be polite, avoids 429 too-many-requests


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Actuals: January 2026, plus 1 Feb in case we use the
    # "decision made in January" reading of the brief.
    fetch_actuals(date(2026, 1, 1), date(2026, 2, 1))

    # Forecasts: a few days of December buffer, then all of January.
    day = date(2025, 12, 29)
    while day <= date(2026, 1, 31):
        fetch_forecasts_for_day(day)
        day += timedelta(days=1)


if __name__ == "__main__":
    main()