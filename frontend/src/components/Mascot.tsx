/** Pip, the sun-blob. Blinks, bounces, and cheers when you finish. */
export function Mascot({ cheer = false, size = 140 }: { cheer?: boolean; size?: number }) {
  return (
    <svg className={cheer ? "mascot mascot--cheer" : "mascot"} width={size} height={size} viewBox="0 0 120 120" aria-hidden="true" focusable="false">
      <g className="mascot__rays" stroke="#2B1B4A" strokeWidth="5" strokeLinecap="round">
        {Array.from({ length: 10 }, (_, i) => (
          <line key={i} x1="60" y1="8" x2="60" y2="19" transform={`rotate(${i * 36} 60 60)`} />
        ))}
      </g>
      <circle cx="60" cy="60" r="35" fill="#FFC933" stroke="#2B1B4A" strokeWidth="5" />
      <circle cx="38" cy="68" r="7" fill="#FF6B9A" opacity="0.7" />
      <circle cx="82" cy="68" r="7" fill="#FF6B9A" opacity="0.7" />
      <g className="mascot__eyes" fill="#2B1B4A">
        <ellipse cx="48" cy="55" rx="4.5" ry="6" />
        <ellipse cx="72" cy="55" rx="4.5" ry="6" />
      </g>
      <path d={cheer ? "M46 68 Q60 86 74 68 Z" : "M48 70 Q60 80 72 70"} fill={cheer ? "#FF6B4A" : "none"} stroke="#2B1B4A" strokeWidth="4.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
