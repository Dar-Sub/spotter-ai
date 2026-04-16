from decimal import Decimal

import pytest

from apps.trips.services.contracts import TripPlanRequest
from apps.trips.services.trip_planner_service import TripPlannerService


@pytest.mark.django_db
def test_trip_planner_persists_trip_and_route_legs():
    service = TripPlannerService()
    trip, result = service.plan_trip(
        TripPlanRequest(
            current_location="Chicago, IL",
            pickup_location="Indianapolis, IN",
            dropoff_location="Atlanta, GA",
            current_cycle_used_hours=Decimal("20.0"),
        ),
    )

    assert trip.pk is not None
    assert trip.route_legs.count() == 2
    assert result.route.total_distance_miles == Decimal("740.0")
