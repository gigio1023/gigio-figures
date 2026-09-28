// Page-side runtime, injected into Chromium by lib/session.mjs. Everything that needs real
// fonts, computed styles, or path geometry runs here: mounting a figure, applying the
// renderer's appearance (radius, operators, dots, math, arrowheads, background), measuring
// labels for layout, and the geometric lint. Node passes all token-derived numbers in.
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const host = () => document.getElementById('host');
  const TF = {};
  window.TF = TF;

  // ---------- mounting ----------

  TF.parse = (src) => {
    const doc = new DOMParser().parseFromString(src, 'image/svg+xml');
    const err = doc.querySelector('parsererror');
    if (err) {
      const text = err.textContent.replace(/\s+/g, ' ');
      const m = /error on line (\d+) at column (\d+): (.*?)\s*(?:Below is a rendering.*)?$/.exec(text);
      throw new Error(`SVG parse error: ${m ? `line ${m[1]}, column ${m[2]}: ${m[3].trim()}` : text.slice(0, 200)}`);
    }
    if (doc.documentElement.localName !== 'svg') throw new Error('root element is not <svg>');
    return doc;
  };

  TF.mount = (src, css) => {
    const doc = TF.parse(src);
    const svg = document.importNode(doc.documentElement, true);
    host().replaceChildren(svg);
    const vb = svg.viewBox.baseVal;
    if (!vb || !vb.width || !vb.height) throw new Error('root <svg> needs a viewBox with width and height');
    svg.setAttribute('width', vb.width);
    svg.setAttribute('height', vb.height);
    const style = document.createElementNS(NS, 'style');
    style.id = 'tf-style';
    style.textContent = css;
    svg.insertBefore(style, svg.firstChild);
    TF.src = src;
    TF.svg = svg;
    return { x: vb.x, y: vb.y, width: vb.width, height: vb.height };
  };

  TF.setCss = (css) => { TF.svg.querySelector('#tf-style').textContent = css; };

  TF.setDisplayWidth = (w) => {
    const vb = TF.svg.viewBox.baseVal;
    TF.svg.setAttribute('width', w);
    TF.svg.setAttribute('height', (vb.height * w) / vb.width);
    return { width: w, height: (vb.height * w) / vb.width };
  };

  TF.texList = () => [...TF.svg.querySelectorAll('text[data-tex]')].map((t) => t.getAttribute('data-tex'));

  // ---------- geometry helpers ----------

  // Matrix from an element's user space to the root svg's user space.
  const toRoot = (el) => TF.svg.getScreenCTM().inverse().multiply(el.getScreenCTM());
  const mapPoint = (m, x, y) => ({ x: m.a * x + m.c * y + m.e, y: m.b * x + m.d * y + m.f });
  const mapBox = (m, b) => {
    const pts = [mapPoint(m, b.x, b.y), mapPoint(m, b.x + b.width, b.y), mapPoint(m, b.x, b.y + b.height), mapPoint(m, b.x + b.width, b.y + b.height)];
    const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y);
    const x = Math.min(...xs), y = Math.min(...ys);
    return { x, y, w: Math.max(...xs) - x, h: Math.max(...ys) - y };
  };
  const scaleOf = (m) => Math.sqrt(Math.abs(m.a * m.d - m.b * m.c));
  const area = (a, b) => Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)) * Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
  const inside = (p, b, shrink = 0) => p.x > b.x + shrink && p.x < b.x + b.w - shrink && p.y > b.y + shrink && p.y < b.y + b.h - shrink;
  const round = (v, d = 1) => Math.round(v * 10 ** d) / 10 ** d;
  const roundBox = (b) => ({ x: round(b.x), y: round(b.y), w: round(b.w), h: round(b.h) });
  const classes = (el) => [...el.classList];
  const collapse = (s) => (s || '').replace(/\s+/g, ' ').trim();

  let canvasCtx;
  const ctx2d = () => (canvasCtx ||= document.createElement('canvas').getContext('2d'));

  // Ink extents of a text element's string in its computed font, from canvas metrics.
  function inkMetrics(t, str) {
    const cs = getComputedStyle(t);
    const c = ctx2d();
    c.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    c.letterSpacing = cs.letterSpacing === 'normal' ? '0px' : cs.letterSpacing;
    const m = c.measureText(str);
    return { ascent: m.actualBoundingBoxAscent, descent: m.actualBoundingBoxDescent, fontAscent: m.fontBoundingBoxAscent };
  }

  // Tight box of a text element in root user units: advance box horizontally, glyph ink vertically.
  function textInkBox(t) {
    const str = collapse(t.textContent);
    const bb = t.getBBox();
    const ink = inkMetrics(t, str);
    const baseline = bb.y + ink.fontAscent;
    return mapBox(toRoot(t), { x: bb.x, y: baseline - ink.ascent, width: bb.width, height: ink.ascent + ink.descent });
  }

  // Shift from the alphabetic baseline to the element's dominant baseline, in its user units.
  function baselineShift(t) {
    const db = getComputedStyle(t).dominantBaseline;
    if (!db || db === 'auto' || db === 'alphabetic') return 0;
    const probe = (value) => {
      const p = t.cloneNode(false);
      p.removeAttribute('data-tex');
      p.textContent = 'x';
      p.setAttribute('y', 0);
      p.setAttribute('dominant-baseline', value);
      t.parentNode.appendChild(p);
      const y = p.getBBox().y;
      p.remove();
      return y;
    };
    return probe(db) - probe('alphabetic');
  }

  // ---------- path parsing (absolute segments) for stroke trimming ----------

  function parsePath(d) {
    let i = 0;
    const segs = [];
    const skip = () => { while (i < d.length && /[\s,]/.test(d[i])) i++; };
    const num = () => {
      skip();
      const m = /^[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?/.exec(d.slice(i));
      if (!m) throw new Error(`bad path data near "${d.slice(i, i + 12)}"`);
      i += m[0].length;
      return parseFloat(m[0]);
    };
    const flag = () => { skip(); const f = d[i++]; if (f !== '0' && f !== '1') throw new Error('bad arc flag'); return +f; };
    let cmd = null, cx = 0, cy = 0, sx = 0, sy = 0, last = null;
    while (true) {
      skip();
      if (i >= d.length) break;
      if (/[a-zA-Z]/.test(d[i])) cmd = d[i++];
      else if (!cmd) throw new Error('path data must start with a command');
      const rel = cmd !== cmd.toUpperCase();
      const C = cmd.toUpperCase();
      const ox = rel ? cx : 0, oy = rel ? cy : 0;
      let seg;
      if (C === 'M') { const x = num() + ox, y = num() + oy; seg = { c: 'M', p: [x, y] }; sx = x; sy = y; cmd = rel ? 'l' : 'L'; }
      else if (C === 'L') seg = { c: 'L', p: [num() + ox, num() + oy] };
      else if (C === 'H') seg = { c: 'L', p: [num() + ox, cy] };
      else if (C === 'V') seg = { c: 'L', p: [cx, num() + oy] };
      else if (C === 'C') seg = { c: 'C', p: [num() + ox, num() + oy, num() + ox, num() + oy, num() + ox, num() + oy] };
      else if (C === 'S') {
        const r = last && last.c === 'C' ? [2 * cx - last.p[2], 2 * cy - last.p[3]] : [cx, cy];
        seg = { c: 'C', p: [...r, num() + ox, num() + oy, num() + ox, num() + oy] };
      } else if (C === 'Q') seg = { c: 'Q', p: [num() + ox, num() + oy, num() + ox, num() + oy] };
      else if (C === 'T') {
        const r = last && last.c === 'Q' ? [2 * cx - last.p[0], 2 * cy - last.p[1]] : [cx, cy];
        seg = { c: 'Q', p: [...r, num() + ox, num() + oy] };
      } else if (C === 'A') seg = { c: 'A', p: [num(), num(), num(), flag(), flag(), num() + ox, num() + oy] };
      else if (C === 'Z') { seg = { c: 'Z', p: [] }; cmd = null; }
      else throw new Error(`unsupported path command ${cmd}`);
      if (seg.c === 'Z') { cx = sx; cy = sy; } else { cx = seg.p[seg.p.length - 2]; cy = seg.p[seg.p.length - 1]; }
      segs.push(seg);
      last = seg;
    }
    return segs;
  }
  const fmt = (v) => String(Math.round(v * 1000) / 1000);
  const pathString = (segs) => segs.map((s) => s.c + s.p.map(fmt).join(' ')).join('');

  // Move a path end (or start) to point q so the stroke stops short of the arrow tip.
  function trimPathEnd(el, which, q) {
    if (el.localName === 'line') {
      const k = which === 'end' ? '2' : '1';
      el.setAttribute('x' + k, fmt(q.x));
      el.setAttribute('y' + k, fmt(q.y));
      return;
    }
    const segs = parsePath(el.getAttribute('d'));
    if (which === 'end') {
      const s = segs[segs.length - 1];
      if (!s || s.c === 'Z' || s.c === 'M') return;
      const n = s.p.length;
      const dx = q.x - s.p[n - 2], dy = q.y - s.p[n - 1];
      if (s.c === 'C') { s.p[2] += dx; s.p[3] += dy; }
      s.p[n - 2] = q.x; s.p[n - 1] = q.y;
    } else {
      const m = segs[0], s = segs[1];
      if (!m || m.c !== 'M') return;
      const dx = q.x - m.p[0], dy = q.y - m.p[1];
      if (s && s.c === 'C') { s.p[0] += dx; s.p[1] += dy; }
      m.p = [q.x, q.y];
    }
    el.setAttribute('d', pathString(segs));
  }

  const pointAt = (el, s) => {
    if (el.localName === 'line') {
      const x1 = el.x1.baseVal.value, y1 = el.y1.baseVal.value, x2 = el.x2.baseVal.value, y2 = el.y2.baseVal.value;
      const L = Math.hypot(x2 - x1, y2 - y1) || 1;
      return { x: x1 + ((x2 - x1) * s) / L, y: y1 + ((y2 - y1) * s) / L };
    }
    const p = el.getPointAtLength(s);
    return { x: p.x, y: p.y };
  };
  const lengthOf = (el) => (el.localName === 'line'
    ? Math.hypot(el.x2.baseVal.value - el.x1.baseVal.value, el.y2.baseVal.value - el.y1.baseVal.value)
    : el.getTotalLength());

  // ---------- appearance ----------

  // Corner radius per class, capped by a share of the shorter side so a thin strip stays a strip.
  function applyRadius(o) {
    const R = o.radius;
    for (const rect of TF.svg.querySelectorAll('rect')) {
      const c = rect.classList;
      const side = Math.min(rect.width.baseVal.value, rect.height.baseVal.value);
      let base = null;
      if (c.contains('cell') || c.contains('band')) base = R.cell;
      else if (c.contains('tensor')) base = R.tensor;
      else if (c.contains('chip')) base = R.chip;
      else if (c.contains('container') || c.contains('zoom')) base = R.container;
      else if (c.contains('box')) base = side >= o.tallNodeHeight ? R.node_tall : R.node;
      if (base === null) continue;
      const r = Math.min(base, R.max_ratio_of_height * side);
      rect.setAttribute('rx', fmt(r));
      rect.setAttribute('ry', fmt(r));
    }
  }

  function applyOperators(o) {
    for (const c of TF.svg.querySelectorAll('circle.op')) {
      c.setAttribute('r', o.opRadius);
      const cx = c.cx.baseVal.value, cy = c.cy.baseVal.value;
      const a = o.opRadius * o.opGlyphArm;
      const kind = c.getAttribute('data-op') || 'plus';
      const q = a * Math.SQRT1_2;
      const d = {
        plus: `M${cx - a} ${cy}H${cx + a}M${cx} ${cy - a}V${cy + a}`,
        minus: `M${cx - a} ${cy}H${cx + a}`,
        times: `M${cx - q} ${cy - q}L${cx + q} ${cy + q}M${cx - q} ${cy + q}L${cx + q} ${cy - q}`,
      }[kind];
      if (!d) throw new Error(`data-op="${kind}" is not plus, times, or minus`);
      const g = document.createElementNS(NS, 'path');
      g.setAttribute('class', ['op-glyph', ...classes(c).filter((k) => o.hues.includes(k))].join(' '));
      g.setAttribute('d', d);
      c.after(g);
    }
  }

  function applyDots(o) {
    for (const c of TF.svg.querySelectorAll('circle.dot')) {
      const k = c.classList;
      const w = k.contains('spine') || k.contains('emph') ? o.stroke.emphasis_u : k.contains('ghost') ? o.stroke.guide_u : o.stroke.edge_u;
      c.setAttribute('r', fmt(o.dotPerStroke * w));
    }
  }

  function applyMath(o) {
    const texts = [...TF.svg.querySelectorAll('text[data-tex]')];
    texts.forEach((t, i) => {
      const m = o.math[i];
      const cs = getComputedStyle(t);
      const size = Math.max(parseFloat(cs.fontSize), o.mathMinSize || 0);
      const anchor = cs.textAnchor || 'start';
      const x = t.x.baseVal.length ? t.x.baseVal[0].value : 0;
      const y = t.y.baseVal.length ? t.y.baseVal[0].value : 0;
      const db = cs.dominantBaseline;
      const centered = db === 'central' || db === 'middle';
      let base = centered ? y : y + baselineShift(t);
      const s = (size * o.mathEmPerLabelSize) / 1000;
      const [vx, , vw] = m.vb;
      const w = vw * s;
      const x0 = anchor === 'middle' ? x - w / 2 : anchor === 'end' ? x - w : x;
      const g = document.createElementNS(NS, 'g');
      g.setAttribute('class', ['math', ...classes(t)].join(' '));
      for (const a of ['data-id', 'style', 'transform', 'opacity']) if (t.hasAttribute(a)) g.setAttribute(a, t.getAttribute(a));
      g.setAttribute('data-tex', t.getAttribute('data-tex'));
      g.setAttribute('data-size', size);
      g.setAttribute('role', 'img');
      g.setAttribute('aria-label', collapse(t.textContent) || t.getAttribute('data-tex'));
      const inner = TF.parse(`<svg xmlns="${NS}"><g transform="translate(${fmt(x0 - vx * s)} ${fmt(base)}) scale(${s.toFixed(6)})">${m.inner}</g></svg>`).documentElement.firstChild;
      const placed = document.importNode(inner, true);
      g.appendChild(placed);
      t.replaceWith(g);
      if (centered) {
        // Center the glyph ink on y; a font baseline shift leaves subscripts and primes low.
        const ink = placed.getBBox();
        base += y - (base + (ink.y * s) + (ink.height * s) / 2);
        placed.setAttribute('transform', `translate(${fmt(x0 - vx * s)} ${fmt(base)}) scale(${s.toFixed(6)})`);
      }
    });
  }

  function applyArrows(o) {
    for (const p of TF.svg.querySelectorAll('path[data-arrow], line[data-arrow]')) {
      const mode = p.getAttribute('data-arrow');
      const ends = mode === 'both' ? ['end', 'start'] : mode === 'start' ? ['start'] : mode === 'end' ? ['end'] : null;
      if (!ends) throw new Error(`data-arrow="${mode}" is not end, start, or both`);
      const w = parseFloat(getComputedStyle(p).strokeWidth);
      const len = o.arrow.base + o.arrow.perStroke * w;
      const half = o.arrow.halfRatio * len;
      const L = lengthOf(p);
      const heads = [];
      const trims = [];
      for (const which of ends) {
        const tip = pointAt(p, which === 'end' ? L : 0);
        const back = pointAt(p, which === 'end' ? Math.max(0, L - 1) : Math.min(L, 1));
        const n = Math.hypot(tip.x - back.x, tip.y - back.y) || 1;
        const dir = { x: (tip.x - back.x) / n, y: (tip.y - back.y) / n };
        const perp = { x: -dir.y, y: dir.x };
        // The round join reaches w/2 past the vertex, so the vertex sits w/2 inside the tip.
        const v = { x: tip.x - (dir.x * w) / 2, y: tip.y - (dir.y * w) / 2 };
        const a1 = { x: v.x - dir.x * len + perp.x * half, y: v.y - dir.y * len + perp.y * half };
        const a2 = { x: v.x - dir.x * len - perp.x * half, y: v.y - dir.y * len - perp.y * half };
        const head = document.createElementNS(NS, 'path');
        head.setAttribute('class', ['arrowhead', ...classes(p).filter((c) => c !== 'control')].join(' '));
        head.setAttribute('d', `M${fmt(a1.x)} ${fmt(a1.y)}L${fmt(v.x)} ${fmt(v.y)}L${fmt(a2.x)} ${fmt(a2.y)}`);
        head.setAttribute('data-tip', `${fmt(tip.x)},${fmt(tip.y)}`);
        if (p.hasAttribute('data-id')) head.setAttribute('data-for', p.getAttribute('data-id'));
        heads.push(head);
        // Stop the line at the vertex minus half a stroke: its butt end then sits inside the chevron's ink.
        const trim = Math.min(w, L / 3);
        trims.push({ which, q: pointAt(p, which === 'end' ? L - trim : trim) });
      }
      for (const t of trims) trimPathEnd(p, t.which, t.q);
      p.after(...heads);
      // Arrows are drawn now; a re-render of the output must not draw them twice.
      p.removeAttribute('data-arrow');
    }
  }

  function applyBackground() {
    const vb = TF.svg.viewBox.baseVal;
    const bg = document.createElementNS(NS, 'rect');
    bg.setAttribute('class', 'tf-bg');
    bg.setAttribute('x', vb.x);
    bg.setAttribute('y', vb.y);
    bg.setAttribute('width', vb.width);
    bg.setAttribute('height', vb.height);
    TF.svg.querySelector('#tf-style').after(bg);
  }

  TF.prepare = (o) => {
    applyRadius(o);
    applyOperators(o);
    applyDots(o);
    applyMath(o);
    applyArrows(o);
    applyBackground();
  };

  TF.serialize = (css) => {
    const svg = TF.svg.cloneNode(true);
    const vb = TF.svg.viewBox.baseVal;
    svg.setAttribute('width', vb.width);
    svg.setAttribute('height', vb.height);
    svg.querySelector('#tf-style').textContent = css;
    svg.querySelector('#tf-style').removeAttribute('id');
    return new XMLSerializer().serializeToString(svg);
  };

  // Characters per font face, for subsetting the portable SVG's embedded fonts.
  TF.fontUsage = () => {
    const use = {};
    for (const t of TF.svg.querySelectorAll('text')) {
      const cs = getComputedStyle(t);
      const role = /JetBrains Mono/.test(cs.fontFamily.split(',')[0]) ? 'mono' : 'sans';
      const key = `${role}-${parseInt(cs.fontWeight, 10)}`;
      use[key] = (use[key] || '') + t.textContent;
    }
    for (const k of Object.keys(use)) use[k] = [...new Set(use[k].replace(/\s/g, ''))].join('') + ' ';
    return use;
  };

  // ---------- measurement for layout ----------

  TF.measureTexts = (items) => {
    const out = [];
    for (const it of items) {
      const t = document.createElementNS(NS, 'text');
      t.setAttribute('class', it.cls);
      t.textContent = it.text;
      TF.svg.appendChild(t);
      const ink = inkMetrics(t, it.text);
      out.push({ width: t.getComputedTextLength(), ascent: ink.ascent, descent: ink.descent, size: parseFloat(getComputedStyle(t).fontSize) });
      t.remove();
    }
    return out;
  };

  // ---------- lint ----------

  const HANGUL = /[ᄀ-ᇿ㄰-㆏가-힯]/;
  // Combining marks, spacing and phonetic modifier letters, super- and subscripts.
  const UNICODE_MATH = /[̀-ͯ᪰-᫿᷀-᷿⃐-⃿ʰ-˿ᴬ-ᵪᵸᶛ-ᶿ⁰-₟²³¹]/g;
  const APPEARANCE_ATTRS = ['fill', 'stroke', 'stroke-width', 'stroke-dasharray', 'stroke-linecap', 'stroke-linejoin', 'stroke-opacity', 'fill-opacity',
    'font-family', 'font-size', 'font-weight', 'font-style', 'letter-spacing', 'color', 'marker-start', 'marker-mid', 'marker-end'];
  const APPEARANCE_ELEMENTS = ['style', 'marker', 'linearGradient', 'radialGradient', 'pattern', 'filter'];
  const EDGE_SEL = 'path.edge, line.edge, path.spine, line.spine, path.leader, line.leader';

  function describe(el) {
    if (el.getAttribute('data-id')) return el.getAttribute('data-id');
    const owner = el.parentElement && el.parentElement.closest('[data-id]');
    const own = owner ? ` in ${owner.getAttribute('data-id')}` : '';
    if (el.localName === 'text' || el.classList.contains('math')) {
      const label = el.classList.contains('math') ? el.getAttribute('data-tex') : collapse(el.textContent);
      return `text "${label.slice(0, 32)}"${own}`;
    }
    const cls = el.getAttribute('class');
    const same = [...TF.svg.querySelectorAll(el.localName)].filter((e) => e.getAttribute('class') === cls);
    return `${el.localName}.${(cls || '').split(/\s+/).join('.')}[${same.indexOf(el)}]${own}`;
  }

  function staticChecks(o, add) {
    const doc = TF.parse(TF.src);
    const root = doc.documentElement;
    const vb = (root.getAttribute('viewBox') || '').trim().split(/[\s,]+/).map(Number);
    const all = [root, ...root.querySelectorAll('*')];
    const srcDescribe = (el) => {
      if (el.getAttribute('data-id')) return el.getAttribute('data-id');
      const owner = el.parentElement && el.parentElement.closest('[data-id]');
      const base = el.localName === 'text' ? `text "${collapse(el.textContent).slice(0, 32)}"` : `<${el.localName}>`;
      return owner ? `${base} in ${owner.getAttribute('data-id')}` : base;
    };
    for (const el of all) {
      if (APPEARANCE_ELEMENTS.includes(el.localName)) add('source-appearance', [srcDescribe(el)], { element: el.localName }, `<${el.localName}> in the source; the renderer owns appearance`);
      for (const a of APPEARANCE_ATTRS) if (el.hasAttribute(a)) add('source-appearance', [srcDescribe(el)], { attribute: a, value: el.getAttribute(a) }, `${a}= in the source; use classes`);
      const st = el.getAttribute('style');
      if (st) {
        const props = st.split(';').map((d) => d.split(':')[0].trim().toLowerCase()).filter(Boolean);
        const bad = props.filter((p) => p !== 'opacity');
        if (bad.length) add('source-appearance', [srcDescribe(el)], { style: st }, `style= may only set opacity, found ${bad.join(', ')}`);
      }
      if (el.localName === 'rect' && vb.length === 4) {
        const n = (a) => el.getAttribute(a);
        const full = (a, v) => n(a) === '100%' || parseFloat(n(a)) >= v - 1;
        const x = parseFloat(n('x') || 0), y = parseFloat(n('y') || 0);
        if (x <= vb[0] + 1 && y <= vb[1] + 1 && full('width', vb[2]) && full('height', vb[3])) {
          add('source-appearance', [srcDescribe(el)], { rect: [x, y, n('width'), n('height')] }, 'background rect in the source; the renderer bakes the background');
        }
      }
      if (el.localName === 'foreignObject' || el.localName === 'script') add('external-reference', [srcDescribe(el)], { element: el.localName }, `<${el.localName}> is not portable`);
      for (const a of ['href', 'xlink:href']) {
        const v = el.getAttribute(a);
        if (v && !v.startsWith('#') && !v.startsWith('data:')) add('external-reference', [srcDescribe(el)], { [a]: v }, 'reference to an external resource');
      }
    }
    for (const t of root.querySelectorAll('text')) {
      const s = t.textContent;
      const marks = s.match(UNICODE_MATH);
      if (marks) add('unicode-math', [srcDescribe(t)], { characters: [...new Set(marks)].map((c) => 'U+' + c.codePointAt(0).toString(16).toUpperCase().padStart(4, '0')) }, 'Unicode imitation of math; write TeX in data-tex');
      if (t.classList.contains('mono')) {
        const c = collapse(s);
        if (HANGUL.test(c) || /\s/.test(c)) add('mono-mixed', [srcDescribe(t)], { text: c }, 'mono text must be one identifier without Hangul or spaces');
      }
    }
    const ids = {};
    for (const el of root.querySelectorAll('[data-id]')) (ids[el.getAttribute('data-id')] ||= []).push(el.localName);
    for (const [id, els] of Object.entries(ids)) if (els.length > 1) add('duplicate-id', [id], { count: els.length }, 'data-id used more than once');
    return Object.keys(ids);
  }

  function textItems() {
    const items = [];
    for (const t of TF.svg.querySelectorAll('text')) {
      if (!collapse(t.textContent)) continue;
      const m = toRoot(t);
      items.push({ el: t, box: textInkBox(t), font: parseFloat(getComputedStyle(t).fontSize), scale: scaleOf(m) });
    }
    for (const g of TF.svg.querySelectorAll('g.math')) {
      const m = toRoot(g);
      items.push({ el: g, box: mapBox(m, g.getBBox()), font: parseFloat(g.getAttribute('data-size')), scale: scaleOf(m) });
    }
    return items;
  }

  function sampled(el, step) {
    const m = toRoot(el);
    const L = lengthOf(el);
    const pts = [];
    const n = Math.max(1, Math.ceil(L / step));
    for (let k = 0; k <= n; k++) { const p = pointAt(el, (L * k) / n); pts.push(mapPoint(m, p.x, p.y)); }
    return pts;
  }

  // Ramer-Douglas-Peucker: dense samples back to long straight segments, so the crossing
  // test below does not see every 1u step as "touching" the other line.
  function simplify(pts, eps) {
    if (pts.length < 3) return pts;
    const a = pts[0], b = pts[pts.length - 1];
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    let far = 0, idx = 0;
    for (let i = 1; i < pts.length - 1; i++) {
      const p = pts[i];
      const d = len ? Math.abs((b.x - a.x) * (a.y - p.y) - (a.x - p.x) * (b.y - a.y)) / len : Math.hypot(p.x - a.x, p.y - a.y);
      if (d > far) { far = d; idx = i; }
    }
    if (far <= eps) return [a, b];
    return [...simplify(pts.slice(0, idx + 1), eps).slice(0, -1), ...simplify(pts.slice(idx), eps)];
  }

  // Proper crossing of two polylines, ignoring touching and collinear overlap within tol.
  function crosses(A, B, tol) {
    const side = (p, q, r) => {
      const len = Math.hypot(q.x - p.x, q.y - p.y) || 1;
      const d = ((q.x - p.x) * (r.y - p.y) - (q.y - p.y) * (r.x - p.x)) / len;
      return Math.abs(d) < tol ? 0 : Math.sign(d);
    };
    for (let i = 1; i < A.length; i++) {
      const a = A[i - 1], b = A[i];
      for (let j = 1; j < B.length; j++) {
        const c = B[j - 1], d = B[j];
        if (Math.max(a.x, b.x) < Math.min(c.x, d.x) || Math.max(c.x, d.x) < Math.min(a.x, b.x)) continue;
        if (Math.max(a.y, b.y) < Math.min(c.y, d.y) || Math.max(c.y, d.y) < Math.min(a.y, b.y)) continue;
        if (side(a, b, c) * side(a, b, d) < 0 && side(c, d, a) * side(c, d, b) < 0) return { x: round((a.x + b.x) / 2), y: round((a.y + b.y) / 2) };
      }
    }
    return null;
  }

  // Bends: turns between consecutive straight runs; rounded corners fall between runs.
  function countBends(pts, o) {
    const runs = [];
    for (let i = 1; i < pts.length; i++) {
      const h = Math.atan2(pts[i].y - pts[i - 1].y, pts[i].x - pts[i - 1].x);
      const cur = runs[runs.length - 1];
      const diff = cur ? Math.abs(Math.atan2(Math.sin(h - cur.h), Math.cos(h - cur.h))) : Infinity;
      if (cur && diff < o.bendRunTolerance) cur.n++;
      else runs.push({ h, n: 1 });
    }
    const straight = runs.filter((r) => r.n >= o.bendMinRun);
    let bends = 0;
    for (let i = 1; i < straight.length; i++) {
      const d = Math.abs(Math.atan2(Math.sin(straight[i].h - straight[i - 1].h), Math.cos(straight[i].h - straight[i - 1].h)));
      if (d > o.bendMinTurn) bends++;
    }
    return bends;
  }

  const minDistance = (box, pts) => {
    let best = Infinity;
    for (const p of pts) {
      const dx = Math.max(box.x - p.x, 0, p.x - (box.x + box.w));
      const dy = Math.max(box.y - p.y, 0, p.y - (box.y + box.h));
      best = Math.min(best, Math.hypot(dx, dy));
    }
    return best;
  };

  TF.lint = (o) => {
    const findings = [];
    const add = (id, elements, measured, message) => findings.push({ id, severity: o.severity[id], elements, message, measured });
    const ids = staticChecks(o, add);
    const vb = TF.svg.viewBox.baseVal;
    const k = o.delivery / vb.width;

    // Height
    const hDisp = vb.height * k;
    if (hDisp > o.heightLimit) add('height-limit', ['svg'], { height_css_px: round(hDisp), limit: o.heightLimit, delivery: o.delivery }, 'too tall at the delivery width; rearrange or split');
    else if (hDisp > o.heightBudget) add('height-budget', ['svg'], { height_css_px: round(hDisp), budget: o.heightBudget, delivery: o.delivery }, 'taller than one screen with its caption');

    const items = textItems();
    // Token sizes are set for a 720u canvas in the ~704 px column, where 1u counts as 1 px.
    // Compare against that nominal mapping so a 12u label passes at 704 px but fails when a
    // 1080u figure or a scaled group shrinks it further.
    const kSize = Math.min(1, k / o.nominalScale);
    for (const it of items) {
      const min = it.el.classList.contains('micro') ? o.minMicro : o.minSize;
      const nominal = it.font * it.scale * kSize;
      if (nominal < min - 1e-6) add('text-too-small', [describe(it.el)], { displayed_px: round(it.font * it.scale * k, 2), font_u: it.font, transform_scale: round(it.scale, 3), delivery: o.delivery, min_u: min }, 'text below the minimum size at the delivery width');
    }
    // Canvas bounds
    const canvas = { x: vb.x, y: vb.y, w: vb.width, h: vb.height };
    const past = (b) => {
      const o = { left: canvas.x - b.x, top: canvas.y - b.y, right: b.x + b.w - canvas.x - canvas.w, bottom: b.y + b.h - canvas.y - canvas.h };
      return Object.fromEntries(Object.entries(o).filter(([, v]) => v > 0.5).map(([key, v]) => [key, round(v)]));
    };
    for (const it of items) {
      const over = past(it.box);
      if (Object.keys(over).length) add('outside-canvas', [describe(it.el)], { clipped_u: over }, 'text extends past the canvas and is clipped');
    }
    for (const s of TF.svg.querySelectorAll('rect.box, rect.chip, rect.container, rect.zoom, circle.op')) {
      const over = past(mapBox(toRoot(s), s.getBBox()));
      if (Object.keys(over).length) add('outside-canvas', [describe(s)], { clipped_u: over }, 'shape extends past the canvas and is clipped');
    }
    // Margin: text ink and shape geometry inside the canvas margin, one finding per side.
    // A stroke's half width past a shape placed on the margin is not counted.
    const near = { left: [], top: [], right: [], bottom: [] };
    const inkBoxes = [...items.map((it) => ({ el: it.el, b: it.box })),
      ...[...TF.svg.querySelectorAll('rect, circle, ellipse, path, line, polyline, polygon')]
        .filter((el) => !el.classList.contains('tf-bg') && !el.closest('g.math'))
        .map((el) => ({ el, b: mapBox(toRoot(el), el.getBBox()) }))];
    for (const { el, b } of inkBoxes) {
      const gap = { left: b.x - canvas.x, top: b.y - canvas.y, right: canvas.x + canvas.w - b.x - b.w, bottom: canvas.y + canvas.h - b.y - b.h };
      for (const [side, d] of Object.entries(gap)) if (d > -0.5 && d < o.margin - 0.5) near[side].push({ el, d });
    }
    for (const [side, list] of Object.entries(near)) {
      if (!list.length) continue;
      list.sort((a, b) => a.d - b.d);
      const names = [...new Set(list.map((x) => describe(x.el.classList.contains('arrowhead') && x.el.previousElementSibling ? x.el.previousElementSibling : x.el)))];
      add('margin', names.slice(0, 6), { side, closest_u: round(list[0].d), margin_u: o.margin }, `ink inside the ${side} canvas margin`);
    }
    // Text against text
    for (let i = 0; i < items.length; i++) for (let j = i + 1; j < items.length; j++) {
      const a = area(items[i].box, items[j].box);
      if (a > o.overlapArea) add('text-overlap', [describe(items[i].el), describe(items[j].el)], { area_u2: round(a), a: roundBox(items[i].box), b: roundBox(items[j].box) }, 'labels overlap');
    }
    // Text against lines
    const lines = [...TF.svg.querySelectorAll(EDGE_SEL)];
    const sampledLines = lines.map((el) => ({ el, pts: sampled(el, 1), arrowhead: el.classList.contains('arrowhead') }));
    const own = (a, b) => a.parentElement === b.parentElement && a.parentElement !== TF.svg;
    for (const it of items) for (const ln of sampledLines) {
      if (own(it.el, ln.el)) continue;
      const hits = ln.pts.filter((p) => inside(p, it.box, 0.5)).length;
      if (hits >= 2) add('text-crossed', [describe(it.el), ln.arrowhead ? `arrowhead of ${ln.el.getAttribute('data-for') || describe(ln.el)}` : describe(ln.el)], { samples_inside: hits, text_box: roundBox(it.box) }, 'a line crosses a label that is not its own');
    }
    // Text inside its owning box, tensor, or chip: a sibling shape whose rect holds the text's center.
    for (const it of items) {
      const parent = it.el.parentElement;
      if (!parent || parent === TF.svg) continue;
      const center = { x: it.box.x + it.box.w / 2, y: it.box.y + it.box.h / 2 };
      const owners = [...parent.children]
        .filter((c) => c instanceof SVGGeometryElement && ['box', 'tensor', 'chip'].some((k) => c.classList.contains(k)))
        .map((r) => ({ r, b: mapBox(toRoot(r), r.getBBox()) }))
        .filter(({ b }) => inside(center, b));
      if (!owners.length) continue;
      owners.sort((p, q) => p.b.w * p.b.h - q.b.w * q.b.h);
      const { r, b } = owners[0];
      const inner = { x: b.x + o.inset, y: b.y + o.inset, w: b.w - 2 * o.inset, h: b.h - 2 * o.inset };
      const over = {
        left: round(inner.x - it.box.x), right: round(it.box.x + it.box.w - (inner.x + inner.w)),
        top: round(inner.y - it.box.y), bottom: round(it.box.y + it.box.h - (inner.y + inner.h)),
      };
      if (Object.values(over).some((v) => v > 0.25)) {
        add('text-overflow', [describe(it.el), describe(r)], { overflow_u: over, text_width_u: round(it.box.w), inner_width_u: round(inner.w), inset_u: o.inset }, 'label runs past its box inset');
      }
    }
    // Arrow tips
    const tips = [...TF.svg.querySelectorAll('.arrowhead')].map((h) => { const [x, y] = h.getAttribute('data-tip').split(',').map(Number); return { h, ...mapPoint(toRoot(h), x, y) }; });
    for (let i = 0; i < tips.length; i++) for (let j = i + 1; j < tips.length; j++) {
      if (tips[i].h.previousElementSibling === tips[j].h || tips[j].h.previousElementSibling === tips[i].h) continue;
      const d = Math.hypot(tips[i].x - tips[j].x, tips[i].y - tips[j].y);
      if (d < o.tipGap) add('arrow-tips', [tips[i].h.getAttribute('data-for') || describe(tips[i].h), tips[j].h.getAttribute('data-for') || describe(tips[j].h)], { distance_u: round(d), min_u: o.tipGap }, 'arrow tips too close to tell apart');
    }
    // Edge crossings and bends
    const drawn = sampledLines.filter((l) => !l.arrowhead && !l.el.classList.contains('leader'));
    for (const l of drawn) l.poly = simplify(l.pts, o.crossTolerance / 2);
    for (let i = 0; i < drawn.length; i++) for (let j = i + 1; j < drawn.length; j++) {
      const at = crosses(drawn[i].poly, drawn[j].poly, o.crossTolerance);
      if (at) add('edge-crossing', [describe(drawn[i].el), describe(drawn[j].el)], { at }, 'edges cross');
    }
    for (const l of drawn) {
      const b = countBends(l.pts, o);
      if (b > o.maxBends) add('edge-bends', [describe(l.el)], { bends: b, max: o.maxBends }, 'edge bends too often');
    }
    // Relation styles: emph and ghost restyle a relation; they are not relations of their own.
    const kinds = new Set();
    for (const l of sampledLines) {
      if (l.arrowhead) continue;
      const c = l.el.classList;
      if (c.contains('leader')) kinds.add('leader');
      else if (c.contains('spine')) kinds.add('spine');
      else if (c.contains('edge')) kinds.add(c.contains('control') ? 'control' : 'edge');
    }
    if (kinds.size > o.maxRelations) add('relation-styles', ['svg'], { styles: [...kinds], max: o.maxRelations }, 'more line styles than relations a reader can hold');
    // Focus hues
    const focusHues = new Set();
    for (const el of TF.svg.querySelectorAll('.focus, .emph')) for (const h of o.hues) if (el.classList.contains(h)) focusHues.add(h);
    if (focusHues.size > 1) add('focus-hues', ['svg'], { hues: [...focusHues] }, 'more than one hue among focus and emph elements');
    // Edge label distance
    for (const it of items) {
      if (!it.el.classList.contains('tl')) continue;
      const mine = sampledLines.filter((l) => !l.arrowhead && own(it.el, l.el));
      const pool = mine.length ? mine : sampledLines.filter((l) => !l.arrowhead);
      if (!pool.length) continue;
      const d = Math.min(...pool.map((l) => minDistance(it.box, l.pts)));
      if (d > o.labelFar) add('label-far', [describe(it.el)], { distance_u: round(d), max_u: o.labelFar, owner: mine.length ? describe(mine[0].el) : 'nearest line' }, 'edge label far from its line');
    }
    return { findings, ids, metrics: { width_u: vb.width, height_u: vb.height, delivery_css_px: o.delivery, height_css_px: round(hDisp), texts: items.length, lines: drawn.length } };
  };

  // ---------- contrast (per theme) ----------

  const parseColor = (s) => {
    const m = /rgba?\(([^)]+)\)/.exec(s || '');
    if (!m) return null;
    const v = m[1].split(/[\s,/]+/).filter(Boolean).map(Number);
    return { r: v[0], g: v[1], b: v[2], a: v.length > 3 ? v[3] : 1 };
  };
  const lum = (c) => {
    const f = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  };
  const wcag = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const blend = (fg, alpha, bg) => ({ r: fg.r * alpha + bg.r * (1 - alpha), g: fg.g * alpha + bg.g * (1 - alpha), b: fg.b * alpha + bg.b * (1 - alpha) });
  const hex = (c) => '#' + [c.r, c.g, c.b].map((v) => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase();
  const opacityChain = (el) => {
    let a = 1;
    for (let e = el; e && e !== TF.svg; e = e.parentElement) a *= parseFloat(getComputedStyle(e).opacity);
    return a;
  };

  // Composite of the filled shapes painted before `el` under a root-space point.
  function colorUnder(el, p) {
    const sr = TF.svg.getBoundingClientRect();
    const vb = TF.svg.viewBox.baseVal;
    const cx = sr.left + ((p.x - vb.x) * sr.width) / vb.width, cy = sr.top + ((p.y - vb.y) * sr.height) / vb.height;
    const stack = document.elementsFromPoint(cx, cy).filter((s) => {
      if (!(s instanceof SVGGeometryElement) || !TF.svg.contains(s) || s.closest('text, g.math')) return false;
      if (!(el.compareDocumentPosition(s) & Node.DOCUMENT_POSITION_PRECEDING)) return false;
      const fill = getComputedStyle(s).fill;
      if (!fill || fill === 'none') return false;
      const inv = s.getScreenCTM().inverse();
      const lp = new DOMPoint(cx, cy).matrixTransform(inv);
      return s.isPointInFill(lp);
    });
    let color = parseColor(getComputedStyle(TF.svg.querySelector('.tf-bg')).fill);
    for (const s of stack.reverse()) {
      const cs = getComputedStyle(s);
      const c = parseColor(cs.fill);
      if (!c) continue;
      color = blend(c, c.a * parseFloat(cs.fillOpacity) * opacityChain(s), color);
    }
    return color;
  }

  TF.contrast = (o) => {
    const findings = [];
    for (const it of textItems()) {
      const cs = getComputedStyle(it.el);
      const fg = parseColor(it.el.localName === 'text' ? cs.fill : cs.color);
      if (!fg) continue;
      const alpha = fg.a * opacityChain(it.el) * (it.el.localName === 'text' ? parseFloat(cs.fillOpacity) : 1);
      const b = it.box;
      let worst = null;
      for (const fx of [0.15, 0.5, 0.85]) for (const fy of [0.3, 0.7]) {
        const under = colorUnder(it.el, { x: b.x + b.w * fx, y: b.y + b.h * fy });
        const shown = blend(fg, alpha, under);
        const ratio = wcag(shown, under);
        if (!worst || ratio < worst.ratio) worst = { ratio, text: hex(shown), under: hex(under) };
      }
      if (worst && worst.ratio < o.minContrast) {
        findings.push({ id: 'contrast', severity: o.severity.contrast, elements: [describe(it.el)], message: `text contrast below ${o.minContrast}:1`, measured: { theme: o.theme, ratio: round(worst.ratio, 2), text: worst.text, under: worst.under, min: o.minContrast } });
      }
    }
    return findings;
  };

  // Share of pixels whose channel spread marks them as colored, from a PNG data URL.
  TF.colorArea = async (dataUrl, spread) => {
    const img = new Image();
    img.src = dataUrl;
    await img.decode();
    const c = document.createElement('canvas');
    c.width = img.naturalWidth;
    c.height = img.naturalHeight;
    const g = c.getContext('2d');
    g.drawImage(img, 0, 0);
    const d = g.getImageData(0, 0, c.width, c.height).data;
    let n = 0;
    for (let i = 0; i < d.length; i += 4) if (Math.max(d[i], d[i + 1], d[i + 2]) - Math.min(d[i], d[i + 1], d[i + 2]) > spread) n++;
    return n / (c.width * c.height);
  };
})();
