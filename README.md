# Wind forecast reliability for day-ahead buying

A small web app for a UK energy supplier that buys day-ahead power. It shows the latest wind forecast that was available when the buyer had to decide, and measures how accurate those forecasts were for decisions made in January 2026.

**Live app:** https://frontend-one-bay-9wrqooinhc.vercel.app/
**API:** https://sjbjbowjnf-skjdbfkjwb.onrender.com/health

The API runs on a free tier and sleeps when idle, so the first load can take up to a minute.

## How to run

With Docker (from the project root):

    docker compose up --build

Then open http://localhost:5173. The API is on http://localhost:8000.

Without Docker, in two terminals.

Backend (from `backend`):

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload

Frontend (from `frontend`):

    npm install
    npm run dev

The frontend reads the API address from `VITE_API_URL` in `frontend/.env` (default `http://localhost:8000`). The backend allows browser requests from the origins listed in the `ALLOWED_ORIGINS` environment variable (default `http://localhost:5173`).

Tests: from `backend`, run `pytest` (22 tests).

## Files and folders

    docker-compose.yml          runs backend and frontend together
    .github/workflows/ci.yml    runs the backend tests on every push
    backend/
      Dockerfile, .dockerignore, requirements.txt, pytest.ini
      app/
        main.py                 FastAPI routes: /health, /forecast, /accuracy
        config.py               paths and the default cutoff (09:50)
        data_loader.py          loads the processed CSV files
        selection.py            picks the forecast the buyer had at the cutoff
        actuals.py              turns half-hourly actuals into hourly values
        metrics.py              forecast vs actual comparison, MAE, RMSE, bias, P95
      scripts/
        fetch_data.py           downloads raw WINDFOR and FUELHH data from Elexon
        build_processed.py      builds the two CSV files the API reads
        explore.py              scratch exploration of the raw data
      data/raw, data/processed  downloaded JSON and the CSV files the API loads
      tests/                    pytest tests for selection, actuals, metrics and the API
    frontend/
      Dockerfile, nginx.conf    builds the React app and serves it with nginx
      vercel.json               sends every address to index.html (needed for /accuracy)
      src/
        main.jsx, App.jsx       entry point, header with the cutoff selector, tabs, routes
        CutoffContext.jsx       holds the selected cutoff for all pages
        api.js                  the two calls to the backend
        pages/ForecastPage.jsx  forecast chart for one delivery day, optional actuals
        pages/AccuracyPage.jsx  accuracy cards and error-by-hour chart

## Assumptions

- Window: purchase decisions made in January 2026, so delivery days 2 Jan to 1 Feb 2026 (744 hours).
- Default cutoff is 09:50 UK time on the day before delivery. The selectable cutoffs are 09:20, 09:50 and 15:30. These are my choices for plausible day-ahead decision times and can be changed in the app. <<< if you have a source for these gate-closure times, add the link; if not, keep the sentence as written >>>
- Selection rule: for each delivery hour, keep forecasts published at or before the cutoff, then take the latest.
- UK time equals UTC in January, so all times are UTC.
- Actuals (FUELHH, wind) are half-hourly. Each delivery hour is the average of its two half-hours, and an hour is kept only if both exist. Gaps stay gaps.
- error = forecast - actual, so a positive error means the forecast was too high.

## Results (decisions made in January 2026, 744 hours, MW)

| Cutoff | MAE | RMSE | Bias | P95 over-forecast |
|---|---|---|---|---|
| 09:20 | 2,039 | 2,505 | +1,748 | 5,283 |
| 09:50 | 2,013 | 2,506 | +1,730 | 5,322 |
| 15:30 | 1,873 | 2,327 | +1,709 | 4,513 |

What the numbers show:

- At the 09:50 cutoff the forecast was too high on 28 of the 31 delivery days. The worst day was 28 Jan, with a mean forecast of about 11,135 MW against a mean actual of about 5,760 MW.
- The P95 of the signed error equals the P95 of the absolute error at all three cutoffs, so the largest misses were all over-forecasts.
- The 15:30 cutoff has the smallest errors. The difference between 09:20 and 09:50 is small.
- The bias barely changes with the cutoff, so a later forecast reduces the size of the misses but not the tendency to over-forecast.
- Errors are largest in the early hours (hours 3 to 5 UTC at every cutoff) and smallest in the afternoon.
- These results come from one month of data and describe how the forecast behaved then, not what a safe buffer is in other months.

## What I could not establish

I did not establish why the forecast runs high. I checked that it is not caused by the cutoff logic or an hour offset. The brief treats the WINDFOR forecast and the FUELHH wind figure as the same quantity, and I did too, but the Elexon pages I read do not say exactly what each dataset counts, so I cannot rule out a difference. For the buyer this does not change the numbers: the buffer comes from the observed forecast-minus-actual error, whatever its cause. I did not test other possible causes, such as limits on output.

## AI tool usage

I used Claude (Anthropic) as an assistant. React, FastAPI and deployment are part of my usual stack, so there I used it to move faster: it drafted a good part of the code (frontend) and helped me whenever I got stuck. I typed, ran and tested every file.

Energy markets were familiar from my electrical engineering background, but the UK specifics, such as the day-ahead timelines and requirements, were new to me, and Claude explained those whenever I was confused about a part. Docker was also new to me, so I used Claude to learn it step by step, and it guided me through writing the Dockerfiles and the compose file.