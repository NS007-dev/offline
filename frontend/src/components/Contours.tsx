/**
 * Topographic contour lines: a map you're not meant to follow.
 * Drawn from a little maths so the shapes look hand-drawn but never change between renders.
 */
function blob(radius: number, phase: number): string {
  const points: string[] = [];
  const steps = 72;
  for (let i = 0; i <= steps; i++) {
    const angle = (i / steps) * Math.PI * 2;
    const wobble = 1 + 0.13 * Math.sin(3 * angle + phase) + 0.07 * Math.sin(5 * angle - phase * 1.7) + 0.04 * Math.sin(8 * angle + phase);
    const x = 200 + Math.cos(angle) * radius * wobble;
    const y = 200 + Math.sin(angle) * radius * wobble * 0.88;
    points.push(`${i === 0 ? "M" : "L"}${x.toFixed(1)} ${y.toFixed(1)}`);
  }
  return points.join(" ") + " Z";
}

const RINGS = Array.from({ length: 9 }, (_, i) => ({ radius: 22 + i * 21, phase: 0.6 + i * 0.22 }));

export function Contours() {
  return (
    <svg className="contours" viewBox="0 0 400 400" aria-hidden="true" focusable="false">
      {RINGS.map((ring, i) => (
        <path key={i} d={blob(ring.radius, ring.phase)} fill="none" stroke="currentColor" strokeWidth={i % 4 === 0 ? 1.6 : 0.9} />
      ))}
    </svg>
  );
}
