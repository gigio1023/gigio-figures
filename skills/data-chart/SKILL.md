---
name: data-chart
description: >
  Use when the user wants a data chart, graph, or plot of measured data:
  line, bar, scatter, dot-plot, histogram, heatmap, or small multiples,
  produced programmatically with matplotlib and exported to PNG (SVG when
  vector is wanted). Covers chart-type selection, honest scales, and a
  clean minimal look, with an optional editorial preset for the
  blog-figure style. Trigger on "chart", "graph", "plot", and
  benchmark-score figures. NOT for flowcharts, architecture diagrams, or
  box-and-arrow figures (use technical-diagram), and NOT for interactive
  dashboards or web-embedded live charts.
---

# Data Chart

Render measured data as static charts. Two layers govern appearance: a **design floor** every chart keeps regardless of style - honest scales, one focal comparison, no chart junk - and an optional **editorial preset** (the openai.com-style tokens) for blog figures and hosts without their own style. When the requesting document or project has a house style, follow it; the floor still applies. PNG is the proof render and the default deliverable; keep the SVG alongside when the consumer wants vector.

## Routing: chart or diagram?

Decide by the figure's content, not its name:

- **Measured data** - real numbers, many points, true scales (log axes, distributions, time series) - this skill.
- **Structure** - boxes, arrows, layers, pipelines, or a few illustrative values inside a larger schematic - the sibling `technical-diagram` skill. Use `drawio-diagram` only when native draw.io format is part of the request.
- Borderline (3-8 bars): real measurements that may change → this skill (the chart regenerates from data); a decorative sketch inside a diagram → technical-diagram.

## Quick start

1. Pick the chart type from the reader's question with [`references/chart-selection.md`](references/chart-selection.md) - question → chart table, anti-patterns, and accessibility notes - before writing code.
2. Decide the style: the editorial preset below, or the embedding document's house style. For the preset, write a small script importing the style module [`scripts/editorial_mpl.py`](scripts/editorial_mpl.py): `ed.use()` → plot with family colors → `ed.mono_ticks` / `ed.axis_label` → optional `ed.header` → `ed.save(fig, stem)` (writes `stem.svg` + `stem.png`). The module reads the vendored values from [`assets/editorial-tokens.json`](assets/editorial-tokens.json); [`scripts/example_chart.py`](scripts/example_chart.py) is a working reference for a line chart and grouped bars (copy its `subplots_adjust` margins).
3. Run it. No system matplotlib is assumed - use `uv run --with matplotlib python <script>.py` (add other deps the same way). `findfont` warnings about Inter/IBM Plex Mono are expected on machines without those fonts; fallbacks carry the voice.
4. Run the pre-render checks, then **look at the PNG before finishing**: no clipped direct labels or tick text (widen margins, not the font), any required legend fits on one line, one accent focus, and no gridlines or unrequested supporting text.

## Design floor

These hold in every style, preset or house or plain matplotlib:

- One focal comparison: the emphasized series or bars carry the accent; everything else reads as context in gray or muted tones. Emphasis comes from color and placement, never thicker strokes or bigger fonts.
- Direct labels over detached legends; direct value labels on endpoints or one emphasized point only - never every point. Axis and tick text stays neutral ink.
- Honest scales: bars start at zero; a log axis carries no bars (dots instead); one y-scale per chart - two measures of different scale become two charts.
- No chart junk: no gridlines by default, no four-sided frames, no 3D, no gradients, no background tints, no decorative insets to occupy whitespace.
- Do not add a title when the embedding document already names the chart; no legend when direct labels make every series clear; never add a subtitle strip, takeaway band, source footer, badge, or inset merely to fill the canvas.

## Editorial preset (optional)

For the clean blog-figure look, read [`references/chart-language.md`](references/chart-language.md) for the full rule set (anatomy, tokens, marks, dark mode): gridless ink axes, restrained direct labels, one accent family per page, mono numerals. The look is modeled on openai.com editorial figures - geometry, palette, and typographic structure only. Never add the OpenAI logo, blossom mark, or wordmark; never label output as OpenAI-branded or imply affiliation. OpenAI Sans is proprietary - the Inter/IBM Plex Mono stacks in the style module are the approved substitutes.

## Non-negotiables

- Data values come from the user or their files - never invent or "smooth" numbers. Inspect the supplied data before asking. Preserve missing values as gaps when that representation is valid; if omission would change the requested comparison, ask about that series while preparing the supported chart parts. Disclose an omitted series rather than silently dropping it.
- Deterministic scripts: no RNG, no timestamps in output filenames.

## Pre-render checks

Catch failures as assertions before the first render instead of visual review cycles. Assert in the script where cheap, verify by inspection otherwise:

- Series align: every series shares the same x values (or lengths match the frame); no silent NaN drops - count missing values and decide gap vs omit explicitly.
- Axis ranges cover the data with room for endpoint labels; bar baselines include zero.
- Units are consistent within a series; when one subject appears in several configurations, the measurement basis (effort or mode, per attempt vs full run) is stated.
- A log axis has no bars; grouped bars past ~3 groups per category switch to a dot plot.

## Verification before claiming done

1. The script ran cleanly and wrote the renders (PNG always; SVG when vector is wanted).
2. You rendered and actually viewed the PNG at the intended display size.
3. **Cold read**: from the chart alone, a reader can state the takeaway in one sentence. A chart that passes every rule but says nothing fails here.
4. Every number in the chart traces to user-provided data.
5. Report a status with the delivery: `PASSED`, `PASSED WITH FIXES` (what was fixed and rerendered), or `BLOCKED` (which input is missing).

Once these pass, deliver the script and renders. Rerender after a label or layout correction, and after a data fix rerender every chart drawn from those numbers; do not create additional chart types or style variants merely to prolong visual review.

## Gotchas

- Endpoint direct labels sit outside the axes and clip at the figure edge; reserve margin first (`subplots_adjust(right≈0.88)`). Fix clipping with margins, never smaller fonts.
- Coral mid (`#FF9365`) fails 3:1 contrast on white in the preset - keep coral series dashed or direct-labeled, and set coral value labels in `#804126`.
- `ed.header()` draws the canvas to measure each legend label, so call it after the figure size and margins are final; late `subplots_adjust` calls shift the plot under an already-placed header.
- A log cost or price axis has no zero, so bar length carries no meaning - plot dots instead.
- Compare configurations as small multiples on one shared scale; a gap smaller than the source's own spread is not a result.
