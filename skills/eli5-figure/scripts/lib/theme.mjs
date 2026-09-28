// Token file -> CSS. Colors become custom properties on the root <svg>, so one rule set
// serves the light render, the dark render, and the adaptive portable SVG.

export const TEXT_ROLES = {
  tp: 'panel_label',
  t: 'node_label',
  t2: 'node_second_line',
  tl: 'edge_label',
  ta: 'annotation',
  micro: 'micro_caps',
};

const GENERIC_FAMILIES = new Set(['serif', 'sans-serif', 'monospace', 'ui-monospace', 'system-ui']);
const fontStack = (stack) => stack.map((f) => (GENERIC_FAMILIES.has(f) ? f : `"${f}"`)).join(', ');
const cssVar = (name) => `var(--${name.replace(/_/g, '-')})`;

export const hueNames = (tokens) => Object.keys(tokens.themes.light.hues);

export function paletteVars(tokens, theme) {
  const t = tokens.themes[theme];
  if (!t) throw new Error(`unknown theme "${theme}"; use light or dark`);
  const vars = [];
  for (const k of ['bg', 'surface', 'ink', 'ink_2', 'line', 'guide']) vars.push(`--${k.replace(/_/g, '-')}:${t[k]}`);
  for (const [hue, v] of Object.entries(t.hues)) {
    for (const part of ['stroke', 'fill', 'text']) vars.push(`--${hue}-${part}:${v[part]}`);
  }
  return vars.join(';');
}

export function classRules(tokens) {
  const s = tokens.stroke;
  const dash = tokens.dash;
  const hues = hueNames(tokens);
  const r = [];
  const add = (sel, decl) => r.push(`${sel}{${decl}}`);

  add('.tf-bg', `fill:${cssVar('bg')};stroke:none`);
  // Shapes. A tensor looks like a box; only its corner radius differs (set by the runtime).
  const boxes = (suffix = '') => ['.box', '.tensor'].map((b) => b + suffix).join(',');
  add(boxes(), `fill:${cssVar('bg')};stroke:${cssVar('line')};stroke-width:${s.outline_u}px`);
  add(boxes('.focus'), `stroke:${cssVar('ink')};stroke-width:${s.emphasis_u}px`);
  for (const h of hues) add(boxes(`.${h}`), `fill:var(--${h}-fill);stroke:var(--${h}-stroke)`);
  // Context keeps the page fill so it reads on bg and on a container alike.
  add(boxes('.ghost'), `fill:${cssVar('bg')};stroke:${cssVar('guide')}`);
  add(boxes('.runtime'), `stroke-dasharray:${dash.dashed}`);
  add('.chip', `fill:${cssVar('bg')};stroke:${cssVar('guide')};stroke-width:${s.guide_u}px`);
  add('.container', `fill:${cssVar('surface')};stroke:none`);
  add('.container.outline', `fill:none;stroke:${cssVar('guide')};stroke-width:${s.guide_u}px`);
  add('.zoom', `fill:none;stroke:${cssVar('guide')};stroke-width:${s.guide_u}px;stroke-dasharray:${dash.dashed}`);
  add('.op', `fill:${cssVar('bg')};stroke:${cssVar('ink')};stroke-width:${s.edge_u}px`);
  add('.op.runtime', `stroke-dasharray:${dash.dashed}`);
  add('.op-glyph', `fill:none;stroke:${cssVar('ink')};stroke-width:${s.edge_u}px;stroke-linecap:round`);
  for (const h of hues) add(`.op.${h},.op-glyph.${h}`, `stroke:var(--${h}-stroke)`);
  add('.cell', `fill:${cssVar('bg')};stroke:${cssVar('guide')};stroke-width:${s.guide_u}px`);
  for (const h of hues) {
    add(`.cell.on.${h}`, `fill:var(--${h}-stroke);stroke:var(--${h}-stroke)`);
    add(`.cell.tint.${h}`, `fill:var(--${h}-fill);stroke:var(--${h}-stroke)`);
  }
  add('.band', `fill:${cssVar('surface')};stroke:none`);
  // Lines. A hue colors any edge at its own weight; emph adds the emphasis weight.
  const line = 'fill:none;stroke-linejoin:round;stroke-linecap:butt';
  add('.spine', `${line};stroke:${cssVar('ink')};stroke-width:${s.emphasis_u}px`);
  add('.edge', `${line};stroke:${cssVar('ink')};stroke-width:${s.edge_u}px`);
  add('.edge.control', `stroke-dasharray:${dash.dashed}`);
  add('.edge.emph', `stroke-width:${s.emphasis_u}px`);
  add('.edge.ghost', `stroke:${cssVar('guide')};stroke-width:${s.guide_u}px`);
  for (const h of hues) add(`.edge.${h}`, `stroke:var(--${h}-stroke)`);
  add('.leader', `fill:none;stroke:${cssVar('ink_2')};stroke-width:${s.guide_u}px;stroke-dasharray:${dash.dotted};stroke-linecap:${dash.dotted_linecap}`);
  add('.guide', `fill:none;stroke:${cssVar('guide')};stroke-width:${s.guide_u}px`);
  add('.mark', `fill:none;stroke:${cssVar('ink_2')};stroke-width:${s.guide_u}px;stroke-linecap:butt;stroke-linejoin:miter`);
  add('.arrowhead', 'fill:none;stroke-dasharray:none;stroke-linecap:round;stroke-linejoin:round');
  add('.dot', `fill:${cssVar('ink')};stroke:none`);
  for (const h of hues) add(`.dot.${h}`, `fill:var(--${h}-stroke)`);
  add('.dot.ghost', `fill:${cssVar('guide')}`);
  // Text. Math groups take the same classes; their glyphs paint with currentColor.
  const f = tokens.fonts;
  add('text', `font-family:${fontStack(f.sans.stack)};font-feature-settings:${f.sans.features}`);
  for (const [cls, role] of Object.entries(TEXT_ROLES)) {
    const t = tokens.type[role];
    const tracking = t.tracking_em ? `;letter-spacing:${t.tracking_em}em` : '';
    add(`text.${cls}`, `font-size:${t.size_u}px;font-weight:${t.weight}${tracking}`);
    add(`text.${cls},g.math.${cls}`, `fill:${cssVar(t.color)};color:${cssVar(t.color)}`);
  }
  add('text.mono', `font-family:${fontStack(f.mono.stack)};font-weight:${tokens.type.node_label.mono_weight};font-feature-settings:normal;letter-spacing:0`);
  // Labels of a ghost box are ink-2 even without the text modifier.
  const ghostLabels = 'g:has(> .box.ghost, > .tensor.ghost) > text,g:has(> .box.ghost, > .tensor.ghost) > g.math';
  add(`text.ghost,g.math.ghost,${ghostLabels}`, `fill:${cssVar('ink_2')};color:${cssVar('ink_2')}`);
  for (const h of hues) add(`text.${h},g.math.${h}`, `fill:var(--${h}-text);color:var(--${h}-text)`);
  return r.join('\n');
}

export function fontFaceCss(tokens, faces, srcFor) {
  return faces.map((face) => {
    const family = tokens.fonts[face.role].family;
    return `@font-face{font-family:"${family}";font-weight:${face.weight};font-style:normal;font-display:block;src:${srcFor(face)}}`;
  }).join('\n');
}

// Fixed palette for PNG renders.
export function themeCss(tokens, theme) {
  return `svg{${paletteVars(tokens, theme)}}\n${classRules(tokens)}`;
}

// Both palettes: light by default, dark when the viewer prefers it.
export function adaptiveCss(tokens) {
  return [
    `svg{${paletteVars(tokens, 'light')}}`,
    `@media (prefers-color-scheme: dark){svg{${paletteVars(tokens, 'dark')}}}`,
    classRules(tokens),
  ].join('\n');
}
