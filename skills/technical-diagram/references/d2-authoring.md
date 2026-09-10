# D2 authoring

## Contents

- Source shape
- Layout engine, direction, and delivery width
- Style classes
- Labels and fonts
- Rendering and limits

## Source shape

Keep the semantic source small, declare the render configuration inside it, and import the bundled theme from the same directory:

```d2
vars: {
  d2-config: {
    layout-engine: elk
    pad: 16
  }
}

...@editorial-theme
direction: right

user: USER { class: entity }
gateway: GATEWAY { class: [entity; accent] }
service: SERVICE { class: entity }

user -> gateway: request { class: flow }
gateway -> service: { class: flow }
```

The `d2-config` block makes a plain `d2 input.d2 output.svg` reproduce the layout engine and padding without the wrapper script. Command-line flags and environment variables still take precedence, so the wrapper's `--layout elk --pad 16` agrees with the source rather than fighting it. Run `d2 fmt` after editing; the wrapper refuses an unformatted file.

Copy `assets/editorial-theme.d2` beside the output source before rendering. D2 imports are resolved relative to the importing file. The theme's classes style nodes and connections while unused classes remain invisible.

## Layout engine, direction, and delivery width

D2 bundles three layout engines. ELK is the default here because its strictly layered placement keeps one straight reading path. TALA, D2's own engine and open source since v0.9.0, packs the same content into fewer pixels by placing secondary exchanges beside the main path. Dagre stays selectable with `D2_LAYOUT=dagre` but offers no advantage over ELK here. Measured on the bundled four-node example with 16px padding (viewBox width × height):

| direction | dagre | ELK | TALA |
| --- | --- | --- | --- |
| right | 1019 × 220 | 1027 × 180 | 647 × 344 |
| down | 439 × 455 | 389 × 555 | 421 × 477 |

At a 720px delivery width the ELK and dagre horizontal renders scale their 12px edge labels to about 8.4px and their 14px node labels to 9.8px, so they fail the gate; every other cell passes. Tightening ELK spacing alone does not rescue a wide row: `--elk-nodeNodeBetweenLayers 40 --elk-edgeNodeBetweenLayers 24` brings 1027 down to 903, and 30 with 16 to 851.

- Keep ELK for a figure whose rows fit. Use `direction: right` for a short pipeline and `direction: down` for a hierarchy or a staged decomposition.
- When the gate fails, switch the engine first with `D2_LAYOUT=tala` (the wrapper passes it as `--layout`, which overrides the source's `d2-config`), then switch direction, then shorten labels or split. TALA is deterministic (`--tala-seeds 1,2,3` by default) and renders identical output across runs. After switching, confirm that the dominant path is still the obvious one.
- TALA writes the edge-label cutouts of its SVG mask as a semi-transparent value. That is mask luminance, not a painted color, and the validator ignores it.
- Use containers only for real ownership, runtime, trust, or deployment boundaries. Whitespace is enough for visual grouping.
- Let the engine calculate positions. Set explicit width or height only after a render shows that a highly connected node lacks usable routing surface.
- Do not use `near`, manual positions, or invisible spacer nodes to make the canvas look balanced, even though TALA would accept them.

## Style classes

Apply `entity` to technical components and combine it with one semantic class when needed:

- `accent`: every member of one actual role or the dominant path
- `muted`: inactive or contextual structure
- `hot`: at most one exceptional or risky element
- `zone`: a container that marks a real boundary
- `flow`: every ordinary directed connection
- `[flow; secondary-connection]`: return, async, or subordinate connections

D2 renders shape labels bold and connection labels italic by default. The theme sets `bold: false` on `entity` and `zone` and `italic: false` on `flow` to keep the editorial voice; a hand-written class must repeat those two lines or the figure drifts back to bold and italic.

Zero accent or hot elements is valid. Do not alternate classes for variety. Avoid built-in special themes, sketch mode, icons, and fill patterns unless the user requests them or they encode a necessary distinction.

## Labels and fonts

- Prefer a short noun phrase on each node and a 1-3 word label on an edge.
- Keep implementation choices and external dependencies in distinct nodes.
- Use explicit labels only when direction and nearby node names do not already communicate the relationship.
- Prefer plain text. Since v0.9.0 Markdown labels render as native SVG rather than `foreignObject`, but plain text still keeps labels short and portable; use Markdown only when a label needs real inline formatting.
- Quote labels that contain reserved D2 characters. Run the formatter and validator instead of guessing whether the source parses.

D2 embeds subsets of its bundled fonts in the SVG: Source Sans Pro for ordinary text and Source Code Pro for `font: mono`, the theme's technical voice. The four-node example carries about 5KB of font data, so file size is not a reason to avoid the route. Because the theme disables bold and italic, only the regular mono face is ever used; to embed a different font, point `D2_FONT_MONO` (or `--font-mono`) at a `.ttf` file. The sans flags (`--font-regular` and siblings) matter only for labels outside the theme classes.

Korean labels render without errors, but the bundled fonts have no Hangul, so the viewer's own fonts draw the glyphs unless a Hangul-capable TTF is embedded. Point `D2_FONT_MONO` at a Hangul-capable TTF such as Pretendard and D2 embeds a subset of it; measured with a repaired macOS system font, a three-node figure grew by about 9KB, and the Latin text in that figure then shares the sans voice, which is the intended look for a Korean figure. macOS system fonts such as `AppleGothic.ttf` fail D2's TTF-to-WOFF step with `checksum error in table: name` as shipped; re-saving the file with fontTools (`TTFont(src).save(dst)`) repairs the checksums and the result embeds cleanly. Pretendard itself was not exercised in the verification run. D2 sizes Hangul boxes generously regardless of the font; accept the width or shorten the label. Do not mix a mono Latin word into a sans Korean label.

## Rendering and limits

The wrapper runs the whole path:

```bash
bash scripts/render_d2.sh input.d2 output.svg [extra d2 flags...]
```

It resolves to `d2 fmt --check`, `d2 validate`, `d2 --layout $D2_LAYOUT --pad 16 [extra flags] input.d2 output.svg`, an optional PNG proof when `D2_PNG_PROOF=1`, and `scripts/validate_svg.py --target-width $DELIVERY_WIDTH --tokens assets/editorial-tokens.json output.svg`. `D2_LAYOUT` selects the engine (`elk` by default, `tala`, or `dagre`); `DELIVERY_WIDTH` defaults to 720 and `0` disables the legibility gate; `MIN_FONT_PX` defaults to 12. D2's own variables (`D2_FONT_MONO`, `D2_PAD`, and so on) pass straight through.

Known approximations, not reasons to post-process the SVG: D2 accepts integer stroke widths, so the theme uses 1 for the tokens' 1.2; its unfilled triangle is the closest portable match for the open arrowhead; `mono` is the only per-shape font choice. The output nests a second `<svg>` inside the root, carries hashed class names, and starts with an XML declaration; for inlining into HTML pass `--no-xml-tag` or strip the declaration.

Versions: the whole path above, including the wrapper, the theme, the `d2-config` block, TALA, and Hangul embedding, was exercised end to end with D2 v0.9.0 (released 2026-09-07) on 2026-09-10. `d2 fmt --check` and `d2 validate` need v0.7.0 or newer; a PNG proof without a browser needs v0.9.0, and older versions render PNG through Playwright.

Official references: https://d2lang.com/tour/style/, https://d2lang.com/tour/classes/, https://d2lang.com/tour/imports-use-cases/, https://d2lang.com/tour/layouts/, https://d2lang.com/tour/fonts/, https://d2lang.com/tour/vars/, and https://d2lang.com/tour/exports/.
