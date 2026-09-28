#!/usr/bin/env bash
# Prepare the technical-figure toolchain in a user cache.
#
#   bash scripts/setup.sh           install what is missing (idempotent)
#   bash scripts/setup.sh --check   report readiness only; exit 1 when not ready
#
# This is the only step that uses the network: the npm registry for the pinned packages
# in package-lock.json, jsDelivr for the pinned OFL fonts, and PyPI through uvx for
# fonttools (optional; used to embed fonts in the portable SVG). render, lint, layout,
# and sheet never download anything.
#
# It never installs a browser. Browser discovery lives in lib/env.mjs.
#
# Cache layout (TECHNICAL_FIGURE_CACHE, default ${XDG_CACHE_HOME:-~/.cache}/technical-figure):
#   node/   package.json, package-lock.json, node_modules/
#   fonts/  Pretendard-Regular.otf, Pretendard-SemiBold.otf, JetBrainsMono-Regular.ttf,
#           JetBrainsMono-Medium.ttf, OFL-Pretendard.txt, OFL-JetBrainsMono.txt
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CACHE="${TECHNICAL_FIGURE_CACHE:-${XDG_CACHE_HOME:-$HOME/.cache}/technical-figure}"
NODE_DIR="$CACHE/node"
FONT_DIR="$CACHE/fonts"
# fonttools pin lives in package.json "config" so render.mjs reads the same value.
FONTTOOLS_SPEC="$(sed -n 's/.*"fonttools": *"\([^"]*\)".*/\1/p' "$SCRIPT_DIR/package.json")"

PRETENDARD="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9"
JBMONO="https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono@v2.304"
# name|url|sha256
FONTS=(
  "Pretendard-Regular.otf|$PRETENDARD/packages/pretendard/dist/public/static/Pretendard-Regular.otf|3ffbacde6ab8411f1d2db54bb9b1f0b3ee2a738932033722cf0388c06aed1c93"
  "Pretendard-SemiBold.otf|$PRETENDARD/packages/pretendard/dist/public/static/Pretendard-SemiBold.otf|c89bc43027dc7cde5726e96223376f8eec09302b2fc1f8147fd5b57cfc376118"
  "JetBrainsMono-Regular.ttf|$JBMONO/fonts/ttf/JetBrainsMono-Regular.ttf|a0bf60ef0f83c5ed4d7a75d45838548b1f6873372dfac88f71804491898d138f"
  "JetBrainsMono-Medium.ttf|$JBMONO/fonts/ttf/JetBrainsMono-Medium.ttf|31c92d01a8a08528b718a43addf0ad3df0af2ca4b7b3290a452f70f358e14d3d"
  "OFL-Pretendard.txt|$PRETENDARD/LICENSE|d31ddd9f2bed32fd7e302a205cf2380ba0de6529152d239ef99cfb6f261bfc04"
  "OFL-JetBrainsMono.txt|$JBMONO/OFL.txt|30f0c136e3c88e422d0791acd97238870f9054a9729bc34cf2ff0d4ed8cac4ad"
)

sha256() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
  else shasum -a 256 "$1" | cut -d' ' -f1; fi
}

node_ok() {
  command -v node >/dev/null 2>&1 || return 1
  local major; major="$(node -p 'process.versions.node.split(".")[0]')"
  [ "$major" -ge 20 ]
}

deps_ok() {
  [ -f "$NODE_DIR/node_modules/.package-lock.json" ] &&
    cmp -s "$SCRIPT_DIR/package-lock.json" "$NODE_DIR/package-lock.json" &&
    cmp -s "$SCRIPT_DIR/package.json" "$NODE_DIR/package.json"
}

font_ok() { # name sha
  [ -f "$FONT_DIR/$1" ] && [ "$(sha256 "$FONT_DIR/$1")" = "$2" ]
}

fonts_ok() {
  local entry name url sum
  for entry in "${FONTS[@]}"; do
    IFS='|' read -r name url sum <<<"$entry"
    font_ok "$name" "$sum" || return 1
  done
}

browser_path() {
  (cd "$SCRIPT_DIR" && node --input-type=module -e \
    'import { findBrowser } from "./lib/env.mjs"; try { console.log(findBrowser()); } catch (e) { console.log(e.message); process.exit(1); }')
}

fonttools_ok() {
  command -v uvx >/dev/null 2>&1 &&
    uvx --offline --from "$FONTTOOLS_SPEC" pyftsubset --help >/dev/null 2>&1
}

check() {
  local ready=0
  if node_ok; then echo "ok    node $(node --version)"; else echo "MISS  node 20 or newer"; ready=1; fi
  if deps_ok; then echo "ok    npm packages in $NODE_DIR"; else echo "MISS  npm packages (run: bash scripts/setup.sh)"; ready=1; fi
  if fonts_ok; then echo "ok    fonts in $FONT_DIR"; else echo "MISS  fonts (run: bash scripts/setup.sh)"; ready=1; fi
  local b
  if node_ok && b="$(browser_path)"; then echo "ok    browser $b"; else echo "MISS  browser: ${b:-node missing}"; ready=1; fi
  if fonttools_ok; then echo "ok    fonttools (portable SVG embeds fonts)"
  else echo "note  fonttools not cached; portable SVG will not embed fonts (optional)"; fi
  return "$ready"
}

install_deps() {
  deps_ok && return 0
  echo "installing npm packages into $NODE_DIR"
  mkdir -p "$NODE_DIR"
  cp "$SCRIPT_DIR/package.json" "$SCRIPT_DIR/package-lock.json" "$NODE_DIR/"
  (cd "$NODE_DIR" && npm ci --ignore-scripts --no-audit --no-fund --loglevel=error)
}

install_fonts() {
  mkdir -p "$FONT_DIR"
  local entry name url sum tmp
  for entry in "${FONTS[@]}"; do
    IFS='|' read -r name url sum <<<"$entry"
    font_ok "$name" "$sum" && continue
    echo "downloading $name"
    tmp="$FONT_DIR/.$name.part"
    curl -fsSL --retry 2 -o "$tmp" "$url"
    if [ "$(sha256 "$tmp")" != "$sum" ]; then
      rm -f "$tmp"
      echo "sha256 mismatch for $name from $url" >&2
      exit 1
    fi
    mv "$tmp" "$FONT_DIR/$name"
  done
}

warm_fonttools() {
  command -v uvx >/dev/null 2>&1 || { echo "uvx not found; skipping fonttools (portable SVG fonts stay unembedded)"; return 0; }
  fonttools_ok && return 0
  echo "caching $FONTTOOLS_SPEC for uvx"
  uvx --from "$FONTTOOLS_SPEC" pyftsubset --help >/dev/null
}

case "${1:-}" in
  --check) check ;;
  "")
    node_ok || { echo "Node.js 20 or newer is required" >&2; exit 1; }
    install_deps
    install_fonts
    warm_fonttools
    check
    ;;
  *) echo "usage: bash scripts/setup.sh [--check]" >&2; exit 2 ;;
esac
