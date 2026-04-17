const assumptions = [
  "Property-carrying driver rules",
  "11h max driving within a 14h duty window",
  "30m break after 8h cumulative driving",
  "Rolling 70h / 8-day on-duty cap (driving + pickup, drop, fuel)",
  "Cycle-used hours at plan start are spread evenly across the last eight planner calendar days",
  "Fuel stop inserted at approximately every 1,000 miles",
  "1h pickup and 1h dropoff on-duty service time",
];

export function AssumptionsPanel() {
  return (
    <aside className="rounded-2xl border border-slate-700/60 bg-slate-900/70 p-6">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-cyan-300">Planning assumptions</h3>
      <ul className="mt-3 space-y-2 text-sm text-slate-200">
        {assumptions.map((assumption) => (
          <li key={assumption} className="flex gap-2">
            <span className="mt-1 h-1.5 w-1.5 rounded-full bg-cyan-300" />
            <span>{assumption}</span>
          </li>
        ))}
      </ul>
    </aside>
  );
}
