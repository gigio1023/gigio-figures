# Figure style for draw.io

Read `references/local/figure-principles.md` first. The values live in `assets/figure-tokens.json`; the default recipes below translate them into draw.io style strings, and `technical-figure` explains the grammar behind them. When editing an existing diagram, match its established style unless the user explicitly asks for a restyle.

`assets/figure-default-template.drawio` is a minimal working sample: ordinary components, one focal hued component, labeled data edges, and no title, legend, or footer.

## Canvas and units

- One draw.io pixel is one token unit `u` at export scale 1. Lay out a column figure within 720u of width (1080u only for a full-width page) and about 750u of height. A 1400u page placed in a 704 px column shrinks 14u labels to about 7 px.
- Set `background="#FFFFFF"` on `mxGraphModel` beside `adaptiveColors="auto"`. PNG exports bake a background either way; SVG exports are transparent unless the model carries a background.
- Export with `-b 16` for the 16u canvas margin and `-s 2` for a 2x PNG.
- Set `shadow=0` on the model and every cell. Never use `gradientColor`, `glass`, `sketch`, or 3D shapes.
- Spacing follows the 4u grid (4, 8, 12, 16, 24, 32): one-line nodes 36u tall, two-line nodes 52u, siblings 16u apart, groups 24 to 32u apart, container padding 16u. Peers in a row share a height; peers in a column share a width.

## Type

| Role | Size and weight | Color |
| --- | --- | --- |
| Node label | 14, 600 | ink `#2C2C2B` |
| Second line, role | 12.5, 400 | ink-2 `#5F5E5B` |
| Edge label | 12.5, 400 | ink-2 |
| Annotation layer | 12, 400 | ink-2 |
| Panel label such as (a) | 15, 600 | ink |
| Latin all-caps group label | 11, 600, `letter-spacing:0.06em` | ink-2 |
| Korean or mixed-case group label | 12, 600 | ink-2 |

- Labels in every script use the sans stack: `fontFamily=Pretendard, Pretendard Variable, Apple SD Gothic Neo, Noto Sans KR, Helvetica Neue, Arial, sans-serif`.
- Monospace is only for a string that is literally a code identifier: `fontFamily=JetBrains Mono, IBM Plex Mono, ui-monospace, Menlo, monospace` at weight 500. Never mix mono and Hangul in one string; put the identifier on its own line, in a span that sets the mono family and `font-weight:500`.
- draw.io has no numeric weight key. `fontStyle=1` and `&lt;b&gt;` render 700, which the tokens forbid, so set 600 with an HTML span. A two-line node label is:

```text
&lt;span style=&quot;font-weight:600&quot;&gt;Gateway&lt;/span&gt;&lt;br&gt;&lt;span style=&quot;font-size:12.5px;color:#5F5E5B&quot;&gt;policy check&lt;/span&gt;
```

- Minimum size is 12 (11 for Latin all-caps group labels). Never Light or Thin weights, never 700 or heavier, no tracking on sans labels other than the all-caps group label. All text stays horizontal.

## Color

| Token | Light | Use |
| --- | --- | --- |
| bg | `#FFFFFF` | page background, node fills, label backgrounds on the page |
| surface | `#F4F3F1` | containers, ghost fills, chips, label backgrounds inside a container |
| ink | `#2C2C2B` | text, edges, operators, junction dots |
| ink-2 | `#5F5E5B` | second lines, edge labels, annotations, ghost text, leaders |
| line | `#8E8B86` | node outlines |
| guide | `#D4D3CF` | ghost outlines, outline containers, zoom frames, ghost edges |
| blue | stroke `#2769B7`, fill `#E5F1FF`, text `#1E5BA1` | hue 1 |
| vermillion | stroke `#C55123`, fill `#FFEBE4`, text `#A63C0C` | hue 2 |
| magenta | stroke `#C673A3`, fill `#FEEAF2`, text `#943569` | hue 3 |

- One focal element or path per figure carries the 2.25 emphasis stroke and its mapped hue, or ink when no hue applies; everything else stays neutral or ghosted in place. A second hue appears only when the contrast between two meanings is itself the claim.
- Each hue keeps one meaning for the whole document, and a meaning outside the document's semantic map gets position, a label, or a glyph instead of a hue. Colored area stays under about 5 percent of the figure, and color is never the only channel.
- Text on a tint fill stays ink. Hue text colors are for short labels bound to that hue's meaning.

## Node recipes

Ordinary component:

```text
rounded=1;absoluteArcSize=1;arcSize=16;whiteSpace=wrap;html=1;
fillColor=#FFFFFF;strokeColor=#8E8B86;strokeWidth=1.25;fontColor=#2C2C2B;
fontFamily=Pretendard, Pretendard Variable, Apple SD Gothic Neo, Noto Sans KR, Helvetica Neue, Arial, sans-serif;
fontSize=14;spacing=0;spacingLeft=12;spacingRight=12;spacingTop=8;spacingBottom=8;shadow=0;
```

With `absoluteArcSize=1`, `arcSize` is the corner diameter: `arcSize=16` draws the 8u radius of a node taller than 48u, and `arcSize=12` the 6u radius of a one-line node. `spacing` adds to each `spacing*` side, so keep `spacing=0` when setting the sides.

| Kind | `arcSize` | Radius |
| --- | --- | --- |
| Cell in a grid or matrix | `rounded=0` | 0 |
| Tensor | 4 | 2u |
| Chip | 8 | 4u |
| Node up to 48u tall | 12 | 6u |
| Node taller than 48u | 16 | 8u |
| Container, zoom panel | 24 | 12u |

A radius stays at or below 0.2 of the shape's height; a rounder box reads as a button.

Variants replace keys in the ordinary recipe:

| Role | Keys |
| --- | --- |
| Ghost: context kept in place for orientation | `fillColor=#F4F3F1;strokeColor=#D4D3CF;fontColor=#5F5E5B;` |
| Hued: carries its hue's document meaning | `fillColor=#E5F1FF;strokeColor=#2769B7;` (blue), `fillColor=#FFEBE4;strokeColor=#C55123;` (vermillion), `fillColor=#FEEAF2;strokeColor=#C673A3;` (magenta) |
| Focus: the figure's subject | `strokeWidth=2.25;` with the mapped hue or ink when no hue applies |
| Exists only at run time | `dashed=1;dashPattern=5 4;fixDash=1;` |
| Chip: tag, dtype, token | `arcSize=8;fillColor=#F4F3F1;strokeColor=none;fontSize=12.5;fontColor=#5F5E5B;spacingLeft=8;spacingRight=8;`; on a surface container use `fillColor=#FFFFFF;` |
| Container: named module scope, repetition, or condition | `arcSize=24;container=1;collapsible=0;pointerEvents=0;fillColor=#F4F3F1;strokeColor=none;align=left;verticalAlign=top;spacingLeft=16;spacingRight=16;fontSize=12;fontColor=#5F5E5B;` |
| Container outline: scope over a hued or busy area, or nested in a surface container | container keys with `fillColor=none;strokeColor=#D4D3CF;strokeWidth=1;` |
| Zoom panel: detail of an element shown elsewhere | `arcSize=24;fillColor=none;strokeColor=#D4D3CF;strokeWidth=1;dashed=1;dashPattern=5 4;fixDash=1;`, named with the element's identifier, joined to it by a dotted leader |
| Operator ⊕ | `shape=orEllipse;perimeter=ellipsePerimeter;aspect=fixed;html=1;fillColor=#FFFFFF;strokeColor=#2C2C2B;strokeWidth=1.5;` at 18 by 18; `shape=sumEllipse` draws ⊗ |
| Junction dot | `ellipse;perimeter=ellipsePerimeter;aspect=fixed;html=1;fillColor=#2C2C2B;strokeColor=none;` at 5 by 5 on a 1.5 edge and 7 by 7 on a 2.25 edge, filled with its line's color |
| Annotation layer | `text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;fontSize=12;fontColor=#5F5E5B;` plus the sans stack, beside the element it names |

- Every container has a name at its top left, set in a 600 span. A `swimlane` container keeps a horizontal header (never `horizontal=0`, which sets the name vertically) and takes `swimlaneLine=0;fillColor=#F4F3F1;swimlaneFillColor=#F4F3F1;strokeColor=none;` so the header and body read as one surface.
- Arrows end at nodes, not container borders. Do not wrap a single element in a container, and do not give one container both a border and a fill.
- Use a short legend when direct labels would be ambiguous or crowded; build it from sample marks and 12u ink-2 text. A locator is a small ghosted copy of the overview with the region marked.

## Edge recipes

Data or artifact flow:

```text
edgeStyle=orthogonalEdgeStyle;rounded=1;jettySize=auto;orthogonalLoop=1;html=1;
strokeColor=#2C2C2B;strokeWidth=1.5;endArrow=open;endFill=0;endSize=9.25;startArrow=none;
fontFamily=Pretendard, Pretendard Variable, Apple SD Gothic Neo, Noto Sans KR, Helvetica Neue, Arial, sans-serif;
fontSize=12.5;fontColor=#5F5E5B;labelBackgroundColor=#FFFFFF;
```

| Relation | Keys added to the data recipe |
| --- | --- |
| Control: selection, gating, parameters | `dashed=1;dashPattern=5 4;fixDash=1;`, entering from a side other than the data path |
| Emphasis: the claim path | `strokeColor=#2769B7;strokeWidth=2.25;endSize=12;` with the hue's stroke |
| Spine: the stream the figure is about | `strokeWidth=2.25;endSize=12;` in ink |
| Ghost: context flow | `strokeColor=#D4D3CF;strokeWidth=1;endSize=7.5;` |
| Correspondence or zoom leader | `strokeColor=#5F5E5B;strokeWidth=1;dashed=1;dashPattern=1 2;fixDash=1;endArrow=none;` |

- Edges (1.5, ink) stay darker than node outlines (1.25, line) so mechanism reads before boxes. The only widths are 1.0, 1.25, 1.5, and 2.25.
- Start with a small set of relation encodings, usually three or fewer; add one only when the same question needs it and the render keeps it distinguishable. Dashes mean control on lines and run-time-only on outlines; dots mean correspondence. Show unimportance with the ghost recipe, never with a dash.
- draw.io multiplies `dashPattern` by `strokeWidth` unless `fixDash=1` is set, so always set it.
- Arrowheads: draw.io's `open` marker is `endSize + strokeWidth` long, and the token length is `4 + 4.5 × stroke`, so `endSize = 4 + 3.5 × stroke`: 7.5 on 1.0, 9.25 on 1.5, 12 on 2.25. The marker takes its edge's color. Its half width is 0.5 of its length against the token's 0.4, the closest draw.io marker. One arrowhead style per document.
- Edge labels name what passes, the operation, or the condition. Place them on a straight segment about 6u from the line and 8u from an arrowhead (`verticalAlign=bottom` with an offset of `y=-6` on a horizontal segment), and set `labelBackgroundColor` to the fill behind the label: `#FFFFFF` on the page, `#F4F3F1` inside a container.
- Junction dots mark only real splits and merges. For a fan-out, run the trunk into a junction dot and branch from it; a crossing without a dot is not a connection.

## Dark rendering

With `adaptiveColors="auto"`, draw.io derives every dark color itself: it inverts each explicit color and rotates the hue back, which flips lightness and keeps the hue. The same happens to colors inside HTML labels. Measured on draw.io Desktop 31.4.5 with `--theme dark`:

| Token | Light | draw.io dark | Token dark |
| --- | --- | --- | --- |
| bg | `#FFFFFF` | `#121212` | `#191919` |
| surface | `#F4F3F1` | `#1D1C1A` | `#252524` |
| ink | `#2C2C2B` | `#C7C7C6` | `#F0EFED` |
| ink-2 | `#5F5E5B` | `#9D9C99` | `#C4C2BD` |
| line | `#8E8B86` | `#787571` | `#7D7A75` |
| guide | `#D4D3CF` | `#393835` | `#5F5E59` |
| blue stroke, fill, text | `#2769B7`, `#E5F1FF`, `#1E5BA1` | `#69A2E5`, `#17212D`, `#78ACE8` | `#75AEF5`, `#1C2F46`, `#92C1FD` |
| vermillion stroke, fill, text | `#C55123`, `#FFEBE4`, `#A63C0C` | `#E6835B`, `#2E1D17`, `#F59970` | `#ED845B`, `#432519`, `#F9A782` |
| magenta stroke, fill, text | `#C673A3`, `#FEEAF2`, `#943569` | `#AD668F`, `#2D1C23`, `#E997C4` | `#B26191`, `#412331`, `#F1ACCC` |

- Preserved: hue identity, lightness order, text contrast (ink about 11:1 and ink-2 about 6.8:1 on the dark background), the separation of a hue's stroke from its tint, and label backgrounds, which invert with the fill behind them.
- Not preserved: the exact dark tokens. The background is `#121212`, ink is dimmer, and tint fills are darker. Guide drops to about 1.6:1 against the background, below the APCA Lc 15 floor, so ghost outlines, outline containers, zoom frames, and ghost edges nearly vanish.
- For a figure that will be read in dark, write guide colors as `light-dark(#D4D3CF,#5F5E59)`. `light-dark(light,dark)` works in fill, stroke, font, and label background colors and in the model `background` on 31.4.5, and pins both values. To reproduce the dark tokens exactly, pin every color, including the model background, bg-colored fills, and label backgrounds; a pinned `#191919` page behind auto-inverted `#121212` fills shows the nodes as dark patches.
- `--theme light` and `--theme dark` render one theme. With the default `--theme auto`, PNG and PDF render light, and SVG carries both palettes through CSS `light-dark()` with `color-scheme: light dark`; whether an embedding page passes its theme to an SVG in an `<img>` depends on the host, so check once per host.

## Backend limits

- Keep `adaptiveColors="auto"` and the model `background`. The draw.io CLI layout rewrite drops both, and `scripts/apply_auto_layout.py` restores them.
- Exports use the fonts installed on the exporting machine. Without Pretendard the stack falls to Apple SD Gothic Neo on macOS or Noto Sans KR elsewhere, and label widths shift, so check fit on the final machine. The OpenType `ss06` feature cannot be set.
- There is no key for line caps or joins. Arrowheads keep miter joins, and a dotted line uses `1 2` square dots because a `0 3` pattern with butt caps draws nothing.
- HTML labels use a line height of 1.2, so a two-line node's baseline gap is about 16u rather than the 19u token; keep the 52u two-line height.
- A literal `\n` does not create a line break. Use `&lt;br&gt;` with `html=1`, or `&#xa;`.
