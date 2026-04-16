from django.db import models

from .trip import Trip


class RouteLeg(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="route_legs")
    sequence = models.PositiveIntegerField()
    start_name = models.CharField(max_length=255)
    end_name = models.CharField(max_length=255)
    distance_miles = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField()
    geometry_geojson = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(fields=["trip", "sequence"], name="unique_trip_leg_sequence"),
        ]

    def __str__(self) -> str:
        return f"RouteLeg {self.sequence} ({self.start_name} -> {self.end_name})"
