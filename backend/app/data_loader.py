from functools import lru_cache

import pandas as pd

from app.config import PROCESSED_DIR

@lru_cache
def load_forecasts():
    df = pd.read_csv(PROCESSED_DIR / "forecasts.csv")
    df["publishTime"] = pd.to_datetime(df["publishTime"], utc=True)
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
    return df

@lru_cache
def load_actuals():
    df = pd.read_csv(PROCESSED_DIR / "actuals_hourly.csv")
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
    return df