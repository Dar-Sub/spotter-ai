import { useForm } from "react-hook-form";

import type { TripPlanInput } from "../../types/trip";

interface TripPlannerFormProps {
  isLoading: boolean;
  onSubmit: (payload: TripPlanInput) => void;
}

const defaultValues: TripPlanInput = {
  current_location: "",
  pickup_location: "",
  dropoff_location: "",
  current_cycle_used_hours: 0,
};

export function TripPlannerForm({ isLoading, onSubmit }: TripPlannerFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TripPlanInput>({ defaultValues });

  return (
    <form
      className="space-y-4 rounded-2xl border border-slate-700/60 bg-slate-900/70 p-6"
      onSubmit={handleSubmit(onSubmit)}
    >
      <h2 className="text-xl font-semibold text-white">Plan a compliant trip</h2>
      <p className="text-sm text-slate-300">
        Enter operational waypoints and current cycle usage. The planner will generate a legally constrained duty
        schedule and daily ELD logs.
      </p>

      <div className="space-y-2">
        <label className="text-sm text-slate-200">Current location</label>
        <input
          {...register("current_location", { required: "Current location is required" })}
          className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
          placeholder="Chicago, IL"
        />
        {errors.current_location && <p className="text-xs text-rose-300">{errors.current_location.message}</p>}
      </div>

      <div className="space-y-2">
        <label className="text-sm text-slate-200">Pickup location</label>
        <input
          {...register("pickup_location", { required: "Pickup location is required" })}
          className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
          placeholder="Indianapolis, IN"
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm text-slate-200">Dropoff location</label>
        <input
          {...register("dropoff_location", { required: "Dropoff location is required" })}
          className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
          placeholder="Atlanta, GA"
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm text-slate-200">Current cycle used (hours)</label>
        <input
          type="number"
          step="0.25"
          min={0}
          max={70}
          {...register("current_cycle_used_hours", {
            valueAsNumber: true,
            min: 0,
            max: 70,
          })}
          className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400"
        />
        <p className="text-xs text-slate-400">
          Use your current on-duty cycle usage in the last 8 days (0-70 hours).
        </p>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isLoading ? "Generating compliant route plan..." : "Plan trip"}
      </button>
    </form>
  );
}
