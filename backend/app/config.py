from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BACKEND_DIR / "data" / "processed"
DEFAULT_CUTOFF = "09:50" #uk local time on the day before delivery
