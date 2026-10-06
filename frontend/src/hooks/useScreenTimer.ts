import { useCallback, useEffect, useState } from "react";

/**
 * The optional "Outside Button" session timer (spec section 12).
 * The user starts it on purpose. It only counts down inside this page:
 * no history, no other apps, no storage. Closing the tab forgets it.
 */
export function useScreenTimer() {
  const [endsAt, setEndsAt] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());

  const remaining = endsAt === null ? null : Math.max(0, Math.ceil((endsAt - now) / 1000));
  const expired = remaining === 0;

  useEffect(() => {
    if (endsAt === null || expired) return;
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, [endsAt, expired]);

  const start = useCallback((minutes: number) => {
    const current = Date.now();
    setNow(current);
    setEndsAt(current + minutes * 60_000);
  }, []);

  const cancel = useCallback(() => setEndsAt(null), []);

  return { running: endsAt !== null, remaining, expired, start, cancel };
}
