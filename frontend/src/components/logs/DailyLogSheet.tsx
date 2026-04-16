import type { DailyLog } from "../../types/trip";

interface DailyLogSheetProps {
  log: DailyLog;
  activeEntryIndex?: number;
  onSelectEntry?: (entryIndex: number) => void;
}

const STATUS_Y: Record<string, number> = {
  off_duty: 20,
  sleeper: 44,
  driving: 68,
  on_duty_not_driving: 92,
};

function labelForStatus(status: string): string {
  if (status === "off_duty") return "Off";
  if (status === "sleeper") return "SB";
  if (status === "driving") return "D";
  if (status === "on_duty_not_driving") return "ON";
  return status;
}

function colorForSegmentType(segmentType: string): string {
  if (segmentType === "off_duty") return "#94a3b8";
  if (segmentType === "sleeper") return "#a78bfa";
  if (segmentType === "driving") return "#22d3ee";
  if (segmentType === "on_duty_not_driving") return "#fbbf24";
  return "#22d3ee";
}

export function DailyLogSheet({ log, activeEntryIndex, onSelectEntry }: DailyLogSheetProps) {
  const width = 960;
  const height = 120;
  const minuteToX = (minute: number) => (minute / 1440) * (width - 60) + 40;

  return (
    <article className="rounded-xl border border-slate-700 bg-slate-950/50 p-4 print:break-inside-avoid print:border-slate-300 print:bg-white">
      <div className="mb-3 flex items-center justify-between text-xs text-slate-300">
        <p className="text-sm font-semibold text-white print:text-slate-900">{log.log_date}</p>
        <p>
          D {log.driving_hours}h | ON {log.on_duty_hours}h | OFF {log.off_duty_hours}h | SB {log.sleeper_hours}h
        </p>
      </div>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="h-[240px] w-full rounded-lg bg-slate-900 print:bg-white"
      >
        {[0, 6, 12, 18, 24].map((hour) => (
          <g key={hour}>
            <line x1={minuteToX(hour * 60)} y1={10} x2={minuteToX(hour * 60)} y2={110} stroke="#334155" />
            <text x={minuteToX(hour * 60) + 2} y={118} fontSize="9" fill="#94a3b8">
              {hour}
            </text>
          </g>
        ))}

        {Object.entries(STATUS_Y).map(([status, y]) => (
          <g key={status}>
            <line x1={40} y1={y} x2={width - 20} y2={y} stroke="#1e293b" />
            <text x={8} y={y + 3} fontSize="9" fill="#94a3b8">
              {labelForStatus(status)}
            </text>
          </g>
        ))}

        {log.log_entries.map((entry, index) => {
          const y = STATUS_Y[entry.segment_type] ?? 92;
          const x1 = minuteToX(entry.start_minute);
          const x2 = minuteToX(entry.end_minute);
          const active = typeof activeEntryIndex === "number" && activeEntryIndex === index;
          const stroke = colorForSegmentType(entry.segment_type);
          const opacity = active ? 1 : 0.6;
          const strokeWidth = active ? 5 : 3;

          return (
            <line
              key={`${entry.start_time}-${index}`}
              x1={x1}
              y1={y}
              x2={x2}
              y2={y}
              stroke={stroke}
              strokeWidth={strokeWidth}
              opacity={opacity}
              style={{ cursor: onSelectEntry ? "pointer" : "default" }}
              onClick={() => onSelectEntry?.(index)}
            >
              <title>
                {entry.segment_type.replaceAll("_", " ")} {entry.start_minute}-{entry.end_minute} min {entry.location_context
                  ? `(${entry.location_context})`
                  : ""}
              </title>
            </line>
          );
        })}
      </svg>
    </article>
  );
}
