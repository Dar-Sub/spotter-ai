from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.trips.models import Trip
from apps.trips.services.contracts import TripPlanRequest
from apps.trips.services.route_service import RouteServiceError
from apps.trips.services.trip_planner_service import TripPlannerService

from .serializers import TripDetailSerializer, TripPlanRequestSerializer


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok"})


class TripPlanView(APIView):
    authentication_classes = []
    permission_classes = []
    service_class = TripPlannerService

    def post(self, request):
        serializer = TripPlanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        service = self.service_class()
        try:
            trip, result = service.plan_trip(
                TripPlanRequest(
                    current_location=payload["current_location"],
                    pickup_location=payload["pickup_location"],
                    dropoff_location=payload["dropoff_location"],
                    current_cycle_used_hours=payload["current_cycle_used_hours"],
                    start_time=payload.get("start_time"),
                ),
            )
        except RouteServiceError as exc:
            return Response(
                {"detail": str(exc), "code": "route_unavailable"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        trip_data = TripDetailSerializer(trip).data
        trip_data["warnings"] = result.warnings
        trip_data["daily_logs_preview"] = [
            {
                "log_date": log.log_date,
                "total_miles": str(log.total_miles),
                "off_duty_hours": str(log.off_duty_hours),
                "sleeper_hours": str(log.sleeper_hours),
                "driving_hours": str(log.driving_hours),
                "on_duty_hours": str(log.on_duty_hours),
                "remarks": log.remarks,
                "entries": [
                    {
                        "segment_type": entry.segment_type,
                        "start_minute": entry.start_minute,
                        "end_minute": entry.end_minute,
                        "location_context": entry.location_context,
                        "notes": entry.notes,
                    }
                    for entry in log.entries
                ],
            }
            for log in result.daily_logs
        ]
        trip_data["route_summary"] = {
            "total_distance_miles": str(result.route.total_distance_miles),
            "total_duration_minutes": result.route.total_duration_minutes,
            "geometry_geojson": result.route.geometry_geojson,
            "points": [
                {"name": point.name, "latitude": point.latitude, "longitude": point.longitude}
                for point in result.route.points
            ],
        }
        return Response(trip_data, status=status.HTTP_201_CREATED)


class TripDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, trip_id: int):
        trip = (
            Trip.objects.prefetch_related("route_legs", "stops", "duty_segments", "daily_logs")
            .filter(pk=trip_id)
            .first()
        )
        if not trip:
            return Response({"detail": "Trip not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(TripDetailSerializer(trip).data)
