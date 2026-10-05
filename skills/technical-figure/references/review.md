# Review

Review the rendered figure with the checks its route supports, a visual look at both themes, a ledger check against the FigureSpec or equivalent inventory, and for a document a contact sheet. The lint catches geometry that eyes and vision models miss; eyes catch sameness, weak hierarchy, and a wrong claim that no lint can see.

## Lint

`scripts/render.mjs` runs `scripts/lint.mjs` and writes `<stem>.lint.json`; run `node scripts/lint.mjs figure.svg` alone after small edits. It renders the source with the real fonts and measures real bounding boxes, because width estimates from character counts miss overlaps.

The bundled SVG route must have zero lint errors before delivery. Visual inspection can help diagnose a lint failure. The source-format checks below belong to this renderer; other routes use their own format checks and equivalent text, geometry, contrast, and inventory checks. The check id is in parentheses as it appears in the report:

- text overlapping text (`text-overlap`); text crossed by an edge or spine that is not its own (`text-crossed`); text overflowing its box or chip (`text-overflow`); text or shapes clipped at the canvas edge (`outside-canvas`);
- displayed text below the minimum size at the delivery width (`text-too-small`);
- Unicode imitations of math: combining hats, modifier letters, super- and subscript characters (`unicode-math`);
- appearance in the source: fill, stroke, font attributes, `<style>`, markers, a background rect (`source-appearance`);
- external references or `foreignObject` (`external-reference`);
- text contrast below 4.5:1 against what is under it, in either theme (`contrast`);
- arrow tips closer than 10u (`arrow-tips`);
- height beyond the hard limit at the delivery width (`height-limit`);
- `mono` text containing Hangul or spaces (`mono-mixed`);
- with `--spec`, a spec id that no element carries as `data-id` (`missing-element`).

Warnings identify candidates for review, not proven defects. Keep one only with a reason grounded in the rendered figure: ink within the 16u canvas margin (`margin`), height over the one-screen budget, 670 CSS px at the delivery width so the caption still fits (`height-budget`), any edge crossing (`edge-crossing`), more than three bends in an edge (`edge-bends`), more than three relation styles (`relation-styles`), more than one hue among focal elements (`focus-hues`), colored area above about 5 percent (`color-area`), an edge label far from its line (`label-far`), duplicate `data-id`s (`duplicate-id`).

## Look

Open the delivered-theme PNG at its display width (a 1440 px PNG shown at about 704 px), then the other theme. Use the questions below to identify specific defects. Content, readability, and accessibility are requirements; the bundled style and screen-fit targets are defaults that may differ in the destination medium.

Purpose and form

- Can the claim be stated in one sentence, and does the caption's first sentence state it?
- With the caption covered, is the claim's key relation visible as marks?
- Does the form fit the claim's shape (`form-catalog.md`)?
- Would removing an element preserve the claim, its conditions, and the reader's orientation? Remove redundant content; keep mechanism, necessary qualifications, and context needed to interpret the figure.

Hierarchy

- Is the most salient element the claim's subject?
- Are there three weight layers: claim path, context, frame, with the frame lightest?
- Is there one entry point and one reading direction, matching the document's convention?

Encoding and notation

- Does every hue, dash, and glyph mean what the semantic map says?
- Are relation encodings consistent and easy to distinguish? If there are more than three, does each help answer the same question?
- Are data flow and control flow different?
- Are fan-out, exclusive choice, and loops drawn differently?
- Are direction, repetition, and recurrence visible as structure, with exact counts or conditions labeled when the marks alone would mislead?
- Is the key distinction encoded by position or shape, not only by a label?
- Does the figure still work in grayscale?

Grouping and text

- Is every visible group a real set, and is every container named?
- Is each label closer to its element than to anything else?
- Do edges end on nodes, not on container borders?
- Are corresponding elements in parallel panels on the same rows or columns?
- Are names exact and identical to the prose?
- Is every text horizontal, inside its box with margin, and free of repeated names?
- Do numbers, dates, sample sizes, and qualifiers on the canvas encode the mechanism, distinguish cases, or prevent a false reading? Is supporting context beside the figure, with no necessary qualification lost?

Load

- Does the figure fit its delivery medium at readable size, preferably with its caption on one screen for a web document?
- Can the reader distinguish every node and edge kind without excessive lookup?
- Is shared structure drawn once or ghosted in comparisons?
- Is nothing explained that a domain peer already knows?

## Ledger

Checking a figure as a whole misses wrong or missing connections, the most common defect in generated figures. Check the render against the FigureSpec one item at a time.

1. For each node in the spec: present, label exact, role (focus, context, frame) shown as specified.
2. For each edge: present, direction right, style matching its relation, label present when specified.
3. For each group: present, named, containing exactly its members.
4. Then, separately: list every node, edge, label, and group in the render that the spec does not contain, and every `forbidden_edges` relation that the render implies. Each is a defect unless the spec is updated for a reason.

When a vision model does this check, give it the spec items as yes, no, or unclear questions and a 2x crop of the relevant region for small text; treat unclear as a failure. Vision models judge figures unreliably as wholes and give unstable absolute scores, but answer item questions and pairwise comparisons far more consistently.

## Comparing alternatives

When an alternative would resolve a real uncertainty, compare the renders item by item against the claim, exact content, and delivery context. For an unstable automated judgment, swap the order and treat a flip as inconclusive. Prefer specific findings to an unsupported absolute score; do not generate alternatives just to satisfy a count.

| Item | Which figure... | Veto |
|---|---|---|
| Claim | shows the claim within five seconds? | flow direction contradicting the claim |
| Difference | lets the reader point at the difference between options? | unconnected boxes side by side |
| Hierarchy | directs attention to the claim? | competing accents obscure the intended comparison |
| Reading path | can be followed in one direction? | tangled routing |
| Consistency | matches sibling figures' line styles and hue meanings? | a relation drawn in a style the map reserves for another |
| Density | stays readable without dropping content? | essential labels or conditions are unreadable or missing |
| Presentation | makes each mark serve the question and remain legible? | decoration obscures meaning or text is unreadable at delivery size |

## Revision decisions

- Finish when the required content, rendering, and accessibility checks pass. Stop additional polishing unless a relevant defect, change, or requirement justifies it.
- When a defect repeats or an edit makes no progress, diagnose the cause before another attempt. Change layout constraints, form, or authoring tool as appropriate. Split only when it improves comprehension; move content to prose only when its meaning remains clear beside the figure.
- Work within the task's time, compute, and cost budget. If a required input, tool, or resource limit prevents completion, retain the editable source and best render, and report the unresolved check. Reaching an arbitrary revision count is not a completion or failure criterion.
- Fix the source. Change the spec only when the evidence or intended claim changes. Keep compared renders as real files when the comparison informs a decision.

## Contact sheet

For a document, render every figure in reading order at the delivery width:

```bash
node scripts/sheet.mjs fig1.light.png fig2.light.png ... --width 704 --theme light -o sheet.png
node scripts/sheet.mjs old.png new.png --columns 2 --width 704 -o compare.png
```

Check across the sheet: each hue and line style means the same thing everywhere; model depth and pipelines run in the same directions; the same object is drawn with the same glyph; overviews appear once at full size and later only as locators; type sizes match; no figure towers over the others. Review the sheet in the delivered theme and once in the other.
