/** The mission drawn as a route on a map: done stops inked in, the X where you are, the rest still faint. */
export function Trail({ total, current }: { total: number; current: number }) {
  const pts = Array.from({ length: total }, (_, i) => ({ x: 14 + (i * 272) / Math.max(1, total - 1), y: 24 + 9 * Math.sin(i * 1.9) }));
  return (
    <svg className="trail" viewBox="0 0 300 48" aria-hidden="true" focusable="false">
      {pts.slice(1).map((p, i) => (
        <line key={i} x1={pts[i].x} y1={pts[i].y} x2={p.x} y2={p.y} className={i < current ? "trail__done" : "trail__todo"} />
      ))}
      {pts.map((p, i) =>
        i === current ? (
          <g key={i} transform={`translate(${p.x} ${p.y})`}>
            <g className="trail__x">
              <line x1="-7" y1="-7" x2="7" y2="7" />
              <line x1="-7" y1="7" x2="7" y2="-7" />
            </g>
          </g>
        ) : (
          <circle key={i} cx={p.x} cy={p.y} r="5" className={i < current ? "trail__dot trail__dot--done" : "trail__dot"} />
        ),
      )}
    </svg>
  );
}
