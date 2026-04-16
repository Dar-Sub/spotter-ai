# Deployment: Railway (backend) + Vercel (frontend)

This app is a **monorepo**: Django API in `backend/`, Vite + React in `frontend/`. Production uses **PostgreSQL** on Railway and the **static frontend** on Vercel calling the API over HTTPS.

---

## Part A — Push the repo to GitHub

1. Create an empty repo on GitHub (no README if you want a clean first push), e.g. `https://github.com/Dar-Sub/spotter-ai`.
2. From your machine, in the project root:

```bash
cd /path/to/spotter_ai
git init
git branch -M main
git add -A
git commit -m "Initial commit: trip planner, HOS engine, daily logs, Vite UI"
git remote add origin https://github.com/Dar-Sub/spotter-ai.git
git push -u origin main
```

3. If GitHub rejects the push, authenticate with **SSH** (`git@github.com:Dar-Sub/spotter-ai.git`) or a **Personal Access Token** (HTTPS), then run `git push -u origin main` again.

---

## Part B — Railway: sign up through a working API

### 1) Sign up and connect GitHub

1. Go to [railway.app](https://railway.app) and sign up (GitHub login is easiest).
2. **New project** → **Deploy from GitHub repo** → authorize Railway → pick **`Dar-Sub/spotter-ai`** (or your fork).

### 2) Add PostgreSQL

1. In the project, click **+ New** → **Database** → **PostgreSQL**.
2. Wait until Postgres is **Active**. Open the Postgres service → **Variables** (or **Connect**): note **host, port, database name, user, password** (Railway often exposes `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD` on the database service).

### 3) Create the web service (Django)

1. **+ New** → **GitHub Repo** (same repo) *or* duplicate the repo service if Railway already created one.
2. Open the **web** service → **Settings**:
   - **Root Directory**: `backend`
   - **Builder**: Nixpacks (default) is fine; Railway will detect Python from `requirements.txt`.
3. **Variables** (service that runs Django — not only Postgres), add:

| Variable | Example / notes |
|----------|------------------|
| `DB_BACKEND` | `postgres` |
| `POSTGRES_HOST` | Value from Postgres service (private host is fine for same-project networking). |
| `POSTGRES_PORT` | Usually `5432` |
| `POSTGRES_DB` | Database name from Postgres |
| `POSTGRES_USER` | User from Postgres |
| `POSTGRES_PASSWORD` | Password from Postgres |
| `DJANGO_SECRET_KEY` | Long random string (generate locally: `python -c "import secrets; print(secrets.token_urlsafe(48))"`) |
| `DJANGO_DEBUG` | `false` |
| `DJANGO_ALLOWED_HOSTS` | Your Railway app hostname, e.g. `your-service.up.railway.app` (comma-separated if several) |
| `CORS_ALLOWED_ORIGINS` | Your **Vercel** site URL(s), e.g. `https://spotter-ai.vercel.app` (no trailing slash). Add `http://localhost:5173` only if you still want local UI hitting prod API. |
| `APP_TIMEZONE` | `UTC` (or your preference) |
| `ROUTE_PROVIDER` | `osrm` if outbound HTTP to OSRM/Nominatim is allowed; use `stub` if geocoding/routing is blocked or flaky in production. |

4. **Deploy** / **Redeploy** so the service picks up variables. The included `backend/Procfile` runs migrations then **Gunicorn** on `$PORT`.

5. **Networking**: generate a **public URL** (or custom domain) for the web service. Your API base for the frontend will be `https://<railway-host>/api` (this project mounts the API under `/api`).

6. Smoke test: open `https://<railway-host>/api/health/` in a browser; expect a JSON OK-style response.

---

## Part C — Vercel: sign up through a working frontend

### 1) Sign up and import the repo

1. Go to [vercel.com](https://vercel.com) and sign up with GitHub.
2. **Add New** → **Project** → import **`Dar-Sub/spotter-ai`**.
3. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `dist` (Vite default)
   - **Install Command**: `npm install` (default)

### 2) Environment variable (required)

In **Settings → Environment Variables**, add:

| Name | Value |
|------|--------|
| `VITE_API_BASE_URL` | `https://<your-railway-host>/api` |

Use the **same** URL you verified for `/api/health/`, including `https` and **no trailing slash** after `api` unless your backend is mounted differently.

Redeploy after saving env vars (Vercel rebuilds so `import.meta.env.VITE_API_BASE_URL` is baked in at build time).

### 3) Verify end-to-end

1. Open the Vercel **Production** URL.
2. Run a trip plan; confirm the browser’s **Network** tab shows requests to your Railway host and **200** responses (not CORS errors).

---

## Part D — Order of operations (recommended)

1. Push code to GitHub.
2. Deploy **Postgres** + **Django** on Railway; fix `ALLOWED_HOSTS`, DB vars, and `/api/health/` until green.
3. Set **`CORS_ALLOWED_ORIGINS`** on Railway to the **exact** Vercel production origin (`https://....vercel.app`).
4. Deploy **Vercel** with **`VITE_API_BASE_URL`** pointing at Railway `/api`.
5. If you change the Vercel URL (new preview domain, custom domain), update **`CORS_ALLOWED_ORIGINS`** on Railway to match.

---

## Part E — Troubleshooting

| Symptom | What to check |
|---------|----------------|
| CORS error in browser | `CORS_ALLOWED_ORIGINS` must include the **full** frontend origin (scheme + host, no path). |
| 502 / route errors from planner | Set `ROUTE_PROVIDER=stub` to isolate routing; or ensure the Railway service can reach external OSRM/Nominatim. |
| 500 on startup | Railway logs: often missing `DJANGO_SECRET_KEY`, wrong `POSTGRES_*`, or `ALLOWED_HOSTS` missing the Railway hostname. |
| Frontend calls `localhost` in prod | Rebuild Vercel after setting `VITE_API_BASE_URL`; it is inlined at **build** time. |

---

## Local reference

- Backend env template: `backend/.env.example`
- Frontend env template: `frontend/.env.example`
