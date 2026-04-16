export interface TripPlanInput {
  current_location: string;
  pickup_location: string;
  dropoff_location: string;
  current_cycle_used_hours: number;
}

export interface RoutePoint {
  name: string;
  latitude: number;
  longitude: number;
}

export interface RouteSummary {
  total_distance_miles: string;
  total_duration_minutes: number;
  geometry_geojson: {
    type?: string;
    coordinates?: number[][];
  };
  points: RoutePoint[];
}

export interface RouteLeg {
  sequence: number;
  start_name: string;
  end_name: string;
  distance_miles: string;
  duration_minutes: number;
}

export interface StopEvent {
  stop_type: string;
  sequence: number;
  location_name: string;
  latitude: string | null;
  longitude: string | null;
  planned_arrival: string | null;
  planned_departure: string | null;
  duration_minutes: number;
  notes: string;
}

export interface DutySegment {
  day_index: number;
  segment_type: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  location_context: string;
  notes: string;
}

export interface DailyLogEntry {
  segment_type: string;
  start_minute: number;
  end_minute: number;
  start_time: string;
  end_time: string;
  location_context: string;
  notes: string;
}

export interface DailyLog {
  log_date: string;
  total_miles: string;
  off_duty_hours: string;
  sleeper_hours: string;
  driving_hours: string;
  on_duty_hours: string;
  remarks: string;
  log_entries: DailyLogEntry[];
}

export interface TripPlanResponse {
  id: number;
  trip_status: string;
  current_location_text: string;
  pickup_location_text: string;
  dropoff_location_text: string;
  current_cycle_used_hours: string;
  total_distance_miles: string;
  estimated_raw_drive_duration_minutes: number;
  route_legs: RouteLeg[];
  stops: StopEvent[];
  duty_segments: DutySegment[];
  daily_logs: DailyLog[];
  warnings: string[];
  route_summary: RouteSummary;
}
