// Subset the used glyphs of each font face to woff2 data URIs for the portable SVG.
// Runs fonttools through uvx in offline mode; setup.sh cached it, so this never downloads.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { FONT_FACES, fonttoolsSpec } from './env.mjs';
import { fontFaceCss } from './theme.mjs';

const hasUvx = () => spawnSync('uvx', ['--version'], { stdio: 'ignore' }).status === 0;

// Nearest available weight within the same family role.
function faceFor(key) {
  const [role, w] = key.split('-');
  const same = FONT_FACES.filter((f) => f.role === role);
  return same.reduce((a, b) => (Math.abs(b.weight - w) < Math.abs(a.weight - w) ? b : a));
}

// usage: { 'sans-600': 'chars', ... } from TF.fontUsage(). Returns { css, faces, warning }.
export function embedFonts(usage, tokens) {
  if (!Object.keys(usage).length) return { css: '', faces: [] };
  if (!hasUvx()) return { css: '', faces: [], warning: 'uvx not found; the portable SVG names the fonts but does not embed them' };
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'technical-figure-fonts-'));
  const chars = new Map();
  for (const [key, text] of Object.entries(usage)) {
    const face = faceFor(key);
    chars.set(face, (chars.get(face) || '') + text);
  }
  const data = new Map();
  try {
    for (const [face, text] of chars) {
      const txt = path.join(dir, `${face.key}.txt`);
      const out = path.join(dir, `${face.key}.woff2`);
      fs.writeFileSync(txt, text);
      const r = spawnSync('uvx', ['--offline', '--from', fonttoolsSpec(), 'pyftsubset', face.path,
        `--text-file=${txt}`, '--flavor=woff2', '--layout-features=*', '--no-hinting', `--output-file=${out}`], { encoding: 'utf8' });
      if (r.status !== 0) {
        return { css: '', faces: [], warning: `fonttools subsetting failed (${(r.stderr || '').trim().split('\n').pop()}); run bash scripts/setup.sh. Fonts are not embedded` };
      }
      data.set(face, fs.readFileSync(out).toString('base64'));
    }
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
  const faces = [...data.keys()];
  const css = fontFaceCss(tokens, faces, (f) => `url(data:font/woff2;base64,${data.get(f)}) format("woff2")`);
  return { css, faces: faces.map((f) => f.key), bytes: [...data.values()].reduce((s, b) => s + (b.length * 3) / 4, 0) };
}
