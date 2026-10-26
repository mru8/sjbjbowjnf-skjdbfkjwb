
import json
from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"

files = sorted(RAW.glob("windfor_*.json"))

frames = []

for file in files:
    rows = json.loads(file.read_text(encoding="utf-8"))
    frames.append(pd.DataFrame(rows))

df = pd.concat(frames, ignore_index=True)

df["publishTime"] = pd.to_datetime(df["publishTime"], utc=True)
df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
df = df.sort_values(["publishTime", "startTime"])

print("Files loaded:", len(files))
print("Combined shape:", df.shape)

# 1. Distinct forecast runs per publication date
runs = df[["publishTime"]].drop_duplicates().copy()
runs["publishDate"] = runs["publishTime"].dt.date

print("\n1. Forecast runs per publication date:")
print(runs.groupby("publishDate")["publishTime"].nunique().to_string())

# 2. Delivery horizon covered by each forecast run
horizons = df.groupby("publishTime")["startTime"].agg(
    first_delivery="min",
    last_delivery="max",
    delivery_hours="nunique",
)

horizons["hours_ahead_first"] = (
    horizons["first_delivery"] - horizons.index
).dt.total_seconds() / 3600

horizons["hours_ahead_last"] = (
    horizons["last_delivery"] - horizons.index
).dt.total_seconds() / 3600

print("\n2. Forecast horizon per run (first 10 runs):")
print(horizons.head(10).to_string())

print("\nHorizon summary:")
print(horizons[["hours_ahead_first", "hours_ahead_last",
                "delivery_hours"]].describe().to_string())

# 3. Delivery times at minute :30
half_hour = df[df["startTime"].dt.minute == 30]

print("\n3. Rows with startTime at :30:", len(half_hour))
if not half_hour.empty:
    print(half_hour["startTime"].head(10).to_string(index=False))

# 4. Forecast records per delivery hour
counts = df.groupby("startTime").size()

print("\n4. Records per delivery hour:")
print(counts.describe().to_string())
print("Delivery hours with multiple records:", int((counts > 1).sum()))
print("Maximum records for one delivery hour:", int(counts.max()))

print("\nMost repeated delivery hours:")
print(counts[counts > 1].sort_values(ascending=False).head(10).to_string())

# Check exact duplicate rows
print("\nExact duplicate rows:", int(df.duplicated().sum()))
