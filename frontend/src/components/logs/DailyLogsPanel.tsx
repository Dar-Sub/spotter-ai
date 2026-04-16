import type { TripPlanResponse } from "../../types/trip";
import { DailyLogSheet } from "./DailyLogSheet";
import { DailyLogExplorer } from "./DailyLogExplorer";

interface DailyLogsPanelProps {
  trip: TripPlanResponse | null;
}

export function DailyLogsPanel({ trip }: DailyLogsPanelProps) {
  const handlePrint = () => window.print();

  return (
    <section className="rounded-2xl border border-slate-700/60 bg-slate-900/70 p-6">
      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-base font-semibold text-white">Daily ELD logs</h3>
          <p className="mt-0.5 text-xs text-slate-300">
            Interactive duty segments plotted on classic day lanes (click a segment to highlight).
          </p>
        </div>
        {trip ? (
          <button
            type="button"
            onClick={handlePrint}
            className="rounded-md border border-slate-600 px-3 py-1 text-xs font-semibold text-slate-200 transition hover:border-slate-400 hover:text-white print:hidden"
          >
            Print logs
          </button>
        ) : null}
      </div>
      {!trip ? (
        <p className="mt-2 text-sm text-slate-300">No logs yet. Plan a trip to generate day-by-day duty records.</p>
      ) : (
        <div className="mt-4">
          <div
            className="mb-4 flex flex-wrap gap-2 rounded-xl border border-slate-700/80 bg-slate-950/40 px-3 py-2 text-[11px] text-slate-300 print:hidden"
            aria-label="ELD duty status lane legend"
          >
            <span className="font-semibold text-slate-400">Lanes:</span>
            <span className="inline-flex items-center gap-1.5 rounded-md border border-slate-700 bg-slate-900/60 px-2 py-0.5">
              <span className="h-2 w-2 rounded-full" style={{ background: "#94a3b8" }} />
              <span className="font-medium text-slate-200">Off</span>
              <span className="text-slate-500">off duty</span>
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-md border border-slate-700 bg-slate-900/60 px-2 py-0.5">
              <span className="h-2 w-2 rounded-full" style={{ background: "#a78bfa" }} />
              <span className="font-medium text-slate-200">SB</span>
              <span className="text-slate-500">sleeper berth</span>
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-md border border-slate-700 bg-slate-900/60 px-2 py-0.5">
              <span className="h-2 w-2 rounded-full" style={{ background: "#22d3ee" }} />
              <span className="font-medium text-slate-200">D</span>
              <span className="text-slate-500">driving</span>
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-md border border-slate-700 bg-slate-900/60 px-2 py-0.5">
              <span className="h-2 w-2 rounded-full" style={{ background: "#fbbf24" }} />
              <span className="font-medium text-slate-200">ON</span>
              <span className="text-slate-500">on duty not driving</span>
            </span>
          </div>

          {/* Screen UX: interactive explorer */}
          <div className="print:hidden">
            <DailyLogExplorer logs={trip.daily_logs} />
          </div>

          {/* Print UX: show all days */}
          <div className="hidden print:block">
            <div className="space-y-4">
              {trip.daily_logs.map((log) => (
                <DailyLogSheet key={log.log_date} log={log} />
              ))}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
