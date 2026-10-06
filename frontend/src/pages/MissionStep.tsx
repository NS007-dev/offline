import { Trail } from "../components/Trail";
import { useFocusOnMount } from "../hooks/useFocusOnMount";
import { describeFallback } from "../lib/format";
import type { MissionResponse } from "../types/mission";

interface Props {
  response: MissionResponse;
  stepIndex: number;
  onPutPhoneDown: () => void;
  onNext: () => void;
}

export function MissionStep({ response, stepIndex, onPutPhoneDown, onNext }: Props) {
  const headingRef = useFocusOnMount<HTMLHeadingElement>();
  const { mission } = response;
  const step = mission.steps[stepIndex];
  const isFirst = stepIndex === 0;
  const isLast = stepIndex === mission.steps.length - 1;
  // On the first screen the mission title is the page heading (h1); on later steps the step label is.
  const StepHeading = isFirst ? "h2" : "h1";

  return (
    <div className={isFirst ? "stack reveal" : "stack"}>
      {isFirst ? (
        <header className="mission-head">
          <p className="eyebrow">Your mission</p>
          <h1 className="mission-title" ref={headingRef} tabIndex={-1}>
            {mission.title}
          </h1>
          <p className="lead">{mission.intro}</p>
          <p className="safety-note">Stay in ordinary public places. Follow signs, traffic rules and your own good judgement.</p>
          {response.source === "fallback" && <p className="notice">{describeFallback(response.fallback_reason)}</p>}
        </header>
      ) : (
        <p className="eyebrow">{mission.title}</p>
      )}

      <Trail total={mission.steps.length} current={stepIndex} />

      <section className="step" aria-labelledby="step-label">
        <span className="step__numeral" aria-hidden="true">
          {step.number}
        </span>
        <StepHeading className="step__label" id="step-label" ref={isFirst ? undefined : headingRef} tabIndex={isFirst ? undefined : -1}>
          STEP {step.number} <span className="step__of">of {mission.steps.length}</span>
        </StepHeading>
        <p className="step__text">{step.instruction}</p>
      </section>

      <div className="actions">
        {step.phone_down ? (
          <button className="btn btn--primary btn--big" onClick={onPutPhoneDown}>
            PUT PHONE DOWN
          </button>
        ) : (
          <button className="btn btn--primary btn--big" onClick={onNext}>
            {isLast ? "I\u2019M DONE" : "NEXT STEP"}
          </button>
        )}
      </div>

      {isFirst && response.source === "gemma" && (
        <p className="muted center footnote">Written by {response.model ?? "Gemma"}, running locally with Ollama.</p>
      )}
    </div>
  );
}
