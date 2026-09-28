# Visual tokens

`assets/figure-tokens.json` is the authority for every value; the renderer, the lint, and the chart module read it. This file explains the choices so they can be adapted without breaking what they protect. In a repository that vendors this skill, change `shared/figure-style/tokens.json` and resynchronize rather than editing a copy.

## Unit and canvas

The unit `u` is one SVG user unit in a 720u-wide viewBox. Notion's default column and most blog columns are about 704 to 720 CSS px, so 1u is about 1 CSS px where the figure is read, and the 2x PNG has 2 px per u. Designing in the unit the reader sees is what makes the size rules meaningful; a figure authored at 1440 wide and shrunk to a column halves every label.

- 720u for a normal column, 1080u only for a full-width page; a 1080u figure placed in a normal column shrinks its 14u labels to about 9 px.
- Height budget about 750 CSS px so figure and caption share a screen.

## Typography

| Role | Value | Reason |
|---|---|---|
| Latin and Korean labels | Pretendard 400 and 600, `ss06` on | One family covers both scripts with matched weight and height (Hangul advance 0.864 em, x-height 0.530 em); `ss06` separates `I`, `l`, `1`. OFL |
| Code identifiers | JetBrains Mono 500 | Signals a literal string; used only when the whole string is code |
| Math | MathJax glyph paths from TeX | Matches TeX-rendered prose, needs no installed math font, cannot fall back to a wrong glyph |
| Node label | 14u, 600 | Legible at a 704 px column; most readable published figures measured about 2 percent of figure width or more |
| Second line, edge label | 12.5u, 400, ink-2 | One step down in weight and color, not only size |
| Annotation | 12u, 400, ink-2 | The token minimum |
| Latin all-caps micro label | 11u, 600, tracked +0.06em | The only text allowed below 12u; Hangul has no caps, so Korean group labels use 12u 600 |

- Never Light or Thin weights, never 700 or heavier, no tracking on sans labels.
- Two-line nodes use a 19u baseline gap.
- Estimates for planning: Hangul 0.864 em, Latin sans about 0.55 em, mono 0.6 em. Final widths come from measurement; character-count estimates were off by up to a third on mixed labels.
- Math x-height is matched to the label (1ex = 0.49 of the label size) and then scaled by 0.92 so capitals in math do not tower over label capitals.

What published figures use, for orientation: Anthropic's research figures use its brand sans or Roboto with Roboto Mono; Google DeepMind uses Google Sans; OpenAI uses OpenAI Sans on the web; many lab paper figures fall back to DejaVu Sans (matplotlib default) or Calibri with Cambria Math (PowerPoint). Brand typefaces are not redistributable and are not used here.

## Color

Neutrals carry the structure; three hues carry meaning.

| Token | Light | Dark | Use |
|---|---|---|---|
| bg | `#FFFFFF` | `#191919` | baked background, equal to Notion's page backgrounds |
| surface | `#F4F3F1` | `#252524` | containers, ghost fills, bands |
| ink | `#2C2C2B` | `#F0EFED` | text, edges, spine (Notion's own text colors) |
| ink-2 | `#5F5E5B` | `#C4C2BD` | second lines, annotations, ghost text |
| line | `#8E8B86` | `#7D7A75` | node outlines |
| guide | `#D4D3CF` | `#5F5E59` | dividers, axes, frames |
| blue | `#2769B7` | `#75AEF5` | hue 1 |
| vermillion | `#C55123` | `#ED845B` | hue 2 |
| magenta | `#C673A3` | `#B26191` | hue 3 |

- Each hue has a stroke, a tint fill, and a text color per theme in the JSON. Text on a tint fill stays ink; hue-colored text is for short labels only.
- Blue and vermillion are the most separable pair under simulated color-vision deficiency; magenta differs in lightness so it stays apart from both. Red against green and blue against teal nearly merge for some readers, which is why they are not in the set.
- Colored area stays below about 5 percent of the figure. Measured published figures sit between about 1 and 3.5 percent; a figure above that reads as decoration.
- Categorical series in charts use the theme's `categorical` list in order (Okabe-Ito based, adjusted for dark). More than seven categories means grouping or splitting, not more colors.
- Sequential values use one hue's lightness ramp; darker is larger in light theme and lighter is larger in dark theme.
- No alpha tints. When overlap itself must show, use a 0.15 to 0.25 alpha fill with an opaque stroke.
- Contrast: text 4.5:1 against what is actually under it, lines that carry meaning 3:1, guides at least APCA Lc 15.

## Stroke, arrowheads, dashes

| Role | Width |
|---|---|
| Guide, divider, leader, ghost edge | 1.0u |
| Node outline | 1.25u, line color |
| Edge | 1.5u, ink |
| Spine, emphasis path, focus outline | 2.25u |

- Below 1.0u a line blurs when a 2x PNG is shown at column width.
- Open chevron arrowheads with round joins, the edge's own width and color, length 4 + 4.5w and half width 0.4 of the length (about 10.75u on a 1.5u edge). One arrowhead style per document. Arrowhead color always matches its line; the renderer draws them per path.
- Dashed `5 4` is control on lines and run-time-only on box outlines; dotted `0 3` with round caps is correspondence. Unimportance is shown with gray, never with a dash.
- Junction dots at real splits and merges, radius 1.6 times the stroke.

## Shape and spacing

- Radius: cells 0, tensors 2, chips 4, nodes 6 (8 when taller than 48u), containers 12. A node's radius stays at or below 0.2 of its height; round pills read as buttons.
- Spacing on a 4u grid: 4, 8, 12, 16, 24, 32. Node padding 12 × 8, one-line node 36u tall, two-line 52u. Siblings 16u apart, groups 24 to 32u, container padding 16u, canvas margin 16u. Edge labels 6u from their line and 8u from an arrowhead.
- Peers in a column share a width; peers in a row share a height.

## Theme policy

- Always bake the background. A transparent PNG cannot satisfy text contrast on both a white and a near-black page; the best single gray reaches only about 4.2:1 on both, and published transparent figures lose arrows and labels on dark pages.
- Light is the default. Render light and dark from the same source and check both; deliver dark only when the host surface is dark, the document's existing figures are dark, or the user asks.
- The portable SVG carries both palettes under `prefers-color-scheme`. Chromium applies the embedding page's color scheme to an SVG in an `<img>`, but a given host may not pass its theme through; check once per host before relying on it.

## Sources

Values were set from direct measurement and render tests during a 2026-09 study: Notion's CSS color tokens in both themes, published figure palettes and chroma areas (Anthropic, Transformer Circuits, Google DeepMind, DeepSeek, Qwen, MiMo, Meta), font metrics read from the font files, WCAG 2.2 SC 1.4.3 and 1.4.11, APCA, Okabe-Ito, Paul Tol, IBM Carbon, Material 3, Primer, and Atlassian spacing guidance, TikZ's arrow-tip length rule, and 2x renders of candidate stacks at a 708 px display width.
