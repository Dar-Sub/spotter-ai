from datetime import datetime, timezone
from decimal import Decimal

from apps.trips.enums import DutyStatus
from apps.trips.services.contracts import DutySegmentData
from apps.trips.services.logs.daily_log_builder import DailyLogBuilder


def test_daily_log_builder_generates_single_day_totals():
    builder = DailyLogBuilder()
    segments = [
        DutySegmentData(
            day_index=1,
            segment_type=DutyStatus.DRIVING,
            start_time=datetime(2026, 4, 16, 6, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 4, 16, 10, 0, tzinfo=timezone.utc),
            duration_minutes=240,
            location_context="A -> B",
        ),
        DutySegmentData(
            day_index=1,
            segment_type=DutyStatus.ON_DUTY_NOT_DRIVING,
            start_time=datetime(2026, 4, 16, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 4, 16, 11, 0, tzinfo=timezone.utc),
            duration_minutes=60,
            location_context="Pickup",
        ),
    ]

    logs = builder.build(duty_segments=segments, total_trip_miles=Decimal("400"))
    assert len(logs) == 1
    assert logs[0].driving_hours == Decimal("4.00")
    assert logs[0].on_duty_hours == Decimal("1.00")
    assert logs[0].total_miles == Decimal("400.00")


def test_daily_log_builder_splits_cross_midnight_segments():
    builder = DailyLogBuilder()
    segments = [
        DutySegmentData(
            day_index=1,
            segment_type=DutyStatus.DRIVING,
            start_time=datetime(2026, 4, 16, 23, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 4, 17, 1, 0, tzinfo=timezone.utc),
            duration_minutes=120,
            location_context="Overnight leg",
        ),
    ]

    logs = builder.build(duty_segments=segments, total_trip_miles=Decimal("120"))
    assert len(logs) == 2
    assert logs[0].driving_hours == Decimal("1.00")
    assert logs[1].driving_hours == Decimal("1.00")
