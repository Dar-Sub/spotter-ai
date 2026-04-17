from datetime import datetime, timezone
from decimal import Decimal

import pytest
from django.test import override_settings

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


@pytest.mark.django_db
@override_settings(TIME_ZONE="America/New_York")
def test_daily_log_builder_splits_at_local_midnight_not_utc_midnight():
    """Jun 15 02:30–06:30 UTC is Jun 14 22:30 – Jun 15 02:30 Eastern; two local calendar days."""
    builder = DailyLogBuilder()
    segments = [
        DutySegmentData(
            day_index=1,
            segment_type=DutyStatus.DRIVING,
            start_time=datetime(2026, 6, 15, 2, 30, tzinfo=timezone.utc),
            end_time=datetime(2026, 6, 15, 6, 30, tzinfo=timezone.utc),
            duration_minutes=240,
            location_context="overnight",
        ),
    ]

    logs = builder.build(duty_segments=segments, total_trip_miles=Decimal("240"))
    assert len(logs) == 2
    assert logs[0].log_date == "2026-06-14"
    assert logs[1].log_date == "2026-06-15"
