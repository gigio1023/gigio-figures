// graph.json -> contract SVG through an elkjs layered layout. Labels are measured in Chromium
// with the real fonts before layout so node sizes and label boxes are exact.
import { cacheRequire } from './env.mjs';
import { arrowParams } from './figure.mjs';
import { placeEdgeLabels, placeGroupLabel, r2, roundedPath, snapToCircle, straighten } from './layout-geometry.mjs';
import { mathMetrics } from './math.mjs';
import { hueNames, TEXT_ROLES, themeCss } from './theme.mjs';

// Tuned in the layout trials: layered, orthogonal, model order kept, hierarchy in one pass.
const ELK_BASE = {
  'elk.algorithm': 'layered',
  'elk.edgeRouting': 'ORTHOGONAL',
  'elk.hierarchyHandling': 'INCLUDE_CHILDREN',
  'elk.layered.nodePlacement.strategy': 'BRANDES_KOEPF',
  'elk.layered.nodePlacement.bk.fixedAlignment': 'BALANCED',
  'elk.layered.considerModelOrder.strategy': 'NODES_AND_EDGES',
  'elk.layered.crossingMinimization.forceNodeModelOrder': 'true',
  'elk.spacing.nodeNode': '28',
  'elk.layered.spacing.nodeNodeBetweenLayers': '44',
  'elk.layered.spacing.edgeNodeBetweenLayers': '20',
  'elk.spacing.edgeEdge': '12',
  // Also the stub length out of a side port: long enough for an arrowhead plus a rounded bend.
  'elk.spacing.edgeNode': '20',
  'elk.edgeLabels.inline': 'false',
  'elk.layered.edgeLabels.sideSelection': 'ALWAYS_UP',
  'elk.json.edgeCoords': 'ROOT',
  'elk.json.shapeCoords': 'ROOT',
};

const SIDE = { N: 'NORTH', E: 'EAST', S: 'SOUTH', W: 'WEST', NORTH: 'NORTH', EAST: 'EAST', SOUTH: 'SOUTH', WEST: 'WEST' };
const FLOW = {
  UP: { out: 'NORTH', in: 'SOUTH' },
  DOWN: { out: 'SOUTH', in: 'NORTH' },
  RIGHT: { out: 'EAST', in: 'WEST' },
  LEFT: { out: 'WEST', in: 'EAST' },
};
const OPS = { '+': 'plus', '⊕': 'plus', plus: 'plus', '×': 'times', '⊗': 'times', '*': 'times', times: 'times', '-': 'minus', '−': 'minus', '⊖': 'minus', minus: 'minus' };
const LATIN_CAPS = /^[A-Z0-9 ._/-]+$/;
// Two ports fit on one side of an operator: at 45 degrees their arrow tips stay about 12.7u apart.
const OP_MAX_PER_SIDE = 2;

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const up = (v, step) => Math.ceil(v / step - 1e-9) * step;
const kindOf = (n) => n.kind || 'box';

// Layout failures the author fixes by changing the graph; the CLI prints them without a stack.
export class LayoutError extends Error {
  constructor(message, exitCode = 1) { super(message); this.exitCode = exitCode; }
}

function validate(g) {
  const bad = (msg) => { throw new LayoutError(msg, 2); };
  if (!FLOW[g.direction]) bad(`direction must be UP, DOWN, RIGHT, or LEFT, got "${g.direction}"`);
  for (const [k, v] of Object.entries(g.spacing || {})) {
    if (!['node', 'layer'].includes(k)) bad(`spacing.${k} is not supported; use spacing.node and spacing.layer`);
    if (!(v > 0)) bad(`spacing.${k} must be a positive number`);
  }
  const ids = new Set();
  for (const n of g.nodes) {
    if (!n.id) bad('every node needs an id');
    if (ids.has(n.id)) bad(`duplicate node id "${n.id}"`);
    ids.add(n.id);
    if (!['box', 'op', 'chip'].includes(kindOf(n))) bad(`node "${n.id}": kind must be box, op, or chip`);
    if (kindOf(n) === 'op' && !OPS[n.title || '+']) bad(`node "${n.id}": op title must be + ⊕ × ⊗ − ⊖`);
    if (kindOf(n) !== 'op' && !n.title && !n.tex) bad(`node "${n.id}" needs a title`);
  }
  for (const e of g.edges) {
    for (const end of ['from', 'to']) if (!ids.has(e[end])) bad(`edge ${e.from} -> ${e.to}: unknown node "${e[end]}"`);
    for (const s of ['fromSide', 'toSide']) if (e[s] && !SIDE[e[s]]) bad(`edge ${e.from} -> ${e.to}: ${s} must be N, E, S, or W`);
    if (e.arrow && !['end', 'start', 'both', 'none'].includes(e.arrow)) bad(`edge ${e.from} -> ${e.to}: arrow must be end, start, both, or none`);
  }
  for (const gr of g.groups) {
    if (ids.has(gr.id)) bad(`group id "${gr.id}" collides with a node id`);
    for (const m of gr.members || []) if (!ids.has(m)) bad(`group "${gr.id}": unknown member "${m}"`);
  }
}

// Every string the figure will draw, with its text class, measured in one browser round trip.
async function measureLabels(session, graph) {
  const { page, tokens } = session;
  const size = (cls) => tokens.type[TEXT_ROLES[cls.split(' ')[0]]].size_u;
  const jobs = [];
  const want = (key, cls, text, tex) => jobs.push({ key, cls, text, tex });
  for (const n of graph.nodes) {
    if (kindOf(n) === 'op') continue;
    const cls = n.kind === 'chip' ? 't2' : 't';
    want(`${n.id}.title`, n.mono ? `${cls} mono` : cls, n.title || n.tex, n.tex);
    if (n.sub || n.subTex) want(`${n.id}.sub`, 't2', n.sub || n.subTex, n.subTex);
  }
  graph.edges.forEach((e, i) => {
    if (e.label || e.tex) want(`edge${i}`, ['tl', ...(e.labelClasses || [])].join(' '), e.label || e.tex, e.tex);
  });
  for (const g of graph.groups) if (g.label) want(`group.${g.id}`, LATIN_CAPS.test(g.label) ? 'micro' : 't2', g.label);

  await page.evaluate((c) => TF.mount('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"/>', c), themeCss(tokens, 'light'));
  const plain = jobs.filter((j) => !j.tex);
  const measured = await page.evaluate((items) => TF.measureTexts(items), plain.map((j) => ({ cls: j.cls, text: j.text })));
  const out = {};
  plain.forEach((j, i) => { out[j.key] = { ...j, ...measured[i] }; });
  for (const j of jobs.filter((x) => x.tex)) out[j.key] = { ...j, ...mathMetrics(j.tex, size(j.cls), tokens), size: size(j.cls) };
  return out;
}

function sizeNodes(graph, labels, tokens) {
  const sp = tokens.spacing_u;
  const sizes = {};
  for (const n of graph.nodes) {
    if (kindOf(n) === 'op') { sizes[n.id] = { w: 2 * tokens.operator_radius_u, h: 2 * tokens.operator_radius_u }; continue; }
    const title = labels[`${n.id}.title`], sub = labels[`${n.id}.sub`];
    const textW = Math.max(title.width, sub ? sub.width : 0);
    if (n.kind === 'chip') {
      const padX = 2 * sp.unit;
      sizes[n.id] = { w: up(textW + 2 * padX, sp.unit), h: sp.scale.find((s) => s >= title.size + 2 * sp.unit) };
      continue;
    }
    const inkH = title.ascent + title.descent;
    const h = sub ? sp.node_height_two_line : Math.max(sp.node_height_one_line, up(inkH + 2 * sp.node_padding_y, sp.unit));
    sizes[n.id] = { w: up(textW + 2 * sp.node_padding_x, sp.unit), h };
  }
  // Opt-in per group: box members share the widest width so a row of peers reads as a set.
  for (const g of graph.groups.filter((x) => x.equal)) {
    const peers = g.members.filter((m) => kindOf(graph.nodeById[m]) === 'box');
    const w = Math.max(0, ...peers.map((m) => sizes[m].w));
    for (const m of peers) sizes[m].w = w;
  }
  return sizes;
}

// Ports: fan-out from one side shares a port (ELK then reports junction points); every
// incoming edge gets its own port. Order on each side follows model order.
function buildPorts(graph, flow) {
  const nodeIndex = Object.fromEntries(graph.nodes.map((n, i) => [n.id, i]));
  const ports = {};
  const edgePorts = [];
  const add = (node, id, side, order) => {
    const list = (ports[node] ||= []);
    if (!list.some((p) => p.id === id)) list.push({ id, side, order });
  };
  graph.edges.forEach((e, i) => {
    const out = SIDE[e.fromSide] || flow.out;
    const inn = SIDE[e.toSide] || flow.in;
    const style = (e.classes || []).slice().sort().join('.') || 'edge';
    const src = `${e.from}:out:${out}:${style}`;
    const dst = `${e.to}:in:${inn}:${i}`;
    add(e.from, src, out, nodeIndex[e.to] + i / 1000);
    add(e.to, dst, inn, nodeIndex[e.from] + i / 1000);
    edgePorts.push({ src, dst, srcSide: out, dstSide: inn });
  });
  for (const n of graph.nodes.filter((x) => kindOf(x) === 'op')) {
    for (const side of Object.values(FLOW).map((f) => f.in)) {
      const count = (ports[n.id] || []).filter((p) => p.side === side).length;
      if (count > OP_MAX_PER_SIDE) {
        throw new LayoutError(`operator "${n.id}" has ${count} edges on its ${side} side and at most ${OP_MAX_PER_SIDE} arrow tips fit there; route the others to different sides with toSide or fromSide (N, E, S, W)`, 2);
      }
    }
  }
  return { ports, edgePorts };
}

// ELK numbers FIXED_ORDER ports clockwise from the top-left: NORTH left to right, EAST top to
// bottom, SOUTH right to left, WEST bottom to top. Model order runs left to right and top to
// bottom, so SOUTH and WEST lists are reversed before numbering.
function elkPorts(list, node, size) {
  const bySide = (s) => list.filter((p) => p.side === s).sort((a, b) => a.order - b.order);
  const sides = { NORTH: bySide('NORTH'), EAST: bySide('EAST'), SOUTH: bySide('SOUTH'), WEST: bySide('WEST') };
  const ordered = [...sides.NORTH, ...sides.EAST, ...[...sides.SOUTH].reverse(), ...[...sides.WEST].reverse()];
  const isOp = kindOf(node) === 'op';
  // An operator's ports sit on its bounding box: one at the side's middle, two at 45 degrees on
  // the circle. Endpoints are snapped from the box onto the circle after layout.
  const r = size.w / 2, off = r * Math.SQRT1_2;
  const opPos = (p) => {
    const same = sides[p.side];
    const t = same.length === 1 ? 0 : (same.indexOf(p) === 0 ? -off : off);
    return {
      NORTH: [r + t, 0], SOUTH: [r + t, size.h], EAST: [size.w, r + t], WEST: [0, r + t],
    }[p.side];
  };
  return ordered.map((p, i) => ({
    id: p.id,
    width: 0,
    height: 0,
    ...(isOp ? { x: opPos(p)[0], y: opPos(p)[1] } : {}),
    layoutOptions: { 'elk.port.side': p.side, 'elk.port.index': String(i) },
  }));
}

function lineHalfWidth(classes, stroke) {
  if (classes.includes('spine') || classes.includes('emph')) return stroke.emphasis_u / 2;
  if (classes.includes('ghost') || classes.includes('leader')) return stroke.guide_u / 2;
  return stroke.edge_u / 2;
}

// opts.wide allows the 1080u full-width canvas when the layout does not fit 720u.
export async function layoutGraph(session, input, opts = {}) {
  const tokens = session.tokens;
  const graph = { direction: 'UP', nodes: [], edges: [], groups: [], ...input };
  validate(graph);
  graph.nodeById = Object.fromEntries(graph.nodes.map((n) => [n.id, n]));
  for (const g of graph.groups) g.members = [...new Set([...(g.members || []), ...graph.nodes.filter((n) => n.group === g.id).map((n) => n.id)])];
  const groupOf = {};
  for (const g of graph.groups) for (const m of g.members) groupOf[m] = g.id;

  const sp = tokens.spacing_u;
  const gap = sp.edge_label_gap;
  const vertical = ['UP', 'DOWN'].includes(graph.direction);
  const labels = await measureLabels(session, graph);
  const sizes = sizeNodes(graph, labels, tokens);
  const { ports, edgePorts } = buildPorts(graph, FLOW[graph.direction]);
  const labelH = (l) => l.ascent + l.descent;
  const memberIndex = {};
  for (const g of graph.groups) graph.nodes.filter((n) => groupOf[n.id] === g.id).forEach((n, i) => { memberIndex[n.id] = i; });

  const elkNode = (n) => ({
    id: n.id,
    width: sizes[n.id].w,
    height: sizes[n.id].h,
    ports: elkPorts(ports[n.id] || [], n, sizes[n.id]),
    layoutOptions: {
      'elk.portConstraints': kindOf(n) === 'op' ? 'FIXED_POS' : 'FIXED_ORDER',
      // Order hint for the group's semi-interactive crossing minimization.
      ...(n.id in memberIndex ? { 'elk.position': vertical ? `(${memberIndex[n.id] * 1000}, 0)` : `(0, ${memberIndex[n.id] * 1000})` } : {}),
    },
  });

  // One ELK pass plus geometry cleanup. minWidth widens groups whose label found no free spot.
  async function place(minWidth) {
    const children = [];
    const placedGroups = new Set();
    for (const n of graph.nodes) {
      const gid = groupOf[n.id];
      if (!gid) { children.push(elkNode(n)); continue; }
      if (placedGroups.has(gid)) continue;
      placedGroups.add(gid);
      const gl = labels[`group.${gid}`];
      const top = sp.container_padding + (gl ? labelH(gl) + sp.scale[1] : 0);
      const width = Math.max(minWidth[gid] || 0, gl ? gl.width + 2 * sp.container_padding : 0);
      children.push({
        id: gid,
        layoutOptions: {
          'elk.padding': `[top=${top},left=${sp.container_padding},bottom=${sp.container_padding},right=${sp.container_padding}]`,
          'elk.nodeSize.constraints': 'MINIMUM_SIZE',
          // elkjs 0.12.0 applies a group's minimum size in the rotated frame for UP and DOWN.
          'elk.nodeSize.minimum': vertical ? `(0, ${Math.ceil(width)})` : `(${Math.ceil(width)}, 0)`,
          // Fixed-order ports otherwise reorder group members. NODES_AND_EDGES here crashes
          // elkjs 0.12.0's model-order comparator; PREFER_EDGES plus position hints keep order.
          'elk.layered.considerModelOrder.strategy': 'PREFER_EDGES',
          'elk.layered.crossingMinimization.semiInteractive': 'true',
          'elk.layered.edgeLabels.sideSelection': ELK_BASE['elk.layered.edgeLabels.sideSelection'],
        },
        children: graph.nodes.filter((m) => groupOf[m.id] === gid).map(elkNode),
      });
    }
    // In UP and DOWN flows ELK turns each edge label into a node of its own layer, which can
    // reorder real nodes; those labels are placed after layout instead.
    const edges = graph.edges.map((e, i) => {
      const l = labels[`edge${i}`];
      return {
        id: `e${i}`,
        sources: [edgePorts[i].src],
        targets: [edgePorts[i].dst],
        labels: l && !vertical ? [{ id: `e${i}.label`, text: l.text, width: l.width, height: labelH(l) }] : [],
      };
    });
    const spacing = graph.spacing || {};
    const ELK = cacheRequire('elkjs/lib/elk.bundled.js');
    const res = await new ELK().layout({
      id: 'root',
      layoutOptions: {
        ...ELK_BASE,
        'elk.direction': graph.direction,
        // Horizontal flows spend layer gaps on the 720u width budget; use the wider group gap there.
        ...(!vertical ? { 'elk.layered.spacing.nodeNodeBetweenLayers': String(sp.group_gap[1]) } : {}),
        ...(spacing.node ? { 'elk.spacing.nodeNode': String(spacing.node) } : {}),
        ...(spacing.layer ? { 'elk.layered.spacing.nodeNodeBetweenLayers': String(spacing.layer) } : {}),
        'elk.spacing.edgeLabel': String(gap),
        'elk.padding': `[top=${sp.canvas_margin},left=${sp.canvas_margin},bottom=${sp.canvas_margin},right=${sp.canvas_margin}]`,
      },
      children,
      edges,
    });

    const width = Math.ceil(res.width), height = Math.ceil(res.height);
    const u = tokens.units;
    if (width > u.canvas_width_u && !opts.wide) {
      throw new LayoutError([
        `layout is ${width}u wide; the column canvas is ${u.canvas_width_u}u. Try, in order:`,
        `  1. another direction (a long chain reads better DOWN or UP than RIGHT)`,
        `  2. fewer nodes per row (stack peers, or move a side branch to another layer with sides)`,
        `  3. splitting the figure into two`,
        `  or pass --wide for the ${u.wide_canvas_width_u}u full-width canvas.`,
      ].join('\n'));
    }
    if (width > u.wide_canvas_width_u) throw new LayoutError(`layout is ${width}u wide, wider than the ${u.wide_canvas_width_u}u full-width canvas; change direction, put fewer nodes per row, or split the figure`);
    const canvas = width <= u.canvas_width_u ? u.canvas_width_u : u.wide_canvas_width_u;
    const dx = r2((canvas - width) / 2);
    const P = (p) => ({ x: r2(p.x + dx), y: r2(p.y) });

    const shapes = {};
    (function walk(n) { for (const c of n.children || []) { shapes[c.id] = { x: r2(c.x + dx), y: r2(c.y), w: r2(c.width), h: r2(c.height) }; walk(c); } })(res);

    // Where a port-attached segment may slide: along its node side, clear of the corners, and
    // only for an unshared port on a box or chip (an operator's port stays at the circle's side).
    const margin = tokens.radius_u.node + sp.unit;
    const shared = {};
    for (const ep of edgePorts) shared[ep.src] = (shared[ep.src] || 0) + 1;
    const slide = (nodeId, side, port) => {
      const b = shapes[nodeId];
      if (kindOf(graph.nodeById[nodeId]) === 'op' || shared[port] > 1) return null;
      return side === 'NORTH' || side === 'SOUTH' ? { k: 'x', lo: b.x + margin, hi: b.x + b.w - margin } : { k: 'y', lo: b.y + margin, hi: b.y + b.h - margin };
    };
    const lines = res.edges.map((e, i) => {
      const sec = e.sections && e.sections[0];
      let pts = sec ? [sec.startPoint, ...(sec.bendPoints || []), sec.endPoint].map(P) : [];
      const ep = edgePorts[i];
      const src = graph.edges[i];
      if (shared[ep.src] === 1) pts = straighten(pts, { start: slide(src.from, ep.srcSide, ep.src), end: slide(src.to, ep.dstSide, null) }, 2 * sp.unit);
      const circle = (id) => ({ x: shapes[id].x + shapes[id].w / 2, y: shapes[id].y + shapes[id].h / 2 });
      if (kindOf(graph.nodeById[src.to]) === 'op' && pts.length > 1) snapToCircle(pts.at(-1), pts.at(-2), circle(src.to), tokens.operator_radius_u);
      if (kindOf(graph.nodeById[src.from]) === 'op' && pts.length > 1) snapToCircle(pts[0], pts[1], circle(src.from), tokens.operator_radius_u);
      return { src, pts, junctions: (e.junctionPoints || []).map(P), labels: (e.labels || []).map((l) => ({ ...l, x: l.x + dx })) };
    });
    const segments = lines.flatMap((l) => l.pts.slice(1).map((p, k) => [l.pts[k], p]));
    const groupLabels = {};
    for (const g of graph.groups) {
      const gl = labels[`group.${g.id}`];
      if (!gl) continue;
      const b = shapes[g.id];
      const band = { x: b.x + sp.container_padding, right: b.x + b.w - sp.container_padding, y: b.y + sp.container_padding, h: labelH(gl) };
      groupLabels[g.id] = { x: placeGroupLabel(band, gl, segments, gap), y: band.y + gl.ascent, band };
    }
    return { canvas, height, shapes, lines, segments, groupLabels };
  }

  let geo = await place({});
  const blocked = Object.entries(geo.groupLabels).filter(([, v]) => v.x === null).map(([id]) => id);
  if (blocked.length) {
    // Members stay left-aligned in a wider group, so the lane right of the last crossing edge grows.
    const minWidth = {};
    for (const id of blocked) {
      const { band } = geo.groupLabels[id];
      const b = geo.shapes[id];
      const crossX = geo.segments.filter(([p, q]) => Math.max(p.y, q.y) > band.y - gap && Math.min(p.y, q.y) < band.y + band.h + gap
        && Math.max(p.x, q.x) > b.x && Math.min(p.x, q.x) < b.x + b.w).map(([p, q]) => Math.max(p.x, q.x));
      minWidth[id] = Math.max(...crossX) - b.x + gap + labels[`group.${id}`].width + sp.container_padding;
    }
    geo = await place(minWidth);
  }
  const { canvas, height, shapes, lines, groupLabels } = geo;
  const warnings = [];
  if (canvas > tokens.units.canvas_width_u) warnings.push(`using the ${canvas}u full-width canvas; render with --width ${canvas}`);

  // Member order: in any row (members whose extents overlap along the flow), input order must hold.
  for (const g of graph.groups) {
    const ms = g.members.map((id) => ({ id, b: shapes[id], i: memberIndex[id] }));
    const flowSpan = (b) => (vertical ? [b.y, b.y + b.h] : [b.x, b.x + b.w]);
    const cross = (b) => (vertical ? b.x : b.y);
    const swapped = [];
    for (const a of ms) for (const b of ms) {
      const [a0, a1] = flowSpan(a.b), [b0, b1] = flowSpan(b.b);
      if (a.i < b.i && a0 < b1 && b0 < a1 && cross(a.b) > cross(b.b)) swapped.push(`${a.id} after ${b.id}`);
    }
    if (swapped.length) warnings.push(`group "${g.id}": ELK changed member order (${swapped.join(', ')}); reorder nodes or edges in the input`);
  }

  // Edge labels for UP and DOWN flows, placed now that the routes are fixed.
  const arrow = arrowParams(tokens);
  const clearEnd = arrow.base + arrow.perStroke * tokens.stroke.emphasis_u + sp.edge_label_gap_from_arrowhead;
  const arrowOf = (e) => e.arrow ?? ((e.classes || []).includes('leader') ? 'none' : 'end');
  let labelBoxes = [];
  if (vertical) {
    const obstacles = [
      ...graph.nodes.map((n) => shapes[n.id]),
      ...Object.entries(groupLabels).map(([id, g]) => ({ x: g.x ?? g.band.x, y: g.band.y, w: labels[`group.${id}`].width, h: g.band.h })),
    ];
    labelBoxes = placeEdgeLabels(lines.map((l, i) => {
      const lab = labels[`edge${i}`];
      const a = arrowOf(l.src);
      return { pts: l.pts, half: lineHalfWidth(l.src.classes || [], tokens.stroke), label: lab ? { width: lab.width, height: labelH(lab) } : null, arrowEnd: a === 'end' || a === 'both', arrowStart: a === 'start' || a === 'both' };
    }), {
      obstacles,
      containers: graph.groups.map((g) => shapes[g.id]),
      canvas: { x: sp.canvas_margin, y: sp.canvas_margin, w: canvas - 2 * sp.canvas_margin, h: height - 2 * sp.canvas_margin },
      gap,
      clearEnd,
    });
    lines.forEach((l, i) => { if (labels[`edge${i}`] && !labelBoxes[i]) warnings.push(`no free spot beside edge ${l.src.from} -> ${l.src.to} for its label; shorten it or add spacing.layer`); });
  }

  const out = [];
  out.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${canvas} ${height}" data-figure="technical-figure">`);
  out.push(`  <!-- Laid out by scripts/layout.mjs (elkjs, direction ${graph.direction}). Change classes here; change structure in the graph and re-run. -->`);

  for (const g of graph.groups) {
    const b = shapes[g.id];
    const given = g.classes || [];
    const rectCls = (given.includes('zoom') ? given : ['container', ...given.filter((c) => c !== 'container')]).join(' ');
    out.push(`  <g data-id="${esc(g.id)}">`);
    out.push(`    <rect class="${rectCls}" x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}"/>`);
    const gl = labels[`group.${g.id}`];
    if (gl) {
      const pos = groupLabels[g.id];
      if (pos.x === null) warnings.push(`every position for the label of group "${g.id}" is crossed by an edge; change the edge sides`);
      out.push(`    <text class="${gl.cls}" x="${r2(pos.x ?? pos.band.x)}" y="${r2(pos.y)}">${esc(gl.text)}</text>`);
    }
    out.push('  </g>');
  }

  for (const n of graph.nodes) {
    const b = shapes[n.id];
    const extra = (n.classes || []).filter((c) => !['box', 'chip', 'op'].includes(c));
    const cx = r2(b.x + b.w / 2), cy = r2(b.y + b.h / 2);
    out.push(`  <g data-id="${esc(n.id)}">`);
    if (kindOf(n) === 'op') {
      const opCls = ['op', ...extra.filter((c) => c === 'runtime' || hueNames(tokens).includes(c))].join(' ');
      out.push(`    <circle class="${opCls}" data-op="${OPS[n.title || '+']}" cx="${cx}" cy="${cy}" r="${tokens.operator_radius_u}"/>`);
    } else {
      out.push(`    <rect class="${[n.kind || 'box', ...extra].join(' ')}" x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}"/>`);
      const title = labels[`${n.id}.title`], sub = labels[`${n.id}.sub`];
      const half = sub ? tokens.type.two_line_baseline_gap_u / 2 : 0;
      const mod = extra.includes('ghost') ? ' ghost' : '';
      const line = (l, y) => `    <text class="${l.cls}${mod}" x="${cx}" y="${r2(y)}" text-anchor="middle" dominant-baseline="central"${l.tex ? ` data-tex="${esc(l.tex)}"` : ''}>${esc(l.text)}</text>`;
      out.push(line(title, cy - half));
      if (sub) out.push(line(sub, cy + half));
    }
    out.push('  </g>');
  }

  const hues = hueNames(tokens);
  const dots = new Map();
  lines.forEach((l, i) => {
    const e = l.src;
    const cls = e.classes || [];
    const base = cls.includes('spine') ? 'spine' : cls.includes('leader') ? 'leader' : 'edge';
    const pathCls = [base, ...cls.filter((c) => c !== base)].join(' ');
    const arrow = arrowOf(e);
    const id = e.id || `${e.from}-${e.to}`;
    const pathEl = `<path class="${pathCls}" data-id="${esc(id)}" d="${roundedPath(l.pts, tokens.radius_u.node)}"${arrow !== 'none' ? ` data-arrow="${arrow}"` : ''}/>`;
    const lab = labels[`edge${i}`];
    const box = vertical ? labelBoxes[i] : l.labels[0];
    if (lab && box) {
      out.push('  <g>');
      out.push(`    ${pathEl}`);
      out.push(`    <text class="${lab.cls}" x="${r2(box.x + (box.w ?? box.width) / 2)}" y="${r2(box.y + lab.ascent)}" text-anchor="middle"${lab.tex ? ` data-tex="${esc(lab.tex)}"` : ''}>${esc(lab.text)}</text>`);
      out.push('  </g>');
    } else out.push(`  ${pathEl}`);
    const dotCls = ['dot', ...cls.filter((c) => ['spine', 'emph', 'ghost', ...hues].includes(c))].join(' ');
    for (const j of l.junctions) dots.set(`${j.x},${j.y}`, `  <circle class="${dotCls}" cx="${j.x}" cy="${j.y}" r="${Math.round(tokens.junction_dot_radius_per_stroke * tokens.stroke.edge_u * 100) / 100}"/>`);
  });
  out.push(...dots.values());
  out.push('</svg>');
  return { svg: out.join('\n') + '\n', width: canvas, height, warnings };
}
