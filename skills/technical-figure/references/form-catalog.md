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
| Participants exchange messages over time | Sequence diagram | Participants as columns, time down | Synchronous and asynchronous arrows differ | Time axis implied but unclear |
| A system moves between states on events | State machine | States as nodes, events on transitions | Terminal and initial states marked | States confused with actions |
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
- **Request sequence:** sequence diagram; only the participants the question involves.
