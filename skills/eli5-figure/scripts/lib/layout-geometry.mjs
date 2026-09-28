// Polyline geometry for layout.mjs: rounding, jog removal, operator snapping, label placement.
// Points are {x, y} in canvas units; edges are orthogonal polylines.

export const r2 = (v) => Math.round(v * 2) / 2;
const axisOf = (a, b) => (Math.abs(a.x - b.x) < 0.01 ? 'v' : Math.abs(a.y - b.y) < 0.01 ? 'h' : null);
const overlaps = (a, b) => a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
const grow = (b, d) => ({ x: b.x - d, y: b.y - d, w: b.w + 2 * d, h: b.h + 2 * d });

export function roundedPath(pts, radius) {
  let d = `M${pts[0].x} ${pts[0].y}`;
  for (let i = 1; i < pts.length - 1; i++) {
    const a = pts[i - 1], b = pts[i], c = pts[i + 1];
    const l1 = Math.hypot(b.x - a.x, b.y - a.y), l2 = Math.hypot(c.x - b.x, c.y - b.y);
    const r = Math.min(radius, l1 / 2, l2 / 2);
    if (r < 0.5) { d += `L${b.x} ${b.y}`; continue; }
    const p = { x: r2(b.x - ((b.x - a.x) / l1) * r), y: r2(b.y - ((b.y - a.y) / l1) * r) };
    const q = { x: r2(b.x + ((c.x - b.x) / l2) * r), y: r2(b.y + ((c.y - b.y) / l2) * r) };
    d += `L${p.x} ${p.y}Q${b.x} ${b.y} ${q.x} ${q.y}`;
  }
  const z = pts[pts.length - 1];
  return d + `L${z.x} ${z.y}`;
}

function cleanPolyline(pts) {
  const out = [];
  for (const p of pts) if (!out.length || Math.hypot(p.x - out.at(-1).x, p.y - out.at(-1).y) > 0.01) out.push(p);
  return out.filter((p, i) => i === 0 || i === out.length - 1 || axisOf(out[i - 1], p) !== axisOf(p, out[i + 1]));
}

// ELK leaves short S-jogs where an edge crosses a container boundary. Remove each jog by
// sliding one of its two parallel neighbors onto the other; a segment that ends on a port may
// slide only along that node side (`ends.start` / `ends.end`, null when the port is fixed).
export function straighten(pts, ends, jogMax) {
  for (let changed = true; changed;) {
    changed = false;
    for (let i = 1; i + 2 < pts.length; i++) {
      const [a, b, c, d] = [pts[i - 1], pts[i], pts[i + 1], pts[i + 2]];
      const run = axisOf(a, b), jog = axisOf(b, c);
      if (!run || !jog || run === jog || axisOf(c, d) !== run || Math.hypot(c.x - b.x, c.y - b.y) >= jogMax) continue;
      const along = run === 'v' ? 'y' : 'x', k = run === 'v' ? 'x' : 'y';
      if (Math.sign(b[along] - a[along]) !== Math.sign(d[along] - c[along])) continue;
      const fits = (end, v) => end && end.k === k && v >= end.lo && v <= end.hi;
      if (i + 2 < pts.length - 1 || fits(ends.end, b[k])) { c[k] = b[k]; d[k] = b[k]; }
      else if (i - 1 > 0 || fits(ends.start, c[k])) { a[k] = c[k]; b[k] = c[k]; }
      else continue;
      pts = cleanPolyline(pts);
      changed = true;
      break;
    }
  }
  return pts;
}

// Move an endpoint that sits on an operator's bounding box onto the circle, along its segment.
export function snapToCircle(end, prev, c, r) {
  const axis = axisOf(end, prev);
  if (axis === 'v' && Math.abs(end.x - c.x) < r) end.y = r2(c.y + Math.sign(prev.y - c.y) * Math.sqrt(r * r - (end.x - c.x) ** 2));
  if (axis === 'h' && Math.abs(end.y - c.y) < r) end.x = r2(c.x + Math.sign(prev.x - c.x) * Math.sqrt(r * r - (end.y - c.y) ** 2));
}

// Leftmost x in the band where the label crosses no edge segment, or null when every spot is crossed.
export function placeGroupLabel(band, label, segments, gap) {
  let x = band.x;
  while (x + label.width <= band.right) {
    const hit = segments.find(([a, b]) => Math.max(a.x, b.x) > x - gap && Math.min(a.x, b.x) < x + label.width + gap
      && Math.max(a.y, b.y) > band.y - gap && Math.min(a.y, b.y) < band.y + band.h + gap);
    if (!hit) return x;
    x = Math.max(hit[0].x, hit[1].x) + gap;
  }
  return null;
}

const segBox = ([a, b], half) => grow({ x: Math.min(a.x, b.x), y: Math.min(a.y, b.y), w: Math.abs(a.x - b.x), h: Math.abs(a.y - b.y) }, half);

// Edge labels placed after layout, beside the longest free straight run of their own edge:
// `gap` from the line, clear of the arrowhead, nodes, other lines, other labels, and container
// borders. Returns one box per labeled line, or null where no free spot exists.
// lines: [{ pts, half, label: {width, height} | null, arrowEnd, arrowStart }]
export function placeEdgeLabels(lines, { obstacles, containers, canvas, gap, clearEnd }) {
  const placed = [];
  const allSegs = lines.flatMap((l) => l.pts.slice(1).map((p, k) => ({ seg: [l.pts[k], p], half: l.half })));
  const free = (box) => {
    const halo = grow(box, 2);
    if (box.x < canvas.x || box.y < canvas.y || box.x + box.w > canvas.x + canvas.w || box.y + box.h > canvas.y + canvas.h) return false;
    if (obstacles.some((o) => overlaps(halo, o))) return false;
    if (placed.some((o) => o && overlaps(halo, o))) return false;
    if (allSegs.some(({ seg, half }) => overlaps(box, segBox(seg, half + 1)))) return false;
    // Inside or outside a container, never across its border.
    return containers.every((c) => !overlaps(box, c) || (box.x >= c.x && box.y >= c.y && box.x + box.w <= c.x + c.w && box.y + box.h <= c.y + c.h));
  };
  for (const l of lines) {
    if (!l.label) { placed.push(null); continue; }
    const { width: w, height: h } = l.label;
    const segs = l.pts.slice(1).map((p, k) => {
      let [a, b] = [{ ...l.pts[k] }, { ...p }];
      const len = Math.hypot(b.x - a.x, b.y - a.y) || 1;
      const ux = (b.x - a.x) / len, uy = (b.y - a.y) / len;
      // Keep the label clear of the arrowheads at the ends of the edge.
      if (k === l.pts.length - 2 && l.arrowEnd) b = { x: b.x - ux * clearEnd, y: b.y - uy * clearEnd };
      if (k === 0 && l.arrowStart) a = { x: a.x + ux * clearEnd, y: a.y + uy * clearEnd };
      return { a, b, len: Math.hypot(b.x - a.x, b.y - a.y), axis: axisOf(l.pts[k], p) };
    }).filter((s) => s.axis && s.len > 0).sort((p, q) => q.len - p.len);
    let spot = null;
    for (const s of segs) {
      for (const t of [0.5, 0.3, 0.7, 0.15, 0.85]) {
        const m = { x: s.a.x + (s.b.x - s.a.x) * t, y: s.a.y + (s.b.y - s.a.y) * t };
        const off = l.half + gap;
        const cands = s.axis === 'v'
          ? [{ x: m.x + off, y: m.y - h / 2 }, { x: m.x - off - w, y: m.y - h / 2 }]
          : [{ x: m.x - w / 2, y: m.y - off - h }, { x: m.x - w / 2, y: m.y + off }];
        for (const c of cands) {
          const box = { x: r2(c.x), y: r2(c.y), w, h };
          const along = s.axis === 'v' ? [box.y, box.y + h, Math.min(s.a.y, s.b.y), Math.max(s.a.y, s.b.y)] : [box.x, box.x + w, Math.min(s.a.x, s.b.x), Math.max(s.a.x, s.b.x)];
          if (along[0] < along[2] || along[1] > along[3]) continue;
          if (free(box)) { spot = box; break; }
        }
        if (spot) break;
      }
      if (spot) break;
    }
    placed.push(spot);
  }
  return placed;
}
