# Mechanism route

Box-and-arrow figures: architectures, pipelines, module internals, residual-stream spines, zoom panels. Two ways to author them end in the same SVG contract and the same renderer.

## Choosing between layout and hand placement

| Situation | Author with |
|---|---|
| More than about 15 nodes, many edges, or routing that is hard to plan | `scripts/layout.mjs` (automatic layered layout) |
| A spine with side branches, zoom panels, grids, or any composition whose meaning depends on exact placement | hand-authored SVG with computed coordinates |
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

## Editing an existing figure

- A contract source (classes only, rendered by `render.mjs`): change only the affected elements, keep their `data-id`s and untouched geometry, and rerender. Do not regenerate the whole file for a local change.
- A legacy SVG with inline colors and fonts: for a small correction, edit it in place in its own style and say so; to bring it into the document's grammar, redraw it as a contract source from its FigureSpec. Mixing the two leaves a figure that the lint rejects and the set does not match.

## Checks specific to this route

- The document's central object is the heaviest neutral line.
- No edge enters a container border; edges end on nodes.
- The router or controller reaches its targets with `control` edges, and data reaches them from the data source.
- Repetition shows as an `N×` label on the stack or a bracket, not as copies.
- Every node named in the spec carries its `data-id`.
