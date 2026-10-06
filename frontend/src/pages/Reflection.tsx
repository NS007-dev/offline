import { useState } from "react";
import { useFocusOnMount } from "../hooks/useFocusOnMount";

interface Props {
  prompt: string;
  onDone: (text: string | null) => void;
}

const MAX_CHARS = 200;
const MOODS = ["Calm", "Curious", "Delighted", "Surprised", "Tired"];

export function Reflection({ prompt, onDone }: Props) {
  const headingRef = useFocusOnMount<HTMLHeadingElement>();
  const [text, setText] = useState("");
  const [mood, setMood] = useState("");

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    onDone(`${mood} ${text.trim()}`.trim() || null);
  }

  return (
    <form className="stack" onSubmit={handleSubmit}>
      <h1 className="screen-title" ref={headingRef} tabIndex={-1}>
        What did you notice?
      </h1>
      <div className="moods" role="group" aria-label="How did it feel?">
        {MOODS.map((m) => (
          <button type="button" key={m} className="mood" aria-pressed={mood === m} onClick={() => setMood(mood === m ? "" : m)}>
            {m}
          </button>
        ))}
      </div>
      <label className="lead" htmlFor="reflection">
        {prompt}
      </label>
      <textarea
        id="reflection"
        className="textarea"
        rows={3}
        maxLength={MAX_CHARS}
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder="One sentence is plenty."
      />
      <p className="muted">Optional. It isn&rsquo;t saved or sent anywhere.</p>
      <div className="actions">
        <button type="submit" className="btn btn--primary btn--big">
          {text.trim() || mood ? "DONE" : "SKIP"}
        </button>
      </div>
    </form>
  );
}
