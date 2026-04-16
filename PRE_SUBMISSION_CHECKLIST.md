# Pre-Submission Checklist

Use this right before sending the assessment submission.

## Functionality

- [ ] Planning works end-to-end: route -> stops/timeline -> daily ELD sheets
- [ ] `POST /api/trips/plan/` returns `route_legs`, `stops`, `duty_segments`, and `daily_logs`
- [ ] Daily log sheets render in the frontend (SVG lanes + plotted entries)
- [ ] Print mode works for daily logs (at least one day)

## Compliance / correctness

- [ ] HOS engine outputs include explicit break/reset/fuel/pickup/dropoff events
- [ ] Warnings appear for cycle-limit conditions near 70 hours

## UX polish

- [ ] Empty state is clear before planning
- [ ] Loading skeleton appears during plan generation
- [ ] Error state is actionable when routing fails
- [ ] Marker legend is visible and consistent with stop types

## Quality gates

- [ ] Backend tests: `pytest` pass
- [ ] Frontend tests: `npm run test` pass
- [ ] Frontend build: `npm run build` pass

## Demo readiness

- [ ] Run Loom walkthrough using `LOOM_WALKTHROUGH_CHECKLIST.md`
- [ ] Have a “happy path” trip + one “warning/limit near” trip ready for discussion
