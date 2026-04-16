# Frontend (React + TypeScript)

UI for the Spotter Trip Planner and HOS Simulator.

## Run locally

```bash
cp .env.example .env
npm install
npm run dev
```

## Commands

- `npm run dev`: start local dev server
- `npm run test`: run Vitest test suite
- `npm run build`: TypeScript + production build

## Environment

- `VITE_API_BASE_URL`: backend API base URL (default in example points to local Django)

## Key UI areas

- Planner form and assumptions rail
- Route map with waypoints and stop legend
- Stops + duty timeline
- Daily ELD SVG log sheets (with print mode)
