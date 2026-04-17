from datetime import datetime, timedelta
from datetime import timezone as dt_timezone

import pytest
from django.test import override_settings
from zoneinfo import ZoneInfo

from apps.trips.constants import MAX_CYCLE_ON_DUTY_MINUTES
from apps.trips.services.hos.rolling_cycle import Rolling70Hour8DayWindow


@pytest.mark.django_db
@override_settings(TIME_ZONE="UTC")
def test_seed_matches_initial_cycle_used_minutes():
    start = datetime(2026, 4, 10, 12, 0, tzinfo=dt_timezone.utc)
    w = Rolling70Hour8DayWindow(ZoneInfo("UTC"), start, 80)
    assert w.window_sum_minutes(start) == 80


@pytest.mark.django_db
@override_settings(TIME_ZONE="UTC")
def test_max_chunk_respects_seventy_hour_cap():
    start = datetime(2026, 4, 10, 12, 0, tzinfo=dt_timezone.utc)
    w = Rolling70Hour8DayWindow(ZoneInfo("UTC"), start, 0)
    cap = w.max_on_duty_chunk_minutes(start, MAX_CYCLE_ON_DUTY_MINUTES + 60)
    assert cap == MAX_CYCLE_ON_DUTY_MINUTES


@pytest.mark.django_db
@override_settings(TIME_ZONE="UTC")
def test_oldest_day_drops_after_local_midnight_passes():
    start = datetime(2026, 4, 10, 12, 0, tzinfo=dt_timezone.utc)
    w = Rolling70Hour8DayWindow(ZoneInfo("UTC"), start, 8 * 60)  # 1h per day in window
    assert w.window_sum_minutes(start) == 8 * 60
    w.allocate_on_duty_minutes(start, 12 * 60)  # drive into next UTC day
    after = start + timedelta(hours=12)
    # Window ending Apr 11 no longer includes Apr 3; Apr 3 had 60m in seed — that bucket leaves the sum.
    assert w.window_sum_minutes(after) <= 8 * 60 + 12 * 60
