#!/usr/bin/env node
// Contact sheet: a document's figures in reading order at the delivery width, each labeled.
// --columns N sets figures side by side (old vs new, framing A vs B); rows fill left to right.
// A figure narrower than the width stays at its own 1x size; wider ones scale down to it.
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { parseCli, run } from './lib/cli.mjs';
import { loadTokens } from './lib/env.mjs';
import { cachedFontFaces, launch } from './lib/session.mjs';

const USAGE = 'node scripts/sheet.mjs fig1.png fig2.png ... [--width 704] [--columns N] [--theme light|dark] -o sheet.png';
const tokens = loadTokens();
const { values, positionals } = parseCli(USAGE, {
  width: { type: 'string', default: String(tokens.units.delivery_width_css_px) },
  columns: { type: 'string', default: '1' },
  theme: { type: 'string', default: 'light' },
  out: { type: 'string', short: 'o' },
}, { min: 1, max: Infinity });
const theme = tokens.themes[values.theme];
const columns = Number(values.columns);
if (!values.out || !theme || !(columns >= 1)) { console.error(`usage: ${USAGE}`); process.exit(2); }
for (const f of positionals) if (!fs.existsSync(f)) { console.error(`${f}: not found`); process.exit(2); }

const width = Number(values.width);
const sp = tokens.spacing_u.scale;
const [gapLabel, margin, gapFigure] = [sp[1], sp[4], sp[5]];
const label = tokens.type.annotation;
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
const family = tokens.fonts.sans.stack.map((f) => (f.includes(' ') ? `"${f}"` : f)).join(',');
const figures = positionals.map((f) => `<figure><img src="${pathToFileURL(path.resolve(f)).href}"><figcaption>${esc(path.basename(f))}</figcaption></figure>`).join('');
const html = `<!doctype html><html><head><meta charset="utf-8"><style>${cachedFontFaces(tokens)}
html,body{margin:0;background:${theme.bg}}
main{display:grid;grid-template-columns:repeat(${columns},${width}px);gap:${gapFigure}px;padding:${margin}px;width:max-content;align-items:start}
figure{margin:0}
img{display:block;max-width:${width}px}
figcaption{margin-top:${gapLabel}px;font:${label.weight} ${label.size_u}px ${family};color:${theme[label.color]}}
</style></head><body><main>${figures}</main></body></html>`;

await run(async () => {
  const { page, open, close } = await launch({ scale: tokens.units.export_scale });
  try {
    await page.setViewportSize({ width: columns * (width + gapFigure) + 2 * margin, height: 800 });
    await open('sheet.html', html);
    await page.evaluate(async ([scale, font]) => {
      await document.fonts.load(font, 'Ag가');
      for (const img of document.images) {
        await img.decode();
        img.style.width = `${img.naturalWidth / scale}px`;
      }
    }, [tokens.units.export_scale, `${label.weight} ${label.size_u}px "${tokens.fonts.sans.family}"`]);
    await (await page.$('main')).screenshot({ path: values.out });
  } finally {
    await close();
  }
});
console.log(`wrote ${values.out} (${positionals.length} figures, ${columns} per row, ${width} CSS px each, ${values.theme})`);
