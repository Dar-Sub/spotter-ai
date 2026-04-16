from django.db import models

from apps.trips.enums import DutyStatus

from .trip import Trip


class DutySegment(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="duty_segments")
    day_index = models.PositiveIntegerField()
    segment_type = models.CharField(max_length=32, choices=DutyStatus.choices)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    location_context = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self) -> str:
        return f"DutySegment {self.segment_type} ({self.start_time} -> {self.end_time})"
