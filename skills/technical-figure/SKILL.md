---
name: technical-figure
description: >
  Plan and draw figures for technical documents, posts, and papers: architecture and mechanism diagrams, process flows, vector and math geometry, grids and tensor shapes, method or model comparisons, and charts of measured data, rendered as themed PNG and SVG for a domain peer. Plans a document's figure set and visual grammar first when it needs several figures and defaults to a lint-checked pipeline with real fonts and TeX math. Use for any figure, diagram, chart, plot, or infographic request that does not name a native format ("그림 그려줘", "다이어그램", "시각화", "차트"). NOT for native .drawio files (drawio-diagram), Mermaid-only output (mermaid-diagrams), interactive dashboards (insight-dashboard), image generation, or a deliberately simplified figure for readers outside the field (eli5-figure, explicit request only).
---

# Technical Figure

Produce figures a domain peer can verify and that look deliberate: one claim per figure, the mechanism drawn as structure rather than written as text, one visual grammar across the whole document, and a render that holds up at the width and theme where it will be read. Crude figures rarely come from the drawing tool. They come from a missing plan: every box drawn with the same weight, one accent color meaning something different in each figure, and comparisons that redraw the shared structure until the difference disappears. The bundled pipeline measures what it draws. Use an established project style or another suitable authoring route when it serves the artifact; preserve the content, accessibility, and rendered review contract below.

## Quick path

1. **Scope.** A document, a section with several figures, or a request to redo a document's figures starts with the figure plan in `references/planning.md`: claim inventory, figure budget, semantic map, and a thumbnail storyboard. A single standalone figure starts at step 2 and still borrows the document's semantic map when one exists.
2. **FigureSpec.** Record the spec, using `assets/templates/figure-spec.json` or the project's equivalent: the reader's question, the claim in one sentence (it becomes the caption's first sentence), the exact names and relations the peer needs, the one focal element, and what goes to the caption instead of the canvas.
3. **Form.** Choose the form from the claim's shape with `references/form-catalog.md`, not from the request's noun. Compare alternative framings when the form is uncertain or a first render fails the claim test. Select the strongest supported framing within the task; ask only when the choice depends on a consequential missing preference.
4. **Grammar and tokens.** Use `references/grammar.md` and `assets/figure-tokens.json` as the default visual language, explained in `references/visual-tokens.md`. Preserve an established document grammar when present; keep encodings consistent and legible.
5. **Author.** Choose a route below. For the bundled SVG renderer, follow `references/svg-contract.md`: classes and `data-*` attributes carry semantics; the renderer supplies colors, fonts, and arrowheads. Other routes keep their editable source and use their own rendering contract.
6. **Render and lint.** For the bundled SVG route, check dependencies with `bash scripts/setup.sh --check`, reusing a current successful check. Run setup without `--check` only when dependency installation is authorized, then `node scripts/render.mjs <figure>.svg`. It writes light and dark PNGs, a portable SVG, and a lint report, judged at a 704 px column unless `--width` says otherwise (`--width 1080` for a full-width page). Fix every lint error.
7. **Review.** Open both PNGs and judge them at the delivery width with `references/review.md`: the claim is visible without the caption, the focal element reads first, every spec element is present and nothing unspecified was added. Continue until the required checks pass within the task's time and resource budget. When a defect repeats or an edit makes no progress, diagnose the cause and change the layout, form, or tool before another attempt; see the revision rules in `references/review.md`.
8. **Deliver.** For a figure set, render the contact sheet (`node scripts/sheet.mjs`, `--columns 2` to compare framings or old and new side by side) and check the grammar holds across figures before delivering.

Run scripts from the skill directory; they resolve assets relative to themselves.

## Reader and content contract

- **The reader is a domain peer.** Knowledge is not their bottleneck; this project's structure is. Assume the field's vocabulary and supply the exact names, mechanisms, and relationships they could not reconstruct without the figure. A deliberately simplified register is `eli5-figure`'s job and only on explicit request.
- **Exact names first.** Label a component by the name it carries in code, configuration, or the running system; add a role on a second line only when the name does not say what it does.
- **Edges carry mechanism.** An edge label names what passes (a tensor, a value, a dtype), the operation the edge performs, or its condition. Delete labels that repeat the target's name or narrate time (`then`, `after training`, `inputs`).
- **The canvas holds the answer and its necessary conditions.** Keep numbers, dates, sample sizes, and qualifiers when they encode the mechanism, distinguish the compared cases, or prevent a false reading. Equations, dimensions, thresholds, axis values, repetition counts, and state labels may stay. Put supporting context and provenance in the caption or prose; preserve any qualification needed to keep the claim accurate.
- **Too much to read is fixed by organizing, then splitting, then moving to prose** only what answers a different question. Never abstract names into roles or delete mechanism to make a figure fit, and never shrink type below the token minimum.

## Visual grammar in brief

These defaults establish a coherent style; `references/grammar.md` holds the full set with sources. Adapt presentation to the document while preserving the meaning of every encoding.

- **Emphasis budget.** One focal element or path per figure carries the emphasis stroke, in its hue when the semantic map gives its meaning one, otherwise in ink. Everything else is neutral ink or a ghost that keeps its position so the reader can orient. Visual weight has three layers: the claim path, the context structure, and the frame (containers, guides, axes), lightest last.
- **One meaning per hue, fixed for the document.** The semantic map from the plan assigns each hue (blue, vermillion, magenta) one meaning, such as "read" or "edited weights", and every figure, chart, and colored word in the prose follows it. A figure that needs a hue for a new meaning adds it to the map or uses layout instead.
- **Distinct relation encodings.** Aim for a small set of relation styles, usually three or fewer. Solid for data or artifact flow, dashed for control (selection, gating, parameters), dotted without an arrowhead for correspondence and zoom leaders. A dashed outline on a box means it exists only at run time.
- **Draw the mechanism's structure.** Counts, direction, repetition, recurrence, and branching become spatial structure: four streams are four lines, a top-k choice shows selected and unselected experts, a residual stream is a spine that components read from and write back to through ⊕.
- **Compare on one scaffold.** Variants share coordinates; the shared structure is drawn once or ghosted, and only the difference carries emphasis. Parallel panels keep the same layout, order, and rows.
- **One typographic voice.** Pretendard for Latin and Korean labels, JetBrains Mono only for strings that literally appear in code, and TeX through `data-tex` for every symbol with a hat, sub-, or superscript.
- **Keep the canvas focused.** The caption carries the title and source line. Omit decorative logos, emoji, shadows, and filler; preserve numeric or qualified labels under the content contract. Zoom panels, locators, short legends, and adjacent annotations stay when they explain the mechanism. A visual effect that encodes data, such as a sequential color ramp or spatial depth in geometry, is content.

## Routes

| Figure | Route | Read |
| --- | --- | --- |
| Box-and-arrow mechanism, architecture, pipeline, more than about 15 nodes or routing-heavy | `node scripts/layout.mjs graph.json -o figure.svg` (elkjs layered layout with ports and junction dots), then refine the SVG by hand if needed | `references/routes/mechanism.md` |
| Mechanism with a spine, zoom panels, or at most about 15 nodes on a grid | hand-authored SVG on the 4u grid with computed coordinates; size boxes with `node scripts/measure.mjs` | `references/routes/mechanism.md` |
| Vector, projection, subspace, or other math geometry | coordinates computed from the actual vectors, written as SVG | `references/routes/geometry.md` |
| Token × layer grids, matrices, tensor shapes, bit fields | coordinates from arithmetic (cell, gap, index) | `references/routes/grid-tensor.md` |
| Measured data | `scripts/figure_mpl.py` with the same tokens | `references/routes/chart.md` |

The bundled SVG routes end in `scripts/render.mjs`. The chart module renders and checks its own outputs as described in `references/routes/chart.md`. These are default routes. An existing project renderer, Graphviz, Mermaid, or another suitable tool may be used when it preserves exact labels, math, relationships, editable source, and the requested artifact. Check its real exports for font metrics, clipping, contrast, and geometry at the delivery width. Image-generated decoration cannot establish factual labels, equations, values, or relationships; keep those source-defined and verifiable.

## Theme and delivery

- Canvas 720u wide for a normal column (1080u for a full-width page), exported at 2x with the background baked in. A transparent PNG with dark lines disappears on a dark page.
- Light is the default theme. Every figure is rendered in both themes and must hold up in each; the context picks the one delivered. A dark host surface, a document whose existing figures are dark, or an explicit request means dark; otherwise deliver light and keep the dark render beside it. When only some figures of an existing document are redone, deliver the theme the rest of its figures use so one page does not mix themes. The portable SVG switches palettes with `prefers-color-scheme`; offer it only after checking once that the host passes its theme to embedded SVG.
- For a column figure, target about 750 CSS px at the delivery width so the figure and its caption fit on one screen. Rearrange or split when height hurts reading; a different delivery medium may need a different composition. The bundled SVG renderer still enforces its documented height limit.

## Verification

1. **Lint:** for the bundled SVG route, `render.mjs` runs `scripts/lint.mjs` with real fonts and bounding boxes. Errors (overlap, overflow, text below the minimum size, Unicode math, appearance in the source, contrast, arrow collisions, excessive height) must be zero. Warnings need a reason to stay. Other routes need equivalent geometry, text, contrast, and content checks; report what ran and any unavailable check. The bundled source-format checks are not requirements for unrelated formats.
2. **Look:** open both PNGs. Judge the render, not the source: legible at the delivery width, focal element first, nothing clipped, lines never crossing text.
3. **Ledger:** check every node, edge, and label in the FigureSpec against the render one by one (present, correct direction, correct style), then look separately for anything drawn that the spec does not contain. "Unclear" is a failure.
4. **Alternatives:** when choosing between framings, compare the renders against the claim and review rubric. A second comparison with the order swapped is useful when an automated judgment is unstable; an absolute score cannot replace specific findings.
5. **Set:** for a document, the contact sheet shows every figure in order at the delivery width in the delivered theme; each hue, line style, and direction must mean the same thing everywhere.
6. **Recurring defects:** consult relevant entries in `references/defect-memory.md`. Keep task findings in existing project notes only within the project's recording authority. Update reusable skill guidance only when skill maintenance is requested; a figure correction does not authorize writing to an installed skill or persistent memory.

## Output

Lead with the artifacts: PNG for the delivered theme, the other theme, the source, and the portable SVG when offered. Then report the route, delivery width and theme, the lint summary, whether the render was visually inspected, the caption draft (claim first, then the reading key for any encoding new to the document, then deferred counts and conditions), and any fact moved from the canvas to prose.

## Setup

The pipeline needs Node.js 20 or newer and a Chromium-family browser (Google Chrome, Chromium, Edge, or a Playwright browser build). `scripts/setup.sh` installs pinned npm packages and the OFL fonts into a user cache (`$TECHNICAL_FIGURE_CACHE`, default `~/.cache/technical-figure`) and is the only step that uses the network. It never installs a browser; when none is found it prints the command to do so. Charts need `uv` (`uv run --with matplotlib`). Font embedding in the portable SVG uses `uvx` with fonttools when available.

## Reference router

| Need | Read or run |
| --- | --- |
| Figure plan for a document, FigureSpec, acceptance tests, caption split | `references/planning.md` |
| Which form fits a claim; archetypes for ML and systems figures | `references/form-catalog.md` |
| Emphasis, hue map, line styles, containers, comparison, annotation, banned elements | `references/grammar.md` |
| Font, size, color, stroke, radius, spacing, theme values and why | `references/visual-tokens.md`, `assets/figure-tokens.json` |
| SVG classes, math, arrowheads, render outputs | `references/svg-contract.md` |
| Route details | `references/routes/*.md` |
| Lint ids, visual review, ledger protocol, comparison rubric, contact sheet | `references/review.md` |
| Recurring defects and their repairs | `references/defect-memory.md` |
| Public figures worth studying and what each teaches | `references/exemplars.md` |
| Vocabulary for the user | `references/glossary.md` |
| Starter files | `assets/templates/`, rendered examples in `assets/examples/` |

## Gotchas

- A clean render of uniform boxes is still a crude figure. Switching layout engines removes overlaps but not sameness; the fix is the emphasis budget and drawing the mechanism, not another tool.
- The accent drifts. Each figure picks "the thing it points at" and the same blue ends up meaning ten things across a document. Assign hues in the plan and check the contact sheet.
- Comparisons redraw everything. Three full stacks side by side with a small difference in each hide that difference; draw the scaffold once or ghost it and emphasize only what changes.
- The simplest figure becomes the house exemplar and pulls the whole set toward labeled boxes. Choose the most mechanism-rich figure as the reference for a set.
- Width estimated from character counts is wrong by up to a third for mixed Korean and Latin labels. Let `layout.mjs` and `lint.mjs` measure with the real fonts.
- A vision model asked for a score gives unstable numbers and misses wrong connections. Check the ledger item by item and compare pairs instead.
- Unicode imitations of math (`r̂ᵀx`) misalign in every sans font. Use `data-tex`.
