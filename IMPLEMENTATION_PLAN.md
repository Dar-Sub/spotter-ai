# Spotter Trip Planner - Implementation Plan

## 1) Purpose and Success Criteria

This document defines the build plan for a production-style MVP full stack trucking trip planner and HOS simulator that is:

- Technically strong (clean architecture, testable logic, clear contracts)
- Product-ready (clear flows, polished UI states, operational UX)
- Demo-ready (easy to explain in Loom with clear boundaries and decisions)
- Correctness-focused (FMCSA constraints encoded in a deterministic simulation engine)

## 2) Product Vision

Build an internal logistics planning tool where a dispatcher or operations user can:

1. Enter current location, pickup, dropoff, and current cycle-used hours
2. Generate a compliant trip plan with map route and timeline
3. See inserted compliance/service events (breaks, fuel, resets, pickup/dropoff)
4. Review daily ELD-style log sheets across multi-day trips

The system should feel trustworthy, operational, and intentionally designed.

## 3) Scope for MVP v1

### In Scope

- Django + DRF backend with persistent trip artifacts
- Route acquisition via external routing API
- HOS simulation engine (single driver, property carrying assumptions)
- Fuel stop and break insertion logic
- Daily log sheet data generation
- React + TypeScript frontend with map/timeline/log rendering
- Error/loading/empty states and polished UX
- Unit + integration tests for core logic and API

### Out of Scope (Documented Simplifications)

- Split sleeper berth optimization
- Team driving
- Real-time traffic re-optimization
- Multi-timezone legal edge handling beyond a single planning time base
- Full dispatch account system (auth can be stubbed or omitted for v1)

## 4) Technical Stack

## Backend

- Python 3.12+
- Django 5+
- Django REST Framework
- PostgreSQL
- `django-cors-headers`
- `httpx` for external API calls
- `pytest` + `pytest-django`

## Frontend

- React + Vite + TypeScript
- Tailwind CSS
- TanStack Query
- Zustand (optional; only if client state grows)
- Leaflet + React Leaflet for map rendering
- SVG-based log sheet renderer

## Deployment

- Frontend: Vercel
- Backend: Render or Railway
- PostgreSQL managed instance
- Environment-based configuration via `.env`

## 5) UX and Visual Direction (from investigation)

Adopt a product shell inspired by the investigated Spotter design language:

- Dark blue/teal app shell and hero accents
- Clean rounded cards, strong spacing, high contrast hierarchy
- Operational dashboard feel (not a marketing clone)
- Intentional empty states and confidence-building microcopy

Design intent for planner page:

- Left: planning form + assumptions helper
- Right: live map and route markers
- Bottom/result area: summary metrics, schedule timeline, daily logs

## 6) Proposed Repository Structure

```
spotter_ai/
  backend/
    manage.py
    config/
      settings/
      urls.py
    apps/
      trips/
        api/
          serializers.py
          views.py
          urls.py
        models/
          trip.py
          route.py
          stop.py
          duty.py
          log.py
        services/
          trip_planner_service.py
          route_service.py
          hos/
            engine.py
            rules.py
            state.py
            events.py
          logs/
            daily_log_builder.py
          mappers/
            response_mapper.py
        tests/
          unit/
          integration/
        constants.py
        enums.py
  frontend/
    src/
      app/
      pages/
      components/
        form/
        map/
        timeline/
        logs/
        ui/
      services/
      hooks/
      types/
      utils/
```

## 7) Backend Architecture

### Layering

- **API Layer**: validation, request/response contracts, no business logic
- **Service Layer**: orchestration (`TripPlannerService`)
- **Domain Logic Layer**: HOS simulation engine (pure deterministic logic)
- **Infrastructure Layer**: routing/geocoding clients and persistence

### Key Principle

The HOS algorithm remains isolated and mostly pure to maximize correctness and testability.

## 8) Domain Model (Initial)

## `Trip`

- Input fields: current/pickup/dropoff text, cycle-used hours
- Route summary: total miles, drive duration
- Status and computed summary metrics
- Created/updated timestamps

## `RouteLeg`

- Ordered leg sequence (current->pickup, pickup->dropoff)
- Distance, duration, geometry

## `Stop`

- Typed events: `pickup`, `dropoff`, `fuel`, `break`, `overnight_reset`
- Sequence, optional coordinate, timing, duration, notes

## `DutySegment`

- Duty statuses: `off_duty`, `sleeper`, `driving`, `on_duty_not_driving`
- Start/end timestamps, day index, location context, optional stop link

## `DailyLog`

- One record per log date with totals per duty status
- Remarks and references to source segments

## 9) Route Service Contract

Define a backend interface independent from provider details:

```python
class RouteService(Protocol):
    def build_trip_route(
        self,
        current_location: str,
        pickup_location: str,
        dropoff_location: str,
    ) -> NormalizedRoute:
        ...
```

`NormalizedRoute` returns:

- geocoded waypoints
- total distance miles
- total duration minutes
- ordered legs
- route geometry polyline or GeoJSON
- interpolation helpers for approximate stop placement

Provider adapters (OpenRouteService/OSRM) can be swapped later without changing HOS logic.

## 10) HOS Engine Design

Implement a deterministic engine that consumes normalized route progress and emits duty timeline.

### Core State

- current timestamp
- remaining route miles/minutes
- cumulative driving since last break
- driving hours in current shift
- on-duty window elapsed (14h clock)
- rolling cycle-used hours (70/8)

### Decision Loop (High-Level)

At each step, engine picks next legal event:

1. Start shift if currently off duty
2. Execute required service event (pickup/dropoff/fuel if due and reached)
3. Drive until nearest constraint:
   - break threshold (8h cumulative drive)
   - 11h drive cap
   - 14h window cap
   - cycle cap remainder
   - destination reached
4. Insert 30 min break if required
5. Insert fuel stop (on-duty not driving) at ~1000 mile intervals
6. Insert 10h reset when shift limits reached
7. Continue until dropoff complete

### Engine Output

- ordered `DutySegment` list
- ordered `Stop` list
- summary totals (days, miles, ETA, total on-duty)
- warnings and violations (if impossible constraints or near-limit conditions)

### Purity and Testability

- `engine.py` should accept typed input DTOs and return typed output DTOs
- no DB writes and no network calls inside the engine
- orchestration service persists outputs after simulation succeeds

## 11) API Design

## `POST /api/trips/plan/`

Request:

- `current_location`
- `pickup_location`
- `dropoff_location`
- `current_cycle_used_hours`
- optional `start_time`

Response:

- `trip_id`
- normalized route
- stop plan
- duty segments
- daily logs
- summary metrics
- warnings

## `GET /api/trips/{id}/`

Returns full persisted trip plan and render-ready payload.

## `GET /api/health/`

Simple readiness endpoint.

## 12) Frontend Architecture

## Page Layout

- `PlannerPage` in three vertical zones:
  1. Planner header and form
  2. Map + summary/timeline panel
  3. Daily log sheets area

## Data Flow

- Submit form -> `planTrip` mutation (TanStack Query)
- Response normalized into typed view models
- Map, timeline, and logs read from shared trip plan model

## Core Components

- `TripPlannerForm`
- `RouteMapPanel`
- `TripSummaryCards`
- `StopsTimeline`
- `DailyLogSheet` (SVG)
- `DailyLogsCarousel` or stacked list

## UX Quality Requirements

- skeleton/loading state while generating plan
- graceful empty state before first submit
- actionable error state with retry
- non-blocking warning banner for assumptions/edge messages

## 13) Daily Log Rendering Plan

Use SVG for deterministic and crisp rendering.

`DailyLogSheet` receives:

- date metadata
- 24h segmented duty status timeline
- event annotations (fuel/break/pickup/dropoff/reset)
- summary totals

Rendering approach:

- fixed 24-hour x-axis grid
- four y-levels for duty statuses
- step-line path for status transitions
- overlay labels for key events

## 14) Testing Strategy

## Unit tests (engine heavy)

- short trip (<8h driving) no break needed
- break insertion after 8h cumulative drive
- 10h reset insertion on multi-day trip
- fuel stop insertion at 1000+ mile intervals
- near-cycle-limit behavior with high initial cycle-used
- pickup/dropoff service time incorporation

## Integration tests (API)

- valid plan request returns complete contract
- invalid inputs return clear 400 errors
- mocked route provider failure returns graceful error contract

## Frontend tests (targeted)

- form validation and disabled submit logic
- successful render of summary/map/log sections
- error-state rendering

## 15) Delivery Phases and Milestones

## Phase 1 - Foundation

- scaffold backend/frontend
- configure DB, CORS, env settings
- create base app shell and route

## Phase 2 - Route Integration

- geocoding + directions adapter
- normalized route DTOs
- route persistence

## Phase 3 - HOS Engine

- implement state machine/decision loop
- generate duty segments and stops
- validate assumptions and warnings

## Phase 4 - Daily Logs

- transform segments into day buckets
- generate log-friendly structures
- build backend response mapper

## Phase 5 - Frontend Experience

- polished form, map, timeline, log sheets
- loading/error/empty/warning states
- responsive layout and visual polish

## Phase 6 - Hardening and Demo Readiness

- tests, bug fixes, docs, deployment
- seed scenarios for fast demos
- Loom walkthrough script points

## 16) Key Risks and Mitigations

- **Routing API instability** -> provider abstraction + robust fallback errors
- **Algorithm complexity drift** -> strict service boundaries and unit tests first
- **UI complexity for log graph** -> SVG-first, reusable primitives, snapshot checks
- **Time overruns** -> prioritize correctness + core polish before extra features

## 17) Definition of Done (Assessment-Ready)

- End-to-end trip plan generation works with realistic addresses
- HOS constraints are visibly reflected in schedule and logs
- Multi-day logs render clearly and consistently
- Codebase is modular, readable, and tested
- README explains architecture, assumptions, and tradeoffs clearly
- Deployment works with clean env setup and stable demo flow

## 18) Immediate Next Step

Start Phase 1 implementation:

1. Scaffold `backend/` Django project and `frontend/` Vite React TypeScript app
2. Add initial folder architecture and base modules
3. Implement core Django models and enums
4. Define route/HOS service contracts (interfaces + DTOs) before writing engine logic

