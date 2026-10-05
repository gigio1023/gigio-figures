# Figure principles

The content and accessibility requirements hold for every figure backend in this repository. The visual language below is the default; an explicit request or established project style can replace its presentation choices. `technical-figure` carries the full grammar, planning method, and review; this file is the shared core that the other skills vendor.

## Reader and content

- The default reader is a domain peer who lacks only this project's context. Knowledge is not their bottleneck; the specific structure is. A deliberately simplified register is drawn only on explicit request.
- One figure answers one question with one claim. The claim becomes the caption's first sentence; the figure shows it as marks, not only as words.
- Exact names first: label a component by the name it carries in code, configuration, or the running system; add a role on a second line only when the name does not say what it does.
- Edges carry mechanism: what passes, the operation, or the condition. Delete edge labels that repeat the target's name or narrate time.
- The canvas holds the answer and its necessary conditions. Keep numbers, dates, sample sizes, and qualifiers when they encode the mechanism, distinguish compared cases, or prevent a false reading. Equations, dimensions, thresholds, axis values, repetition counts, and state labels may stay. Put supporting context and provenance in the caption or prose; preserve qualifications needed to keep the claim accurate.
- When a figure is hard to read: organize, then split into a series, then move to prose only what answers a different question. Never abstract names into roles, delete mechanism, or shrink type to make a figure fit.
- In a document with several figures, plan them together: one semantic map for hues and line styles, one direction per kind of figure, one glyph per recurring object.

## Visual language

- Emphasis budget: one focal element or path per figure carries the emphasis stroke and its mapped hue, or ink when no hue applies; context stays neutral or ghosted in place; frames are lightest.
- A hue has one meaning for the whole document. Neutral means "not the subject".
- Use distinct, consistent encodings for relations. Start with a small set, usually three or fewer: solid for data or artifact flow, dashed for control, dotted without an arrowhead for correspondence.
- Draw the mechanism's structure: counts, direction, repetition, recurrence, and selection become marks and positions.
- Comparisons share one scaffold; differences carry emphasis. Preserve the conditions that make each comparison valid.
- One typographic voice: a single sans family for labels in every script, monospace only for literal code identifiers, TeX-rendered math.
- Light is the default theme; deliver the theme required by the host or document. Bake backgrounds into raster exports and check light and dark legibility from the same source. Color is never the only channel; also use labels, positions, shapes, or line styles.
- The caption carries titles, source lines, and supporting context. Omit decorative logos, emoji, shadows, and filler. Numeric or qualified labels follow the content rule above. Zoom panels, locators, short legends, and adjacent annotations stay when they explain the answer; a color ramp or spatial depth may encode data or geometry.

## Values

The values (font stacks, sizes, colors for both themes, strokes, arrowheads, radii, spacing, limits) live in `tokens.json`. Each skill vendors a copy as `assets/figure-tokens.json`; resynchronize with `python3 scripts/sync_figure_style.py` instead of editing a copy.

## Identity

The design system is independent. It does not reproduce any company's brand assets or proprietary typefaces, and figures made with it must not claim affiliation with any publisher whose work informed it.
