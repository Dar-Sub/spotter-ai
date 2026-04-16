export function ResultsSkeleton() {
  return (
    <section className="space-y-4" aria-label="Loading trip results">
      {[0, 1, 2].map((row) => (
        <div key={row} className="h-24 animate-pulse rounded-xl border border-slate-700/50 bg-slate-900/50" />
      ))}
      <div className="h-80 animate-pulse rounded-xl border border-slate-700/50 bg-slate-900/50" />
    </section>
  );
}
