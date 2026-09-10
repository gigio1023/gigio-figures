#!/usr/bin/env bash
# Format-check, validate, and render a D2 source with ELK, then check the SVG.
#
# usage: bash scripts/render_d2.sh <input.d2> <output.svg> [extra d2 flags...]
#
# Extra flags are passed to every d2 render call, for example
#   --elk-nodeNodeBetweenLayers 40 --elk-edgeNodeBetweenLayers 24   tighten a wide horizontal layout
#   --font-mono /path/Pretendard-Regular.ttf                         embed a Hangul-capable font
#
# Environment:
#   D2_BIN          d2 executable (default: the first `d2` on PATH)
#   D2_LAYOUT       layout engine: elk (default), tala, or dagre; TALA usually packs a wide row into fewer pixels
#   DELIVERY_WIDTH  pixel width the figure will be shown at; 0 disables the legibility gate (default 720)
#   MIN_FONT_PX     smallest acceptable rendered label size (default 12)
#   D2_PNG_PROOF    set to 1 to also write <output>.png; needs D2 v0.9.0 or a Playwright-capable older D2
#   D2_FONT_*       D2's own font variables (D2_FONT_MONO, D2_FONT_REGULAR, ...) pass straight through
set -euo pipefail

usage() {
  echo "usage: bash scripts/render_d2.sh <input.d2> <output.svg> [extra d2 flags...]" >&2
}

if [[ $# -lt 2 ]]; then
  usage
  exit 2
fi

input=$1
output=$2
shift 2
extra=("$@")
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
tokens="$script_dir/../assets/editorial-tokens.json"
d2_bin=${D2_BIN:-}
layout=${D2_LAYOUT:-elk}

if [[ ! -f "$input" ]]; then
  echo "input not found: $input" >&2
  exit 2
fi
if [[ "$output" != *.svg ]]; then
  echo "output must end in .svg: $output" >&2
  exit 2
fi
if [[ -z "$d2_bin" ]]; then
  d2_bin=$(command -v d2 || true)
fi
if [[ -z "$d2_bin" || ! -x "$d2_bin" ]]; then
  echo "D2 renderer not found; install d2 or set D2_BIN to an executable. Without D2, use the direct SVG route (references/direct-svg.md)." >&2
  exit 127
fi

"$d2_bin" fmt --check "$input"
"$d2_bin" validate "$input"
"$d2_bin" --layout "$layout" --pad 16 ${extra[@]+"${extra[@]}"} "$input" "$output"

if [[ "${D2_PNG_PROOF:-0}" == "1" ]]; then
  png="${output%.svg}.png"
  "$d2_bin" --layout "$layout" --pad 16 ${extra[@]+"${extra[@]}"} "$input" "$png"
  echo "PNG proof: $png"
fi

python3 "$script_dir/validate_svg.py" \
  --target-width "${DELIVERY_WIDTH:-720}" \
  --min-font-px "${MIN_FONT_PX:-12}" \
  --tokens "$tokens" \
  "$output"
