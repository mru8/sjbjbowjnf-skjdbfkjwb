from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").json() == {"status": "ok"}

def test_forecast_uses_latest_edition_before_cutoff():
    body = client.get("/forecast", params={"day": "2026-01-15"}).json()
    assert len(body["hours"]) == 24
    assert {h["publishTime"] for h in body["hours"]} == {"2026-01-14T09:30:00+00:00"}

def test_forecast_for_day_without_data_is_404():
    assert client.get("/forecast", params={"day": "2026-03-01"}).status_code == 404

def test_invalid_cutoff_is_rejected():
    r = client.get("/forecast", params={"day": "2026-01-15", "cutoff": "25:99"})
    assert r.status_code == 422

def test_accuracy_for_january():
    body = client.get("/accuracy", params={"start": "2026-01-01", "end": "2026-01-31"}).json()
    assert body["summary"]["n_hours"] == 744
    assert body["summary"]["bias"] > 0

def test_accuracy_end_before_start_is_rejected():
    r = client.get("/accuracy", params={"start": "2026-01-31", "end": "2026-01-01"})
    assert r.status_code == 422