import type { TripPlanResponse } from "../../types/trip";
import { useEffect, useMemo, useRef } from "react";
import L, { type Map as LeafletMap } from "leaflet";

interface RouteMapPanelProps {
  trip: TripPlanResponse | null;
}

function extractLineCoordinates(trip: TripPlanResponse): [number, number][] {
  const coords = trip.route_summary.geometry_geojson?.coordinates ?? [];
  return coords
    .filter((pair) => Array.isArray(pair) && pair.length >= 2)
    .map((pair) => [pair[1], pair[0]] as [number, number]);
}

function getStopColor(stopType: string): string {
  if (stopType === "pickup") return "#34d399";
  if (stopType === "dropoff") return "#60a5fa";
  if (stopType === "fuel") return "#fbbf24";
  if (stopType === "break") return "#a78bfa";
  if (stopType === "overnight_reset") return "#f87171";
  return "#22d3ee";
}

function getStopRadius(stopType: string): number {
  if (stopType === "pickup") return 10;
  if (stopType === "dropoff") return 10;
  if (stopType === "fuel") return 8;
  if (stopType === "break") return 7;
  if (stopType === "overnight_reset") return 7;
  return 7;
}

function getStopWeight(stopType: string): number {
  if (stopType === "pickup" || stopType === "dropoff") return 4;
  if (stopType === "fuel") return 3;
  if (stopType === "break" || stopType === "overnight_reset") return 3;
  return 3;
}

function getStopZIndex(stopType: string): number {
  if (stopType === "pickup" || stopType === "dropoff") return 1000;
  if (stopType === "fuel") return 900;
  if (stopType === "break") return 850;
  if (stopType === "overnight_reset") return 800;
  return 800;
}

export function RouteMapPanel({ trip }: RouteMapPanelProps) {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<LeafletMap | null>(null);

  if (!trip) {
    return (
      <section className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/60 p-6">
        <h3 className="text-base font-semibold text-white">Route map</h3>
        <p className="mt-2 text-sm text-slate-300">
          Your interactive route visualization will appear here after planning a trip.
        </p>
      </section>
    );
  }

  const lineCoords = useMemo(() => extractLineCoordinates(trip), [trip]);

  const hasCoordinatedStop = (stopType: string): boolean => {
    return trip.stops.some((s) => {
      if (s.stop_type !== stopType) return false;
      const lat = s.latitude != null ? Number(s.latitude) : NaN;
      const lon = s.longitude != null ? Number(s.longitude) : NaN;
      return !Number.isNaN(lat) && !Number.isNaN(lon);
    });
  };

  useEffect(() => {
    if (!mapContainerRef.current || !trip) {
      return;
    }

    if (mapRef.current) {
      mapRef.current.remove();
      mapRef.current = null;
    }

    const fallbackCenter = L.latLng(trip.route_summary.points[0].latitude, trip.route_summary.points[0].longitude);
    const map = L.map(mapContainerRef.current).setView(fallbackCenter, 6);
    mapRef.current = map;

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);

    const showPickup = !hasCoordinatedStop("pickup");
    const showDropoff = !hasCoordinatedStop("dropoff");

    const stopLatLngs: [number, number][] = [];

    trip.route_summary.points.forEach((point, idx) => {
      // Avoid duplicates: the backend draws pickup/dropoff via `trip.stops` when available.
      if (idx === 1 && !showPickup) return;
      if (idx === 2 && !showDropoff) return;

      const color = idx === 0 ? "#14b8a6" : idx === 1 ? "#34d399" : "#60a5fa";
      const isStart = idx === 0;
      const radius = isStart ? 8 : 10;
      const weight = isStart ? 3 : 4;
      const zIndex = isStart ? 600 : getStopZIndex(idx === 1 ? "pickup" : "dropoff");
      L.circleMarker([point.latitude, point.longitude], {
        radius,
        color,
        fillColor: color,
        fillOpacity: 0.95,
        weight,
        // Leaflet supports zIndexOffset, but types for circle markers can be strict.
        zIndexOffset: zIndex,
      } as any)
        .addTo(map)
        .bindPopup(point.name);

      stopLatLngs.push([point.latitude, point.longitude]);
    });

    trip.stops.forEach((stop) => {
      const lat = stop.latitude != null ? Number(stop.latitude) : NaN;
      const lon = stop.longitude != null ? Number(stop.longitude) : NaN;
      if (Number.isNaN(lat) || Number.isNaN(lon)) {
        return;
      }
      const color = getStopColor(stop.stop_type);
      const radius = getStopRadius(stop.stop_type);
      const weight = getStopWeight(stop.stop_type);
      const zIndexOffset = getStopZIndex(stop.stop_type);

      const marker = L.circleMarker([lat, lon], {
        radius,
        color: getStopColor(stop.stop_type),
        fillColor: color,
        fillOpacity: 0.92,
        weight,
        zIndexOffset,
      } as any)
        .addTo(map);

      const title = stop.stop_type.replaceAll("_", " ");
      const bodyLines = [
        stop.location_name || "En route",
        stop.planned_arrival && stop.planned_departure
          ? `${new Date(stop.planned_arrival).toLocaleString([], {
              month: "short",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })} – ${new Date(stop.planned_departure).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}`
          : null,
        stop.duration_minutes ? `${stop.duration_minutes} min` : null,
        stop.notes || null,
      ]
        .filter(Boolean)
        .join("<br/>");

      marker.bindPopup(`<strong>${title}</strong><br/>${bodyLines}`);

      stopLatLngs.push([lat, lon]);
    });

    if (lineCoords.length > 1) {
      // Improve visibility: draw a dark underlay + bright highlight overlay.
      L.polyline(lineCoords, {
        color: "#0b3a5a",
        weight: 10,
        opacity: 0.35,
        lineJoin: "round",
        lineCap: "round",
      }).addTo(map);

      L.polyline(lineCoords, {
        color: "#ffffff",
        weight: 3,
        opacity: 0.35,
        lineJoin: "round",
        lineCap: "round",
      }).addTo(map);

      L.polyline(lineCoords, {
        color: "#22d3ee",
        weight: 5,
        opacity: 1,
        lineJoin: "round",
        lineCap: "round",
      }).addTo(map);

      // Fit the view to both the route geometry and any coordinated stops.
      const bounds = L.latLngBounds(stopLatLngs.length ? stopLatLngs : (lineCoords as [number, number][]));
      map.fitBounds(bounds, { padding: [32, 32] });
    } else {
      map.setView(fallbackCenter, 7);
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [lineCoords, trip]);

  return (
    <section className="rounded-2xl border border-slate-700/60 bg-slate-900/70 p-6">
      <h3 className="text-base font-semibold text-white">Route map</h3>
      <p className="mt-2 text-sm text-slate-300">OSM route geometry and major trip waypoints.</p>
      <div
        ref={mapContainerRef}
        className="mt-4 h-[560px] overflow-hidden rounded-xl border border-slate-700"
      />
      <div className="mt-4 flex flex-wrap gap-3 text-xs text-slate-300">
        <span className="inline-flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-emerald-400" /> Pickup
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-blue-400" /> Dropoff
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-amber-300" /> Fuel
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-violet-400" /> Break
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-rose-400" /> Overnight reset
        </span>
      </div>
    </section>
  );
}
