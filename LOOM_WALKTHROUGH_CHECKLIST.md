# Loom Walkthrough Checklist (3-5 minutes)

## 1) Product intro (20-30s)

- Explain this is an internal logistics planning MVP, not a demo toy.
- Show inputs: current, pickup, dropoff, cycle-used hours.
- State outputs: map, stop timeline, duty segments, daily logs.

## 2) User flow demo (60-90s)

- Enter a realistic trip.
- Click **Plan trip**.
- Highlight loading state and warning/error handling.
- Walk through summary cards and route map.

## 3) Compliance behavior (60-90s)

- Open stop timeline and point out:
  - pickup/dropoff service time
  - inserted break/fuel/reset events
- Explain FMCSA rule constraints reflected in generated schedule.

## 4) Daily logs (45-60s)

- Show generated ELD log sheets.
- Explain 24-hour status plotting and totals.
- Demonstrate print button for log output.

## 5) Code architecture (45-60s)

- Backend:
  - API layer (`api/`)
  - services (`trip_planner_service`, `route_service`, `hos/engine`, `logs/daily_log_builder`)
  - models and persistence boundaries
- Frontend:
  - page orchestration
  - typed API models
  - map/timeline/log components

## 6) Testing + deployment readiness (20-30s)

- Backend pytest coverage for HOS and API paths.
- Frontend tests for planner states.
- Mention env-driven SQLite/Postgres and provider mode toggles.
