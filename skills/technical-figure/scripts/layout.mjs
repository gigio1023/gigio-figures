#!/usr/bin/env node
// Lay out a graph with elkjs and write a contract SVG for render.mjs.
// Labels are measured with the real fonts first; see references/routes/mechanism.md for the input.
// Edge labels: in RIGHT and LEFT flows ELK places them and widens the layer gap to fit; in UP
// and DOWN flows ELK would give each label a layer of its own (which can reorder nodes), so they
// are placed after layout beside the longest free straight run of their edge.
// A layout wider than 720u stops with an error unless --wide allows the 1080u canvas.
import fs from 'node:fs';
import { parseCli, run } from './lib/cli.mjs';
import { loadTokens } from './lib/env.mjs';
import { layoutGraph } from './lib/layout-core.mjs';
import { openSession } from './lib/session.mjs';

const USAGE = 'node scripts/layout.mjs graph.json [-o figure.svg] [--wide]';
const { values, positionals } = parseCli(USAGE, { out: { type: 'string', short: 'o' }, wide: { type: 'boolean' } });
const input = positionals[0];
const out = values.out || input.replace(/(\.graph)?\.json$/i, '') + '.svg';
let result;
await run(async () => {
  const graph = JSON.parse(fs.readFileSync(input, 'utf8'));
  const session = await openSession();
  try {
    result = await layoutGraph(session, graph, { wide: values.wide });
  } finally {
    await session.close();
  }
}, input);
fs.writeFileSync(out, result.svg);
for (const w of result.warnings) console.log(`warn  ${w}`);
console.log(`wrote ${out} (${result.width}x${result.height}u); next: node scripts/render.mjs ${out}${result.width > loadTokens().units.canvas_width_u ? ` --width ${result.width}` : ''}`);
