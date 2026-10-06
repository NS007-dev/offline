import { useCallback, useReducer, useRef } from "react";
import { Shell } from "./components/Shell";
import { ScreenTimerBanner } from "./components/ScreenTimerBanner";
import { useScreenTimer } from "./hooks/useScreenTimer";
import { ApiError, requestMission } from "./lib/api";
import type { ApiErrorKind } from "./lib/api";
import { CheckIn } from "./pages/CheckIn";
import { Complete } from "./pages/Complete";
import { Generating } from "./pages/Generating";
import { Home } from "./pages/Home";
import { MissionStep } from "./pages/MissionStep";
import { PhoneDown } from "./pages/PhoneDown";
import { Reflection } from "./pages/Reflection";
import type { MissionRequest, MissionResponse } from "./types/mission";

type Screen = "home" | "checkin" | "generating" | "step" | "phonedown" | "reflection" | "complete";

interface State {
  screen: Screen;
  response: MissionResponse | null;
  stepIndex: number;
  reflection: string | null;
  error: { kind: ApiErrorKind; message: string } | null;
}

type Action =
  | { type: "go"; screen: Screen }
  | { type: "generating" }
  | { type: "generated"; response: MissionResponse }
  | { type: "failed"; error: { kind: ApiErrorKind; message: string } }
  | { type: "putPhoneDown" }
  | { type: "next" }
  | { type: "reflected"; text: string | null };

const initial: State = { screen: "home", response: null, stepIndex: 0, reflection: null, error: null };

// All screen changes happen here, in one place, so the flow is easy to follow.
function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "go":
      return { ...state, screen: action.screen, error: null };
    case "generating":
      return { ...initial, screen: "generating" };
    case "generated":
      return { ...state, screen: "step", response: action.response, stepIndex: 0, error: null };
    case "failed":
      return { ...state, screen: "generating", error: action.error };
    case "putPhoneDown":
      return { ...state, screen: "phonedown" };
    case "next": {
      const last = (state.response?.mission.steps.length ?? 1) - 1;
      return state.stepIndex >= last
        ? { ...state, screen: "reflection" }
        : { ...state, screen: "step", stepIndex: state.stepIndex + 1 };
    }
    case "reflected":
      return { ...state, screen: "complete", reflection: action.text };
  }
}

export default function App() {
  const [state, dispatch] = useReducer(reducer, initial);
  const timer = useScreenTimer();
  const abortRef = useRef<AbortController | null>(null);
  const lastRequest = useRef<MissionRequest | null>(null);

  const generate = useCallback(async (request: MissionRequest) => {
    lastRequest.current = request;
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    dispatch({ type: "generating" });
    try {
      const response = await requestMission(request, controller.signal);
      dispatch({ type: "generated", response });
    } catch (error) {
      if (controller.signal.aborted) return; // the user pressed Cancel
      const apiError =
        error instanceof ApiError ? error : new ApiError("unreachable", "Something went wrong.");
      dispatch({ type: "failed", error: { kind: apiError.kind, message: apiError.message } });
    }
  }, []);

  const cancelGeneration = useCallback(() => {
    abortRef.current?.abort();
    dispatch({ type: "go", screen: "checkin" });
  }, []);

  const goOut = useCallback(() => {
    timer.cancel(); // the timer has done its job
    dispatch({ type: "go", screen: "checkin" });
  }, [timer]);

  const { screen, response, stepIndex } = state;
  const showTimerBanner = timer.running && (screen === "home" || screen === "checkin");

  return (
    <Shell dim={screen === "phonedown"}>
      {showTimerBanner && timer.remaining !== null && (
        <ScreenTimerBanner remaining={timer.remaining} expired={timer.expired} onGoOutside={goOut} onCancel={timer.cancel} />
      )}

      {screen === "home" && <Home onGoOut={goOut} timerRunning={timer.running} onStartTimer={timer.start} />}

      {screen === "checkin" && <CheckIn onSubmit={generate} onBack={() => dispatch({ type: "go", screen: "home" })} />}

      {screen === "generating" && (
        <Generating
          error={state.error}
          onCancel={cancelGeneration}
          onRetry={() => lastRequest.current && generate(lastRequest.current)}
        />
      )}

      {screen === "step" && response && (
        <MissionStep
          key={stepIndex}
          response={response}
          stepIndex={stepIndex}
          onPutPhoneDown={() => dispatch({ type: "putPhoneDown" })}
          onNext={() => dispatch({ type: "next" })}
        />
      )}

      {screen === "phonedown" && response && (
        <PhoneDown
          key={stepIndex}
          step={response.mission.steps[stepIndex]}
          isLast={stepIndex === response.mission.steps.length - 1}
          onReady={() => dispatch({ type: "next" })}
        />
      )}

      {screen === "reflection" && response && (
        <Reflection prompt={response.mission.reflection_prompt} onDone={(text) => dispatch({ type: "reflected", text })} />
      )}

      {screen === "complete" && response && (
        <Complete closingMessage={response.mission.closing_message} reflection={state.reflection} title={response.mission.title} />
      )}
    </Shell>
  );
}
