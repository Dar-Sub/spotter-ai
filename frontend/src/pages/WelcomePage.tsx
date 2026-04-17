import type { ReactNode } from "react";
import { useId } from "react";
import { Link } from "react-router-dom";

const SKY_DOTS: { top: string; left: string; opacity: string; delay: string }[] = [
  { top: "10%", left: "12%", opacity: "0.35", delay: "0s" },
  { top: "14%", left: "28%", opacity: "0.5", delay: "0.4s" },
  { top: "8%", left: "44%", opacity: "0.28", delay: "0.8s" },
  { top: "18%", left: "58%", opacity: "0.4", delay: "1.1s" },
  { top: "11%", left: "72%", opacity: "0.32", delay: "0.2s" },
  { top: "16%", left: "86%", opacity: "0.45", delay: "0.6s" },
  { top: "22%", left: "6%", opacity: "0.25", delay: "1.4s" },
  { top: "20%", left: "92%", opacity: "0.38", delay: "0.9s" },
];

function TruckIcon({ className, variant = "cyan" }: { className?: string; variant?: "cyan" | "slate" | "amber" }) {
  const uid = useId().replace(/:/g, "");
  const gradId = `welcome-cab-${uid}`;
  const cab = variant === "amber" ? "#fbbf24" : variant === "slate" ? "#94a3b8" : "#22d3ee";
  const trailer = variant === "amber" ? "#fcd34d" : variant === "slate" ? "#cbd5e1" : "#67e8f9";
  return (
    <svg
      className={className}
      viewBox="0 0 168 58"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <defs>
        <linearGradient id={gradId} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor={cab} stopOpacity="0.95" />
          <stop offset="100%" stopColor={cab} stopOpacity="0.65" />
        </linearGradient>
      </defs>
      <rect x="4" y="30" width="96" height="22" rx="3" fill={trailer} fillOpacity="0.88" />
      <rect x="100" y="22" width="48" height="20" rx="2" fill={`url(#${gradId})`} />
      <path fill={cab} fillOpacity="0.9" d="M148 22h14l6 10v20h-20V22Z" />
      <circle cx="26" cy="46" r="7" fill="#020617" stroke={cab} strokeWidth="2" />
      <circle cx="54" cy="46" r="7" fill="#020617" stroke={cab} strokeWidth="2" />
      <circle cx="118" cy="46" r="7" fill="#020617" stroke={cab} strokeWidth="2" />
      <circle cx="146" cy="46" r="7" fill="#020617" stroke={cab} strokeWidth="2" />
      <rect x="108" y="26" width="22" height="11" rx="1" fill="#e0f2fe" fillOpacity="0.35" />
      <rect x="132" y="26" width="10" height="6" rx="1" className="animate-welcome-headlight" fill="#fef08a" fillOpacity="0.9" />
    </svg>
  );
}

function TruckLane({
  children,
  motionClass,
  bobClass,
  delayClass,
}: {
  children: ReactNode;
  motionClass: string;
  bobClass: string;
  delayClass?: string;
}) {
  return (
    <div
      className={`pointer-events-none absolute left-0 will-change-transform ${motionClass} ${delayClass ?? ""}`}
      aria-hidden
    >
      <div className={`will-change-transform ${bobClass}`}>{children}</div>
    </div>
  );
}

export function WelcomePage() {
  return (
    <div className="welcome-motion relative min-h-screen overflow-hidden bg-[#050d14] text-slate-100">
      {/* Sky & depth — unchanged treatment */}
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_120%_80%_at_50%_-10%,rgba(34,211,238,0.18),transparent_55%),radial-gradient(ellipse_90%_60%_at_80%_20%,rgba(56,189,248,0.08),transparent_50%)]"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute inset-0 animate-welcome-shimmer bg-[linear-gradient(115deg,transparent_40%,rgba(255,255,255,0.04)_50%,transparent_60%)]"
        aria-hidden
      />

      {/* Soft constellation (subtle, above road) */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-[42vh]" aria-hidden>
        {SKY_DOTS.map((dot, i) => (
          <span
            key={i}
            className="absolute h-1 w-1 rounded-full bg-cyan-200/80 shadow-[0_0_8px_rgba(34,211,238,0.6)] animate-welcome-shimmer"
            style={{ top: dot.top, left: dot.left, opacity: dot.opacity, animationDelay: dot.delay }}
          />
        ))}
      </div>

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

      {/* Moving trucks — horizontal + vertical bob for “live” feel */}
      <TruckLane motionClass="bottom-[20vh] animate-welcome-truck-a" bobClass="animate-welcome-truck-bob">
        <TruckIcon className="h-16 w-auto text-cyan-200 drop-shadow-[0_0_20px_rgba(34,211,238,0.45)]" variant="cyan" />
      </TruckLane>
      <TruckLane motionClass="bottom-[26vh] animate-welcome-truck-b [animation-delay:-7s]" bobClass="animate-welcome-truck-bob-slow">
        <TruckIcon className="h-12 w-auto text-slate-200/90 drop-shadow-[0_0_14px_rgba(148,163,184,0.35)]" variant="slate" />
      </TruckLane>
      <TruckLane motionClass="bottom-[16vh] animate-welcome-truck-c [animation-delay:-12s]" bobClass="animate-welcome-truck-bob-fast">
        <TruckIcon className="h-10 w-auto text-cyan-100/85" variant="cyan" />
      </TruckLane>
      <TruckLane motionClass="bottom-[22vh] animate-welcome-truck-d [animation-delay:-4s]" bobClass="animate-welcome-truck-bob">
        <TruckIcon className="h-11 w-auto text-amber-200/90 drop-shadow-[0_0_16px_rgba(251,191,36,0.25)]" variant="amber" />
      </TruckLane>
      <TruckLane motionClass="bottom-[18vh] animate-welcome-truck-e [animation-delay:-18s]" bobClass="animate-welcome-truck-bob-slow">
        <TruckIcon className="h-9 w-auto text-slate-300/80" variant="slate" />
      </TruckLane>

      {/* Foreground */}
      <div className="relative z-10 mx-auto flex min-h-screen max-w-5xl flex-col px-5 pb-16 pt-14 md:px-10 md:pt-20">
        <div className="mx-auto w-full max-w-3xl rounded-[2rem] border border-white/[0.08] bg-gradient-to-b from-white/[0.08] to-white/[0.02] p-8 shadow-[0_28px_90px_-24px_rgba(0,0,0,0.85)] backdrop-blur-xl md:p-11">
          <p className="text-center text-xs font-semibold uppercase tracking-[0.35em] text-cyan-400/90">
            Spotter Planner
          </p>
          <h1 className="mx-auto mt-8 max-w-3xl animate-welcome-drift text-center text-4xl font-semibold leading-tight tracking-tight text-white md:text-5xl lg:text-[3.25rem]">
            Welcome: plan routes, respect HOS, and ship ELD-ready logs.
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-center text-base leading-relaxed text-slate-400 md:text-lg">
            A focused operations workspace for property-carrying runs: geocoded legs, compliance stops, and multi-day
            log sheets: no sign-in required.
          </p>

          <div className="mx-auto mt-8 flex flex-wrap justify-center gap-2">
            {["Live route map", "HOS timeline", "Multi-day ELD grids"].map((label) => (
              <span
                key={label}
                className="rounded-full border border-cyan-500/20 bg-cyan-500/[0.07] px-4 py-1.5 text-xs font-medium tracking-wide text-cyan-100/95"
              >
                {label}
              </span>
            ))}
          </div>

          <div className="mt-10 flex flex-col items-center justify-center gap-5 sm:flex-row sm:gap-8">
            <Link
              to="/planner"
              className="group relative inline-flex min-w-[220px] items-center justify-center overflow-hidden rounded-2xl border border-cyan-400/30 bg-[length:220%_100%] px-11 py-4 text-center text-base font-semibold text-slate-950 shadow-[0_0_48px_rgba(34,211,238,0.35)] transition duration-300 animate-welcome-cta-shine bg-[linear-gradient(105deg,#22d3ee_0%,#38bdf8_18%,#22d3ee_36%,#0ea5e9_52%,#22d3ee_70%,#67e8f9_88%,#22d3ee_100%)] hover:scale-[1.02] hover:shadow-[0_0_60px_rgba(34,211,238,0.5)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-200"
            >
              <span className="relative z-10 flex items-center gap-2">
                Continue to planner
                <span aria-hidden className="transition-transform group-hover:translate-x-0.5">
                  →
                </span>
              </span>
            </Link>
            <p className="max-w-xs text-center text-xs leading-relaxed text-slate-500 sm:text-left">
              Trip form, interactive map, stop &amp; duty timeline, and printable-style daily logs.
            </p>
          </div>
        </div>

        <div className="mt-auto flex flex-col items-center pt-16 text-center">
          <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs font-medium tracking-wide text-slate-500">
            <span>FMCSA-style assumptions</span>
            <span className="hidden text-slate-700 sm:inline">·</span>
            <span>Rolling 70h / 8-day window</span>
            <span className="hidden text-slate-700 sm:inline">·</span>
            <span>Leaflet map · Django API</span>
          </div>
          <div
            className="mt-5 h-0.5 w-[min(420px,88vw)] origin-center rounded-full bg-gradient-to-r from-transparent via-cyan-400/70 to-transparent shadow-[0_0_20px_rgba(34,211,238,0.35)] animate-welcome-footer-line"
            aria-hidden
          />
        </div>
      </div>
    </div>
  );
}
