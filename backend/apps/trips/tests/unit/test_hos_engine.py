from datetime import datetime, timezone
from decimal import Decimal

from apps.trips.enums import DutyStatus, StopType
from apps.trips.services.contracts import NormalizedRoute, RouteLegData, RoutePoint, TripPlanRequest
from apps.trips.services.hos.engine import BasicHOSEngine


def build_route(total_miles: str, total_minutes: int) -> NormalizedRoute:
    first_leg_miles = (Decimal(total_miles) * Decimal("0.2")).quantize(Decimal("0.01"))
    second_leg_miles = Decimal(total_miles) - first_leg_miles
    first_leg_minutes = max(1, round(total_minutes * 0.2))
    second_leg_minutes = max(1, total_minutes - first_leg_minutes)
    return NormalizedRoute(
        points=[
            RoutePoint(name="A", latitude=41.0, longitude=-87.0),
            RoutePoint(name="B", latitude=39.0, longitude=-86.0),
            RoutePoint(name="C", latitude=33.0, longitude=-84.0),
        ],
        legs=[
            RouteLegData(
                sequence=1,
                start_name="A",
                end_name="B",
                distance_miles=first_leg_miles,
                duration_minutes=first_leg_minutes,
                geometry_geojson={},
            ),
            RouteLegData(
                sequence=2,
                start_name="B",
                end_name="C",
                distance_miles=second_leg_miles,
                duration_minutes=second_leg_minutes,
                geometry_geojson={},
            ),
        ],
        total_distance_miles=Decimal(total_miles),
        total_duration_minutes=total_minutes,
        geometry_geojson={},
    )


def build_request(cycle_used: str = "10.0") -> TripPlanRequest:
    return TripPlanRequest(
        current_location="A",
        pickup_location="B",
        dropoff_location="C",
        current_cycle_used_hours=Decimal(cycle_used),
        start_time=datetime(2026, 4, 16, 6, 0, tzinfo=timezone.utc),
    )


def test_short_trip_has_pickup_and_dropoff_only():
    engine = BasicHOSEngine()
    result = engine.simulate(build_request(), build_route("300.0", 300))

    stop_types = [stop.stop_type for stop in result.stops]
    assert stop_types == [StopType.PICKUP, StopType.DROPOFF]


def test_long_trip_inserts_break_and_reset():
    engine = BasicHOSEngine()
    result = engine.simulate(build_request(), build_route("1400.0", 1500))

    stop_types = [stop.stop_type for stop in result.stops]
    assert StopType.BREAK in stop_types
    assert StopType.OVERNIGHT_RESET in stop_types
    assert any(segment.segment_type == DutyStatus.OFF_DUTY for segment in result.duty_segments)


def test_very_long_trip_inserts_fuel_stops():
    engine = BasicHOSEngine()
    result = engine.simulate(build_request(), build_route("2500.0", 2600))

    fuel_stops = [stop for stop in result.stops if stop.stop_type == StopType.FUEL]
    assert len(fuel_stops) >= 2


def test_seventy_hours_already_at_cap_cannot_start():
    engine = BasicHOSEngine()
    result = engine.simulate(build_request(cycle_used="70.0"), build_route("100.0", 60))
    assert not result.duty_segments
    assert any("cannot be planned" in w.lower() for w in result.warnings)


def test_tight_cycle_uses_rolling_window_and_may_insert_midnight_waits():
    """69.5h used leaves little 70h/8-day headroom; engine may insert off-duty to local midnight to roll the window."""
    engine = BasicHOSEngine()
    result = engine.simulate(build_request(cycle_used="69.5"), build_route("600.0", 700))
    joined = " ".join(result.warnings).lower()
    assert "rolling 70-hour" in joined or "8-day" in joined
    assert result.duty_segments
    assert any(s.stop_type == StopType.CYCLE_WINDOW_WAIT for s in result.stops) or any(
        d.segment_type == "driving" for d in result.duty_segments
    )


def test_interpolate_lat_lon_endpoints_and_midpoint():
    engine = BasicHOSEngine()

    route_total_miles = Decimal("69.09")  # not used for exactness; overwritten by computed geometry
    geometry = {"type": "LineString", "coordinates": [[0, 0], [0, 1]]}  # GeoJSON [lon, lat]

    # Compute haversine distance for accurate total_distance_miles.
    miles = Decimal(
        str(
            engine._haversine_miles(
                lat1=0.0,
                lon1=0.0,
                lat2=1.0,
                lon2=0.0,
            )
        )
    )

    route = NormalizedRoute(
        points=[],
        legs=[],
        total_distance_miles=miles,
        total_duration_minutes=1,
        geometry_geojson=geometry,
    )

    start = engine._interpolate_lat_lon(route, Decimal("0"))
    assert start is not None
    assert abs(start[0] - 0.0) < 0.01

    mid = engine._interpolate_lat_lon(route, miles / 2)
    assert mid is not None
    assert abs(mid[0] - 0.5) < 0.1

    end = engine._interpolate_lat_lon(route, miles)
    assert end is not None
    assert abs(end[0] - 1.0) < 0.01
