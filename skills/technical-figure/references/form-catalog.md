# Form catalog

Choose the form from the shape of the claim, not from the request's noun. "Diagram" arrives meaning a pipeline, a comparison, a geometry sketch, or an architecture; each has a form that makes its claim visible and forms that bury it. When the form fights the content after a first render, the claim's shape was misread.

## Claim shape to form

| Claim shape | Form | Layout | Encoding | Anti-pattern |
|---|---|---|---|---|
| X is built from these parts with these interfaces | Block diagram | Group by real boundary, align peers | Names on nodes, what passes on edges | Every box the same weight; edges without payload |
| Upper layers work on top of lower ones | Layered stack | One direction for the whole document (depth bottom to top) | Repetition as `N×` bracket | Direction flipping between figures |
| Components read from and write to a shared state | Spine | The state as the longest line; components beside it | Read leaves the spine, write enters through ⊕ | Components drawn in series on the state line |
| Value moves between positions or steps | Grid of lanes | Position on x, depth up | Cross-lane arrows only where information moves | A single stack that hides positions |
| X is produced by steps A, B, C, with branches or loops | Process flow | Left to right; scoped loop box around the repeated part | Solid data flow, dashed control, step numbers along reading order | Loops without scope; narration labels on every edge |
| Methods A, B, C change different objects | Small multiples on one scaffold, or superposition | Same layout and rows; ghosted shared scaffold | Only the intervention point carries the hue; glyph per intervention kind | Three full-weight copies of the same stack |
| Variants of one design differ in one component | Sibling variants | Identical coordinates across panels | Removed parts omitted, added parts in the hue | Re-laid-out panels that force the reader to re-map |
| A new component is added to a known design | Delta highlight | Known design in neutral ink | New parts and edges in one hue with the emphasis stroke; caption names the color | Coloring the whole architecture |
| A system changed from one version to another: parts removed, replaced, or rewired | Architecture delta | Before and after panels on one grid with positions copied; change ledger beside them | Unchanged parts neutral; each change numbered in the panel and named in the ledger | Two snapshots laid out independently |
| The same pipeline runs in two orders or formats | Aligned parallel columns | Corresponding steps on the same row | Format chips on edges | Misaligned rows; shared steps drawn twice |
| A pattern holds across layers or positions | Strip or matrix | One row per model or condition, one cell per layer | Cell color is type; bracket marks the repeating unit | A sublayer stack per layer |
| A value changes with layer or configuration | Chart (line or dot plot) | Layer on x | Mark the layers the claim is about | A box per layer |
| X is a projection or component of Y | Annotated geometry | Axes at 1:1, the reference direction as an axis | Reserved hue for the direction; right-angle mark; components dotted | Distorted axes; perspective 3D |
| A tensor has this shape; a product has this rank | Proportional rectangles | In multiplication order | Side lengths proportional; dimension labels on sides | Dimensions written only as text |
| Candidates are filtered by rules | Grid with filter overlay | One candidate grid | Hatch for excluded regions, × for failed cells, ring for the chosen | A flowchart where the candidate space is invisible |
| A released artifact came from this recipe | Lineage graph | Source at the left or top, branches to artifacts | Node = checkpoint or artifact, edge = operation; main path emphasized, data inputs gray | Step lists without the artifacts they produce |
| One input, several judgments | Fan-out | One input, parallel judges, uniform result chips | Chip style shared by all judgments | A different example per judge |
| Behavior changes along a generated sequence | Token strip on a position axis | Positions left to right | Mark where measurement and change happen; span tint for the outcome | Sentences without an axis |
| Router selects k of N | Offset instance stack or expert row | Router below or beside the experts | Selected experts in full ink, unselected ghosted; structural properties shown on all | Two experts and an ellipsis |
| A set difference defines a direction | Point clouds and difference vector, or mirrored pipelines meeting at ⊖ | 2D schematic, or two columns converging | Marker shape distinguishes sets; the difference vector in the reserved hue | Sets distinguished by color alone |
| Participants exchange messages over time | Sequence diagram | Participants as columns with lifelines, time down | Filled head for a call, dashed line for its return, open head for an asynchronous message; `alt`, `opt`, `loop` frames with guards | Branches as loose arrow clusters; a message pointing up |
| Several actors carry one process and hand work to each other | Swimlane | One lane per actor, time left to right | Each step inside its owner's lane; handoffs cross lane boundaries and name what is handed over | A step spanning two lanes; flow that doubles back |
| A system moves between states on events | State machine | States as nodes, events on transitions | Filled disc into the initial state; terminal states double-outlined; every transition labeled `event [guard] / action` | States confused with actions |
| Work on parallel resources overlaps, waits, and sets the end-to-end time | To-scale timeline | One lane per resource on one shared time axis | Interval lengths from the numbers; idle as uncovered track; critical path in the hue | Equal-width blocks for unequal durations |
| A computation turns this input into that output | Worked example | The mechanism drawn once, values where they are produced | Real values computed from one input; the value the claim is about in focus | Placeholder values or numbers that do not follow from the previous step |
| Quantities split and merge | Sankey | Flow left to right | Width proportional and conserved | Many tiny flows |

## Comparison design

Name the comparison before drawing: the targets (what is compared) and the action (what the reader should find, such as where each method acts, which step differs, or which value is larger).

- **Juxtaposition** (side by side) relies on memory. Use it when the targets have different structure; then keep layout, order, and rows identical where they share structure.
- **Superposition** (one coordinate system) relies on the visual system. Use it when the structure is shared and the difference is small, which is the common case for method comparisons.
- **Explicit encoding** draws the difference itself: a difference vector, an indicator matrix, a selection ring. Use it when the known relation is the claim, and keep it attached to the objects it compares.
- Pick one reference (the unmodified baseline) and align everything else to it.

## Sequences of figures

- Overview first, then zoom. When the zoomed element's place in the overview is not obvious from the previous figure or the caption, the zoom figure keeps a small ghosted locator of the overview with the region marked, joined to the panel by one dotted leader. The locator is hand-authored; `layout.mjs` does not compose it.
- Build-up follows the prose order as (a), (b), (c) panels, each adding one element.
- Parallel cases (three models, three methods, two formats) reuse one layout.
- Reuse one concrete example across the document once it has been introduced, so readers compare like with like.

## Archetypes for ML mechanism documents

These recipes recur in model and interpretability documents. Each names the claim it serves; `exemplars.md` points to public figures that do it well.

### Residual stream spine

Claim: components read the stream and add their outputs back to it. Draw the stream as a vertical `spine` (2.25u, ink) from the embedding at the bottom to the unembedding at the top. Each sublayer sits beside the spine: a read edge leaves the spine into the input projection, the sublayer's output projection returns through an `op` ⊕ on the spine. Only the matrices the claim is about carry the hue; other layers are ghosted in place. Equations sit in a column to the right, aligned with the ⊕ they describe.

### Layer zoom

Claim: this repeated block contains these operations. Left third: the stack with `N×` bracket and the zoomed block marked. Right two thirds: the zoom panel, connected by one dotted leader, its background a lighter tint of the marked block. The stack is a locator and stays small after the document's first overview.

### Mixture of experts

Claim: the router selects k experts per token and their weighted outputs return to the stream. Input at the bottom; router beside it with a small score histogram; routed experts in a row, selected ones in full ink with ⊗ gates, unselected ghosted; shared expert set apart; one ⊕ collects the outputs. Router output is a `control` edge to the gates, never a data edge into the experts: the experts read the hidden state, not the router's output. Write matrices named on the expert output edges.

### Hybrid layer pattern

Claim: layer types alternate in this pattern. A strip with one cell per layer, cell class by type, a bracket over one repeating unit, one row per model when models are compared. The real order of one unit is drawn when the order is the point; otherwise `3×` suffices.

### Intervention comparison

Claim: methods act at different places or times. One ghosted scaffold of the model per method (or one scaffold with all intervention points superposed); the intervention point in the hue; a runtime hook as a glyph on the spine with a dashed outline; an edited weight as a hued box marked with a prime; a trained update as an adapter chip. Each panel's header states the operation, and the shared parts are identical across panels.

### Precision and format path

Claim: two pipelines differ in the order of quantize and edit steps. Two aligned columns with corresponding steps on the same row; casts as italic labels on edges; stored dtypes as chips under nodes; block or tile scale structure as a small inset beside, never over, the step it explains; where error enters, a short annotation on that step.

### Recipe lineage

Claim: this artifact was produced from that base through these operations. Checkpoints and artifacts as nodes, operations on edges, the main path in the hue with the emphasis stroke, data inputs gray, stage boundaries as bands or a ruler beneath.

### Direction from a contrast

Claim: a direction is the difference of two conditional means. Either two mirrored columns (prompts, activations, mean) meeting at ⊖ and producing a vector glyph, or a 2D schematic with two point clouds (filled and hollow markers), their means, and the difference vector in the reserved hue. A confound is shown as a second axis that moves one cloud.

### Projection and rank-one update

Claim: removing a component is a projection; the weight change has rank one. Geometry at 1:1 with the direction as an axis; for the matrix view, proportional rectangles in product order with the direction column and its row factor in the hue.

## Archetypes for systems documents

- **Service architecture:** group by deployment or trust boundary; edges name protocol and payload; external systems at the edge of the canvas; one focal request path in the hue.
- **Data pipeline:** left to right; stages as bands; artifacts as nodes between operations; failure or retry path as a separate dashed control edge.
- **Request sequence:** sequence diagram; only the participants the question involves. Sequence diagrams, swimlanes, and state machines follow the recipes in `routes/mechanism.md`.
- **Migration:** architecture delta, below.
- **Pipeline or step schedule:** to-scale timeline, below, when the claim is about time; a process flow when only the order matters.

## Change, time, and worked-example forms

These three forms make claims a box diagram cannot: what changed between two versions, how long things take and where time is lost, and what a computation does to real values. Each makes a stronger promise than a schematic, so each has rules that keep the promise checkable.

### Architecture delta

Claim: the system changed from version A to version B in these specific ways. Use it when parts were removed, replaced, changed, or rewired; additions alone are a delta highlight on one panel. A delta shows two states, not the order of the migration, its downtime, or its rollback; those need a process flow or a timeline.

- **One grid, copied positions.** Draw the before panel, copy every coordinate into the after panel, then edit only what changed. Panels share size and internal grid: side by side when each fits in about 330u, stacked otherwise. With `layout.mjs`, lay out the union of both versions once and derive each panel by dropping what it lacks; laying out each panel separately makes unchanged parts appear to move.
- **Movement is a change.** A retained element moves only when its new position is part of the change, such as crossing a trust or deployment boundary, and the move gets a ledger entry.
- **Panel headers name the versions** (`v1.4`, `v2.0`, or dates) as `tp` labels; the caption's first sentence states the change.
- **Change ledger.** A short numbered list beside or between the panels: one entry per changed element and kind of change, starting with the change word, then the exact name, then the difference, as in `CHANGED orders: dispatch → enqueue` or `REWIRED submit: api → queue`. About six entries fit; a larger migration splits by subsystem rather than dropping edges.
- **Marks.** Unchanged parts stay neutral in both panels. Each changed element carries its ledger number as a small `chip` in the panel where the change shows, so the ledger links to the figure without color. Added parts appear only after, in the hue the semantic map gives to "new in this version". Removed parts appear only before, with their chip; their slot in the after panel stays empty against the copied grid. A changed part keeps its position, takes the hue after, and shows the new property in its second line. A rewired edge is hued after, and the ledger names its old and new endpoints.
- **Contract.** Mark each changed element with `data-delta` and give repeated elements panel-prefixed ids (`svg-contract.md`). Review checks that every unchanged element has the same local coordinates in both panels and that ledger entries, chips, and `data-delta` marks correspond one to one.

### To-scale timeline

Claim: these intervals overlap, wait, and add up to this end-to-end time. Use it for pipeline bubbles, overlap of compute and communication, a latency breakdown, or stragglers. When the durations are illustrative or only the order matters, a process flow or sequence diagram makes no length claim and is the honest form. Many runs or a distribution of durations belong on the chart route.

- **Data first.** List every interval as resource, start, end, label, from measurements or a computed schedule, in the FigureSpec `example` with `geometry: exact`. Compute coordinates with a short script: `x = origin + k × start`, `width = k × duration`, one `k` for every lane, chosen so the full span fills the plot width.
- **Lanes are resources**: a device, stream, worker, or queue, named in a left gutter. One horizontal time axis under the lanes, ticks at round values, the unit at the axis start. No second axis.
- **Busy intervals** are `box` rects with their outline, labeled inside with the operation when the label fits and outside or in the caption otherwise. Data coordinates are exempt from the 4u grid, so 10 ms and 11 ms stay different lengths.
- **Idle stays visible.** Each lane has a `band` track across the whole axis behind its intervals, so idle time reads as uncovered track. Label idle with its duration when idle is the claim (`idle 38 ms`). The outline on busy intervals keeps them distinct in the dark theme, where track and page are close in value. Never compress idle time or fill it to make the lanes look busy.
- **The critical path** (the chain of intervals that sets the end time) carries the hue and the `focus` outline; dependency edges between lanes are drawn only along it.
- **One honest scale.** An axis break needs a visible break mark and a caption note. A very short interval keeps its true width and moves its label outside. Two schedules compared, such as before and after an optimization, stack on the same scale with aligned origins, and a bracket under each states the end-to-end time.
- **Contract.** Mark the scaled group with `data-scale` and each interval with `data-span` (`svg-contract.md`). Review recomputes two or three intervals from their spans and checks that the last end equals the end-to-end time the caption reports.

### Worked example

Claim: on this concrete input, the mechanism produces these values. Use it when real numbers make the mechanism easier to verify than symbols: a softmax over four logits, top-k routing of one token, quantizing one block, a rotary rotation of one vector pair, BPE merges on one word, an attention mask over five tokens.

- **Computed, never typed.** Generate every value with a short script from one stated input and record the input and outputs in the FigureSpec `example`. Each value follows from the previous one by the operation on the edge between them, so a peer can recompute any step.
- **Smallest telling instance.** Three to six elements per vector, matrices near 4×4. When the real dimension is larger, show the first entries, an ellipsis, and the true size as a dimension label.
- **Values where they are produced.** Numbers sit in the cells, chips, or boxes of the step that produces them; operations label the edges between steps. A quantity keeps its position and format at every step so its change is visible.
- **Fixed precision.** One number of decimals per quantity across the figure. When rounding breaks an identity, such as probabilities that sum to 0.99, state the rounding in the caption.
- **Emphasis on the outcome.** The value the claim is about (the selected expert, the clipped entry, the masked position) carries the hue; inputs and unchanged values stay in ink.
- **The example must exercise the mechanism.** An input on which the mechanism does nothing visible (no entry clipped, every token kept by the mask, a tie at the top-k boundary) fails the picture test; choose another input. Reuse the chosen example across the document's figures.

## Sources

- cathrynlavery/diagram-design (MIT), https://github.com/cathrynlavery/diagram-design, the architecture-delta, timeline, and Gantt type references: synchronized snapshot coordinates, the change vocabulary, honest time spacing.
- Sleepy-Avacado/FigGenie-paper-diagram-skill (MIT), https://github.com/Sleepy-Avacado/FigGenie-paper-diagram-skill, its spec guide and layout notes: `data-delta` on changed elements, `data-scale` on groups drawn from numbers, idle gaps kept visible on a shared time grid.
