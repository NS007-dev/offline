/** A compass rose. The needle swings, then settles. `spin` makes it search (used while loading). */
export function Compass({ spin = false, size = 150 }: { spin?: boolean; size?: number }) {
  const ticks = Array.from({ length: 24 }, (_, i) => i);
  return (
    <svg className={spin ? "compass compass--spin" : "compass"} width={size} height={size} viewBox="0 0 160 160" aria-hidden="true" focusable="false" fill="none" stroke="currentColor">
      <circle cx="80" cy="80" r="70" strokeWidth="2.5" />
      <circle cx="80" cy="80" r="62" strokeWidth="1" />
      {ticks.map((i) => (
        <line key={i} x1="80" y1="10" x2="80" y2={i % 6 === 0 ? 24 : 17} strokeWidth={i % 6 === 0 ? 2.5 : 1} transform={`rotate(${i * 15} 80 80)`} />
      ))}
      <path d="M80 28 L88 80 L80 132 L72 80 Z" strokeWidth="1.5" fill="currentColor" opacity="0.12" />
      <path d="M28 80 L80 72 L132 80 L80 88 Z" strokeWidth="1.5" fill="currentColor" opacity="0.12" />
      <g className="compass__needle">
        <path d="M80 34 L87 80 L73 80 Z" fill="#b5342a" stroke="#b5342a" />
        <path d="M80 126 L87 80 L73 80 Z" fill="currentColor" />
      </g>
      <circle cx="80" cy="80" r="4.5" fill="#f3e6c8" strokeWidth="2" />
      <text x="80" y="8" textAnchor="middle" fontSize="11" fontWeight="700" fill="currentColor" stroke="none">N</text>
    </svg>
  );
}
