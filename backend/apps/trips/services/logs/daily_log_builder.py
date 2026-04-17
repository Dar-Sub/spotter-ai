"""Daily log transformation service."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from datetime import timezone as dt_timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils import timezone as dj_timezone

from apps.trips.enums import DutyStatus
from apps.trips.services.contracts import DailyLogData, DailyLogEntryData, DutySegmentData


@dataclass(slots=True)
class SegmentSlice:
    log_date: str
    segment_type: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    start_minute: int
    end_minute: int
    location_context: str
    notes: str


class DailyLogBuilder:
    """Builds daily logs using calendar midnights in Django TIME_ZONE (see APP_TIMEZONE)."""

    def _planning_tz(self) -> ZoneInfo:
        return ZoneInfo(settings.TIME_ZONE)

    def _day_start_utc(self, log_date: str) -> datetime:
        d = date.fromisoformat(log_date)
        return datetime.combine(d, time.min, tzinfo=self._planning_tz()).astimezone(dt_timezone.utc)

    def _ensure_aware_utc(self, dt: datetime) -> datetime:
        if dj_timezone.is_naive(dt):
            return dj_timezone.make_aware(dt, dt_timezone.utc)
        return dt

    def build(
        self,
        duty_segments: list[DutySegmentData],
        total_trip_miles: Decimal,
    ) -> list[DailyLogData]:
        if not duty_segments:
            return []

        total_driving_minutes = sum(
            segment.duration_minutes for segment in duty_segments if segment.segment_type == DutyStatus.DRIVING
        )
        miles_per_driving_minute = (
            (total_trip_miles / Decimal(total_driving_minutes)) if total_driving_minutes > 0 else Decimal("0")
        )

        grouped_slices: dict[str, list[SegmentSlice]] = defaultdict(list)
        for segment in duty_segments:
            for section in self._split_by_day(segment):
                grouped_slices[section.log_date].append(section)

        logs: list[DailyLogData] = []
        for log_date in sorted(grouped_slices.keys()):
            slices = sorted(grouped_slices[log_date], key=lambda s: s.start_minute)
            day_start_utc = self._day_start_utc(log_date)

            # Ensure the full 24h window is represented by filling gaps with implied off-duty.
            filled_slices: list[SegmentSlice] = []
            cursor = 0
            for section in slices:
                if section.start_minute > cursor:
                    gap_start = day_start_utc + timedelta(minutes=cursor)
                    gap_end = section.start_time
                    gap_minutes = int((gap_end - gap_start).total_seconds() // 60)
                    if gap_minutes > 0:
                        filled_slices.append(
                            SegmentSlice(
                                log_date=log_date,
                                segment_type=DutyStatus.OFF_DUTY,
                                start_time=gap_start,
                                end_time=gap_end,
                                duration_minutes=gap_minutes,
                                start_minute=cursor,
                                end_minute=section.start_minute,
                                location_context="Off duty (implied gap)",
                                notes="Implied off-duty between recorded duty segments.",
                            ),
                        )
                filled_slices.append(section)
                cursor = section.end_minute

            if cursor < 24 * 60:
                day_end_exclusive = day_start_utc + timedelta(days=1)
                gap_start = day_start_utc + timedelta(minutes=cursor)
                gap_minutes = int((day_end_exclusive - gap_start).total_seconds() // 60)
                if gap_minutes > 0:
                    filled_slices.append(
                        SegmentSlice(
                            log_date=log_date,
                            segment_type=DutyStatus.OFF_DUTY,
                            start_time=gap_start,
                            end_time=day_end_exclusive - timedelta(microseconds=1),
                            duration_minutes=gap_minutes,
                            start_minute=cursor,
                            end_minute=24 * 60,
                            location_context="Off duty (implied gap)",
                            notes="Implied off-duty to end of day.",
                        ),
                    )

            slices = filled_slices
            minutes_by_type = defaultdict(int)
            day_miles = Decimal("0")
            entries: list[DailyLogEntryData] = []

            for section in slices:
                minutes_by_type[section.segment_type] += section.duration_minutes
                if section.segment_type == DutyStatus.DRIVING:
                    day_miles += Decimal(section.duration_minutes) * miles_per_driving_minute
                entries.append(
                    DailyLogEntryData(
                        segment_type=section.segment_type,
                        start_minute=section.start_minute,
                        end_minute=section.end_minute,
                        start_time=section.start_time,
                        end_time=section.end_time,
                        location_context=section.location_context,
                        notes=section.notes,
                    ),
                )

            logs.append(
                DailyLogData(
                    log_date=log_date,
                    total_miles=day_miles.quantize(Decimal("0.01")),
                    off_duty_hours=(Decimal(minutes_by_type[DutyStatus.OFF_DUTY]) / Decimal("60")).quantize(
                        Decimal("0.01")
                    ),
                    sleeper_hours=(Decimal(minutes_by_type[DutyStatus.SLEEPER]) / Decimal("60")).quantize(
                        Decimal("0.01")
                    ),
                    driving_hours=(Decimal(minutes_by_type[DutyStatus.DRIVING]) / Decimal("60")).quantize(
                        Decimal("0.01")
                    ),
                    on_duty_hours=(
                        Decimal(minutes_by_type[DutyStatus.ON_DUTY_NOT_DRIVING]) / Decimal("60")
                    ).quantize(Decimal("0.01")),
                    remarks="Auto-generated from duty segments.",
                    entries=entries,
                ),
            )
        return logs

    def _split_by_day(self, segment: DutySegmentData) -> list[SegmentSlice]:
        tz = self._planning_tz()
        start = self._ensure_aware_utc(segment.start_time)
        end = self._ensure_aware_utc(segment.end_time)
        slices: list[SegmentSlice] = []

        while start < end:
            start_local = start.astimezone(tz)
            local_date = start_local.date()
            log_date = local_date.isoformat()

            next_local_midnight = datetime.combine(local_date + timedelta(days=1), time.min, tzinfo=tz)
            day_end_utc = next_local_midnight.astimezone(dt_timezone.utc)

            section_end = min(end, day_end_utc)
            duration_minutes = int((section_end - start).total_seconds() // 60)
            if duration_minutes <= 0:
                break

            start_minute = start_local.hour * 60 + start_local.minute
            end_minute = min(24 * 60, start_minute + duration_minutes)

            slices.append(
                SegmentSlice(
                    log_date=log_date,
                    segment_type=segment.segment_type,
                    start_time=start,
                    end_time=section_end,
                    duration_minutes=duration_minutes,
                    start_minute=start_minute,
                    end_minute=end_minute,
                    location_context=segment.location_context,
                    notes=segment.notes,
                ),
            )
            start = section_end

        return slices
