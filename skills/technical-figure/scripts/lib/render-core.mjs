// Themed PNGs, portable SVG, and lint report for one source figure.
import fs from 'node:fs';
import path from 'node:path';
import { embedFonts } from './embed-fonts.mjs';
import { loadFigure, screenshot } from './figure.mjs';
import { lintSource } from './lint-core.mjs';
import { adaptiveCss } from './theme.mjs';

// opts: { themes: ['light','dark'], delivery, portable, specPath, outDir }
export async function renderFigure(session, file, opts) {
  const src = fs.readFileSync(file, 'utf8');
  const stem = path.join(opts.outDir || path.dirname(file), path.basename(file).replace(/\.svg$/i, ''));
  const written = [];
  const notes = [];
  const pngs = {};
  const delivery = opts.delivery || session.tokens.units.delivery_width_css_px;

  for (const theme of opts.themes) {
    await loadFigure(session, src, theme);
    pngs[theme] = await screenshot(session, delivery);
    fs.writeFileSync(`${stem}.${theme}.png`, pngs[theme]);
    written.push(`${stem}.${theme}.png`);
  }

  if (opts.portable) {
    const base = adaptiveCss(session.tokens);
    await loadFigure(session, src, 'light', base);
    const usage = await session.page.evaluate(() => TF.fontUsage());
    const fonts = embedFonts(usage, session.tokens);
    if (fonts.warning) notes.push(fonts.warning);
    else if (fonts.faces.length) notes.push(`portable fonts embedded: ${fonts.faces.join(', ')} (${Math.round(fonts.bytes / 1024)} KB)`);
    const svg = await session.page.evaluate((css) => TF.serialize(css), [fonts.css, base].filter(Boolean).join('\n'));
    fs.writeFileSync(`${stem}.portable.svg`, svg + '\n');
    written.push(`${stem}.portable.svg`);
  }

  const report = await lintSource(session, src, { delivery, specPath: opts.specPath, lightPng: pngs.light });
  report.source = path.basename(file);
  fs.writeFileSync(`${stem}.lint.json`, JSON.stringify(report, null, 2) + '\n');
  written.push(`${stem}.lint.json`);
  return { report, written, notes, delivery };
}
