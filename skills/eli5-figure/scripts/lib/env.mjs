// Paths, cached dependencies, fonts, tokens, and browser discovery shared by every script.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

export const SCRIPTS_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const SKILL_DIR = path.resolve(SCRIPTS_DIR, '..');
export const TOKENS_PATH = path.join(SKILL_DIR, 'assets', 'figure-tokens.json');

export const CACHE_DIR = process.env.TECHNICAL_FIGURE_CACHE
  || path.join(process.env.XDG_CACHE_HOME || path.join(os.homedir(), '.cache'), 'technical-figure');
export const NODE_DIR = path.join(CACHE_DIR, 'node');
export const FONT_DIR = path.join(CACHE_DIR, 'fonts');

const SETUP_HINT = 'run: bash scripts/setup.sh';

// Font faces the renderer loads. Weights follow the token file; files follow setup.sh.
export const FONT_FACES = [
  { key: 'sans-400', role: 'sans', weight: 400, file: 'Pretendard-Regular.otf' },
  { key: 'sans-600', role: 'sans', weight: 600, file: 'Pretendard-SemiBold.otf' },
  { key: 'mono-400', role: 'mono', weight: 400, file: 'JetBrainsMono-Regular.ttf' },
  { key: 'mono-500', role: 'mono', weight: 500, file: 'JetBrainsMono-Medium.ttf' },
].map((f) => ({ ...f, path: path.join(FONT_DIR, f.file) }));

let cachedRequire;
// require() bound to the cached node_modules installed by setup.sh.
export function cacheRequire(id) {
  if (!cachedRequire) {
    const manifest = path.join(NODE_DIR, 'package.json');
    if (!fs.existsSync(path.join(NODE_DIR, 'node_modules'))) {
      throw new Error(`npm packages are not installed in ${NODE_DIR}; ${SETUP_HINT}`);
    }
    cachedRequire = createRequire(manifest);
  }
  return cachedRequire(id);
}

export function loadTokens() {
  return JSON.parse(fs.readFileSync(TOKENS_PATH, 'utf8'));
}

export function fonttoolsSpec() {
  return JSON.parse(fs.readFileSync(path.join(SCRIPTS_DIR, 'package.json'), 'utf8')).config.fonttools;
}

export function checkFonts() {
  const missing = FONT_FACES.filter((f) => !fs.existsSync(f.path)).map((f) => f.file);
  if (missing.length) throw new Error(`fonts missing in ${FONT_DIR}: ${missing.join(', ')}; ${SETUP_HINT}`);
}

const isFile = (p) => {
  try { return fs.statSync(p).isFile(); } catch { return false; }
};

// Newest Playwright build of a given kind, by revision number in the directory name.
function playwrightBuilds(root, prefix, relatives) {
  let dirs = [];
  try { dirs = fs.readdirSync(root).filter((d) => d.startsWith(prefix + '-')); } catch { return []; }
  const rev = (d) => Number(d.slice(prefix.length + 1)) || 0;
  dirs.sort((a, b) => rev(b) - rev(a));
  const found = [];
  for (const d of dirs) for (const rel of relatives) found.push(path.join(root, d, rel));
  return found;
}

function onPath(name) {
  for (const dir of (process.env.PATH || '').split(path.delimiter)) {
    const p = path.join(dir, name);
    if (isFile(p)) return p;
  }
  return null;
}

// Browser discovery order: env override, macOS app bundles, Playwright caches, Linux PATH.
export function findBrowser() {
  const env = process.env.TECHNICAL_FIGURE_BROWSER;
  if (env) {
    if (isFile(env)) return env;
    throw new Error(`TECHNICAL_FIGURE_BROWSER does not point to a file: ${env}`);
  }
  const home = os.homedir();
  const candidates = [];
  if (process.platform === 'darwin') {
    for (const apps of ['/Applications', path.join(home, 'Applications')]) {
      candidates.push(
        path.join(apps, 'Google Chrome.app/Contents/MacOS/Google Chrome'),
        path.join(apps, 'Chromium.app/Contents/MacOS/Chromium'),
        path.join(apps, 'Microsoft Edge.app/Contents/MacOS/Microsoft Edge'),
      );
    }
  }
  const pwRoots = [process.env.PLAYWRIGHT_BROWSERS_PATH, path.join(home, 'Library/Caches/ms-playwright'), path.join(home, '.cache/ms-playwright')].filter(Boolean);
  for (const root of pwRoots) {
    candidates.push(...playwrightBuilds(root, 'chromium_headless_shell', [
      'chrome-headless-shell-mac-arm64/chrome-headless-shell',
      'chrome-headless-shell-mac-x64/chrome-headless-shell',
      'chrome-headless-shell-linux64/chrome-headless-shell',
      'chrome-headless-shell-linux-arm64/chrome-headless-shell',
    ]));
    candidates.push(...playwrightBuilds(root, 'chromium', [
      'chrome-mac-arm64/Chromium.app/Contents/MacOS/Chromium',
      'chrome-mac/Chromium.app/Contents/MacOS/Chromium',
      'chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
      'chrome-linux64/chrome',
      'chrome-linux/chrome',
    ]));
  }
  for (const p of candidates) if (isFile(p)) return p;
  if (process.platform === 'linux') {
    for (const name of ['google-chrome', 'chromium', 'chromium-browser']) {
      const p = onPath(name);
      if (p) return p;
    }
  }
  throw new Error([
    'No Chromium-family browser found.',
    'Install Google Chrome, or a Playwright build with:',
    `  (cd "${NODE_DIR}" && npx playwright install chromium-headless-shell)`,
    'or point TECHNICAL_FIGURE_BROWSER at a Chrome, Chromium, or Edge executable.',
    `Then check with: bash scripts/setup.sh --check`,
  ].join('\n'));
}
