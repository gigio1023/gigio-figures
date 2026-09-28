// A Chromium page with the cached fonts loaded and lib/runtime.js injected.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { cacheRequire, checkFonts, findBrowser, FONT_FACES, loadTokens } from './env.mjs';
import { fontFaceCss } from './theme.mjs';

const RUNTIME = path.join(path.dirname(fileURLToPath(import.meta.url)), 'runtime.js');

export const cachedFontFaces = (tokens) => fontFaceCss(tokens, FONT_FACES, (f) => `url("${pathToFileURL(f.path).href}")`);

// Browser plus a temp dir for file:// pages; an about:blank page (setContent) cannot load file:// fonts or images.
export async function launch({ scale }) {
  checkFonts();
  const { chromium } = cacheRequire('playwright-core');
  const browser = await chromium.launch({ executablePath: findBrowser(), headless: true });
  const page = await browser.newPage({ deviceScaleFactor: scale, viewport: { width: 1600, height: 1200 } });
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'technical-figure-'));
  const open = async (name, html) => {
    const file = path.join(dir, name);
    fs.writeFileSync(file, html);
    await page.goto(pathToFileURL(file).href);
  };
  const close = async () => {
    await browser.close();
    fs.rmSync(dir, { recursive: true, force: true });
  };
  return { browser, page, open, close };
}

export async function openSession({ tokens = loadTokens(), scale = tokens.units.export_scale } = {}) {
  const { browser, page, open, close } = await launch({ scale });
  await open('page.html', `<!doctype html><html><head><meta charset="utf-8"><style>${cachedFontFaces(tokens)}\nhtml,body{margin:0;padding:0}#host{display:inline-block;line-height:0}#host svg{display:block}</style></head><body><div id="host"></div></body></html>`);
  await page.addScriptTag({ path: RUNTIME });
  // Chromium fetches a face only when text first uses it; load every face up front so the
  // first measurements do not silently use a fallback font.
  const failed = await page.evaluate(async (list) => {
    const bad = [];
    for (const f of list) {
      const loaded = await document.fonts.load(`${f.weight} 16px "${f.family}"`, f.sample);
      if (!loaded.length || loaded.some((ff) => ff.status !== 'loaded')) bad.push(`${f.family} ${f.weight}`);
    }
    return bad;
  }, FONT_FACES.map((f) => ({ family: tokens.fonts[f.role].family, weight: f.weight, sample: f.role === 'sans' ? 'Ag가' : 'Ag' })));
  if (failed.length) {
    await close();
    throw new Error(`fonts failed to load in Chromium: ${failed.join(', ')}; run: bash scripts/setup.sh`);
  }
  return { browser, page, tokens, close };
}
