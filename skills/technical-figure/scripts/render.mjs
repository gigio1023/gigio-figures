#!/usr/bin/env node
// Render a contract SVG beside the source: themed 2x PNGs, a portable SVG, and the lint report.
// --width is the delivery column in CSS px: default the token column (704); --width 1080 for a
// full-width figure. Exit 1 on lint errors, or on warnings with --strict.
import path from 'node:path';
import { parseCli, run } from './lib/cli.mjs';
import { formatReport } from './lib/lint-core.mjs';
import { renderFigure } from './lib/render-core.mjs';
import { openSession } from './lib/session.mjs';

const USAGE = 'node scripts/render.mjs figure.svg [--theme light|dark|both] [--width N] [--no-portable] [--strict] [--spec figure-spec.json]';
const { values, positionals } = parseCli(USAGE, {
  theme: { type: 'string', default: 'both' },
  width: { type: 'string' },
  'no-portable': { type: 'boolean' },
  strict: { type: 'boolean' },
  spec: { type: 'string' },
});
const themes = { both: ['light', 'dark'], light: ['light'], dark: ['dark'] }[values.theme];
if (!themes) { console.error(`usage: ${USAGE}`); process.exit(2); }
const file = positionals[0];

let result;
await run(async () => {
  const session = await openSession();
  try {
    result = await renderFigure(session, file, {
      themes,
      delivery: values.width ? Number(values.width) : undefined,
      portable: !values['no-portable'],
      specPath: values.spec,
    });
  } finally {
    await session.close();
  }
}, file);
const { report, written, notes, delivery } = result;
const m = report.metrics;
console.log(`${path.basename(file)}: ${m.width_u}x${m.height_u}u at ${delivery} CSS px (height ${m.height_css_px} px)`);
const shown = (f) => (path.relative(process.cwd(), f).startsWith('..') ? f : path.relative(process.cwd(), f));
for (const f of written) console.log(`  wrote ${shown(f)}`);
for (const n of notes) console.log(`  note  ${n}`);
console.log(formatReport(report.source, report));
process.exit(report.errors || (values.strict && report.warnings) ? 1 : 0);
