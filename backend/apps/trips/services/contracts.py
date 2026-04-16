"""Typed contracts for routing and HOS services."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Protocol


@dataclass(slots=True)
class RoutePoint:
    name: str
    latitude: float
    longitude: float


@dataclass(slots=True)
class RouteLegData:
    sequence: int
    start_name: str
    end_name: str
    distance_miles: Decimal
    duration_minutes: int
    geometry_geojson: dict


@dataclass(slots=True)
class NormalizedRoute:
    points: list[RoutePoint]
    legs: list[RouteLegData]
    total_distance_miles: Decimal
    total_duration_minutes: int
    geometry_geojson: dict


@dataclass(slots=True)
class TripPlanRequest:
    current_location: str
    pickup_location: str
    dropoff_location: str
    current_cycle_used_hours: Decimal
    start_time: datetime | None = None


@dataclass(slots=True)
class DutySegmentData:
    day_index: int
    segment_type: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    location_context: str = ""
    notes: str = ""


@dataclass(slots=True)
class StopData:
    stop_type: str
    sequence: int
    location_name: str
    latitude: float | None = None
    longitude: float | None = None
    planned_arrival: datetime | None = None
    planned_departure: datetime | None = None
    duration_minutes: int = 0
    notes: str = ""


@dataclass(slots=True)
class DailyLogEntryData:
    segment_type: str
    start_minute: int
    end_minute: int
    start_time: datetime
    end_time: datetime
    location_context: str = ""
    notes: str = ""


@dataclass(slots=True)
class DailyLogData:
    log_date: str
    total_miles: Decimal
    off_duty_hours: Decimal
    sleeper_hours: Decimal
    driving_hours: Decimal
    on_duty_hours: Decimal
    remarks: str = ""
    entries: list[DailyLogEntryData] = field(default_factory=list)


@dataclass(slots=True)
class TripPlanResult:
    route: NormalizedRoute
    stops: list[StopData] = field(default_factory=list)
    duty_segments: list[DutySegmentData] = field(default_factory=list)
    daily_logs: list[DailyLogData] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class RouteService(Protocol):
    def build_trip_route(
        self,
        current_location: str,
        pickup_location: str,
        dropoff_location: str,
    ) -> NormalizedRoute:
        """Build a normalized route representation."""


class HOSSimulationEngine(Protocol):
    def simulate(self, request: TripPlanRequest, route: NormalizedRoute) -> TripPlanResult:
        """Return duty timeline and stop plan for a route."""
