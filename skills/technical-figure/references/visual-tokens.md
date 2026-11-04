# Visual tokens

`assets/figure-tokens.json` is the authority for the bundled pipeline's design values; the renderer, the lint, and the chart module read it. This file explains the choices so they can be adapted without breaking what they protect. For authorized maintenance of this design system, change `shared/figure-style/tokens.json` and resynchronize rather than editing a vendored copy. An ordinary figure task can use an established project style through its authoring route without modifying the installed skill.

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
- Math x-height is matched to Pretendard's (1ex = 0.53 of the label size) and then scaled by 0.94, and math never sets below 13u. TeX glyphs have hairline strokes, so math keeps full ink where a sans label of the same class steps down to ink-2, and the renderer adds a 0.012em outline in the glyph color. Without these, math read thinner and fainter than the labels beside it, especially on a container's surface fill.

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
| magenta | `#9E4F7E` | `#D37FAF` | hue 3 |

- Each hue has a stroke, a tint fill, and a text color per theme in the JSON. Text on a tint fill stays ink; hue-colored text is for short labels only.
- Blue and vermillion are the most separable pair under simulated color-vision deficiency. Magenta stands apart from the context gray `line` in lightness, darker than it in light and lighter in dark, and from blue and vermillion in hue. Red against green and blue against teal nearly merge for some readers, which is why they are not in the set.
- Colored area stays below about 5 percent of the figure. Measured published figures sit between about 1 and 3.5 percent; a figure above that reads as decoration.
- Categorical series in charts use the theme's `categorical` list in order: blue, vermillion, reddish purple, orange, sky blue, bluish green, then ink. The hues are Okabe-Ito's with lightness adjusted per theme, and each slot holds the same hue in both themes, so a series keeps its color identity when the theme changes. More than seven categories means grouping or splitting, not more colors.
- Sequential values use one hue's lightness ramp; darker is larger in light theme and lighter is larger in dark theme.
- No alpha tints. When overlap itself must show, use a 0.15 to 0.25 alpha fill with an opaque stroke.
- Contrast: text 4.5:1 against what is actually under it, lines that carry meaning 3:1, guides at least APCA Lc 15.

## Palette separation

Every token palette meets three floors. `scripts/palette_audit.py` uses them as its defaults and exits 1 when a palette misses one.

- **Normal vision: OKLab ΔE×100 of at least 10 for every pair.** CSS Color 4 treats an OKLab difference of 0.02 as just noticeable when it maps colors into a gamut; 10 is five of those steps, because thin lines and small dots need several times the difference that large patches need.
- **Simulated protan and deutan vision: ΔE×100 of at least 8 for every pair.** The simulation is Machado, Oliveira, and Fernandes (2009) at full severity, the worst case; anomalous trichromats, the larger share of readers with color-vision deficiency, see more difference than it shows.
- **Mark contrast: 3:1 against the theme background** for every hue stroke, categorical slot, and `line`, the `graphic_contrast_min` token from WCAG 2.2 SC 1.4.11.

The floors hold for all pairs, since scatter and small multiples can put any two colors side by side; the categorical order then places the best-separated pairs next to each other for lines in order and stacked bars. The context gray stays recessive: in both themes every hue stroke has more contrast against the background than `line`, so a context series never reads louder than a hued one.

The 2026-11-04 change brought the palettes to these floors with lightness steps before hue changes:

- **Magenta.** It had nearly the lightness of `line`, so under deutan the two were 3.9 apart in light and 3.8 in dark. The stroke moved in lightness only, away from the gray: `#C673A3` to `#9E4F7E` in light, `#B26191` to `#D37FAF` in dark. Its fill and text colors are unchanged.
- **Light categorical.** `#E69F00` (2.25:1) and `#56B4E9` (2.31:1) were below 3:1 on white; they are now `#C68800` and `#3D9CDC` at 3.0:1. An orange dark enough for 3:1 falls within deutan reach of `#D55E00` unless it turns brown, so vermillion darkened slightly to `#C94F00`. `#009E73` and `#CC79A7`, neighbors 7.6 apart under deutan, are no longer adjacent; `#009E73` became `#2D986E`, and `#CC79A7` is unchanged.
- **Dark categorical.** Seven pairs were below a floor, down to 9.7 under normal vision, 7.0 under protan, and 5.4 under deutan; lightness steps cleared them: `#3FBF93` to `#57D39E`, `#E08FC0` to `#D785B4`, `#E69F00` to `#F0A91E`, `#9CCBF0` to `#9FCEF3`.
- **Order.** Reddish purple moved to the third slot and bluish green to the sixth, the order whose weakest adjacent pair is strongest across both themes.

Minimum ΔE×100 as of 2026-11-04, all pairs and, for the ordered lists, adjacent pairs:

| Palette | Normal | Protan | Deutan | Lowest contrast |
|---|---|---|---|---|
| light semantic | 14.0 | 9.3 | 10.1 | 3.39:1, `line` |
| dark semantic | 12.6 | 9.8 | 10.3 | 4.11:1, `line` |
| light categorical | 12.9; adjacent 16.7 | 8.4; adjacent 16.1 | 8.7; adjacent 15.6 | 3.01:1 |
| dark categorical | 10.7; adjacent 12.4 | 8.7; adjacent 11.8 | 8.3; adjacent 10.8 | 6.62:1 |

Blue and vermillion remain the farthest semantic pair under every vision (light: 29.2 normal, 22.0 protan, 26.8 deutan). Rerun `python3 scripts/palette_audit.py` after any token change; `--colors` with `--bg` audits a custom palette, and `--all-pairs` lists every distance.

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

Values were set from direct measurement and render tests during a 2026-09 study: Notion's CSS color tokens in both themes, published figure palettes and chroma areas (Anthropic, Transformer Circuits, Google DeepMind, DeepSeek, Qwen, MiMo, Meta), font metrics read from the font files, WCAG 2.2 SC 1.4.3 and 1.4.11, APCA, Okabe-Ito, Paul Tol, IBM Carbon, Material 3, Primer, and Atlassian spacing guidance, TikZ's arrow-tip length rule, and 2x renders of candidate stacks at a 708 px display width. The separation floors follow CSS Color 4's OKLab gamut-mapping JND of 0.02, Ottosson's OKLab (2020), the color-vision-deficiency simulation of Machado, Oliveira, and Fernandes (2009), and Stone, Szafir, and Setlur (2014) on the larger differences that thin marks need.
