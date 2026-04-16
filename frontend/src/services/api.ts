import type { TripPlanInput, TripPlanResponse } from "../types/trip";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

export async function planTrip(payload: TripPlanInput): Promise<TripPlanResponse> {
  const response = await fetch(`${API_BASE_URL}/trips/plan/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(errorBody || "Failed to generate trip plan.");
  }

  return response.json() as Promise<TripPlanResponse>;
}
