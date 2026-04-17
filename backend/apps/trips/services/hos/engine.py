"""HOS simulation engine for single-driver property-carrying assumptions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from datetime import timezone as dt_timezone
from decimal import Decimal
import math
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils import timezone

from apps.trips.constants import (
    BREAK_DURATION_MINUTES,
    BREAK_REQUIRED_AFTER_DRIVING_MINUTES,
    DEFAULT_SHIFT_START_HOUR,
    DROPOFF_DURATION_MINUTES,
    FUEL_STOP_DISTANCE_MILES,
    FUEL_STOP_DURATION_MINUTES,
    MAX_CYCLE_ON_DUTY_MINUTES,
    MAX_DRIVING_PER_SHIFT_MINUTES,
    MAX_SHIFT_WINDOW_MINUTES,
    PICKUP_DURATION_MINUTES,
    RESET_DURATION_MINUTES,
)
from apps.trips.enums import DutyStatus, StopType
from apps.trips.services.contracts import DutySegmentData, NormalizedRoute, StopData, TripPlanRequest, TripPlanResult


@dataclass
class EngineState:
    current_time: datetime
    shift_start_time: datetime
    shift_driving_minutes: int = 0
    shift_elapsed_minutes: int = 0
    driving_since_break_minutes: int = 0
    cycle_on_duty_minutes: int = 0
    stop_sequence: int = 1
    day_index: int = 1
    miles_since_last_fuel: Decimal = Decimal("0")
    miles_driven_total: Decimal = Decimal("0")


class BasicHOSEngine:
    @staticmethod
    def _haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Great-circle distance approximation in miles.

        Used only to estimate where to place inserted compliance markers along the
        route geometry (MVP-level accuracy).
        """

        radius_miles = 3958.7613
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lon2 - lon1)

        a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return radius_miles * c

    def simulate(self, request: TripPlanRequest, route: NormalizedRoute) -> TripPlanResult:
        warnings: list[str] = []
        duty_segments: list[DutySegmentData] = []
        stops: list[StopData] = []

        start_time = request.start_time or self._default_start_time()
        state = EngineState(
            current_time=start_time,
            shift_start_time=start_time,
            cycle_on_duty_minutes=int(float(request.current_cycle_used_hours) * 60),
        )

        pickup_point = route.points[1] if len(route.points) > 2 else route.points[-1]
        dropoff_point = route.points[-1]

        if state.cycle_on_duty_minutes >= MAX_CYCLE_ON_DUTY_MINUTES:
            warnings.append("Current cycle-used hours already meet/exceed 70-hour limit; trip cannot be planned.")
            return TripPlanResult(route=route, warnings=warnings)

        for leg in route.legs:
            leg_minutes_remaining = int(leg.duration_minutes)
            leg_miles_remaining = Decimal(leg.distance_miles)
            miles_per_min = leg_miles_remaining / Decimal(max(leg_minutes_remaining, 1))

            while leg_minutes_remaining > 0:
                cycle_remaining = MAX_CYCLE_ON_DUTY_MINUTES - state.cycle_on_duty_minutes
                if cycle_remaining <= 0:
                    warnings.append("70-hour cycle limit reached before completing route.")
                    return TripPlanResult(route=route, stops=stops, duty_segments=duty_segments, warnings=warnings)

                chunk_limit = min(
                    leg_minutes_remaining,
                    MAX_DRIVING_PER_SHIFT_MINUTES - state.shift_driving_minutes,
                    MAX_SHIFT_WINDOW_MINUTES - state.shift_elapsed_minutes,
                    BREAK_REQUIRED_AFTER_DRIVING_MINUTES - state.driving_since_break_minutes,
                    cycle_remaining,
                )

                if chunk_limit <= 0:
                    self._resolve_zero_capacity(route=route, state=state, stops=stops, duty_segments=duty_segments)
                    continue

                drive_minutes = int(chunk_limit)
                driven_miles = (miles_per_min * Decimal(drive_minutes)).quantize(Decimal("0.01"))
                self._add_duty_segment(
                    duty_segments=duty_segments,
                    state=state,
                    segment_type=DutyStatus.DRIVING,
                    duration_minutes=drive_minutes,
                    location_context=f"{leg.start_name} -> {leg.end_name}",
                )
                leg_minutes_remaining -= drive_minutes
                leg_miles_remaining = max(Decimal("0"), leg_miles_remaining - driven_miles)
                state.shift_driving_minutes += drive_minutes
                state.shift_elapsed_minutes += drive_minutes
                state.driving_since_break_minutes += drive_minutes
                state.cycle_on_duty_minutes += drive_minutes
                state.miles_since_last_fuel += driven_miles
                state.miles_driven_total += driven_miles

                while state.miles_since_last_fuel >= Decimal(FUEL_STOP_DISTANCE_MILES):
                    fuel_lat_lon = self._interpolate_lat_lon(route=route, miles_from_start=state.miles_driven_total)
                    self._add_on_duty_stop(
                        state=state,
                        stops=stops,
                        duty_segments=duty_segments,
                        stop_type=StopType.FUEL,
                        location_name=f"En route fuel stop near {leg.end_name}",
                        latitude=fuel_lat_lon[0] if fuel_lat_lon else None,
                        longitude=fuel_lat_lon[1] if fuel_lat_lon else None,
                        duration_minutes=FUEL_STOP_DURATION_MINUTES,
                        notes="Fueling stop inserted at approximately every 1,000 miles",
                    )
                    state.miles_since_last_fuel -= Decimal(FUEL_STOP_DISTANCE_MILES)

            if leg.sequence == 1:
                self._add_on_duty_stop(
                    state=state,
                    stops=stops,
                    duty_segments=duty_segments,
                    stop_type=StopType.PICKUP,
                    location_name=leg.end_name,
                    latitude=pickup_point.latitude,
                    longitude=pickup_point.longitude,
                    duration_minutes=PICKUP_DURATION_MINUTES,
                    notes="Pickup service time",
                )

        self._add_on_duty_stop(
            state=state,
            stops=stops,
            duty_segments=duty_segments,
            stop_type=StopType.DROPOFF,
            location_name=request.dropoff_location,
            latitude=dropoff_point.latitude,
            longitude=dropoff_point.longitude,
            duration_minutes=DROPOFF_DURATION_MINUTES,
            notes="Dropoff service time",
        )

        warnings.append("Cycle recap is simplified: 70-hour remaining is treated as a static budget for this MVP.")
        return TripPlanResult(route=route, stops=stops, duty_segments=duty_segments, warnings=warnings)

    def _default_start_time(self) -> datetime:
        """Anchor 'today' and default shift start to Django TIME_ZONE (APP_TIMEZONE), stored as UTC."""
        tz = ZoneInfo(settings.TIME_ZONE)
        now_local = timezone.now().astimezone(tz)
        shift_local = now_local.replace(
            hour=DEFAULT_SHIFT_START_HOUR, minute=0, second=0, microsecond=0
        )
        return shift_local.astimezone(dt_timezone.utc)

    def _resolve_zero_capacity(
        self,
        route: NormalizedRoute,
        state: EngineState,
        stops: list[StopData],
        duty_segments: list[DutySegmentData],
    ) -> None:
        stop_lat_lon = self._interpolate_lat_lon(route=route, miles_from_start=state.miles_driven_total)
        if state.shift_driving_minutes >= MAX_DRIVING_PER_SHIFT_MINUTES or state.shift_elapsed_minutes >= MAX_SHIFT_WINDOW_MINUTES:
            # Use sleeper-berth for overnight reset to match classic ELD semantics.
            self._add_sleeper_stop(
                state=state,
                stops=stops,
                duty_segments=duty_segments,
                stop_type=StopType.OVERNIGHT_RESET,
                latitude=stop_lat_lon[0] if stop_lat_lon else None,
                longitude=stop_lat_lon[1] if stop_lat_lon else None,
                duration_minutes=RESET_DURATION_MINUTES,
                notes="10-hour reset due to 11-hour driving or 14-hour window limit",
            )
            state.shift_start_time = state.current_time
            state.shift_driving_minutes = 0
            state.shift_elapsed_minutes = 0
            state.driving_since_break_minutes = 0
            state.day_index += 1
            return

        if state.driving_since_break_minutes >= BREAK_REQUIRED_AFTER_DRIVING_MINUTES:
            self._add_off_duty_stop(
                state=state,
                stops=stops,
                duty_segments=duty_segments,
                stop_type=StopType.BREAK,
                latitude=stop_lat_lon[0] if stop_lat_lon else None,
                longitude=stop_lat_lon[1] if stop_lat_lon else None,
                duration_minutes=BREAK_DURATION_MINUTES,
                notes="30-minute non-driving break after 8 cumulative driving hours",
            )
            state.shift_elapsed_minutes += BREAK_DURATION_MINUTES
            state.driving_since_break_minutes = 0
            return

    def _add_duty_segment(
        self,
        duty_segments: list[DutySegmentData],
        state: EngineState,
        segment_type: str,
        duration_minutes: int,
        location_context: str,
        notes: str = "",
    ) -> tuple[datetime, datetime]:
        start_time = state.current_time
        end_time = state.current_time + timedelta(minutes=duration_minutes)
        duty_segments.append(
            DutySegmentData(
                day_index=state.day_index,
                segment_type=segment_type,
                start_time=start_time,
                end_time=end_time,
                duration_minutes=duration_minutes,
                location_context=location_context,
                notes=notes,
            ),
        )
        state.current_time = end_time
        return start_time, end_time

    def _add_on_duty_stop(
        self,
        state: EngineState,
        stops: list[StopData],
        duty_segments: list[DutySegmentData],
        stop_type: str,
        location_name: str,
        duration_minutes: int,
        notes: str,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> None:
        if duration_minutes > 0:
            start_time, end_time = self._add_duty_segment(
                duty_segments=duty_segments,
                state=state,
                segment_type=DutyStatus.ON_DUTY_NOT_DRIVING,
                duration_minutes=duration_minutes,
                location_context=location_name,
                notes=notes,
            )
            state.shift_elapsed_minutes += duration_minutes
            state.cycle_on_duty_minutes += duration_minutes
        else:
            start_time = end_time = state.current_time

        stops.append(
            StopData(
                stop_type=stop_type,
                sequence=state.stop_sequence,
                location_name=location_name,
                latitude=latitude,
                longitude=longitude,
                planned_arrival=start_time,
                planned_departure=end_time,
                duration_minutes=duration_minutes,
                notes=notes,
            ),
        )
        state.stop_sequence += 1

    def _add_sleeper_stop(
        self,
        state: EngineState,
        stops: list[StopData],
        duty_segments: list[DutySegmentData],
        stop_type: str,
        duration_minutes: int,
        notes: str,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> None:
        start_time, end_time = self._add_duty_segment(
            duty_segments=duty_segments,
            state=state,
            segment_type=DutyStatus.SLEEPER,
            duration_minutes=duration_minutes,
            location_context="Sleeper berth",
            notes=notes,
        )
        stops.append(
            StopData(
                stop_type=stop_type,
                sequence=state.stop_sequence,
                location_name="Sleeper berth",
                latitude=latitude,
                longitude=longitude,
                planned_arrival=start_time,
                planned_departure=end_time,
                duration_minutes=duration_minutes,
                notes=notes,
            ),
        )
        state.stop_sequence += 1

    def _interpolate_lat_lon(
        self,
        route: NormalizedRoute,
        miles_from_start: Decimal,
    ) -> tuple[float, float] | None:
        """
        Interpolate a lat/lon along the route's LineString geometry by distance.

        We approximate where to place inserted compliance stops along the planned route by:
        1) computing cumulative haversine distance along the route coordinates
        2) mapping `miles_from_start` onto that distance curve
        3) linear interpolation between the segment endpoints
        """

        if not route.geometry_geojson:
            return None

        coords = route.geometry_geojson.get("coordinates")
        if not isinstance(coords, list) or len(coords) < 2:
            return None

        # Convert GeoJSON [lon, lat] -> arrays of [lat, lon]
        points: list[tuple[float, float]] = []
        for pair in coords:
            if not isinstance(pair, list) or len(pair) < 2:
                continue
            lon = float(pair[0])
            lat = float(pair[1])
            points.append((lat, lon))

        if len(points) < 2:
            return None

        if route.total_distance_miles <= 0:
            return None

        # Compute cumulative distance along the geometry.
        cumulative: list[float] = [0.0]
        running = 0.0
        for i in range(1, len(points)):
            lat1, lon1 = points[i - 1]
            lat2, lon2 = points[i]
            running += self._haversine_miles(lat1, lon1, lat2, lon2)
            cumulative.append(running)

        if running <= 0:
            return None

        # Map miles_from_start (relative to provider total distance) onto geometry length.
        fraction = float(miles_from_start / route.total_distance_miles)
        fraction = min(1.0, max(0.0, fraction))
        target = fraction * running

        # Find segment containing `target`.
        for i in range(1, len(cumulative)):
            seg_start = cumulative[i - 1]
            seg_end = cumulative[i]
            if target <= seg_end:
                seg_len = seg_end - seg_start
                if seg_len <= 0:
                    lat, lon = points[i]
                    return (lat, lon)
                t = (target - seg_start) / seg_len
                lat1, lon1 = points[i - 1]
                lat2, lon2 = points[i]
                lat = lat1 + t * (lat2 - lat1)
                lon = lon1 + t * (lon2 - lon1)
                return (lat, lon)

        # Fallback to last point.
        lat, lon = points[-1]
        return (lat, lon)

    def _add_off_duty_stop(
        self,
        state: EngineState,
        stops: list[StopData],
        duty_segments: list[DutySegmentData],
        stop_type: str,
        duration_minutes: int,
        notes: str,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> None:
        start_time, end_time = self._add_duty_segment(
            duty_segments=duty_segments,
            state=state,
            segment_type=DutyStatus.OFF_DUTY,
            duration_minutes=duration_minutes,
            location_context="En route",
            notes=notes,
        )
        stops.append(
            StopData(
                stop_type=stop_type,
                sequence=state.stop_sequence,
                location_name="En route",
                latitude=latitude,
                longitude=longitude,
                planned_arrival=start_time,
                planned_departure=end_time,
                duration_minutes=duration_minutes,
                notes=notes,
            ),
        )
        state.stop_sequence += 1
