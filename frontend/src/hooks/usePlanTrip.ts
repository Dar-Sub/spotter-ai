import { useMutation } from "@tanstack/react-query";

import { planTrip } from "../services/api";
import type { TripPlanInput } from "../types/trip";

export function usePlanTrip() {
  return useMutation({
    mutationFn: (payload: TripPlanInput) => planTrip(payload),
  });
}
