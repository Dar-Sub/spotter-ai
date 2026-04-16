from rest_framework import serializers

from apps.trips.models import DailyLog, DutySegment, RouteLeg, Stop, Trip


class TripPlanRequestSerializer(serializers.Serializer):
    current_location = serializers.CharField(max_length=255)
    pickup_location = serializers.CharField(max_length=255)
    dropoff_location = serializers.CharField(max_length=255)
    current_cycle_used_hours = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=70)
    start_time = serializers.DateTimeField(required=False)


class RouteLegSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteLeg
        fields = (
            "sequence",
            "start_name",
            "end_name",
            "distance_miles",
            "duration_minutes",
            "geometry_geojson",
        )


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = (
            "stop_type",
            "sequence",
            "location_name",
            "latitude",
            "longitude",
            "planned_arrival",
            "planned_departure",
            "duration_minutes",
            "notes",
        )


class DutySegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DutySegment
        fields = (
            "day_index",
            "segment_type",
            "start_time",
            "end_time",
            "duration_minutes",
            "location_context",
            "notes",
        )


class DailyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyLog
        fields = (
            "log_date",
            "total_miles",
            "off_duty_hours",
            "sleeper_hours",
            "driving_hours",
            "on_duty_hours",
            "remarks",
            "log_entries",
        )


class TripDetailSerializer(serializers.ModelSerializer):
    route_legs = RouteLegSerializer(many=True)
    stops = StopSerializer(many=True)
    duty_segments = DutySegmentSerializer(many=True)
    daily_logs = DailyLogSerializer(many=True)

    class Meta:
        model = Trip
        fields = (
            "id",
            "current_location_text",
            "pickup_location_text",
            "dropoff_location_text",
            "current_cycle_used_hours",
            "total_distance_miles",
            "estimated_raw_drive_duration_minutes",
            "trip_status",
            "created_at",
            "updated_at",
            "route_legs",
            "stops",
            "duty_segments",
            "daily_logs",
        )
