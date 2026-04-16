# Spotter Trip Planner & HOS Simulator

A production-style full stack logistics planning tool built for a Full Stack Engineer assessment.

The app accepts route and duty-cycle inputs, computes a route, simulates driver duty constraints under FMCSA property-carrying assumptions, and returns map/timeline/log outputs including daily ELD-style log sheets.

## Project Overview

This project is intentionally structured like an internal operations tool, not a toy prototype:

- Clean Django service-layer backend
- Typed React + TypeScript frontend
- Routing abstraction with real provider integration
- Deterministic HOS simulation engine
- Daily log transformation pipeline
- UI states for empty/loading/error/success
- Unit/integration tests for core planning logic

## Tech Stack

### Backend

- Python 3.13
- Django + Django REST Framework
- PostgreSQL (optional) and SQLite fallback
- `django-cors-headers`
- `httpx`
- `pytest` + `pytest-django`

### Frontend

- React 19 + TypeScript
- Vite
- Tailwind CSS
- TanStack Query
- Leaflet
- Vitest + Testing Library

## Architecture Summary

### Backend layers

- `apps/trips/api`: serializers/views/urls (thin HTTP layer)
- `apps/trips/models`: persistence entities (`Trip`, `RouteLeg`, `Stop`, `DutySegment`, `DailyLog`)
- `apps/trips/services`: orchestration + domain logic
  - `trip_planner_service.py`: high-level planning flow
  - `route_service.py`: provider abstraction + OSRM integration
  - `hos/engine.py`: rule-driven HOS simulation
  - `logs/daily_log_builder.py`: duty-to-daily-log transformation

### Frontend structure

- `src/pages/PlannerPage.tsx`: orchestration view
- `src/components/form`: trip input workflow
- `src/components/map`: route + marker visualization
- `src/components/timeline`: stop and duty timeline
- `src/components/logs`: ELD log rendering (SVG)
- `src/services` + `src/hooks`: API and query behavior
- `src/types`: shared API response typing

## HOS Assumptions Implemented

- Property-carrying driver
- 11-hour max driving per shift
- 14-hour on-duty window
- 30-minute non-driving break after 8 cumulative driving hours
- 70-hour cycle cap (simplified static budget model for MVP)
- 10-hour reset insertion when shift limits are hit
- 1 hour pickup service (on-duty not driving)
- 1 hour dropoff service (on-duty not driving)
- Fuel stop inserted approximately every 1,000 miles

## Simplifications & Tradeoffs

- Uses deterministic rule simulation rather than optimization search.
- Uses OSRM + Nominatim for route/geocode in local mode.
- 70-hour/8-day cycle is implemented as a static remaining budget for the current planning run, not a full rolling historical ledger.
- Stop coordinates for inserted fuel/break/reset events may be absent unless directly tied to geocoded points.
- Timezone handling is kept consistent in a single planning time base for MVP clarity.

## API Overview

### `GET /api/health/`

Returns readiness status.

### `POST /api/trips/plan/`

Request body:

- `current_location`
- `pickup_location`
- `dropoff_location`
- `current_cycle_used_hours`
- optional `start_time`

Response includes:

- persisted trip data
- route legs and summary geometry
- planned stops
- duty segments
- daily logs with render-ready `log_entries`
- warnings

### `GET /api/trips/{id}/`

Returns full persisted trip plan and related records.

## Local Setup

### 1) Install backend deps

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 2) Configure backend env

```bash
cp backend/.env.example backend/.env
```

Load env in shell:

```bash
set -a; source backend/.env; set +a
```

### 3) Run backend

```bash
python backend/manage.py migrate
python backend/manage.py runserver
```

### 4) Configure frontend env

```bash
cp frontend/.env.example frontend/.env
```

### 5) Run frontend

```bash
cd frontend
npm install
npm run dev
```

## Database Modes

Configured through `DB_BACKEND` in backend env:

- `sqlite` (default local fallback)
- `postgres` (production-like)

For local Postgres (Docker):

```bash
docker compose -f docker-compose.postgres.yml up -d
```

## Route Provider Modes

Configured by `ROUTE_PROVIDER`:

- `osrm` (default): real route + geometry
- `stub`: deterministic fallback for offline/dev-safe behavior

## Testing

### Backend

```bash
source .venv/bin/activate
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm run test
npm run build
```

## Deployment Notes

Step-by-step (sign-up through smoke tests): **[DEPLOYMENT.md](./DEPLOYMENT.md)** — Railway (Django + Postgres) + Vercel (Vite UI).

### Frontend (Vercel)

- Root directory: `frontend`
- Build command: `npm run build`
- Output dir: `dist`
- Env: `VITE_API_BASE_URL=https://<backend-host>/api`

### Backend (Railway)

- Root directory: `backend`
- Uses `backend/Procfile`: migrations + **Gunicorn** on `$PORT`
- Set env vars from `backend/.env.example` (prod-safe values)
- Use managed Postgres and set `DB_BACKEND=postgres`
- Update CORS and allowed hosts for deployed frontend domain

## Loom Walkthrough Tips

Use `LOOM_WALKTHROUGH_CHECKLIST.md` for a concise demo script:

- user flow
- route acquisition
- HOS decisions
- daily log generation
- architecture and test coverage

## Future Improvements

- Full rolling 8-day cycle ledger with historical duty carry-over
- Rich stop interpolation along polyline for inserted events
- Export logs to PDF
- Authentication and saved trip workspaces
- Improved timezone and geofence realism
