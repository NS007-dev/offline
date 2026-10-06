import { useState } from "react";
import { Compass } from "../components/Compass";
import { useFocusOnMount } from "../hooks/useFocusOnMount";

interface Props {
  closingMessage: string;
  reflection: string | null;
  title: string;
}

export function Complete({ closingMessage, reflection, title }: Props) {
  const headingRef = useFocusOnMount<HTMLHeadingElement>();
  const [stillHere, setStillHere] = useState(false);

  function handleClose() {
    // Browsers only let a page close itself if a script opened it, so this often does nothing.
    window.close();
    window.setTimeout(() => setStillHere(true), 300);
  }

  return (
    <div className="stack stack--center">
      <Compass size={120} />
      <h1 className="closing" ref={headingRef} tabIndex={-1}>
        {closingMessage}
      </h1>
      {reflection && <blockquote className="reflection-echo">&ldquo;{reflection}&rdquo;</blockquote>}
      <p className="stamp" aria-hidden="true">
        <span>EXPEDITION COMPLETE</span>
        <strong>{title}</strong>
      </p>
      <button className="btn btn--primary btn--big" onClick={handleClose}>
        CLOSE OFFLINE
      </button>
      {stillHere && (
        <p className="muted center" role="status">
          Your browser won&rsquo;t let a page close itself. Swipe this tab away, or just lock your phone. Go on.
        </p>
      )}
    </div>
  );
}
