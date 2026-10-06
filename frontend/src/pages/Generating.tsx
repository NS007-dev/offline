import { useEffect, useState } from "react";
import { Compass } from "../components/Compass";
import { useFocusOnMount } from "../hooks/useFocusOnMount";
import type { ApiErrorKind } from "../lib/api";

interface Props {
  error: { kind: ApiErrorKind; message: string } | null;
  onCancel: () => void;
  onRetry: () => void;
}

export function Generating({ error, onCancel, onRetry }: Props) {
  const headingRef = useFocusOnMount<HTMLHeadingElement>();
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    if (error) return;
    const id = window.setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => window.clearInterval(id);
  }, [error]);

  if (error) {
    return (
      <div className="stack">
        <h1 className="screen-title" ref={headingRef} tabIndex={-1}>
          {error.kind === "unreachable" ? "Can\u2019t reach OFFLINE" : "That didn\u2019t work"}
        </h1>
        <p className="lead">{error.message}</p>
        {error.kind === "unreachable" && (
          <p className="muted">
            Start the backend (see the README), then try again:
            <br />
            <code>python3 -m uvicorn app.main:app --reload</code>
          </p>
        )}
        <div className="actions">
          <button className="btn btn--primary btn--big" onClick={onRetry}>
            TRY AGAIN
          </button>
          <button className="link-button" onClick={onCancel}>
            Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="stack stack--center">
      <Compass spin size={110} />
      <h1 className="screen-title" ref={headingRef} tabIndex={-1}>
        Finding your mission&hellip;
      </h1>
      <p className="lead" role="status">
        Gemma is writing it right here on your device.
      </p>
      {seconds >= 20 && (
        <p className="muted">Local models can take a little while. Hang tight, or go back and try later.</p>
      )}
      <button className="link-button" onClick={onCancel}>
        Cancel
      </button>
    </div>
  );
}
