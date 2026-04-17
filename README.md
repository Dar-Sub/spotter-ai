# Spotter Trip Planner & HOS Simulator

Full-stack trip planner with route geometry, planned stops, FMCSA-style hours-of-service simulation (property-carrying, simplified), and multi-day ELD-style daily logs. **Backend:** Django + DRF. **Frontend:** React, TypeScript, Vite, Leaflet.

## Tech stack

**Backend:** Python 3.13, Django, Django REST Framework, PostgreSQL or SQLite, `django-cors-headers`, `httpx`, pytest.

**Frontend:** React 19, TypeScript, Vite, Tailwind CSS, TanStack Query, Leaflet, Vitest.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
# optional: set -a; source backend/.env; set +a
python backend/manage.py migrate
python backend/manage.py runserver
```

In another terminal:

```bash
cp frontend/.env.example frontend/.env   # point VITE_API_BASE_URL at your API, e.g. http://localhost:8000/api
cd frontend && npm install && npm run dev
```

**Database:** `DB_BACKEND=sqlite` (default) or `postgres`. For local Postgres: `docker compose -f docker-compose.postgres.yml up -d` and set the `POSTGRES_*` variables from `backend/.env.example`.

**Routing:** `ROUTE_PROVIDER=osrm` (default) or `stub` for offline-safe demo routes.

**Time:** `APP_TIMEZONE` sets Django `TIME_ZONE` — daily log `log_date` and local “midnight” splits use this zone; default trip `start_time` is “today at 06:00” in this zone (UTC on Railway unless you change it).

## API

- `GET /api/health/` — health check  
- `POST /api/trips/plan/` — plan a trip (locations, optional cycle hours / start time)  
- `GET /api/trips/{id}/` — fetch a persisted plan  

See serializers and views under `backend/apps/trips/api/` for request/response shapes.

## Tests

```bash
source .venv/bin/activate && cd backend && pytest
cd frontend && npm run test && npm run build
```

## Deployment (sketch)

Deploy the Django app with Postgres (e.g. Railway: service root `backend`, env from `backend/.env.example`, `DB_BACKEND=postgres`, `DJANGO_ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` set for your frontend origin). Deploy the Vite app (e.g. Vercel: root `frontend`, `npm run build`, output `dist`) with `VITE_API_BASE_URL=https://<your-api-host>/api` at build time.
