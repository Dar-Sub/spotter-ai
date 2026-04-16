from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.trips.enums import TripStatus


class Trip(models.Model):
    current_location_text = models.CharField(max_length=255)
    pickup_location_text = models.CharField(max_length=255)
    dropoff_location_text = models.CharField(max_length=255)
    current_cycle_used_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(70)],
    )
    total_distance_miles = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_raw_drive_duration_minutes = models.IntegerField(default=0)
    trip_status = models.CharField(
        max_length=32,
        choices=TripStatus.choices,
        default=TripStatus.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Trip {self.pk} ({self.current_location_text} -> {self.dropoff_location_text})"
