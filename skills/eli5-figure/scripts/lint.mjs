#!/usr/bin/env node
// Lint a figure source with real fonts and measured geometry. Exit 1 when any error is found.
// --width is the delivery column in CSS px: default the token column (704); --width 1080 for a
// full-width figure.
import fs from 'node:fs';
import path from 'node:path';
import { parseCli, run } from './lib/cli.mjs';
import { formatReport, lintSource } from './lib/lint-core.mjs';
import { openSession } from './lib/session.mjs';

const USAGE = 'node scripts/lint.mjs figure.svg [--width N] [--json] [--spec figure-spec.json]';
const { values, positionals } = parseCli(USAGE, { width: { type: 'string' }, json: { type: 'boolean' }, spec: { type: 'string' } });
const file = positionals[0];
let report;
await run(async () => {
  const src = fs.readFileSync(file, 'utf8');
  const session = await openSession();
  try {
    report = await lintSource(session, src, { delivery: values.width ? Number(values.width) : undefined, specPath: values.spec });
  } finally {
    await session.close();
  }
}, file);
console.log(values.json ? JSON.stringify(report, null, 2) : formatReport(path.basename(file), report));
process.exit(report.errors ? 1 : 0);
