#!/usr/bin/env node
// Measure label strings with the real fonts before hand-authoring a figure.
//   node scripts/measure.mjs "self_attn" "Attention" --class t --mono
//   node scripts/measure.mjs "W_O" "x^{(\ell)}" --tex --class t2
// Prints width and ink height in u, and the box width that fits the label (token padding,
// rounded up to the 4u grid). TeX is sized exactly as render.mjs sets it.
import { parseCli, run } from './lib/cli.mjs';
import { mathMetrics } from './lib/math.mjs';
import { openSession } from './lib/session.mjs';
import { TEXT_ROLES, themeCss } from './lib/theme.mjs';

const USAGE = 'node scripts/measure.mjs text... [--class t|t2|tl|ta|tp|micro] [--mono] [--tex]';
const { values, positionals } = parseCli(USAGE, {
  class: { type: 'string', default: 't' },
  mono: { type: 'boolean' },
  tex: { type: 'boolean' },
}, { min: 1, max: Infinity });
if (!TEXT_ROLES[values.class] || (values.mono && values.tex)) { console.error(`usage: ${USAGE}`); process.exit(2); }

await run(async () => {
  const session = await openSession();
  const { tokens } = session;
  let rows;
  try {
    const role = tokens.type[TEXT_ROLES[values.class]];
    if (values.tex) {
      rows = positionals.map((t) => ({ text: t, ...mathMetrics(t, role.size_u, tokens) }));
    } else {
      await session.page.evaluate((c) => TF.mount('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"/>', c), themeCss(tokens, 'light'));
      const cls = values.mono ? `${values.class} mono` : values.class;
      const m = await session.page.evaluate((items) => TF.measureTexts(items), positionals.map((t) => ({ cls, text: t })));
      rows = positionals.map((t, i) => ({ text: t, ...m[i] }));
    }
    const sp = tokens.spacing_u;
    const boxW = (w) => Math.ceil((w + 2 * sp.node_padding_x) / sp.unit) * sp.unit;
    const f = (v) => v.toFixed(1).padStart(6);
    const pad = Math.max(4, ...rows.map((r) => r.text.length)) + 2;
    console.log(`class ${values.class}${values.mono ? ' mono' : ''}${values.tex ? ' (TeX)' : ''}, ${role.size_u}u`);
    console.log(`${'text'.padEnd(pad)} width  ascent descent  height  box_w`);
    for (const r of rows) console.log(`${r.text.padEnd(pad)}${f(r.width)}  ${f(r.ascent)} ${f(r.descent)}  ${f(r.ascent + r.descent)}  ${String(boxW(r.width)).padStart(5)}`);
  } finally {
    await session.close();
  }
});
