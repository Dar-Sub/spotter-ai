import { Link } from "react-router-dom";

function TruckIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 140 56"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <path
        fill="currentColor"
        fillOpacity="0.92"
        d="M8 32h72c2 0 4 1 5 3l10 14h32c3 0 5 2 5 5v2H8v-24Z"
      />
      <path fill="currentColor" fillOpacity="0.75" d="M86 18h38l10 14H86V18Z" />
      <circle cx="28" cy="44" r="7" fill="#0f172a" stroke="currentColor" strokeWidth="2" />
      <circle cx="58" cy="44" r="7" fill="#0f172a" stroke="currentColor" strokeWidth="2" />
      <circle cx="102" cy="44" r="7" fill="#0f172a" stroke="currentColor" strokeWidth="2" />
      <circle cx="124" cy="44" r="7" fill="#0f172a" stroke="currentColor" strokeWidth="2" />
      <rect x="94" y="22" width="18" height="10" rx="1" fill="#22d3ee" fillOpacity="0.35" />
    </svg>
  );
}

export function WelcomePage() {
  return (
    <div className="welcome-motion relative min-h-screen overflow-hidden bg-[#050d14] text-slate-100">
      {/* Sky & depth */}
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_120%_80%_at_50%_-10%,rgba(34,211,238,0.18),transparent_55%),radial-gradient(ellipse_90%_60%_at_80%_20%,rgba(56,189,248,0.08),transparent_50%)]"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute inset-0 animate-welcome-shimmer bg-[linear-gradient(115deg,transparent_40%,rgba(255,255,255,0.04)_50%,transparent_60%)]"
        aria-hidden
      />

      {/* Horizon glow */}
      <div
        className="pointer-events-none absolute bottom-[38%] left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-500/40 to-transparent"
        aria-hidden
      />

      {/* Road plane */}
      <div
        className="pointer-events-none absolute inset-x-0 bottom-0 h-[46vh] bg-gradient-to-b from-slate-900 via-slate-950 to-black"
        style={{ clipPath: "polygon(8% 0, 92% 0, 100% 100%, 0 100%)" }}
        aria-hidden
      />
      {/* Road motion stripes */}
      <div
        className="pointer-events-none absolute bottom-0 left-[10%] right-[10%] h-[42vh] animate-welcome-road opacity-70"
        style={{
          clipPath: "polygon(10% 0, 90% 0, 100% 100%, 0 100%)",
          backgroundImage:
            "repeating-linear-gradient(to bottom, transparent 0, transparent 28px, rgba(34,211,238,0.22) 28px, rgba(34,211,238,0.22) 32px, transparent 32px, transparent 60px)",
          backgroundSize: "100% 96px",
        }}
        aria-hidden
      />
      <div
        className="pointer-events-none absolute bottom-[6vh] left-1/2 h-1 w-[min(72vw,720px)] -translate-x-1/2 rounded-full bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent blur-sm"
        aria-hidden
      />

      {/* Moving trucks */}
      <div
        className="pointer-events-none absolute bottom-[20vh] left-0 animate-welcome-truck-a text-cyan-200/90"
        aria-hidden
      >
        <TruckIcon className="h-14 w-auto drop-shadow-[0_0_12px_rgba(34,211,238,0.35)]" />
      </div>
      <div
        className="pointer-events-none absolute bottom-[26vh] left-0 animate-welcome-truck-b text-slate-300/80 [animation-delay:-7s]"
        aria-hidden
      >
        <TruckIcon className="h-11 w-auto opacity-90" />
      </div>
      <div
        className="pointer-events-none absolute bottom-[16vh] left-0 animate-welcome-truck-c text-cyan-100/70 [animation-delay:-12s]"
        aria-hidden
      >
        <TruckIcon className="h-9 w-auto" />
      </div>

      {/* Foreground content */}
      <div className="relative z-10 mx-auto flex min-h-screen max-w-5xl flex-col px-5 pb-16 pt-14 md:px-10 md:pt-20">
        <p className="text-center text-xs font-semibold uppercase tracking-[0.35em] text-cyan-400/90">
          Spotter Planner
        </p>
        <h1 className="mx-auto mt-10 max-w-3xl animate-welcome-drift text-center text-4xl font-semibold leading-tight tracking-tight text-white md:text-5xl lg:text-[3.25rem]">
          Welcome: plan routes, respect HOS, and ship ELD-ready logs.
        </h1>
        <p className="mx-auto mt-5 max-w-2xl text-center text-base text-slate-400 md:text-lg">
          A focused operations workspace for property-carrying runs: geocoded legs, compliance stops, and multi-day log
          sheets: no sign-in required.
        </p>

        <div className="mt-12 flex flex-col items-center justify-center gap-4 sm:flex-row sm:gap-6">
          <Link
            to="/planner"
            className="inline-flex min-w-[200px] items-center justify-center rounded-xl bg-gradient-to-r from-cyan-500 to-sky-500 px-10 py-3.5 text-center text-base font-semibold text-slate-950 shadow-[0_0_40px_rgba(34,211,238,0.35)] transition hover:brightness-110 hover:shadow-[0_0_48px_rgba(34,211,238,0.45)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300"
          >
            Continue to planner
          </Link>
          <p className="text-center text-xs text-slate-500 sm:text-left">Opens the trip form, map, timeline, and daily logs.</p>
        </div>

        <div className="mt-auto flex flex-wrap items-center justify-center gap-x-8 gap-y-3 pt-20 text-xs text-slate-600">
          <span>FMCSA-style assumptions</span>
          <span className="hidden sm:inline">·</span>
          <span>Rolling 70h / 8-day window</span>
          <span className="hidden sm:inline">·</span>
          <span>Leaflet map · Django API</span>
        </div>
      </div>
    </div>
  );
}
