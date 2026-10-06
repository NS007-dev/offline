import type { MissionRequest, MissionResponse } from "../types/mission";

// Empty by default: the Vite dev server proxies /api to the backend.
const API_BASE = import.meta.env.VITE_API_BASE ?? "";

// A little longer than the backend's own wait for Ollama (120s by default).
const REQUEST_TIMEOUT_MS = 150_000;

export type ApiErrorKind = "unreachable" | "server" | "timeout";

export class ApiError extends Error {
  kind: ApiErrorKind;
  constructor(kind: ApiErrorKind, message: string) {
    super(message);
    this.kind = kind;
  }
}

/** Ask the backend for a mission. Pass `signal` so the user can cancel. */
export async function requestMission(
  request: MissionRequest,
  signal: AbortSignal,
): Promise<MissionResponse> {
  const timeout = new AbortController();
  const timer = window.setTimeout(() => timeout.abort(), REQUEST_TIMEOUT_MS);
  const onUserAbort = () => timeout.abort();
  signal.addEventListener("abort", onUserAbort);

  try {
    const response = await fetch(`${API_BASE}/api/mission`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
      signal: timeout.signal,
    });
    if (!response.ok) {
      throw new ApiError("server", `The OFFLINE backend answered with an error (${response.status}).`);
    }
    const data = (await response.json()) as MissionResponse;
    if (!data?.mission || !Array.isArray(data.mission.steps) || data.mission.steps.length === 0) {
      throw new ApiError("server", "The OFFLINE backend sent a mission the app could not read.");
    }
    return data;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (signal.aborted) throw error; // the user cancelled; the caller handles this quietly
    if (timeout.signal.aborted) {
      throw new ApiError("timeout", "The mission took too long to arrive.");
    }
    throw new ApiError("unreachable", "Could not reach the OFFLINE backend.");
  } finally {
    window.clearTimeout(timer);
    signal.removeEventListener("abort", onUserAbort);
  }
}
