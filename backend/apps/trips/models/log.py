from django.db import models

from .trip import Trip


class DailyLog(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="daily_logs")
    log_date = models.DateField()
    total_miles = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    off_duty_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sleeper_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    driving_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    on_duty_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)
    log_entries = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["log_date"]
        constraints = [
            models.UniqueConstraint(fields=["trip", "log_date"], name="unique_trip_log_date"),
        ]

    def __str__(self) -> str:
        return f"DailyLog {self.log_date} (Trip {self.trip_id})"
