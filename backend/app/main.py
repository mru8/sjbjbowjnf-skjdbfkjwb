import os

from fastapi.middleware.cors import CORSMiddleware

from datetime import date

import pandas as pd
from fastapi import FastAPI, HTTPException, Query

from app.config import DEFAULT_CUTOFF
from app.data_loader import load_actuals, load_forecasts
from app.metrics import build_comparison, summarise
from app.selection import select_forecast_at_cutoff

CUTOFF_PATTERN = r"^([01]\d|2[0-3]):[0-5]\d$" #HH:MM , 24 hr clock

app = FastAPI(title="Wind forecast reliability")
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['GET'])

def day_window(first_day, last_day):
    """UTC timestamps covering first_day 00:00 up to the end of the last_day"""
    lo = pd.Timestamp(first_day, tz="UTC")
    hi = pd.Timestamp(last_day, tz="UTC") + pd.Timedelta(days=1)
    return lo, hi

@app.get("/health")
def health():
    return {"status" : "ok"}

@app.get("/forecast")
def forecast(day: date, cutoff:str = Query(DEFAULT_CUTOFF, pattern=CUTOFF_PATTERN)):
    """The forecast the buyer had at the cutoff for each hour of one delivery day,
    with the actual alongside (null where no actual exists)."""
    selected = select_forecast_at_cutoff(load_forecasts(), cutoff)
    lo, hi = day_window(day, day)
    rows = selected[(selected["startTime"] >= lo) & (selected["startTime"] < hi)]
    if rows.empty:
        raise HTTPException(status_code=404, detail=f"No forecast available for {day}")

    merged = rows.rename(columns={"generation": "forecast"}).merge(
        load_actuals(), on="startTime", how="left"
    )
    return {
        "day": day.isoformat(),
        "cutoff": cutoff,
        "hours": [
            {
                "startTime": r.startTime.isoformat(),
                "publishTime": r.publishTime.isoformat(),
                "forecast": float(r.forecast),
                "actual": None if pd.isna(r.actual) else float(r.actual),
            }
            for r in merged.itertuples()
        ],
    }

@app.get("/accuracy")
def accuracy(start: date, end: date, cutoff: str = Query(DEFAULT_CUTOFF, pattern=CUTOFF_PATTERN)):
    """Accuracy of the forecasts the buyer had at the cutoff, over delivery days start..end."""
    if end < start:
        raise HTTPException(status_code=422, detail="end must not be before start")

    selected = select_forecast_at_cutoff(load_forecasts(), cutoff)
    comparison = build_comparison(selected, load_actuals())
    lo, hi = day_window(start, end)
    window = comparison[(comparison["startTime"] >= lo) & (comparison["startTime"] < hi)]
    if window.empty:
        raise HTTPException(status_code=404, detail="No data in that range")

    by_hour = (
        window.groupby(window["startTime"].dt.hour)
        .agg(mae=("abs_error", "mean"), bias=("error", "mean"))
        .reset_index()
        .rename(columns={"startTime": "hour"})
    )
    return {
        "cutoff": cutoff,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "summary": summarise(window),
        "by_hour": [
            {"hour": int(r.hour), "mae": float(r.mae), "bias": float(r.bias)}
            for r in by_hour.itertuples()
        ],
    }