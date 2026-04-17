"""Domain enums for trip planning."""

from django.db import models


class TripStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PLANNED = "planned", "Planned"
    FAILED = "failed", "Failed"


class StopType(models.TextChoices):
    PICKUP = "pickup", "Pickup"
    DROPOFF = "dropoff", "Dropoff"
    FUEL = "fuel", "Fuel"
    BREAK = "break", "Break"
    OVERNIGHT_RESET = "overnight_reset", "Overnight Reset"
    CYCLE_WINDOW_WAIT = "cycle_window_wait", "Cycle window wait"


class DutyStatus(models.TextChoices):
    OFF_DUTY = "off_duty", "Off Duty"
    SLEEPER = "sleeper", "Sleeper Berth"
    DRIVING = "driving", "Driving"
    ON_DUTY_NOT_DRIVING = "on_duty_not_driving", "On Duty Not Driving"
