// These types mirror the JSON the backend returns (see backend/app/models/mission.py).

export type TimeOption = 15 | 30 | 60 | 90;
export type Need = "clear_head" | "explore" | "move" | "be_alone" | "surprise";
export type Environment = "unsure" | "city" | "park" | "suburb" | "countryside";

export interface MissionRequest {
  time_minutes: TimeOption;
  need: Need;
  environment: Environment;
}

export interface Step {
  number: number;
  instruction: string;
  phone_down: boolean;
  duration_minutes: number;
}

export interface Mission {
  title: string;
  intro: string;
  estimated_minutes: number;
  steps: Step[];
  reflection_prompt: string;
  closing_message: string;
}

export interface MissionResponse {
  mission: Mission;
  source: "gemma" | "fallback";
  model: string | null;
  retried: boolean;
  fallback_reason: string | null;
}
