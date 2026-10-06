import { useFocusOnMount } from "../hooks/useFocusOnMount";
import { useCountdown } from "../hooks/useCountdown";
import { formatClock } from "../lib/format";
import type { Step } from "../types/mission";

interface Props {
  step: Step;
  isLast: boolean;
  onReady: () => void;
}

/** Deliberately bare: a quiet timer, the instruction, and one button. */
export function PhoneDown({ step, isLast, onReady }: Props) {
  const headingRef = useFocusOnMount<HTMLHeadingElement>();
  const { remaining, done } = useCountdown(step.duration_minutes * 60);
  const hasTimer = step.duration_minutes > 0;

  return (
    <div className="stack stack--center phone-down">
      <h1 className="phone-down__title" ref={headingRef} tabIndex={-1}>
        Phone down.
      </h1>

      {hasTimer && (
        <div className="ring">
          <svg viewBox="0 0 200 200" aria-hidden="true" focusable="false">
            <circle cx="100" cy="100" r="88" className="ring__track" />
            <circle cx="100" cy="100" r="88" className="ring__bar" strokeDasharray={553} strokeDashoffset={553 * (1 - remaining / (step.duration_minutes * 60))} />
          </svg>
          <p className="phone-down__clock" role="timer" aria-live="off">
            {formatClock(remaining)}
          </p>
        </div>
      )}

      <p className="phone-down__instruction">{step.instruction}</p>

      <p className="visually-hidden" role="status">
        {done && hasTimer ? "Time is up. You can come back when you are ready." : ""}
      </p>

      <button className={done || !hasTimer ? "btn btn--primary btn--big" : "btn btn--ghost"} onClick={onReady}>
        {done || !hasTimer ? (isLast ? "I\u2019M DONE" : "READY FOR THE NEXT STEP") : "I\u2019m done early"}
      </button>
    </div>
  );
}
