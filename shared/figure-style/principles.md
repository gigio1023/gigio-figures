# Figure principles

These rules hold for every figure backend in this repository. `technical-figure` carries the full grammar, planning method, and review; this file is the shared core that the other skills vendor.

## Reader and content

- The default reader is a domain peer who lacks only this project's context. Knowledge is not their bottleneck; the specific structure is. A deliberately simplified register is drawn only on explicit request.
- One figure answers one question with one claim. The claim becomes the caption's first sentence; the figure shows it as marks, not only as words.
- Exact names first: label a component by the name it carries in code, configuration, or the running system; add a role on a second line only when the name does not say what it does.
- Edges carry mechanism: what passes, the operation, or the condition. Delete edge labels that repeat the target's name or narrate time.
- The canvas holds names and mechanism. Counts, sample sizes, timestamps, provenance, and hedges belong in the caption or prose unless the question is about them.
- When a figure is hard to read: organize, then split into a series, then move to prose only what answers a different question. Never abstract names into roles, delete mechanism, or shrink type to make a figure fit.
- In a document with several figures, plan them together: one semantic map for hues and line styles, one direction per kind of figure, one glyph per recurring object.

## Visual language

- Emphasis budget: one focal element or path per figure carries a hue and the emphasis stroke; context stays neutral or ghosted in place; frames are lightest.
- A hue has one meaning for the whole document. Neutral means "not the subject".
- One line style per relation, at most three relations per figure: solid for data or artifact flow, dashed for control, dotted without an arrowhead for correspondence.
- Draw the mechanism's structure: counts, direction, repetition, recurrence, and selection become marks and positions.
- Comparisons share one scaffold; only differences carry emphasis.
- One typographic voice: a single sans family for labels in every script, monospace only for literal code identifiers, TeX-rendered math.
- Backgrounds are baked, never transparent; light and dark renders come from the same source.
- Never in the canvas: titles, footers, counts, hedges, logos, emoji, decorative icons, 3D, shadows, gradients, bullet lists inside boxes, or decoration to fill space. Zoom panels, small locators, legends of at most three items, and a gray annotation layer are allowed when they carry meaning.

## Values

The values (font stacks, sizes, colors for both themes, strokes, arrowheads, radii, spacing, limits) live in `tokens.json`. Each skill vendors a copy as `assets/figure-tokens.json`; resynchronize with `python3 scripts/sync_figure_style.py` instead of editing a copy.

## Identity

The design system is independent. It does not reproduce any company's brand assets or proprietary typefaces, and figures made with it must not claim affiliation with any publisher whose work informed it.
