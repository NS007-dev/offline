import { formatClock } from "../lib/format";

interface Props {
  remaining: number;
  expired: boolean;
  onGoOutside: () => void;
  onCancel: () => void;
}

/** Shown only on Home and Check-in, and only if the user started the timer. */
export function ScreenTimerBanner({ remaining, expired, onGoOutside, onCancel }: Props) {
  if (expired) {
    return (
      <div className="timer-banner timer-banner--expired" role="alert">
        <p className="timer-banner__text">Your screen time is up. Time to go outside.</p>
        <button className="btn btn--primary btn--small" onClick={onGoOutside}>
          I&rsquo;M GOING OUT
        </button>
      </div>
    );
  }
  return (
    <div className="timer-banner">
      <p className="timer-banner__text">
        Screen timer: <strong>{formatClock(remaining)}</strong> left
      </p>
      <button className="link-button" onClick={onCancel}>
        Stop timer
      </button>
    </div>
  );
}
