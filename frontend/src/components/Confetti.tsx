const COLOURS = ["#FFC933", "#FF6B9A", "#4CC9F0", "#5AD8A6", "#8B5CF6", "#FF6B4A"];
/** Pure-CSS confetti burst. Shapes are fixed, so it never re-randomises. */
export function Confetti() {
  return (
    <div className="confetti" aria-hidden="true">
      {Array.from({ length: 30 }, (_, i) => (
        <span key={i} style={{ left: `${(i * 37) % 100}%`, background: COLOURS[i % 6], animationDelay: `${(i % 7) * 0.12}s`, animationDuration: `${2.4 + (i % 5) * 0.4}s`, transform: `rotate(${i * 47}deg)` }} />
      ))}
    </div>
  );
}
