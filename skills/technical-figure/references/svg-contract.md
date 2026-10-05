# SVG authoring contract

The bundled SVG routes use this source contract: a semantic SVG that carries structure and classes but no colors, fonts, or arrowheads. `scripts/render.mjs` applies the theme from `assets/figure-tokens.json`, typesets math, draws arrowheads, rasterizes with real fonts, and runs `scripts/lint.mjs`. Keeping appearance out of this source lets one figure render in light and dark and lets the lint check token use. The chart module and other authoring tools have their own source contracts; this file does not require converting them to this format.

## Root

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420" data-figure="technical-figure">
  ...
</svg>
```

- Width is 720u for a normal column and 1080u only for a full-width page. Height is whatever the content needs within the height budget.
- Do not add a background rect, `<style>`, `fill=`, `stroke=`, `font-family=`, or `marker-end=`. The renderer adds them. A `style` attribute is allowed only for `opacity` on a context element that the grammar calls for.
- Put elements in reading order. Group a node's shape and its labels in one `<g>` so the lint can tell which text belongs to which box. Group an edge path with its label the same way: the lint measures a label's distance to the line in its own `<g>` and does not count that line as crossing it.

## Classes

Shapes:

| Class | Mark | Default appearance |
| --- | --- | --- |
| `box` | `rect` for a component, module, artifact | bg fill, `line` outline 1.25u, radius 6 (8 when the shorter side is 52u or more), at most 0.2 of the shorter side |
| `box ghost` | context element that stays for orientation | bg fill, guide outline; its labels are ink-2 without a text modifier |
| `box blue`, `box vermillion`, `box magenta` | element that carries the document meaning mapped to that hue | hue tint fill, hue outline |
| `box focus` | the figure's subject; with a hue class it takes the hue | ink outline 2.25u, or hue outline 2.25u |
| `box runtime` | exists only at run time, not persisted | dashed outline |
| `chip` | small label box, token, dtype tag | bg fill, guide outline 1.0u, radius 4 |
| `tensor` | `rect` drawn to a matrix or tensor's proportions; takes hue, `focus`, and `ghost` like `box` | box appearance, radius 2 |
| `container` | named group or module scope; its name is a `t` text (a module name) or a `micro` text (a Latin group label) at the top left inside the 16u padding | surface fill, no outline, radius 12 |
| `container outline` | scope drawn on a hued or busy area | guide outline 1.0u, no fill |
| `zoom` | detail panel for an element shown elsewhere | guide outline 1.0u dashed, no fill |
| `op` | `circle` for ⊕, ⊗, ⊖ operators; `data-op="plus"` (default), `"times"`, or `"minus"` picks the sign the renderer draws; takes a hue class and `runtime` | bg fill, ink outline and sign 1.5u, r 9; a hue colors outline and sign; `runtime` dashes the outline |
| `cell` | grid, matrix, vector cell | bg fill, guide outline 1.0u, radius 0 |
| `cell on` with a hue class | selected or active cell | hue stroke color as fill |
| `cell tint` with a hue class | cell in a highlighted region | hue tint fill, hue outline |
| `band` | background band marking a region of an axis | surface fill, no outline |
| `spine` | `path` or `line` for a stream the figure is about (residual stream, bus) | ink, 2.25u |
| `edge` | `path` or `line` for data or artifact flow | ink, 1.5u |
| `edge control` | selection, gating, parameter influence | ink, 1.5u, dashed |
| `edge` with a hue class | a relation bound to that hue's meaning, at its own weight (`edge control vermillion` stays 1.5u dashed) | hue |
| `edge emph` | the claim path; usually with a hue class | 2.25u |
| `edge ghost` | context flow | guide, 1.0u |
| `leader` | correspondence or zoom leader, no arrowhead | ink-2, 1.0u, dotted |
| `guide` | axis, divider, layer rule | guide, 1.0u |
| `mark` | right-angle mark, tick | ink-2, 1.0u, solid |
| `dot` | `circle` junction where a line really splits or merges; add its line's `spine`, `emph` and hue, or `ghost` | same color as its line, radius 1.6 times its stroke |

Text (`<text>` elements; one class from the first group, optional modifiers):

| Class | Role | Size and weight |
| --- | --- | --- |
| `t` | node or panel label | 14u, 600, ink |
| `t2` | second line, role, dtype | 12.5u, 400, ink-2 |
| `tl` | edge label | 12.5u, 400, ink-2 |
| `ta` | annotation layer beside the figure content | 12u, 400, ink-2 |
| `tp` | panel label such as (a), (b) | 15u, 600, ink |
| `micro` | Latin all-caps group label | 11u, 600, ink-2, tracked |
| modifier `mono` | the whole string is a literal code identifier | JetBrains Mono 500 |
| modifier `blue`, `vermillion`, `magenta` | text bound to that hue's meaning | hue text color |
| modifier `ghost` | label of a ghost element | ink-2 |

- `text-anchor` and `dominant-baseline` are allowed attributes. Use `dominant-baseline="central"` for single labels centered in a box. On a `data-tex` text, `central` centers the math's ink on y, so subscripts and primes do not pull it low.
- `mono` never mixes with Hangul or spaces in one string. Split into two `<text>` elements, or keep the identifier on its own line.

## Math

Write TeX in a `data-tex` attribute on a `<text>` element. Keep the element's text content as a plain fallback.

```svg
<text class="t" x="360" y="120" text-anchor="middle" data-tex="W_O">W_O</text>
<text class="tl" x="300" y="210" data-tex="\hat r^\top x">r^T x</text>
```

The renderer replaces the element with MathJax glyph paths at the same anchor, sized so the math x-height matches the label's (scaled by 0.94, never below 13u), in full ink unless the element is `ghost` or hued, with a slight outline that thickens the hairline TeX glyphs. Unicode combining marks and modifier letters (`r̂`, `ᵀ`, `⁽ˡ⁾`) are lint failures in any text; use `data-tex` instead.

## Arrowheads

Add `data-arrow="end"`, `data-arrow="start"`, or `data-arrow="both"` to an `edge`, `spine`, or `emph` path. The renderer draws an open chevron at the path end, oriented along the last segment, with the path's own stroke width and color, length `4 + 4.5w` and half width `0.4` of the length. The path should end exactly on the target boundary; the renderer shortens the stroke so the line does not poke through the chevron tip.

## Identity for review

Give every element that the FigureSpec names a `data-id` equal to its spec id: nodes on the `<g>`, edges on the path. The ledger review and the lint's missing-element check use these ids.

## Render outputs

`node scripts/render.mjs figure.svg` writes, beside the source:

| File | Content |
| --- | --- |
| `figure.light.png`, `figure.dark.png` | 2x PNG with the theme background baked in |
| `figure.portable.svg` | self-contained SVG: both palettes under `prefers-color-scheme`, fonts subset and embedded when fonttools is available, math as paths |
| `figure.lint.json` | lint findings with severity, check id, element ids, and measured values |

Flags: `--theme light|dark|both` (default both), `--width N` (the delivery column in CSS px; default `units.delivery_width_css_px`, 704, whatever the viewBox width; a 1080u full-width figure passes `--width 1080`), `--no-portable`, `--strict` (warnings fail), `--spec figure-spec.json` (report spec ids with no `data-id` as `missing-element`).
