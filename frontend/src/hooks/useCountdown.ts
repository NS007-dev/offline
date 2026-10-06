import { useEffect, useRef, useState } from "react";

/**
 * Counts down from `totalSeconds`.
 * It compares against the clock instead of counting ticks, so it stays correct
 * even if the phone screen sleeps and the browser pauses timers.
 */
export function useCountdown(totalSeconds: number) {
  const endsAt = useRef(Date.now() + totalSeconds * 1000);
  const [remaining, setRemaining] = useState(totalSeconds);

  useEffect(() => {
    endsAt.current = Date.now() + totalSeconds * 1000;
    const tick = () => setRemaining(Math.max(0, Math.ceil((endsAt.current - Date.now()) / 1000)));
    tick();
    const id = window.setInterval(tick, 500);
    document.addEventListener("visibilitychange", tick);
    return () => {
      window.clearInterval(id);
      document.removeEventListener("visibilitychange", tick);
    };
  }, [totalSeconds]);

  return { remaining, done: remaining === 0 };
}
