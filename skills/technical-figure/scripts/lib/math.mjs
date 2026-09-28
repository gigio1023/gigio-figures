// TeX -> glyph paths with mathjax-full's SVG output (fontCache none: every glyph is an inline path).
import { cacheRequire } from './env.mjs';

let state;

function init() {
  if (state) return state;
  const { mathjax } = cacheRequire('mathjax-full/js/mathjax.js');
  const { TeX } = cacheRequire('mathjax-full/js/input/tex.js');
  cacheRequire('mathjax-full/js/input/tex/AllPackages.js');
  const { SVG } = cacheRequire('mathjax-full/js/output/svg.js');
  const { liteAdaptor } = cacheRequire('mathjax-full/js/adaptors/liteAdaptor.js');
  const { RegisterHTMLHandler } = cacheRequire('mathjax-full/js/handlers/html.js');
  const adaptor = liteAdaptor();
  RegisterHTMLHandler(adaptor);
  const output = new SVG({ fontCache: 'none' });
  const doc = mathjax.document('', {
    InputJax: new TeX({ packages: ['base', 'ams', 'boldsymbol', 'newcommand'] }),
    OutputJax: output,
  });
  state = { adaptor, doc, xHeight: output.font.params.x_height, cache: new Map() };
  return state;
}

// Returns the viewBox (1000 units per em, baseline at y = 0) and the inner SVG markup.
export function typeset(tex) {
  const s = init();
  if (s.cache.has(tex)) return s.cache.get(tex);
  const node = s.doc.convert(tex, { display: false, em: 16, ex: 8, containerWidth: 1280 });
  const svg = s.adaptor.firstChild(node);
  const inner = s.adaptor.innerHTML(svg);
  if (inner.includes('data-mml-node="merror"')) {
    const msg = /title="([^"]*)"/.exec(inner)?.[1] || s.adaptor.textContent(svg);
    throw new Error(`TeX error in data-tex="${tex}": ${msg}`);
  }
  const vb = s.adaptor.getAttribute(svg, 'viewBox').split(/\s+/).map(Number);
  const out = { vb, inner };
  s.cache.set(tex, out);
  return out;
}

// Math em size per unit of label font size: math ex matched to the label, then scaled.
export function mathEmPerLabelSize(tokens) {
  const m = tokens.fonts.math;
  return (m.ex_per_label_size / init().xHeight) * m.scale_after_ex_match;
}

// Math glyphs are thinner than the sans labels, so math never sets below its own minimum size.
export function mathSize(labelSize, tokens) {
  return Math.max(labelSize, tokens.fonts.math.min_size_u || 0);
}

// Width and vertical extent of typeset TeX at a label size, in user units.
export function mathMetrics(tex, labelSize, tokens) {
  const { vb } = typeset(tex);
  const k = (mathSize(labelSize, tokens) * mathEmPerLabelSize(tokens)) / 1000;
  return { width: vb[2] * k, ascent: -vb[1] * k, descent: (vb[3] + vb[1]) * k };
}
