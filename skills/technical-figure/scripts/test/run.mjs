#!/usr/bin/env node
// Toolchain tests: lint fixtures must produce exactly their expected ids, the layout graphs
// must lay out and lint clean, and the clean figures render in both themes.
//   node scripts/test/run.mjs [--out DIR]
// Outputs go to DIR (default: <cache>/test-out), never into the skill directory.
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { CACHE_DIR } from '../lib/env.mjs';
import { layoutGraph } from '../lib/layout-core.mjs';
import { formatReport, lintSource } from '../lib/lint-core.mjs';
import { renderFigure } from '../lib/render-core.mjs';
import { openSession } from '../lib/session.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const FIX = path.join(HERE, 'fixtures');
const { values } = parseArgs({ options: { out: { type: 'string' } } });
const OUT = path.resolve(values.out || path.join(CACHE_DIR, 'test-out'));
fs.mkdirSync(OUT, { recursive: true });

// [fixture, expected error ids, expected warning ids or null to ignore warnings, options]
const LINT_CASES = [
  ['clean-residual.svg', [], []],
  ['clean-classes.svg', [], []],
  ['bad-text-overlap.svg', ['text-overlap'], null],
  ['bad-text-crossed.svg', ['text-crossed'], null],
  ['bad-text-overflow.svg', ['text-overflow'], null],
  ['bad-text-too-small.svg', ['text-too-small'], null],
  ['bad-unicode-math.svg', ['unicode-math'], null],
  ['bad-source-appearance.svg', ['source-appearance'], null],
  ['bad-external-reference.svg', ['external-reference'], null],
  ['bad-contrast.svg', ['contrast'], null],
  ['bad-arrow-tips.svg', ['arrow-tips'], null],
  ['bad-height-limit.svg', ['height-limit'], null],
  ['bad-mono-mixed.svg', ['mono-mixed'], null],
  ['bad-outside-canvas.svg', ['outside-canvas'], null],
  ['clean-residual.svg', ['missing-element'], [], { specPath: path.join(FIX, 'clean-residual.spec.json') }],
  ['warn-mix.svg', [], ['duplicate-id', 'edge-bends', 'edge-crossing', 'focus-hues', 'height-budget', 'label-far', 'margin', 'relation-styles']],
  ['warn-color-area.svg', [], ['color-area']],
  ['wide-1080.svg', ['text-too-small'], null],
  ['wide-1080.svg', [], [], { delivery: 1080 }],
];
const LAYOUT_CASES = ['moe.graph.json', 'pipeline.graph.json', 'op-sides.graph.json'];
const chain = (n, direction) => ({ direction, nodes: Array.from({ length: n }, (_, i) => ({ id: `n${i}`, title: `stage ${i}` })), edges: Array.from({ length: n - 1 }, (_, i) => ({ from: `n${i}`, to: `n${i + 1}` })) });
// [name, graph, options, expected error pattern or canvas width]
const LAYOUT_LIMITS = [
  ['three edges on one operator side', { nodes: [{ id: 'a', title: 'a' }, { id: 'b', title: 'b' }, { id: 'c', title: 'c' }, { id: 'o', title: '+', kind: 'op' }], edges: [{ from: 'a', to: 'o' }, { from: 'b', to: 'o' }, { from: 'c', to: 'o' }] }, {}, /at most 2 arrow tips/],
  ['chain wider than the column', chain(8, 'RIGHT'), {}, /u wide; the column canvas is 720u/],
  ['same chain with --wide', chain(8, 'RIGHT'), { wide: true }, 1080],
];

const ids = (report, severity) => [...new Set(report.findings.filter((f) => f.severity === severity).map((f) => f.id))].sort();
const same = (a, b) => a.length === b.length && a.every((x, i) => x === b[i]);

let failures = 0;
const fail = (msg, report) => {
  failures++;
  console.log(`FAIL ${msg}`);
  if (report) console.log(formatReport('', report).split('\n').slice(1).join('\n'));
};

const session = await openSession();
try {
  for (const [file, errs, warns, opts = {}] of LINT_CASES) {
    const src = fs.readFileSync(path.join(FIX, file), 'utf8');
    const report = await lintSource(session, src, opts);
    const gotE = ids(report, 'error'), gotW = ids(report, 'warning');
    const label = `${file}${opts.specPath ? ' (with spec)' : ''}${opts.delivery ? ` at ${opts.delivery} px` : ''}`;
    if (!same(gotE, [...errs].sort())) fail(`${label}: errors [${gotE}] expected [${errs}]`, report);
    else if (warns && !same(gotW, [...warns].sort())) fail(`${label}: warnings [${gotW}] expected [${warns}]`, report);
    else console.log(`ok   ${label}: errors [${gotE}]${warns ? ` warnings [${gotW}]` : ''}`);
  }

  const toRender = ['clean-residual.svg', 'clean-classes.svg'].map((f) => {
    fs.copyFileSync(path.join(FIX, f), path.join(OUT, f));
    return path.join(OUT, f);
  });
  for (const file of LAYOUT_CASES) {
    const graph = JSON.parse(fs.readFileSync(path.join(FIX, file), 'utf8'));
    const out = path.join(OUT, file.replace(/\.graph\.json$/, '.svg'));
    try {
      const { svg, width, height, warnings } = await layoutGraph(session, graph);
      fs.writeFileSync(out, svg);
      if (warnings.length) fail(`${file}: layout warnings: ${warnings.join('; ')}`);
      else console.log(`ok   ${file}: laid out ${width}x${height}u`);
      toRender.push(out);
    } catch (e) {
      fail(`${file}: layout failed: ${e.message}`);
    }
  }

  for (const [name, graph, opts, expect] of LAYOUT_LIMITS) {
    try {
      const { width } = await layoutGraph(session, graph, opts);
      if (expect === width) console.log(`ok   layout ${name}: ${width}u canvas`);
      else fail(`layout ${name}: laid out at ${width}u, expected ${expect}`);
    } catch (e) {
      if (expect instanceof RegExp && expect.test(e.message)) console.log(`ok   layout ${name}: refused`);
      else fail(`layout ${name}: ${e.message}`);
    }
  }

  const bad = spawnSync(process.execPath, [path.join(HERE, '..', 'lint.mjs'), path.join(FIX, 'malformed.svg')], { encoding: 'utf8' });
  const errLines = bad.stderr.trim().split('\n');
  if (bad.status === 2 && errLines.length === 1 && /malformed\.svg: SVG parse error: line \d+, column \d+/.test(errLines[0])) console.log(`ok   malformed.svg: exit 2, ${errLines[0].replace(/^.*malformed/, 'malformed')}`);
  else fail(`malformed.svg: exit ${bad.status}, stderr: ${bad.stderr}`);

  for (const file of toRender) {
    const { report } = await renderFigure(session, file, { themes: ['light', 'dark'], portable: true });
    if (report.errors) fail(`render ${path.basename(file)}: ${report.errors} lint errors`, report);
    else console.log(`ok   render ${path.basename(file)}: 0 errors, ${report.warnings} warnings -> ${path.join(OUT, path.basename(file, '.svg'))}.{light,dark}.png`);
  }
} finally {
  await session.close();
}
console.log(failures ? `\n${failures} failed` : '\nall passed');
process.exit(failures ? 1 : 0);
