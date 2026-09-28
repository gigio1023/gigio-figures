// Mount a source SVG in the session page and apply the renderer's appearance for one theme.
import { typeset, mathEmPerLabelSize } from './math.mjs';
import { hueNames, themeCss } from './theme.mjs';

// Glyph arm of an operator as a fraction of its radius; the circle stays visibly larger than the sign.
const OP_GLYPH_ARM = 0.55;

export function arrowParams(tokens) {
  const a = tokens.arrowhead;
  const m = /^\s*([\d.]+)\s*\+\s*([\d.]+)\s*\*\s*stroke\s*$/.exec(a.length_u);
  if (!m) throw new Error(`cannot read arrowhead.length_u "${a.length_u}" in the token file`);
  return { base: Number(m[1]), perStroke: Number(m[2]), halfRatio: a.half_width_ratio };
}

export function prepareOptions(tokens, math) {
  return {
    radius: tokens.radius_u,
    tallNodeHeight: tokens.spacing_u.node_height_two_line,
    opRadius: tokens.operator_radius_u,
    opGlyphArm: OP_GLYPH_ARM,
    dotPerStroke: tokens.junction_dot_radius_per_stroke,
    stroke: tokens.stroke,
    arrow: arrowParams(tokens),
    mathEmPerLabelSize: mathEmPerLabelSize(tokens),
    mathMinSize: tokens.fonts.math.min_size_u || 0,
    hues: hueNames(tokens),
    math,
  };
}

// Returns the viewBox of the mounted figure.
export async function loadFigure(session, src, theme, css = themeCss(session.tokens, theme)) {
  const { page, tokens } = session;
  const vb = await page.evaluate(([s, c]) => TF.mount(s, c), [src, css]);
  const vp = page.viewportSize();
  // elementsFromPoint and screenshots only see what is inside the viewport.
  const need = { width: Math.max(vp.width, Math.ceil(vb.width * 1.5) + 16), height: Math.max(vp.height, Math.ceil(vb.height * 1.5) + 16) };
  if (need.width > vp.width || need.height > vp.height) await page.setViewportSize(need);
  const texs = await page.evaluate(() => TF.texList());
  const math = texs.map((t) => typeset(t));
  await page.evaluate((o) => TF.prepare(o), prepareOptions(tokens, math));
  return vb;
}

// 2x PNG of the mounted figure at the delivery width in CSS px.
export async function screenshot(session, delivery) {
  await session.page.evaluate((w) => TF.setDisplayWidth(w), delivery);
  const el = await session.page.$('#host svg');
  return el.screenshot({ type: 'png' });
}
