import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_endpoint():
    client = APIClient()
    response = client.get("/api/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.django_db
def test_plan_trip_creates_trip():
    client = APIClient()
    response = client.post(
        "/api/trips/plan/",
        {
            "current_location": "Chicago, IL",
            "pickup_location": "Indianapolis, IN",
            "dropoff_location": "Atlanta, GA",
            "current_cycle_used_hours": "12.5",
        },
        format="json",
    )
    assert response.status_code == 201
    data = response.json()
    assert data["trip_status"] == "planned"
    assert len(data["route_legs"]) == 2
    assert "daily_logs" in data
