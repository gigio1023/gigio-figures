---
name: eli5-figure
description: >
  Draw one deliberately simple figure, on explicit request only ("ELI5", "쉽게 그려줘", "비전문가용", "explain like I'm five", or the skill named): a single everyday analogy, at most five concepts, reduced from the exact technical-figure figure, with the literal mapping and the analogy's limits kept in the surrounding prose rather than in the figure. NOT the default for any diagram request; figures and charts for domain readers use technical-figure, native .drawio files use drawio-diagram.
---

# ELI5 Figure

Draw one figure that a smart adult outside the field understands in ten seconds, without making it say anything false. This is the deliberately simple register; the exact register is `technical-figure`, and this skill reduces that exact structure rather than drawing from the source material directly. Nothing is written above or below the figure: the analogy sentence, the literal mapping, and the limits of the analogy live in the surrounding prose or in the response.

## Quick path

1. Have the exact structure first. If a `technical-figure` figure or an equivalent inventory of exact nodes and labeled edges exists, start from it; otherwise write that inventory down before simplifying. Reducing from the exact structure is what keeps the simple figure true.
2. Form the reader brief and the reduction record in the contract below. Choose one analogy and hold it.
3. Read `references/eli5-principles.md`. The default authoring pipeline is vendored from `technical-figure`: a small graph for `scripts/layout.mjs` (see `assets/eli5-example.json`), or a hand-authored SVG that follows `references/svg-contract.md`. Check dependencies with `bash scripts/setup.sh --check`, reusing a current successful check. Run setup without `--check` only when dependency installation is authorized, then lay out and render:

   ```bash
   node scripts/layout.mjs <file>.json -o <file>.svg
   node scripts/render.mjs <file>.svg
   ```

   `render.mjs` writes light and dark PNGs, a portable SVG, and a lint report; lint errors must be zero. An existing project renderer or another suitable tool may be used with editable source and equivalent checks for text, geometry, contrast, and exact relationships. Preserve the document's established style; otherwise use the bundled tokens.

4. Inspect the render at delivery width in both themes and apply `references/review.md`. Light is the default; deliver the theme required by the host or document. Deliver the figure, and put the analogy sentence, the literal mapping, the analogy's limit, and the reduction record in the prose beside it or in the response.

## Reader brief and reduction record

```text
reader: <who, outside the field; default: a smart adult with no background in this domain>
question: <the one thing they must grasp>
analogy: <one everyday situation the reader has lived through, chosen before drawing>
exact_source: <the technical-figure figure or inventory this reduces>
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
- Plain words in the boxes. Keep an exact name only when the reader will meet it again (a product they use, a file they will be asked to open); it is then the second line.
- Every arrow says what moves or what happens. No unlabeled arrows; this reader has no schema to fill them.
- No magic box. A node whose action the reader cannot picture ("processing", "logic", "the system") is not allowed; say what it does in the analogy's terms.
- Keep numbers, dates, and qualifiers when they encode the mechanism or prevent a false reading. If expiry answers the reader's question, a label such as `discard after 5 minutes` belongs on the relevant action. Put supporting context in prose; preserve an unconfirmed state when omitting it would imply a completed action.
- Simplify language, never facts. A merged node may hide detail; it may not assert what the exact figure contradicts. Where the analogy would imply a false relation, draw the real relation at that point and state the break in prose.
- Nothing above or below the figure: no caption, analogy sentence, mapping table, footer, "in reality" panel, or legend inside the SVG. Those belong to the document.
- The shared visual language is the default: the figure-style tokens in both themes, one focal hue on the part the reader must grasp, neutral ink for the rest. No icons, clip art, emoji, or drawings of people; the analogy is carried by words and structure.

## Verification

Before finishing, confirm in this order:

1. **Render:** at the delivery width every label is legible, nothing is clipped, no arrow crosses unrelated content, and the geometry is what the source intends.
2. **Truth:** every relation drawn exists in the exact structure; nothing merged or hidden contradicts the exact figure; the reduction record lists every merge and omission.
3. **Ten-second test:** a reader with no domain background can say, from the figure alone, what happens and to whom. When the stakes justify it, give the figure alone to a reader with none of this context, a person or an isolated worker, and ask what happens and to whom.
4. **Negative space:** nothing is written above or below the figure, and every element changes the reader's understanding.

## Output

Lead with the artifact. Then give, as prose: the analogy in one sentence, the literal mapping (simple label to exact name), where the analogy breaks, and the reduction record. Report the delivery width and theme, the lint summary, and whether the render was inspected. Keep the source beside the render.

## Reference router

| Need | Read or run |
| --- | --- |
| ELI5 rules, their sources, anti-patterns, and the worked example | `references/eli5-principles.md` |
| Truth, reader, render, and negative-space audit | `references/review.md` |
| Shared content and appearance invariants | `references/figure-principles.md` |
| SVG classes, math, arrowheads, render outputs | `references/svg-contract.md` |
| Layout from a small graph | execute `scripts/layout.mjs` |
| Render in both themes with the lint | execute `scripts/render.mjs` |
| Worked example with its reduction record | `assets/eli5-example.json` and the example section of `references/eli5-principles.md` |

The full planning and grammar references are available in `technical-figure` when installed. This package's vendored principles, review, pipeline, and tokens support standalone use.

## Gotchas

- The tempting shortcut is to draw from the source material and "simplify as you go". That produces true-looking figures with invented relations. Start from the exact inventory and record the reduction.
- "Simply", "just", "basically", "magic" in labels or prose talk down; delete them.
- A vocabulary constraint (only common words) makes a figure cryptic. Constrain the number of concepts, not the words; "sticky note" beats "the box that remembers what you asked".
- The analogy sentence wants to become a title above the figure and the mapping wants to become a footer. Both are prose.
- Do not set a plain-language label in the mono voice; an exact name the reader will meet again is the only mono text, on its own second line.
