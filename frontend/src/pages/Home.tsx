import { Compass } from "../components/Compass";
import { useFocusOnMount } from "../hooks/useFocusOnMount";


interface Props {
  onGoOut: () => void;
  timerRunning: boolean;
  onStartTimer: (minutes: number) => void;
}

const TIMER_CHOICES = [10, 20, 30, 45];

export function Home({ onGoOut, timerRunning, onStartTimer }: Props) {
  const headingRef = useFocusOnMount<HTMLHeadingElement>();
  return (
    <>
      <div className="stack stack--center home">
        <Compass />
        <h1 className="wordmark" ref={headingRef} tabIndex={-1}>
          OFFLINE
        </h1>
        <p className="tagline">An AI adventure guide designed to become unnecessary.</p>
        <button className="btn btn--primary btn--big" onClick={onGoOut}>
          I&rsquo;M GOING OUT
        </button>
      </div>

      {!timerRunning && (
        <details className="screen-timer">
          <summary>Screen-time reminder (optional)</summary>
          <p className="muted">
            Start a timer when you begin scrolling. OFFLINE will nudge you outside when it ends. It only counts
            time inside this page and never looks at anything else.
          </p>
          <div className="screen-timer__buttons">
            {TIMER_CHOICES.map((minutes) => (
              <button key={minutes} className="btn btn--ghost btn--small" onClick={() => onStartTimer(minutes)}>
                {minutes} min
              </button>
            ))}
          </div>
        </details>
      )}
    </>
  );
}
