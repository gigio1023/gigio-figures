# Review

Review in order: deterministic lint, a visual look at both renders, a ledger check against the FigureSpec, and for a document a contact sheet. The lint catches geometry that eyes and vision models miss; eyes catch sameness, weak hierarchy, and a wrong claim that no lint can see.

## Lint

`scripts/render.mjs` runs `scripts/lint.mjs` and writes `<stem>.lint.json`; run `node scripts/lint.mjs figure.svg` alone after small edits. It renders the source with the real fonts and measures real bounding boxes, because width estimates from character counts miss overlaps.

Errors must be zero before anyone looks at the figure. The check id is in parentheses as it appears in the report:

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

Warnings need a stated reason to stay: ink within the 16u canvas margin (`margin`), height over the one-screen budget, 670 CSS px at the delivery width so the caption still fits (`height-budget`), any edge crossing (`edge-crossing`), more than three bends in an edge (`edge-bends`), more than three relation styles (`relation-styles`), more than one hue among focal elements (`focus-hues`), colored area above about 5 percent (`color-area`), an edge label far from its line (`label-far`), duplicate `data-id`s (`duplicate-id`).

## Look

Open the delivered-theme PNG at its display width (a 1440 px PNG shown at about 704 px), then the other theme. Answer each question yes or no; a no is a defect to fix.

Purpose and form

- Can the claim be stated in one sentence, and does the caption's first sentence state it?
- With the caption covered, is the claim's key relation visible as marks?
- Does the form fit the claim's shape (`form-catalog.md`)?
- Would removing any element leave the claim intact? (If yes, remove it. An equation that implements the claimed step is mechanism and stays.)

Hierarchy

- Is the most salient element the claim's subject?
- Are there three weight layers: claim path, context, frame, with the frame lightest?
- Is there one entry point and one reading direction, matching the document's convention?

Encoding and notation

- Does every hue, dash, and glyph mean what the semantic map says?
- Is each relation drawn with one line style, and are there at most three?
- Are data flow and control flow different?
- Are fan-out, exclusive choice, and loops drawn differently?
- Are counts, directions, repetition, and recurrence drawn as structure rather than written?
- Is the key distinction encoded by position or shape, not only by a label?
- Does the figure still work in grayscale?

Grouping and text

- Is every visible group a real set, and is every container named?
- Is each label closer to its element than to anything else?
- Do edges end on nodes, not on container borders?
- Are corresponding elements in parallel panels on the same rows or columns?
- Are names exact and identical to the prose?
- Is every text horizontal, inside its box with margin, and free of repeated names?
- Are counts, dates, hedges, and configuration lists absent from the canvas?

Load

- Does the figure and its caption fit on one screen?
- Are there at most about five node kinds and five edge kinds?
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

When choosing between two framings or between a revision and its predecessor, compare them item by item and ask which is better on each; ask twice with the order swapped and treat a flip as a tie. Never assign absolute scores.

| Item | Which figure... | Veto |
|---|---|---|
| Claim | shows the claim within five seconds? | flow direction contradicting the claim |
| Difference | lets the reader point at the difference between options? | unconnected boxes side by side |
| Hierarchy | is read focal element first? | accents in two or more places |
| Reading path | can be followed in one direction? | tangled routing |
| Consistency | matches sibling figures' line styles and hue meanings? | a relation drawn in a style the map reserves for another |
| Density | stays readable without dropping content? | sentences in the canvas |
| Defaults | shows fewer generic defaults (all-caps eyebrows, neon on black, glow, emoji, identical cards with shadows, badges on unordered items, text under 11 px)? | two or more present |

## Revision limits

- At most three revision rounds per figure. A round is a render reviewed against the spec and the look questions; layout trials before the first full review do not count. Revise the spec or the source, never patch pixels.
- When the same failure appears twice, change approach: split the figure, change the form, or move content to prose.
- Version renders (`figure-v1`, `figure-v2`) so comparisons use real files.

## Contact sheet

For a document, render every figure in reading order at the delivery width:

```bash
node scripts/sheet.mjs fig1.light.png fig2.light.png ... --width 704 --theme light -o sheet.png
node scripts/sheet.mjs old.png new.png --columns 2 --width 704 -o compare.png
```

Check across the sheet: each hue and line style means the same thing everywhere; model depth and pipelines run in the same directions; the same object is drawn with the same glyph; overviews appear once at full size and later only as locators; type sizes match; no figure towers over the others. Review the sheet in the delivered theme and once in the other.
