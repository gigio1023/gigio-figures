---
name: eli5-figure
description: >
  Use only when the user explicitly asks for a deliberately simple figure: "ELI5", "쉽게 그려줘", "비전문가용", "경영진용 그림", "explain like I'm five", "one-picture version", or names eli5-figure. Produces one small SVG figure in the shared editorial style that carries a single everyday analogy and at most five concepts, declared as a reduction of the exact figure it stands in for, with the literal mapping and the analogy's limits stated in the surrounding prose rather than inside the figure. NOT the default for any diagram request: architecture, process, and system figures for domain readers use technical-diagram; native .drawio files use drawio-diagram; measured data uses data-chart.
---

# ELI5 Figure

Draw one figure that a smart adult outside the field understands in ten seconds, without making it say anything false. This is the deliberately simple register; the exact register is `technical-diagram`, and this skill reduces that exact structure rather than drawing from the source material directly. Nothing is written above or below the figure: the analogy sentence, the literal mapping, and the limits of the analogy live in the surrounding prose or in the response.

## Quick path

1. Have the exact structure first. If a `technical-diagram` figure or an equivalent inventory of exact nodes and labeled edges exists, start from it; otherwise write that inventory down before simplifying. Reducing from the exact structure is what keeps the simple figure true.
2. Form the reader brief and the reduction record in the contract below. Choose one analogy and hold it.
3. Read `references/eli5-principles.md`. Author on the same routes as `technical-diagram`: D2 with `assets/eli5-theme.d2` (the editorial theme in the sans voice) copied beside the source, or direct SVG from `assets/direct-svg-template.svg` with the `entity` and `edge` classes switched to the sans stack from `assets/editorial-tokens.json`. Format with `d2 fmt <file>.d2`, then render and gate:

   ```bash
   bash scripts/render_d2.sh <file>.d2 <file>.svg
   python3 scripts/validate_svg.py --target-width 720 --tokens assets/editorial-tokens.json <file>.svg
   ```

4. Inspect the render, not only the source (`D2_PNG_PROOF=1` on D2 v0.9.0 or newer, or `qlmanage -t -s 1440 -o <dir> <file>.svg` on macOS). Apply `references/review.md`. Deliver the figure, and put the analogy sentence, the literal mapping, the analogy's limit, and the reduction record in the prose beside it or in the response.

## Reader brief and reduction record

```text
reader: <who, outside the field; default: a smart adult with no background in this domain>
question: <the one thing they must grasp>
analogy: <one everyday situation the reader has lived through, chosen before drawing>
exact_source: <the technical-diagram figure or inventory this reduces>
kept: [exact names the reader will meet again, shown as a second line]
merged: [{from: [exact nodes], to: <one simple node>}]
hidden: [nodes and edges left out, each with the reason it does not change the reader's answer]
analogy_breaks: <where the analogy stops being true>
delivery_width: <px; 720 unless stated>
```

The reduction record is provenance, not figure content. It goes in the response or the document's prose so that a reader who moves from the simple figure to the exact one can see what was merged and what was hidden. Infer the brief from the request and material; ask only when the exact structure is missing and cannot be reconstructed.

## Content rules

- One analogy, chosen first, held throughout. Two analogies in one figure are two figures.
- At most five concepts, one path, at most one branch. If the exact structure has two mechanisms, draw one and name the other in prose.
- Plain words in the boxes, in the sans voice. Keep an exact name only when the reader will meet it again (a product they use, a file they will be asked to open); it is then the second line.
- Every arrow says what moves or what happens. No unlabeled arrows; this reader has no schema to fill them.
- No magic box. A node whose action the reader cannot picture ("processing", "logic", "the system") is not allowed; say what it does in the analogy's terms.
- Simplify language, never facts. A merged node may hide detail; it may not assert what the exact figure contradicts. Where the analogy would imply a false relation, draw the real relation at that point and state the break in prose.
- Nothing above or below the figure: no caption, analogy sentence, mapping table, footer, "in reality" panel, or legend inside the SVG. Those belong to the document.
- The editorial visual language is unchanged: white canvas, near-black ink, one accent, soft corners, thin open arrowheads. No icons, clip art, emoji, or drawings of people; the analogy is carried by words and structure.

## Verification

Before finishing, confirm in this order:

1. **Render:** at the delivery width every label is legible, nothing is clipped, no arrow crosses unrelated content, and the geometry is what the source intends.
2. **Truth:** every relation drawn exists in the exact structure; nothing merged or hidden contradicts the exact figure; the reduction record lists every merge and omission.
3. **Ten-second test:** a reader with no domain background can say, from the figure alone, what happens and to whom. Give the figure alone to a fresh-context reader or subagent when the stakes justify it.
4. **Negative space:** nothing is written above or below the figure, and every element changes the reader's understanding.

## Output

Lead with the artifact. Then give, as prose: the analogy in one sentence, the literal mapping (simple label to exact name), where the analogy breaks, and the reduction record. Report the route, the delivery width, the validation result with the smallest rendered label size, and whether the render was inspected. Keep the source beside the render.

## Reference router

| Need | Read or run |
| --- | --- |
| ELI5 rules, their sources, anti-patterns, and the worked example | `references/eli5-principles.md` |
| Truth, reader, render, and negative-space audit | `references/review.md` |
| Shared content and appearance invariants | `references/editorial-principles.md` |
| D2 syntax, layout engines, delivery width, and direct SVG recipe | the D2 authoring and direct SVG references inside the installed `technical-diagram` skill; the theme, tokens, template, and scripts vendored here are the same files |
| Render with the legibility gate (`D2_LAYOUT`, `DELIVERY_WIDTH`, `D2_PNG_PROOF`) | execute `scripts/render_d2.sh` |
| Standalone SVG check | execute `scripts/validate_svg.py` |
| Worked example with its reduction record | `assets/eli5-example.d2` and the example section of `references/eli5-principles.md` |

## Gotchas

- The tempting shortcut is to draw from the source material and "simplify as you go". That produces true-looking figures with invented relations. Start from the exact inventory and record the reduction.
- "Simply", "just", "basically", "magic" in labels or prose talk down; delete them.
- A vocabulary constraint (only common words) makes a figure cryptic. Constrain the number of concepts, not the words; "sticky note" beats "the box that remembers what you asked".
- The analogy sentence wants to become a title above the figure and the mapping wants to become a footer. Both are prose.
- The D2 theme here drops the mono font so plain-language labels read as prose; do not mix a mono technical label into a sans figure except as the second-line exact name.
- D2 renders shape labels bold and connection labels italic unless told otherwise; the theme sets both off, and a hand-written class must repeat `bold: false` and `italic: false`.
