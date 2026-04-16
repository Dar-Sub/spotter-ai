# Local Setup

## Database modes

The backend supports two database modes via `DB_BACKEND`:

- `sqlite` (default): zero-config local development
- `postgres`: production-like local development

If `DB_BACKEND` is not set, SQLite is used.

Copy env template:

```bash
cp backend/.env.example backend/.env
```

## Run with SQLite (default)

```bash
source .venv/bin/activate
set -a; source backend/.env; set +a
export DB_BACKEND=sqlite
python backend/manage.py migrate
python backend/manage.py runserver
```

## Run with PostgreSQL

Start PostgreSQL:

```bash
docker compose -f docker-compose.postgres.yml up -d
```

Run backend against Postgres:

```bash
source .venv/bin/activate
set -a; source backend/.env; set +a
export DB_BACKEND=postgres
python backend/manage.py migrate
python backend/manage.py runserver
```

## Frontend

```bash
cp frontend/.env.example frontend/.env
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`  
Backend URL: `http://127.0.0.1:8000`  
Health endpoint: `http://127.0.0.1:8000/api/health/`

## Optional: run tests

Backend:

```bash
cd backend
source ../.venv/bin/activate
pytest
```

Frontend:

```bash
cd frontend
npm run test
```

## Route provider mode

Set in `backend/.env`:

```bash
ROUTE_PROVIDER=osrm
```

Available values:

- `osrm` (default): real route + geometry via public OSRM + Nominatim geocoding
- `stub`: deterministic fallback route for offline/demo-safe local work
