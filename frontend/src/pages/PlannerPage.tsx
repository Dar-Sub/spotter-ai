import { TripPlannerForm } from "../components/form/TripPlannerForm";
import { RouteMapPanel } from "../components/map/RouteMapPanel";
import { StopsTimeline } from "../components/timeline/StopsTimeline";
import { AssumptionsPanel } from "../components/ui/AssumptionsPanel";
import { ResultsSkeleton } from "../components/ui/ResultsSkeleton";
import { TripSummaryCards } from "../components/ui/TripSummaryCards";
import { DailyLogsPanel } from "../components/logs/DailyLogsPanel";
import { usePlanTrip } from "../hooks/usePlanTrip";
import type { TripPlanInput } from "../types/trip";

export function PlannerPage() {
  const { mutate, data, isPending, error } = usePlanTrip();

  const onSubmit = (payload: TripPlanInput) => {
    mutate(payload);
  };

  return (
    <main className="mx-auto min-h-screen w-full max-w-7xl px-4 py-10 md:px-8">
      <header className="mb-8 overflow-x-auto text-center [-webkit-overflow-scrolling:touch]">
        <p className="text-sm font-medium uppercase tracking-[0.25em] text-cyan-300">Spotter Planner</p>
        <h1 className="mt-3 whitespace-nowrap text-4xl font-semibold tracking-tight text-white md:text-4xl">
          Trucking trip planner, HOS compliance, and daily ELD logs
        </h1>
        <p className="mt-3 whitespace-nowrap text-sm text-slate-300 md:text-base">
        Plan routes, model FMCSA constraints, and generate production-style driver log artifacts for operations times.
        </p>
      </header>

      <section className="grid gap-6 lg:grid-cols-[380px_1fr]">
        <div className="space-y-6">
          <TripPlannerForm isLoading={isPending} onSubmit={onSubmit} />
          <AssumptionsPanel />
        </div>
        <div className="space-y-6">
          {error && (
            <div className="rounded-xl border border-rose-500/60 bg-rose-950/40 p-4 text-sm text-rose-200">
              Unable to generate trip plan. Verify addresses, route provider availability, and backend health, then retry.
            </div>
          )}
          {data?.warnings?.length ? (
            <div className="rounded-xl border border-amber-500/60 bg-amber-950/40 p-4 text-sm text-amber-200">
              {data.warnings.join(" ")}
            </div>
          ) : null}
          {isPending ? (
            <ResultsSkeleton />
          ) : (
            <>
              {!data ? (
                <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-8 text-center">
                  <p className="text-lg font-semibold text-white">Ready to generate a compliant trip plan</p>
                  <p className="mt-2 text-sm text-slate-300">
                    Enter route details and cycle-used hours to produce a route map, legal duty timeline, and ELD-ready
                    daily logs.
                  </p>
                </div>
              ) : null}
              <TripSummaryCards trip={data ?? null} />
              <RouteMapPanel trip={data ?? null} />
              <StopsTimeline trip={data ?? null} />
              <DailyLogsPanel trip={data ?? null} />
            </>
          )}
        </div>
      </section>
    </main>
  );
}
