"""Rolling 70-hour / 8-calendar-day on-duty window (FMCSA property-carrying, planning TZ)."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from datetime import timezone as dt_timezone
from zoneinfo import ZoneInfo

from apps.trips.constants import MAX_CYCLE_ON_DUTY_MINUTES


class Rolling70Hour8DayWindow:
    """
    Tracks on-duty minutes (driving + on-duty-not-driving only) per local calendar day.

    At any instant ``as_of``, the regulated window is the eight consecutive calendar dates
    ending on ``as_of``'s local date (inclusive). The sum of on-duty minutes on those days
    must not exceed ``MAX_CYCLE_ON_DUTY_MINUTES`` (70h).

    Initial ``current_cycle_used_hours`` from the request is spread evenly across those
    eight days at trip start so the window total matches the declared usage.
    """

    __slots__ = ("tz", "buckets")

    def __init__(self, tz: ZoneInfo, trip_start: datetime, initial_on_duty_used_minutes: int) -> None:
        if trip_start.tzinfo is None:
            msg = "Rolling70Hour8DayWindow requires timezone-aware datetimes"
            raise ValueError(msg)
        self.tz = tz
        anchor = trip_start.astimezone(tz).date()
        self.buckets: dict[date, int] = {}
        days = [anchor - timedelta(days=7 - i) for i in range(8)]
        total = max(0, int(initial_on_duty_used_minutes))
        base, rem = divmod(total, 8)
        for i, d in enumerate(days):
            self.buckets[d] = base + (1 if i < rem else 0)

    def window_sum_minutes(self, as_of: datetime) -> int:
        end_d = as_of.astimezone(self.tz).date()
        start_d = end_d - timedelta(days=7)
        total = 0
        d = start_d
        while d <= end_d:
            total += self.buckets.get(d, 0)
            d += timedelta(days=1)
        self._prune_before(start_d)
        return total

    def _prune_before(self, oldest_in_window: date) -> None:
        stale = [d for d in self.buckets if d < oldest_in_window]
        for d in stale:
            del self.buckets[d]

    def remaining_on_duty_minutes(self, as_of: datetime) -> int:
        return max(0, MAX_CYCLE_ON_DUTY_MINUTES - self.window_sum_minutes(as_of))

    def max_on_duty_chunk_minutes(self, start: datetime, upper_bound: int) -> int:
        if upper_bound <= 0:
            return 0
        if not self._would_exceed_after_add(start, upper_bound):
            return upper_bound
        lo, hi = 0, upper_bound
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self._would_exceed_after_add(start, mid):
                hi = mid - 1
            else:
                lo = mid
        return lo

    def _would_exceed_after_add(self, start: datetime, minutes: int) -> bool:
        if minutes <= 0:
            return False
        snap = self.buckets.copy()
        self.allocate_on_duty_minutes(start, minutes)
        end = start + timedelta(minutes=minutes)
        over = self.window_sum_minutes(end) > MAX_CYCLE_ON_DUTY_MINUTES
        self.buckets = snap
        return over

    def allocate_on_duty_minutes(self, start: datetime, minutes: int) -> None:
        """Add on-duty minutes, splitting at local midnights in ``self.tz``."""
        remaining = minutes
        t = start
        guard = 0
        while remaining > 0:
            guard += 1
            if guard > 5000:
                msg = "allocate_on_duty_minutes exceeded iteration guard"
                raise RuntimeError(msg)
            tl = t.astimezone(self.tz)
            d = tl.date()
            next_local_mid = datetime.combine(d + timedelta(days=1), time.min, tzinfo=self.tz)
            next_utc = next_local_mid.astimezone(dt_timezone.utc)
            room = int((next_utc - t).total_seconds() // 60)
            if room <= 0:
                t = next_utc
                continue
            chunk = min(remaining, room)
            self.buckets[d] = self.buckets.get(d, 0) + chunk
            remaining -= chunk
            t += timedelta(minutes=chunk)
