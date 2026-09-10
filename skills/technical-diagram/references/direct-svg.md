# Direct SVG route

Author the SVG by hand when the figure is inlined into an HTML document that supplies its own fonts and color tokens, when an existing SVG must be edited, when the user asks for SVG source, when the composition needs geometry D2 cannot express, or when no D2 renderer is installed. The route produces the same editorial look as the D2 route from the same tokens; it trades automatic layout for exact control over width, corridors, and typography.

## Contents

- Canvas and delivery size
- Structure
- Layout recipe
- Tokens
- Fonts and Korean labels
- Embedding modes
- Verification

## Canvas and delivery size

Set the `viewBox` width to the delivery width, 720 by default, and let the height follow the content. A figure that is wider than its column is scaled down by the host, so a 14px label in a 1200px canvas arrives at about 8px; the validator's `--target-width` check fails the figure before a reader sees that. When content does not fit, stack rows vertically, shorten role-first labels, or split by abstraction level. Never reduce type below 12px rendered, and never widen the canvas past the delivery width to make an overfull row fit.

Keep `width` and `height` attributes equal to the `viewBox` for a standalone file so hosts without CSS sizing show the figure at its designed scale.

## Structure

Start from `assets/direct-svg-template.svg`. It fixes the parts that are easy to get wrong and leaves the semantic content to you:

- Root `<svg>` with `xmlns`, a finite `viewBox`, `role="img"`, and `aria-labelledby` pointing at a `<title>` and `<desc>`. These are accessibility metadata, not a visible title; the no-title rule is about visible text.
- `<defs>` holding two open arrowhead markers (`arrow-ink`, `arrow-muted`) with `markerUnits="userSpaceOnUse"` so arrowheads do not scale with stroke width and `orient="auto-start-reverse"` so a return path can reuse them.
- One `<style>` block with classes for the two text voices (`entity`, `edge`, `note`, `ko`), the box fills (`box`, `box-accent`, `box-muted`), and the connection strokes (`flow`, `flow-secondary`). Colors and sizes in that block are the token values; change them only by changing the tokens.
- One `<g id="role">` per semantic node containing its `<rect>` and `<text>`, and one `<g id="source-to-target">` per connection containing its `<path>` and label. Stable ids let the validator, reviewers, and later edits address parts by role.
- Text as `<text>` and `<tspan>`, never outlined paths. SVG does not wrap text; give every line its own `<tspan>` with an explicit `x`, keep labels to two lines, and use `text-anchor="middle"` on box labels so centering survives label edits.

Keep gradients, filters, shadows, textures, decorative dots, and any title or footer area out of the file.

## Layout recipe

Estimate before you place. A monospace Latin glyph advances about 0.6em, a sans-serif glyph about 0.52em, and a Hangul or CJK glyph a full 1em. For a 14px label, `APPLICATION SERVER` is therefore about 151px wide and needs a box at least 176px wide to keep 12px of inner padding.

- Margins: 24px from the canvas edge to the first box.
- Boxes: 64px tall in a row, corner radius 16, at least 16px of inner padding on each side of the longest label line; inner sub-boxes use radius 4.
- Corridors: the gap between two connected boxes is at least the edge label width plus 16px; place the label above the line for a forward path and below it for a return path so neither needs an opaque background.
- Paths: straight `H` or `V` segments with one bend at most; end the path one pixel before the target border so the marker tip touches the border instead of entering the box.
- Secondary paths: dashed `2 2`, gray stroke, gray marker, in their own corridor rather than stacked on the dominant path.
- Rows: when a row would exceed the delivery width, break it into two rows and route down, then across.

Do the arithmetic in the source as you write coordinates; the validator estimates label widths the same way and warns when a label leaves less than 8px inside its box.

## Tokens

`assets/editorial-tokens.json` is the single source of the values below. The template's style block repeats them for portability.

| Role | Value |
| --- | --- |
| Ink (text, primary stroke, arrowheads) | `#0D0D0D` |
| Canvas and ordinary box fill | `#FFFFFF` |
| Muted fill, line, text | `#EEEEEE`, `#CCCCCC`, `#929591` |
| Accent (one role or the dominant path) | fill `#EAF1FE`, stroke `#2E4780` |
| Hot (at most one element) | fill `#FFEDDE`, stroke `#CC6F47`, text `#804126` |
| Stroke width | 1.2 |
| Corner radius | 16 for nodes, 4 for inner boxes |
| Arrowhead | open, unfilled |

Green is reserved for a real two-system comparison. Emphasis comes from the accent fill or the single hot element, never from a thicker stroke or a larger label.

## Fonts and Korean labels

Latin technical labels use the mono stack (`"IBM Plex Mono", Menlo, monospace`); human commentary uses the sans stack (`Inter, "Helvetica Neue", Helvetica, Arial, sans-serif`). Korean labels use the Korean sans stack (`Pretendard, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif`) through the `ko` class; monospace Korean faces are rare and mixing a mono Latin word into a sans Korean label reads as two voices. A bilingual figure keeps one voice per label and the same geometry across language variants where the estimated widths allow it.

A standalone SVG cannot embed these fonts, so the viewer's installed fonts draw the text and the stacks above list fallbacks that exist on macOS, Windows, and Linux. A figure inlined into a single-file HTML document inherits the document's embedded fonts, which is the main reason inline figures take this route.

## Embedding modes

Inline in HTML: omit the XML declaration, keep the single root `<svg>` with its `viewBox`, and let the document's CSS size it. When the host document defines color variables, write `fill="var(--c-ink, #0D0D0D)"` so the figure follows the document theme and still renders standalone; the validator checks the fallback value against the palette. Captions, figure numbers, and the stated takeaway belong to the document, not to the SVG.

Standalone file (Notion upload, README, Slack): keep `width` and `height`, keep colors as hex, and remember that Notion shows the image at column width with no width control, so the figure must already read at 720px.

## Verification

Run the validator with the delivery width and the tokens:

```bash
python3 scripts/validate_svg.py --target-width 720 --tokens assets/editorial-tokens.json output.svg
```

Then look at the rendered figure. On macOS without an SVG viewer, QuickLook writes a PNG proof:

```bash
qlmanage -t -s 1440 -o <dir> output.svg
```

The proof appears as `<dir>/output.svg.png`. Parsing cannot detect clipped text, a wrong font fallback, an edge crossing a label, or an element that should not exist, so compare the finished ids and labels against the required semantic inventory and apply `references/review.md`, including its negative-space audit.
