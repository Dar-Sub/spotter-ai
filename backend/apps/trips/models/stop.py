from django.db import models

from apps.trips.enums import StopType

from .trip import Trip


class Stop(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="stops")
    stop_type = models.CharField(max_length=32, choices=StopType.choices)
    sequence = models.PositiveIntegerField()
    location_name = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    planned_arrival = models.DateTimeField(null=True, blank=True)
    planned_departure = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(fields=["trip", "sequence"], name="unique_trip_stop_sequence"),
        ]

    def __str__(self) -> str:
        return f"Stop {self.sequence} ({self.stop_type})"
