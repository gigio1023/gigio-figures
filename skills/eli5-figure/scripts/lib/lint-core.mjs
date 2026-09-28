// Lint driver: geometric checks on the prepared figure, contrast in both themes,
// colored area on the light PNG, and spec ids when a FigureSpec is given.
import fs from 'node:fs';
import { loadFigure, screenshot } from './figure.mjs';
import { hueNames, themeCss } from './theme.mjs';

// Lint policy. Design values (sizes, contrast, height budget, colored area) come from the token file.
const POLICY = {
  overlapArea: 4, // u², text boxes may touch but not overlap
  inset: 3, // u, text keeps this margin inside its box or chip
  tipGap: 10, // u, minimum distance between two arrow tips
  labelFar: 14, // u, an edge label farther than this from its line reads as floating
  maxBends: 3,
  maxRelations: 3,
  heightLimit: 900, // CSS px at the delivery width
  crossTolerance: 0.5, // u, points this close to a line count as touching, not crossing
  bendRunTolerance: 0.1, // rad, heading drift allowed within one straight run
  bendMinRun: 3, // samples (1u each) that make a run straight; rounded corners are shorter
  bendMinTurn: 0.35, // rad, smallest heading change counted as a bend
  // A pixel is colored when its RGB channel spread exceeds this. Token tint fills spread 20-27
  // and hue strokes 83 or more, so tints count as neutral area and strokes and text as color.
  coloredSpread: 50,
};

export const SEVERITY = {
  'text-overlap': 'error',
  'text-crossed': 'error',
  'text-overflow': 'error',
  'text-too-small': 'error',
  'unicode-math': 'error',
  'source-appearance': 'error',
  'external-reference': 'error',
  contrast: 'error',
  'arrow-tips': 'error',
  'height-limit': 'error',
  'mono-mixed': 'error',
  'outside-canvas': 'error',
  'missing-element': 'error',
  'height-budget': 'warning',
  margin: 'warning',
  'edge-crossing': 'warning',
  'edge-bends': 'warning',
  'relation-styles': 'warning',
  'focus-hues': 'warning',
  'color-area': 'warning',
  'label-far': 'warning',
  'duplicate-id': 'warning',
};

function specIds(specPath) {
  const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
  const ids = [];
  for (const key of ['nodes', 'edges', 'groups']) for (const item of spec[key] || []) if (item.id) ids.push(item.id);
  return ids;
}

// Lints `src` in the session at the delivery width (default: the token column width).
// Leaves the light theme mounted.
export async function lintSource(session, src, { delivery, specPath, lightPng } = {}) {
  const { page, tokens } = session;
  await loadFigure(session, src, 'light');
  const width = delivery || tokens.units.delivery_width_css_px;
  const opts = {
    ...POLICY,
    delivery: width,
    nominalScale: tokens.units.delivery_width_css_px / tokens.units.canvas_width_u,
    minSize: tokens.type.min_size_u,
    minMicro: tokens.type.min_size_micro_caps_u,
    // The one-screen budget holds the figure and its caption.
    heightBudget: tokens.units.max_height_css_px - tokens.units.caption_allowance_css_px,
    margin: tokens.spacing_u.canvas_margin,
    hues: hueNames(tokens),
    severity: SEVERITY,
  };
  const result = await page.evaluate((o) => TF.lint(o), opts);
  const findings = result.findings;

  for (const theme of ['light', 'dark']) {
    await page.evaluate((c) => TF.setCss(c), themeCss(tokens, theme));
    findings.push(...await page.evaluate((o) => TF.contrast(o), { theme, minContrast: tokens.limits.text_contrast_min, severity: SEVERITY }));
  }
  await page.evaluate((c) => TF.setCss(c), themeCss(tokens, 'light'));

  const png = lightPng || await screenshot(session, width);
  const share = await page.evaluate(([u, s]) => TF.colorArea(u, s), [`data:image/png;base64,${png.toString('base64')}`, POLICY.coloredSpread]);
  if (share > tokens.limits.chroma_area_max) {
    findings.push({ id: 'color-area', severity: SEVERITY['color-area'], elements: ['svg'], message: 'colored area above the budget; color reads as decoration', measured: { share: Math.round(share * 1000) / 1000, max: tokens.limits.chroma_area_max } });
  }
  result.metrics.color_area = Math.round(share * 1000) / 1000;

  if (specPath) {
    const present = new Set(result.ids);
    for (const id of specIds(specPath)) {
      if (!present.has(id)) findings.push({ id: 'missing-element', severity: SEVERITY['missing-element'], elements: [id], message: 'FigureSpec id has no data-id in the figure', measured: { spec: specPath } });
    }
  }

  const order = { error: 0, warning: 1 };
  findings.sort((a, b) => order[a.severity] - order[b.severity] || a.id.localeCompare(b.id));
  const errors = findings.filter((f) => f.severity === 'error').length;
  return { errors, warnings: findings.length - errors, metrics: result.metrics, findings };
}

const brief = (m) => Object.entries(m || {})
  .filter(([k]) => !['text_box', 'a', 'b', 'box', 'canvas', 'spec'].includes(k))
  .map(([k, v]) => `${k}=${typeof v === 'object' ? JSON.stringify(v) : v}`)
  .join(' ');

export function formatReport(name, report) {
  const lines = [`lint ${name}: ${report.errors} error${report.errors === 1 ? '' : 's'}, ${report.warnings} warning${report.warnings === 1 ? '' : 's'}`];
  for (const f of report.findings) {
    lines.push(`  ${f.severity === 'error' ? 'error' : 'warn '} ${f.id.padEnd(18)} ${f.elements.join(' | ')}  ${brief(f.measured)}`);
  }
  return lines.join('\n');
}
