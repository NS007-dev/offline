/** 125 -> "2:05" */
export function formatClock(totalSeconds: number): string {
  const safe = Math.max(0, Math.floor(totalSeconds));
  const minutes = Math.floor(safe / 60);
  const seconds = safe % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

/** Plain-English reason shown when the app had to use a built-in mission. */
export function describeFallback(reason: string | null): string {
  switch (reason) {
    case "ollama_unavailable":
      return "Gemma isn't running on this device right now, so OFFLINE used a built-in mission.";
    case "model_missing":
      return "The Gemma model isn't installed yet, so OFFLINE used a built-in mission.";
    case "timeout":
      return "Gemma took too long to answer, so OFFLINE used a built-in mission.";
    case "invalid_output":
      return "Gemma's mission didn't pass OFFLINE's safety checks, so a built-in mission was used instead.";
    default:
      return "OFFLINE used a built-in mission this time.";
  }
}
