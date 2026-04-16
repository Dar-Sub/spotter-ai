import type { TripPlanResponse } from "../../types/trip";

interface StopsTimelineProps {
  trip: TripPlanResponse | null;
}

export function StopsTimeline({ trip }: StopsTimelineProps) {
  const stopTone = (stopType: string): string => {
    if (stopType === "pickup") return "bg-emerald-500/15 text-emerald-300 border-emerald-500/30";
    if (stopType === "dropoff") return "bg-blue-500/15 text-blue-300 border-blue-500/30";
    if (stopType === "fuel") return "bg-amber-500/15 text-amber-300 border-amber-500/30";
    if (stopType === "break") return "bg-violet-500/15 text-violet-300 border-violet-500/30";
    if (stopType === "overnight_reset") return "bg-rose-500/15 text-rose-300 border-rose-500/30";
    return "bg-cyan-500/15 text-cyan-300 border-cyan-500/30";
  };

  const formatDuration = (minutes: number): string => {
    if (minutes >= 60) {
      const h = Math.floor(minutes / 60);
      const m = minutes % 60;
      return m ? `${h}h ${m}m` : `${h}h`;
    }
    return `${minutes}m`;
  };

  const formatTime = (value: string | null) =>
    value ? new Date(value).toLocaleString(undefined, { hour: "2-digit", minute: "2-digit", month: "short", day: "numeric" }) : "TBD";

  return (
    <section className="rounded-2xl border border-slate-700/60 bg-slate-900/70 p-6">
      <h3 className="text-base font-semibold text-white">Stop and compliance timeline</h3>
      {!trip ? (
        <p className="mt-2 text-sm text-slate-300">
          Timeline events (pickup, break, fuel, reset, dropoff) will appear after planning.
        </p>
      ) : (
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          <article className="rounded-lg bg-slate-950/60 p-3">
            <p className="mb-2 text-xs uppercase tracking-wide text-slate-400">Stops</p>
            <ul className="space-y-2 text-sm text-slate-200">
              {trip.stops.map((stop) => (
                <li key={`${stop.sequence}-${stop.stop_type}`} className="rounded-md border border-slate-800 p-2">
                  <div className="mb-1 flex items-center justify-between gap-2">
                    <p className="font-medium capitalize text-white">{stop.stop_type.replaceAll("_", " ")}</p>
                    <span className={`rounded border px-2 py-0.5 text-[10px] font-semibold uppercase ${stopTone(stop.stop_type)}`}>
                      {formatDuration(stop.duration_minutes)}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300">{stop.location_name || "En route"}</p>
                  <p className="text-xs text-slate-400">
                    {formatTime(stop.planned_arrival)} - {formatTime(stop.planned_departure)}
                  </p>
                  {stop.notes && (
                    <p className="mt-1 text-[11px] text-slate-400 line-clamp-2">
                      {stop.notes}
                    </p>
                  )}
                </li>
              ))}
            </ul>
          </article>

          <article className="rounded-lg bg-slate-950/60 p-3">
            <p className="mb-2 text-xs uppercase tracking-wide text-slate-400">Recent duty segments</p>
            <ul className="space-y-2 text-sm text-slate-200">
              {trip.duty_segments.slice(0, 8).map((segment, index) => (
                <li key={`${segment.start_time}-${index}`} className="rounded-md border border-slate-800 p-2">
                  <p className="font-medium capitalize text-white">{segment.segment_type.replaceAll("_", " ")}</p>
                  <p className="text-xs text-slate-300">{segment.location_context || "En route"}</p>
                  <p className="text-xs text-slate-400">
                    {new Date(segment.start_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} -{" "}
                    {new Date(segment.end_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </p>
                </li>
              ))}
            </ul>
          </article>
        </div>
      )}
    </section>
  );
}
