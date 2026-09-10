# gigio-figures

Portable figure skills for coding agents. They share one restrained editorial design system while keeping semantic authoring, native draw.io compatibility, and measured-data charts in separate workflows.

| Skill | Use it for | Default artifact |
| --- | --- | --- |
| [`technical-diagram`](skills/technical-diagram/SKILL.md) | Architecture, system maps, process flows, and box-and-arrow schematics | D2 + ELK → SVG, or direct SVG |
| [`drawio-diagram`](skills/drawio-diagram/SKILL.md) | Explicit native `.drawio` requests and existing draw.io edits | editable mxGraph XML |
| [`data-chart`](skills/data-chart/SKILL.md) | Real measurements, scales, series, and benchmark plots | matplotlib → SVG + PNG |

The routing rule is content and artifact based:

- Generic technical structure uses `technical-diagram`.
- Native draw.io format or draw.io-specific metadata uses `drawio-diagram`.
- Real numeric data on a meaningful scale uses `data-chart`.

## Install

Install through the Skills CLI. The `--agent` value selects the target harness; manual paths and restart behavior are documented for [Claude Code](.claude/INSTALL.md), [Codex](.codex/INSTALL.md), [Cursor](.cursor/INSTALL.md), and [Gemini CLI](.gemini/INSTALL.md).

```bash
npx skills add gigio1023/gigio-figures@technical-diagram --agent claude-code
npx skills add gigio1023/gigio-figures@drawio-diagram --agent claude-code
npx skills add gigio1023/gigio-figures@data-chart --agent claude-code
```

Swap `--agent` for `codex`, `cursor`, or `gemini-cli`. Each skill is standalone; install only the routes you need.

## Usage

Ask naturally. Explicit skill invocation is optional when the request clearly names the artifact or content.

```text
Draw a compact architecture diagram for this ingestion pipeline.
Create an editable .drawio version of this service map.
Plot these benchmark scores as an editorial-style bar chart.
```

## Shared editorial style

![Editorial default style sample](skills/drawio-diagram/assets/editorial-default-template.drawio.png)

The default language is white canvas, near-black ink, one accent family, soft corners, thin strokes, open arrowheads, and monospace technical labels paired with sans-serif commentary. Empty space may remain empty; titles, legends, captions, rails, badges, icons, and insets are never page filler.

`shared/editorial-style/` is the repository source of truth:

- [`tokens.json`](shared/editorial-style/tokens.json) stores canonical colors, font stacks, and geometry.
- [`principles.md`](shared/editorial-style/principles.md) stores backend-neutral content and visual invariants.
- [`provenance.md`](shared/editorial-style/provenance.md) records the measured source and identity boundary.
- `adapters/` translates the design system to D2 and draw.io.

Each skill vendors the small subset it needs so individual installation remains self-contained. Synchronize and verify those copies with:

```bash
python3 scripts/sync_editorial_style.py
python3 scripts/sync_editorial_style.py --check
```

The language was measured from 65 post-February-2025 openai.com editorial SVGs, but it is an independent implementation of general design properties. It does not include the OpenAI logo, blossom, wordmark, or OpenAI Sans; output must not claim affiliation or endorsement.

## technical-diagram

Two routes share one look. The D2 route writes a small semantic source, imports the bundled editorial classes, lets a layout engine place nodes and routes (ELK by default, TALA with `D2_LAYOUT=tala`), and emits SVG with subsetted fonts embedded. The direct SVG route starts from `assets/direct-svg-template.svg` and is used for figures inlined into styled HTML documents, for existing SVG edits, for geometry D2 cannot express, and whenever no D2 renderer is installed. Both routes deliberately avoid decorative themes, icons, legends, and spacer nodes, and both are checked for legibility at the delivery width (720px by default): a label that would render below 12px after the host scales the figure fails the check.

Requirements:

- D2 is optional; the skill does not install it silently and uses the direct SVG route without it.
- D2 v0.9.0 is the verified baseline; the whole path (wrapper, theme, TALA, Hangul font embedding) was exercised with it. `d2 fmt --check` and `d2 validate` need v0.7.0 or newer, and the PNG proof without a browser needs v0.9.0.

From `skills/technical-diagram/`:

```bash
bash scripts/render_d2.sh assets/editorial-example.d2 /tmp/editorial-example.svg
D2_PNG_PROOF=1 DELIVERY_WIDTH=1100 bash scripts/render_d2.sh assets/editorial-example.d2 /tmp/editorial-example.svg
D2_LAYOUT=tala bash scripts/render_d2.sh assets/editorial-example.d2 /tmp/editorial-example-tala.svg
python3 scripts/validate_svg.py --target-width 720 --tokens assets/editorial-tokens.json assets/direct-svg-template.svg
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Extra arguments after the output path go to `d2`, for example `--elk-nodeNodeBetweenLayers 40` to tighten a horizontal layout or `--font-mono /path/Pretendard-Regular.ttf` to embed a Hangul-capable font. The bundled example renders 1027px wide at ELK's defaults, so the first command above fails the 720px gate on purpose; the second passes at a delivery width wider than the render, and the third passes at 720px because TALA lays the same source out 647px wide.

## drawio-diagram

This route is intentionally native-format specific. It prefers bare, uncompressed `mxGraphModel` XML and explicit automatic layout for new files. Manual terminal pins and waypoints are a fallback for routes that remain ambiguous after layout.

From `skills/drawio-diagram/`:

```bash
python3 scripts/apply_auto_layout.py input.drawio laid-out.drawio horizontalFlow
python3 scripts/validate_drawio_xml.py path/to/file.drawio
python3 scripts/validate_drawio_layout.py path/to/file.drawio
python3 -m unittest discover -s scripts -p 'test_*.py'
```

The committed upstream `jgraph/drawio-mcp` digests provide offline factual lookup. Local workflow guidance wins when an older vendored agent instruction conflicts with the current skill.

## data-chart

This route uses matplotlib for reproducible charts whose numbers, scales, and series must remain truthful. The style module reads the skill-local snapshot of the shared tokens. A title or legend is added only when the surrounding artifact and direct labels cannot communicate the same information.

From `skills/data-chart/scripts/`:

```bash
uv run --with matplotlib python example_chart.py
```

SVG keeps text as text (`svg.fonttype: none`); the PNG is the visual proof render.

## Repository layout

- `shared/editorial-style/` — canonical style tokens, principles, provenance, and backend adapters
- `skills/technical-diagram/` — D2 authoring, direct SVG route and template, renderer, validator
- `skills/drawio-diagram/` — native XML guidance, references, assets, validators
- `skills/data-chart/` — chart language and matplotlib implementation
- `scripts/sync_editorial_style.py` — standalone-skill snapshot synchronization
- `.claude/`, `.codex/`, `.cursor/`, `.gemini/` — harness installation guides

## Markdown authoring

Keep each natural-language Markdown paragraph on one source line, including prose within list items and Markdown templates. Do not manually wrap prose to 80, 100, or any other column width; use editor soft wrapping for readability. Preserve paragraph boundaries, list structure, tables, fenced code, HTML, intentional hard breaks, frontmatter semantics, and literal examples. This convention does not change code or docstring line-length constraints.

The upstream vendoring script copies source bytes. After refreshing `skills/drawio-diagram/references/fetched/`, apply this paragraph convention to its Markdown prose and update `NOTICE` to identify any locally adjusted files. Preserve upstream revision and fetch metadata.

## Attribution

This repository vendors upstream files from `jgraph/drawio-mcp` under Apache-2.0 and layers local guidance on top. Exact mappings and the vendored revision are recorded in [`NOTICE`](NOTICE).
