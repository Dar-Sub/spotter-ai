"""Daily log transformation service."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from decimal import Decimal

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

            # Ensure the full 24h window is represented by filling gaps with implied off-duty.
            filled_slices: list[SegmentSlice] = []
            cursor = 0
            for section in slices:
                if section.start_minute > cursor:
                    gap_minutes = section.start_minute - cursor
                    filled_slices.append(
                        SegmentSlice(
                            log_date=log_date,
                            segment_type=DutyStatus.OFF_DUTY,
                            start_time=section.start_time.replace(hour=cursor // 60, minute=cursor % 60),
                            end_time=section.start_time.replace(
                                hour=section.start_minute // 60,
                                minute=section.start_minute % 60,
                            ),
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
                # Trailing off-duty to midnight.
                last = slices[-1]
                gap_minutes = 24 * 60 - cursor
                filled_slices.append(
                    SegmentSlice(
                        log_date=log_date,
                        segment_type=DutyStatus.OFF_DUTY,
                        start_time=last.end_time.replace(hour=cursor // 60, minute=cursor % 60),
                        end_time=last.end_time.replace(hour=23, minute=59),
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
        start = segment.start_time
        end = segment.end_time
        slices: list[SegmentSlice] = []

        while start < end:
            day_end = datetime.combine(start.date(), time.max, tzinfo=start.tzinfo) + timedelta(microseconds=1)
            section_end = min(end, day_end)
            duration_minutes = int((section_end - start).total_seconds() // 60)
            if duration_minutes <= 0:
                break
            start_minute = start.hour * 60 + start.minute
            end_minute = min(24 * 60, start_minute + duration_minutes)
            slices.append(
                SegmentSlice(
                    log_date=start.date().isoformat(),
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
