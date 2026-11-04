# Planning figures

Plan before drawing. A figure set without a plan drifts: each figure picks its own accent, direction, and notation, and the reader relearns the grammar on every page. A figure without a claim becomes an inventory of boxes. Both failures are invisible in any single render and obvious on a contact sheet.

## Document plan

Write one plan for a document, a section with several figures, or a redo of a document's figures. Keep it in the working notes or beside the figure sources; it is not document content.

```markdown
# Figure plan: <document>

## Claims
| id | section | claim (one sentence the reader should believe after the figure) | shape | picture test | figure |
|---|---|---|---|---|---|

## Semantic map
| hue or style | meaning in this document | never used for |
|---|---|---|
| blue | ... | ... |
| vermillion | ... | ... |
| magenta | ... | ... |
| dashed line | control: selection, gating, parameters | anything else |
| dashed outline | exists only at run time | ... |
| ghost | context kept for orientation | ... |

## Conventions
- Direction: <e.g. model depth bottom to top; pipelines and time left to right; token position left to right>
- Recurring glyphs: <e.g. residual stream = vertical spine; write = arrow into ⊕; vector = cell strip>
- Names: <exact identifiers and the spelling used in prose and figures>
- Theme: <delivered theme and why>

## Storyboard
<one line per figure in reading order: id, form, what is new relative to the previous figure (one idea), transition type: zoom, build-up, parallel case, new platform>
```

Steps:

1. **Claim inventory.** List what the reader must come to believe, as sentences of the form "X does Y to Z under condition C". A heading is not a claim.
2. **Picture test.** A figure wins when the claim involves structure of three or more named things, geometry, an order with branches or loops, alternatives on the same structure, or a pattern across positions or layers. Prose or a table wins for a single fact, a number, a definition, or a configuration list. Configuration values and model cards are tables, not figures.
3. **Figure budget.** One claim per figure. Merge claims that answer the same question; split a figure that answers two. Put the overview in the main text and the zooms and derivations near the details they explain.
4. **Master figure.** Choose one platform figure early in the document, usually the system or model overview, and make later mechanism figures zooms, highlights, or build-ups of it. A reader who learned the platform once reads every later figure faster.
5. **Semantic map.** Assign each hue and line style one meaning for the whole document before drawing any figure. The bundled palette offers three hues. Prefer layout, labels, or shape before adding color; an established palette or a needed extension must keep meanings distinct in both themes and in grayscale. Charts in the document use the same map.
6. **Storyboard.** Place every planned figure as a thumbnail in reading order and name what each adds. Each transition changes one thing: zoom in, add one element, show the parallel case, or introduce a new platform. Parallel cases (three methods, two models) use the same layout.
7. **Exemplar choice.** When the set has an internal reference figure, choose the most mechanism-rich one, not the simplest.

## Figure brief

A figure whose content the request leaves open gets a short brief that the user confirms before anything is drawn. A wrong brief costs one message; a wrong figure costs a redraw, and the user judges "is this the right figure?" faster from a brief than from a FigureSpec.

**When.** The content is open when the material does not settle which components are new, which path is the main one, or what single point the figure argues: "draw our system" over a design doc with several candidate paths, or notes that never say what the work contributes. Skip the brief and its confirmation round when the request already names the components and the point, when an existing figure is being redone, or when the document plan already fixes the claim; go straight to the FigureSpec.

**Contents.** Prose or short bullets in the user's language, with every label exactly as it will appear in the figure:

1. **Components**: every element that will be drawn, in reading order and grouped by container, each with one clause on its job and a tag: `new` (what this work contributes), `existing` (reused unchanged), `external` (another team's or vendor's system), or `baseline` in a comparison.
2. **Main path**: numbered steps, each `from → to: what moves`; then the secondary flows in a sentence, saying which are control, feedback, or optional.
3. **The point**: the one claim the figure argues and where the eye lands first.
4. **Assumptions**: three to five items inferred rather than read, each with its source, such as `Cache is existing: §3.2 says it reuses the serving cache`. These are the only questions; everything else takes a default.

**Asking.** Send the brief once, with the assumptions as the questions; ask at most three, phrased as the guess plus its alternative. When every guess is well supported by the material, draw instead of waiting and deliver the figure with the assumption list so the user can correct it.

**Into the spec.** Components become `nodes`, and their tags guide `role` and hue: new parts usually carry the focus or the hue the semantic map gives to "new". The main path becomes the `edges` along it and `focus`; the point becomes `claim`; confirmed assumptions become spec facts, and unconfirmed ones go to the delivery note. After confirmation, a change of content goes into the brief first, then the spec, then the drawing.

## FigureSpec

Record the required content before authoring, using `<id>.spec.json` beside `<id>.svg` or an equivalent project inventory; `assets/templates/figure-spec.json` is the bundled template. The renderer cannot add what the spec lacks, the review checks the render against it, and `render.mjs --spec` reports any spec id that the figure does not carry as `data-id`.

| Field | Content |
|---|---|
| `question` | The one question the reader has at this point in the document |
| `claim` | The answer as one complete sentence; it becomes the caption's first sentence |
| `form` | From `form-catalog.md` |
| `comparison` | For comparisons: the targets, the action the reader performs, and juxtapose, superpose, or explicit encoding; otherwise null |
| `geometry` | `exact` when coordinates come from real values, `schematic` otherwise; schematic coordinates must not imply measured distance or angle; exact counts, dimensions, and thresholds can still be labeled |
| `example` | The concrete values an exact or illustrative figure uses, so the figure can be regenerated |
| `nodes` | `id`, exact `label`, optional `sub` (second line) or `tex`, optional `kind` (`op`, `chip`), `role` (`focus`, `context`, `frame`, `ghost`). In small multiples, give repeated elements panel-prefixed ids (`a-wo`, `b-wo`) and list the ones the ledger must check |
| `edges` | `id`, `from`, `to`, `relation` (`data`, `control`, `write`, `correspondence`), `label` when the names do not make it unambiguous |
| `groups` | real boundaries only: module scope, repetition, zoom panel, condition |
| `focus` | the one element or path that carries the emphasis |
| `hues` | the semantic-map entries this figure uses |
| `forbidden_edges` | relations a reader might assume and that do not exist |
| `canvas` | what is drawn |
| `caption` | `claim`, `reading_key` for any encoding new to the document, `deferred` supporting context, conditions applying to the whole figure, and provenance |

## Alternatives

Compare alternative framings when the claim, form, or reading path remains uncertain. Vary the structure that could resolve the uncertainty, then select by the review rubric at the delivery width. Record a choice that affects the rest of the set in the plan. Ask the user only when a consequential preference cannot be inferred. Reuse a suitable established form without generating alternatives as a prerequisite.

## Acceptance tests

A figure is done when all of these hold:

- **Claim visibility.** With the caption covered, the claim's key relation is visible as marks, not only as words.
- **One question.** Every element relates to the answer to the spec's question.
- **Grammar conformity.** Every hue, line style, and glyph means what the semantic map says.
- **Name conformity.** Names in the canvas match the prose and the other figures character for character.
- **Canvas content.** Keep numbers, dates, sample sizes, and qualifiers when they encode the mechanism, distinguish compared cases, or prevent a false reading. Place supporting context and provenance beside the figure.
- **Transition cost.** Relative to the previous figure, one new idea.
- **Comparison fairness.** Juxtaposed panels share layout, order, axes, and rows.
- **Delivery fit.** The figure remains legible in the intended medium; a web figure preferably fits on one screen with its caption.

## Canvas and caption

| Place | Holds | Does not hold |
|---|---|---|
| Canvas | exact names; relations; equations; dimensions, thresholds, values, dates, or qualifiers needed to interpret the answer | supporting context unrelated to the depicted mechanism or comparison; source records |
| Caption, first sentence | the claim, stated as an assertion | "Figure N shows ..." |
| Caption, second sentence | how to read an encoding that appears for the first time in the document | a repeat of encodings already defined |
| Caption, rest | supporting counts, conditions applying to the whole figure, sources, illustrative status, step text for numbered markers | a necessary local condition that cannot be matched to its mark |

Label directly beside the element rather than in a legend. A distant label connects with a thin neutral leader. Numbered markers may link to procedural detail below the figure, but keep operation names and conditions visible when they are needed to follow the mechanism.

## Sources

- Sleepy-Avacado/FigGenie-paper-diagram-skill (MIT), https://github.com/Sleepy-Avacado/FigGenie-paper-diagram-skill, its brief template and spec guide: the brief confirmed before drawing, component tags, the numbered main path, assumptions with their sources, and drawing without a round trip when the guess is well supported.
