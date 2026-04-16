"""Route provider adapters with normalized response mapping."""

import os
from decimal import Decimal

import httpx

from .contracts import NormalizedRoute, RouteLegData, RoutePoint, RouteService


class RouteServiceError(Exception):
    """Raised when route acquisition fails."""


class StubRouteService:
    """
    Temporary route service.

    This deterministic fallback keeps development moving until the external
    routing provider integration is implemented in Phase 2.
    """

    def build_trip_route(
        self,
        current_location: str,
        pickup_location: str,
        dropoff_location: str,
    ) -> NormalizedRoute:
        if not all([current_location, pickup_location, dropoff_location]):
            raise RouteServiceError("All location fields are required for route planning.")

        legs = [
            RouteLegData(
                sequence=1,
                start_name=current_location,
                end_name=pickup_location,
                distance_miles=Decimal("120.0"),
                duration_minutes=130,
                geometry_geojson={},
            ),
            RouteLegData(
                sequence=2,
                start_name=pickup_location,
                end_name=dropoff_location,
                distance_miles=Decimal("620.0"),
                duration_minutes=640,
                geometry_geojson={},
            ),
        ]

        points = [
            RoutePoint(name=current_location, latitude=41.8781, longitude=-87.6298),
            RoutePoint(name=pickup_location, latitude=39.7684, longitude=-86.1581),
            RoutePoint(name=dropoff_location, latitude=33.7490, longitude=-84.3880),
        ]

        return NormalizedRoute(
            points=points,
            legs=legs,
            total_distance_miles=Decimal("740.0"),
            total_duration_minutes=770,
            geometry_geojson={
                "type": "LineString",
                # OSRM/GeoJSON convention is [lon, lat]
                "coordinates": [[p.longitude, p.latitude] for p in points],
            },
        )


class NominatimGeocoder:
    """Simple geocoder backed by OpenStreetMap Nominatim."""

    BASE_URL = "https://nominatim.openstreetmap.org/search"

    def __init__(self, timeout_seconds: float = 20.0) -> None:
        self.timeout_seconds = timeout_seconds

    def geocode(self, address: str) -> RoutePoint:
        if not address.strip():
            raise RouteServiceError("Address is required for geocoding.")

        headers = {"User-Agent": "spotter-ai-trip-planner/1.0 (local-development)"}
        params = {"q": address, "format": "jsonv2", "limit": 1}
        with httpx.Client(timeout=self.timeout_seconds, headers=headers) as client:
            response = client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

        if not data:
            raise RouteServiceError(f"Could not geocode location: {address}")

        best = data[0]
        return RoutePoint(
            name=address,
            latitude=float(best["lat"]),
            longitude=float(best["lon"]),
        )


class OSRMRouteService:
    """Route builder using public OSRM demo server."""

    BASE_URL = "https://router.project-osrm.org/route/v1/driving"
    MILES_PER_METER = Decimal("0.000621371")

    def __init__(self, geocoder: NominatimGeocoder | None = None, timeout_seconds: float = 30.0) -> None:
        self.geocoder = geocoder or NominatimGeocoder()
        self.timeout_seconds = timeout_seconds

    def build_trip_route(
        self,
        current_location: str,
        pickup_location: str,
        dropoff_location: str,
    ) -> NormalizedRoute:
        points = [
            self.geocoder.geocode(current_location),
            self.geocoder.geocode(pickup_location),
            self.geocoder.geocode(dropoff_location),
        ]

        coordinates = ";".join(f"{p.longitude},{p.latitude}" for p in points)
        url = f"{self.BASE_URL}/{coordinates}"
        params = {"overview": "full", "geometries": "geojson", "steps": "false"}

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()

        routes = payload.get("routes") or []
        if not routes:
            raise RouteServiceError("Route provider returned no route.")

        route = routes[0]
        legs_raw = route.get("legs", [])
        legs: list[RouteLegData] = []
        for idx, leg in enumerate(legs_raw, start=1):
            legs.append(
                RouteLegData(
                    sequence=idx,
                    start_name=points[idx - 1].name,
                    end_name=points[idx].name,
                    distance_miles=(Decimal(str(leg["distance"])) * self.MILES_PER_METER).quantize(Decimal("0.01")),
                    duration_minutes=max(1, round(float(leg["duration"]) / 60)),
                    geometry_geojson={},
                ),
            )

        total_miles = (Decimal(str(route["distance"])) * self.MILES_PER_METER).quantize(Decimal("0.01"))
        total_duration_minutes = max(1, round(float(route["duration"]) / 60))
        return NormalizedRoute(
            points=points,
            legs=legs,
            total_distance_miles=total_miles,
            total_duration_minutes=total_duration_minutes,
            geometry_geojson=route.get("geometry", {}),
        )


def build_route_service() -> RouteService:
    """
    Create routing provider from environment.

    Defaults to OSRM for a keyless local experience. During pytest, deterministic
    stub routing is used to keep tests fast and stable.
    """
    if os.getenv("PYTEST_CURRENT_TEST"):
        return StubRouteService()

    provider = os.getenv("ROUTE_PROVIDER", "osrm").lower()
    if provider == "stub":
        return StubRouteService()
    if provider == "osrm":
        return OSRMRouteService()
    raise RouteServiceError(f"Unsupported ROUTE_PROVIDER: {provider}")
