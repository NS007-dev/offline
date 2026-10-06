import { useState } from "react";
import { ChoiceGroup } from "../components/ChoiceGroup";
import { useFocusOnMount } from "../hooks/useFocusOnMount";
import type { Environment, MissionRequest, Need, TimeOption } from "../types/mission";

interface Props {
  onSubmit: (request: MissionRequest) => void;
  onBack: () => void;
}

const TIMES: { value: TimeOption; label: string; icon: string }[] = [
  { value: 15, label: "15 min", icon: "◔" },
  { value: 30, label: "30 min", icon: "◑" },
  { value: 60, label: "60 min", icon: "◕" },
  { value: 90, label: "90+ min", icon: "●" },
];

const NEEDS: { value: Need; label: string; icon: string }[] = [
  { value: "clear_head", label: "Clear my head", icon: "☁" },
  { value: "explore", label: "Explore", icon: "⚑" },
  { value: "move", label: "Move", icon: "➤" },
  { value: "be_alone", label: "Be alone", icon: "☾" },
  { value: "surprise", label: "Surprise me", icon: "✦" },
];

const PLACES: { value: Environment; label: string }[] = [
  { value: "unsure", label: "Not sure" },
  { value: "city", label: "City or town" },
  { value: "park", label: "Park or green space" },
  { value: "suburb", label: "Neighbourhood streets" },
  { value: "countryside", label: "Countryside or village" },
];

export function CheckIn({ onSubmit, onBack }: Props) {
  const headingRef = useFocusOnMount<HTMLHeadingElement>();
  const [time, setTime] = useState<TimeOption | null>(null);
  const [need, setNeed] = useState<Need | null>(null);
  const [environment, setEnvironment] = useState<Environment>("unsure");

  const ready = time !== null && need !== null;

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (time !== null && need !== null) onSubmit({ time_minutes: time, need, environment });
  }

  return (
    <form className="stack" onSubmit={handleSubmit}>
      <h1 className="screen-title" ref={headingRef} tabIndex={-1}>
        Quick check-in
      </h1>

      <ChoiceGroup legend="How much time do you have?" name="time" layout="grid" options={TIMES} value={time} onChange={setTime} />
      <ChoiceGroup legend="What do you need?" name="need" layout="grid" options={NEEDS} value={need} onChange={setNeed} />

      <details className="optional">
        <summary>Where are you? (optional)</summary>
        <p className="muted">No location is ever requested. This just helps shape the mission.</p>
        <ChoiceGroup legend="Where are you?" name="environment" options={PLACES} value={environment} onChange={setEnvironment} />
      </details>

      <div className="actions">
        <button type="submit" className="btn btn--primary btn--big" disabled={!ready} aria-describedby="checkin-hint">
          SEND ME OUT
        </button>
        {!ready && (
          <p id="checkin-hint" className="muted center">
            Choose a time and a need to continue.
          </p>
        )}
        <button type="button" className="link-button" onClick={onBack}>
          Back
        </button>
      </div>
    </form>
  );
}
