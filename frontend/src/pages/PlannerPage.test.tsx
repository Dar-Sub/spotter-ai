import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { PlannerPage } from "./PlannerPage";

vi.mock("../components/map/RouteMapPanel", () => ({
  RouteMapPanel: () => <div data-testid="route-map-panel">map</div>,
}));

const usePlanTripMock = vi.hoisted(() => vi.fn());
vi.mock("../hooks/usePlanTrip", () => ({
  usePlanTrip: usePlanTripMock,
}));

describe("PlannerPage states", () => {
  it("renders loading skeleton", () => {
    usePlanTripMock.mockReturnValue({
      mutate: vi.fn(),
      data: null,
      isPending: true,
      error: null,
    });

    render(<PlannerPage />);
    expect(screen.getByLabelText("Loading trip results")).toBeInTheDocument();
  });

  it("renders error message", () => {
    usePlanTripMock.mockReturnValue({
      mutate: vi.fn(),
      data: null,
      isPending: false,
      error: new Error("network"),
    });

    render(<PlannerPage />);
    expect(screen.getByText(/Unable to generate trip plan/i)).toBeInTheDocument();
  });

  it("renders success sections", () => {
    usePlanTripMock.mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      error: null,
      data: {
        id: 1,
        trip_status: "planned",
        current_location_text: "A",
        pickup_location_text: "B",
        dropoff_location_text: "C",
        current_cycle_used_hours: "12.0",
        total_distance_miles: "700.0",
        estimated_raw_drive_duration_minutes: 700,
        route_legs: [{ sequence: 1, start_name: "A", end_name: "B", distance_miles: "200", duration_minutes: 200 }],
        stops: [],
        duty_segments: [],
        daily_logs: [],
        warnings: [],
        route_summary: { total_distance_miles: "700.0", total_duration_minutes: 700, geometry_geojson: {}, points: [] },
      },
    });

    render(<PlannerPage />);
    expect(screen.getByText(/Trip status/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Daily ELD logs" })).toBeInTheDocument();
  });
});
