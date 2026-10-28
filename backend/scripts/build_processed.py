"""Turn the raw Elexon JSON into two small CSV files that the API loads.

Run from the backend folder: python -m scripts.build processed
"""

import json
from pathlib import Path

import pandas as pd

from app.actuals import to_hourly

BACKEND = Path(__file__).resolve().parents[1]
RAW = BACKEND / "data" / "raw"
OUT = BACKEND / "data" / "processed"

def load(pattern):
    rows = []
    for f in sorted(RAW.glob(pattern)):
        rows.extend(json.loads(f.read_text()))
    return pd.DataFrame(rows)

def main():
    OUT.mkdir(parents=True, exist_ok=True)

    forecasts = load("windfor_*.json")
    forecasts["publishTime"] = pd.to_datetime(forecasts["publishTime"], utc=True)
    forecasts["startTime"] = pd.to_datetime(forecasts["startTime"], utc=True)
    forecasts = (
        forecasts.drop_duplicates(["publishTime", "startTime"], keep="last")
        [["publishTime", "startTime", "generation"]]
        .sort_values(["startTime", "publishTime"])
    )
    forecasts.to_csv(OUT / "forecasts.csv", index=False)

    actuals = load("fuelhh_wind_*.json")
    actuals["startTime"] = pd.to_datetime(actuals["startTime"], utc=True)
    hourly = to_hourly(actuals)
    hourly.to_csv(OUT / "actuals_hourly.csv", index=False)

    print("forecasts.csv:", len(forecasts), "rows")
    print("actuals_hourly.csv", len(hourly), "rows")

if __name__ == "__main__":
    main()