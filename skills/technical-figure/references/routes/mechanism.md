# Mechanism route

Box-and-arrow figures: architectures, pipelines, module internals, residual-stream spines, zoom panels, sequence diagrams, swimlanes, and state machines. Two ways to author them end in the same SVG contract and the same renderer.

## Choosing between layout and hand placement

| Situation | Author with |
|---|---|
| More than about 15 nodes, many edges, or routing that is hard to plan | `scripts/layout.mjs` (automatic layered layout) |
| A spine with side branches, zoom panels, grids, or any composition whose meaning depends on exact placement | hand-authored SVG with computed coordinates |
| Sequence diagrams, swimlanes, and to-scale timelines, where position encodes time or ownership | hand-authored SVG with computed coordinates |
| A state machine with more than about 8 states | `scripts/layout.mjs`, then add the initial disc and self-loops by hand |
| A layout from `layout.mjs` is right except for one region | layout first, then edit only that region in the SVG |

Automatic layout is a useful starting point for dense graphs; computed placement suits spines, grids, and zoom compositions. Choose by topology and the observed render. Preserve a working layout when editing, and change route when the current one obscures required relationships.

## Automatic layout

```bash
node scripts/layout.mjs graph.json -o figure.svg
node scripts/render.mjs figure.svg
```

`graph.json`:

```json
{
  "direction": "UP",
  "nodes": [
    {"id": "x", "title": "hidden state", "kind": "chip"},
    {"id": "router", "title": "router", "sub": "top-k", "classes": ["box"]},
    {"id": "e1", "title": "expert 1", "classes": ["box", "blue", "focus"], "group": "experts"},
    {"id": "sum", "title": "+", "kind": "op"}
  ],
  "edges": [
    {"from": "x", "to": "router", "fromSide": "N", "toSide": "S"},
    {"from": "router", "to": "e1", "classes": ["control"], "label": "gate weight"},
    {"from": "e1", "to": "sum", "classes": ["emph", "blue"]}
  ],
  "groups": [{"id": "experts", "label": "routed experts", "classes": ["container"], "members": ["e1"]}]
}
```

- `direction`: `UP` for model depth, `RIGHT` for pipelines and time; one direction per document for the same kind of figure.
- Node `kind`: `box` (default), `op` (operator circle; `title` is `+`, `×`, or `−`), `chip`. `mono: true` sets the title in the mono voice; `tex` replaces the title with math.
- Node `subTex` sets the second line in math. Edge fields: `id` (becomes `data-id`), `classes`, `label` or `tex` for a math label, `labelClasses` (for example a hue for a hued edge's label), `arrow` (`end` by default, `start`, `both`, `none`).
- Group fields: `label`, `classes` (`container` or `zoom`), `members`, and `"equal": true` to give members in the same layer one width.
- Top-level `spacing: {"node": 24, "layer": 40}` overrides the node and layer gaps. A layout wider than 720u stops with a message unless `--wide` is passed for a full-width page.
- At most two edges may enter one side of an `op` node; they are spread apart on the circle. More are refused; route them to other sides.
- Edge sides (`N`, `E`, `S`, `W`) fix where an edge leaves and enters. Give them for every edge whose side matters: outputs on the downstream side, skip and residual inputs from the side.
- Order in the arrays is kept where it does not add crossings, so list peers in reading order.
- The script measures every label with the real fonts before layout, emits junction dots at real splits, rounds orthogonal bends, and keeps edge labels beside their lines.

Refine after layout by editing classes (focus, ghost, hue) in the SVG rather than moving coordinates. When the layout is wrong, change the input: sides, order, grouping, or direction.

When a layout misbehaves, check these first; they cause most failed trials:

- **Width over 720u.** `layout.mjs` stops unless `--wide` is given. Change direction, put fewer peers in a row, shorten labels without dropping names, or split the figure; `spacing` tightens node and layer gaps as a last step.
- **Order changed inside a group.** The layout warns when a group's members move out of input order. Edges leaving the group from members in the middle and labels on those edges are the usual cause; route those edges from the group's sides or reposition the label without losing its meaning.
- **Edge labels in UP or DOWN layouts** occupy a layer of their own and can push nodes into another row. Prefer short labels, a TeX label on the edge, or naming the payload in the target's second line.
- **Several inputs into one operator side** stack their arrow tips. Give them different `toSide` values.
- **A shape `layout.mjs` cannot express** (a spine with side reads, a locator, text-only nodes, edges meeting edges): author that figure by hand instead of forcing the graph.

Treat layout trials as diagnostic work: when the same defect repeats, change the relevant constraints or authoring route rather than retrying unchanged input.

## Hand-authored SVG

Work on the 4u grid with the token spacing. Compute coordinates in a short script or by explicit arithmetic; do not eyeball them.

1. Fix the canvas width (720u) and the margin (16u). Divide the width into columns for the composition, such as a narrow locator column and a wide zoom column.
2. Size nodes from their labels: measure each label with `node scripts/measure.mjs --class t "label"` (or `--tex` for math), then add 12u of horizontal padding on each side; 36u tall for one line, 52u for two.
3. Place peers on shared rows or columns with equal sizes; align centers of connected nodes so straight edges stay straight.
4. Route edges orthogonally with at most two bends, ending exactly on the target's boundary. Leave 16u clear between parallel edges and between edges and unrelated boxes.
5. Put each edge label 6u beside its line on a straight segment, never on the line and never on a bend.

### Residual spine recipe

The spine is a vertical `spine` path at a fixed x, running from the embedding node to the unembedding node. For each sublayer at height y:

- the read edge leaves the spine horizontally at y + offset into the sublayer's input node, placed in a column to the right of the spine;
- the sublayer's internals run upward inside that column;
- the write edge returns horizontally into an `op` ⊕ centered on the spine;
- norm operations sit on the read branch, not on the spine.

The spine is the longest and heaviest neutral line in the figure. Hue goes only to the read or write edges and matrices the claim is about; the other layers are `ghost`. Equations sit in a further right column, vertically aligned with the ⊕ they describe.

### Zoom composition recipe

Left column about 30 percent of the width: the ghosted locator stack with the zoomed block marked (hue outline or tint). Right column: the `zoom` panel. One `leader` connects the marked block's right edge to the panel's left edge. The panel's label is the block's identifier. Inside the panel, follow the same direction as the stack.

## Sequence diagrams

A sequence diagram answers who sends what to whom, in what order, and who waits. Its notation is UML's, which a peer reads without a key; the recipe maps that notation onto the contract classes.

**Participants and lifelines.** Participants are a row of equal `box`es at the top, exact names, ordered so most messages run left to right and the first caller sits at the left. Each lifeline is a vertical `guide` line from the box's bottom edge to the bottom of the figure. At 720u, about five lifelines fit at a 144u pitch; more participants than that split the figure (happy path and failure path) or move to the wide canvas. Include only the participants the question involves.

**Time runs down.** Messages are horizontal lines on rows at a fixed pitch, 40u when labeled, so vertical position is order and equal steps mean equal order, not equal time. No message points upward. A message that takes noticeable time in transit may slope down; the slope is then a claim about delay.

| Message | Line | Head | Contract |
|---|---|---|---|
| Synchronous call | solid | filled | `edge` path that stops at the head's base, plus the head as a closed `path class="dot"` triangle whose tip touches the receiver's activation bar |
| Return | dashed | open | `edge control` with `data-arrow="end"`; labeled with the returned value, never with "return" |
| Asynchronous message (event, signal, fire and forget) | solid | open | `edge` with `data-arrow="end"`; no paired return |
| Self call | solid U-loop | filled or open by its kind | path leaving the activation bar, 24u out and 16u to 20u down, back into the same bar; label to the right of the loop |

Size the filled head like the chevron, length `4 + 4.5w` (10.75u for a 1.5u edge) and half width 0.4 of the length, so the two heads differ only in fill. Give the triangle the same hue, `emph`, or `ghost` class as its edge so it takes the edge's color. Inside a sequence figure a dashed message means a return, the reading UML gives it; record that meaning for sequence figures in the semantic map and keep control relations out of the same figure.

**Activation bars.** When who is blocked matters, an activation bar is a `box` 8u wide centered on the lifeline, from the message that starts the participant's work to the last message it sends for that work. A nested call on the same participant offsets a second bar 4u to the right. Messages start and end on bar edges (lifeline ± 4u). Every bar closes. When blocking is not part of the claim, omit bars from the whole figure rather than from some participants.

**Combined fragments.** A branch, option, or repetition is a frame, never two loose clusters of arrows:

- The frame is a `container outline` spanning only the lifelines with messages inside it, at least 12u beyond the outermost activation bars.
- The operator is a `micro` label (`ALT`, `OPT`, `LOOP`) at the frame's top left; its guard in brackets is a `ta` label beside it: `[token valid]`, `[cache miss]`, `[for each shard]`, `[attempt < 3]`. Place both in the gap right of the first lifeline the frame covers, never across a lifeline or an activation bar; the lint does not see lifelines or bars as lines, so check this in the render.
- `alt` has two regions divided by a `guide` line across the frame; the second region's guard (`[else]` or its own condition) sits at its top left. `opt` and `loop` have one region, and a `loop` guard states its bound.
- One fragment per figure by default and at most one level of nesting. A figure that needs more becomes an overview with the happy path and a detail figure for the branch.

**Labels and emphasis.** A message label is a `tl` 6u above its line, starting 8u from the sending end: left-anchored for a rightward message, right-anchored for a leftward one. A label must not cross a lifeline it passes; shorten it or start it nearer the sender. One message, or one call with its return, carries the emphasis; a hue only when the semantic map gives that message's meaning one.

**Budget.** About 5 lifelines and 12 messages at 720u. Beyond that, split rather than shrink.

## Swimlanes

A swimlane answers who does each step of one process and where work changes hands. When actors call each other and wait for replies, the figure is a sequence diagram instead; when no actor dimension matters, it is a process flow.

- **Lanes are actors**: a team, service, process, or device, one lane each, in an order that keeps most handoffs between neighbors. Horizontal lanes carry their names in a left gutter (`t`, right-aligned, vertically centered); separate lanes with `guide` rules across the full width, or alternate `band` fills when there are more than three lanes, not both.
- **Each step belongs to exactly one lane.** A step two actors share is two steps or a handoff. A lane with a single step is fine.
- **Time runs left to right**: a step's x follows its order. Steps in different lanes share an x only when they happen together, because aligned steps read as simultaneous.
- **Handoffs are the subject.** An edge that crosses a lane boundary carries a `tl` label naming what is handed over (an artifact, a request, an approval) and crosses the boundary perpendicularly, never running along a lane rule. The handoff the claim is about, such as the one that adds the most latency or fails most often, carries the emphasis. Edges within a lane stay short and unlabeled when the order is obvious.
- **Flow does not double back.** Reorder steps and lanes before drawing a backward edge; a real loop goes in a scoped loop box that names its exit condition.

## State machines

A state machine answers which conditions a system can be in, which events move it between them, and where it can end.

- **States** are `box`es named with the state's exact identifier, in the `mono` voice when it is a literal enum value. A state is a condition that holds (`running`, `draining`); a box named by a verb is an action, and actions belong after `/` on a transition.
- **Transitions** are `edge`s, each labeled `event [guard] / action` with empty parts omitted. An unlabeled transition is a defect, because the trigger is the content.
- **The initial state is marked** by a filled disc, a closed `path class="dot"` circle of radius 6u, with an unlabeled edge into the initial state. One per machine or region.
- **Terminal states** carry a double outline: a second `box` 4u inside the first, with the label inside the inner one.
- **Layout follows a typical instance**: the main lifecycle left to right (or top to bottom in a document that runs depth that way), success and failure outcomes at the far end, back edges such as retry or requeue routed under the main row with their guards.
- **Self-loops** leave and re-enter the top edge of their state about 40u apart and rise 24u to 28u; the label sits above the loop.
- **A transition from every state** (cancel, timeout) is one `ta` annotation such as `any state → cancelled on SIGTERM`, not an edge from each state.
- **Budget**: more transitions than twice the number of states usually means two machines, or a transition table in the prose.

## Editing an existing figure

- A contract source (classes only, rendered by `render.mjs`): change only the affected elements, keep their `data-id`s and untouched geometry, and rerender. Do not regenerate the whole file for a local change.
- A legacy SVG with inline colors and fonts: for a small correction, edit it in place in its own style and say so; to bring it into the document's grammar, redraw it as a contract source from its FigureSpec. Mixing the two leaves a figure that the lint rejects and the set does not match.

## Checks specific to this route

- The document's central object is the heaviest neutral line.
- No edge enters a container border; edges end on nodes.
- The router or controller reaches its targets with `control` edges, and data reaches them from the data source.
- Repetition shows as an `N×` label on the stack or a bracket, not as copies.
- Every node named in the spec carries its `data-id`.
- In a sequence diagram, no message points upward, every synchronous call has its return, every activation bar closes, and no label or fragment operator crosses a lifeline.
- In a swimlane, every lane is named and every step sits inside one lane.
- In a state machine, exactly one initial disc per machine or region, every transition labeled, and terminal states double-outlined.

## Sources

- OMG UML 2.5.1, Interactions and State Machines: filled heads for synchronous calls, open heads for asynchronous messages, dashed replies, combined fragments with guards, the initial pseudostate.
- cathrynlavery/diagram-design (MIT), https://github.com/cathrynlavery/diagram-design, the sequence, swimlane, and state type references: message kinds, fragment budgets, handoffs as the swimlane's key edges, labeled transitions.
