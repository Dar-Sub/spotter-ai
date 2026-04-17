import { useEffect, useMemo, useState } from "react";

import type { DailyLog } from "../../types/trip";
import { DailyLogSheet } from "./DailyLogSheet";

interface DailyLogExplorerProps {
  logs: DailyLog[];
}

function formatMinuteAsTime(minute: number): string {
  const hh = Math.floor(minute / 60)
    .toString()
    .padStart(2, "0");
  const mm = (minute % 60).toString().padStart(2, "0");
  return `${hh}:${mm}`;
}

export function DailyLogExplorer({ logs }: DailyLogExplorerProps) {
  const [activeLogIndex, setActiveLogIndex] = useState(0);
  const activeLog = logs[activeLogIndex];

  const [activeEntryIndex, setActiveEntryIndex] = useState<number | null>(null);

  const entryColor = useMemo(() => {
    const colorByType: Record<string, string> = {
      off_duty: "#94a3b8",
      sleeper: "#a78bfa",
      driving: "#22d3ee",
      on_duty_not_driving: "#fbbf24",
    };
    return colorByType;
  }, []);

  useEffect(() => {
    const log = logs[activeLogIndex];
    setActiveEntryIndex(log?.log_entries?.length ? 0 : null);
  }, [activeLogIndex, logs]);

  const activeEntry = activeLog?.log_entries[activeEntryIndex ?? -1];

  return (
    <div className="mt-4 space-y-4">
      <div className="flex flex-wrap gap-2">
        {logs.map((log, idx) => (
          <button
            key={log.log_date}
            type="button"
            onClick={() => setActiveLogIndex(idx)}
            className={[
              "rounded-lg border px-3 py-1 text-xs font-semibold transition",
              idx === activeLogIndex
                ? "border-cyan-400 bg-cyan-400/10 text-cyan-200"
                : "border-slate-700 bg-slate-900/30 text-slate-200 hover:border-slate-500",
            ].join(" ")}
          >
            {log.log_date}
          </button>
        ))}
      </div>

      {activeLog ? (
        <DailyLogSheet
          log={activeLog}
          activeEntryIndex={activeEntryIndex ?? undefined}
          onSelectEntry={(entryIdx) => setActiveEntryIndex(entryIdx)}
        />
      ) : null}

      <div className="rounded-2xl border border-slate-700 bg-slate-900/40 p-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-300">Day entry list</p>
            <p className="mt-1 text-xs text-slate-400">Click a row to highlight that segment on the log sheet.</p>
          </div>
          {activeEntry ? (
            <div className="rounded-xl border border-slate-700 bg-slate-950/40 px-3 py-2 text-xs text-slate-200">
              <p className="font-semibold text-white">
                {activeEntry.segment_type.replaceAll("_", " ")}
              </p>
              <p className="mt-1 text-slate-300">
                {formatMinuteAsTime(activeEntry.start_minute)} - {formatMinuteAsTime(activeEntry.end_minute)} (
                {activeEntry.location_context || "En route"})
              </p>
            </div>
          ) : null}
        </div>

        <div className="mt-3 max-h-[320px] space-y-2 overflow-auto pr-1">
          {activeLog?.log_entries.map((entry, idx) => {
            const isActive = activeEntryIndex === idx;
            return (
              <button
                key={`${entry.start_time}-${idx}`}
                type="button"
                onClick={() => setActiveEntryIndex(idx)}
                className={[
                  "w-full rounded-lg border p-2 text-left transition",
                  isActive ? "border-cyan-400 bg-cyan-400/10" : "border-slate-800 bg-slate-950/30 hover:border-slate-600",
                ].join(" ")}
              >
                <div className="flex items-center justify-between gap-2">
                  <p className="truncate text-xs font-semibold text-white">{entry.segment_type.replaceAll("_", " ")}</p>
                  <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-slate-200">
                    <span className="inline-block h-2 w-2 rounded-full" style={{ background: entryColor[entry.segment_type] ?? "#22d3ee" }} />
                    {formatMinuteAsTime(entry.start_minute)}-{formatMinuteAsTime(entry.end_minute)}
                  </span>
                </div>
                {entry.location_context ? (
                  <p className="mt-1 text-[11px] text-slate-300 line-clamp-2">{entry.location_context}</p>
                ) : null}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

