import type { TripPlanResponse } from "../../types/trip";

interface TripSummaryCardsProps {
  trip: TripPlanResponse | null;
}

function formatDuration(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
}

export function TripSummaryCards({ trip }: TripSummaryCardsProps) {
  if (!trip) {
    return null;
  }

  const totalStops = trip.stops.length;

  return (
    <section className="grid gap-3 md:grid-cols-4">
      <article className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
        <p className="text-xs uppercase tracking-wide text-slate-400">Total miles</p>
        <p className="mt-2 text-2xl font-semibold text-white">{trip.total_distance_miles}</p>
      </article>
      <article className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
        <p className="text-xs uppercase tracking-wide text-slate-400">Raw drive time</p>
        <p className="mt-2 text-2xl font-semibold text-white">
          {formatDuration(trip.estimated_raw_drive_duration_minutes)}
        </p>
      </article>
      <article className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
        <p className="text-xs uppercase tracking-wide text-slate-400">Trip status</p>
        <p className="mt-2 text-2xl font-semibold capitalize text-emerald-300">{trip.trip_status}</p>
      </article>
      <article className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
        <p className="text-xs uppercase tracking-wide text-slate-400">Planned stops</p>
        <p className="mt-2 text-2xl font-semibold text-cyan-300">{totalStops}</p>
      </article>
    </section>
  );
}
