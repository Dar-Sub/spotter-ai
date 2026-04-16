"""Application service orchestrating route and HOS planning."""

from apps.trips.enums import TripStatus
from apps.trips.models import DailyLog, DutySegment, RouteLeg, Stop, Trip
from apps.trips.services.contracts import HOSSimulationEngine, RouteService, TripPlanRequest, TripPlanResult
from apps.trips.services.logs.daily_log_builder import DailyLogBuilder
from apps.trips.services.route_service import build_route_service

from .hos.engine import BasicHOSEngine


class TripPlannerService:
    def __init__(
        self,
        route_service: RouteService | None = None,
        hos_engine: HOSSimulationEngine | None = None,
        daily_log_builder: DailyLogBuilder | None = None,
    ) -> None:
        self.route_service = route_service or build_route_service()
        self.hos_engine = hos_engine or BasicHOSEngine()
        self.daily_log_builder = daily_log_builder or DailyLogBuilder()

    def plan_trip(self, request: TripPlanRequest) -> tuple[Trip, TripPlanResult]:
        route = self.route_service.build_trip_route(
            current_location=request.current_location,
            pickup_location=request.pickup_location,
            dropoff_location=request.dropoff_location,
        )

        trip = Trip.objects.create(
            current_location_text=request.current_location,
            pickup_location_text=request.pickup_location,
            dropoff_location_text=request.dropoff_location,
            current_cycle_used_hours=request.current_cycle_used_hours,
            total_distance_miles=route.total_distance_miles,
            estimated_raw_drive_duration_minutes=route.total_duration_minutes,
            trip_status=TripStatus.PLANNED,
        )

        RouteLeg.objects.bulk_create(
            [
                RouteLeg(
                    trip=trip,
                    sequence=leg.sequence,
                    start_name=leg.start_name,
                    end_name=leg.end_name,
                    distance_miles=leg.distance_miles,
                    duration_minutes=leg.duration_minutes,
                    geometry_geojson=leg.geometry_geojson,
                )
                for leg in route.legs
            ],
        )

        result = self.hos_engine.simulate(request=request, route=route)
        result.daily_logs = self.daily_log_builder.build(
            duty_segments=result.duty_segments,
            total_trip_miles=route.total_distance_miles,
        )

        Stop.objects.bulk_create(
            [
                Stop(
                    trip=trip,
                    stop_type=stop.stop_type,
                    sequence=stop.sequence,
                    location_name=stop.location_name,
                    latitude=stop.latitude,
                    longitude=stop.longitude,
                    planned_arrival=stop.planned_arrival,
                    planned_departure=stop.planned_departure,
                    duration_minutes=stop.duration_minutes,
                    notes=stop.notes,
                )
                for stop in result.stops
            ],
        )
        DutySegment.objects.bulk_create(
            [
                DutySegment(
                    trip=trip,
                    day_index=segment.day_index,
                    segment_type=segment.segment_type,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    duration_minutes=segment.duration_minutes,
                    location_context=segment.location_context,
                    notes=segment.notes,
                )
                for segment in result.duty_segments
            ],
        )
        DailyLog.objects.bulk_create(
            [
                DailyLog(
                    trip=trip,
                    log_date=log.log_date,
                    total_miles=log.total_miles,
                    off_duty_hours=log.off_duty_hours,
                    sleeper_hours=log.sleeper_hours,
                    driving_hours=log.driving_hours,
                    on_duty_hours=log.on_duty_hours,
                    remarks=log.remarks,
                    log_entries=[
                        {
                            "segment_type": entry.segment_type,
                            "start_minute": entry.start_minute,
                            "end_minute": entry.end_minute,
                            "start_time": entry.start_time.isoformat(),
                            "end_time": entry.end_time.isoformat(),
                            "location_context": entry.location_context,
                            "notes": entry.notes,
                        }
                        for entry in log.entries
                    ],
                )
                for log in result.daily_logs
            ],
        )
        return trip, result
