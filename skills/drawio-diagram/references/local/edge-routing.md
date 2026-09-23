# Edge routing and connections

## Contents

- The mental model
- Every edge, always
- Floating vs fixed terminals
- Recipes
- Waypoints
- Crossings and z-order
- Terminal hygiene
- Verify

Edges are the most common failure in generated diagrams: lines crossing component bodies, wrapping around shapes, overlapping each other, or starting and ending on the wrong sides. All of these come from one wrong assumption.

## The mental model

**A saved edge style does not route around obstacles by itself.** The ordinary built-in router draws a straight or simple right-angle path with awareness of the two terminals, not unrelated shapes. An explicit authoring-time layout such as `orthogonalEdge` can calculate an obstacle-aware route, but no cleanup pass runs merely because the finished `.drawio` file is later opened.

Consequence: the author owns the saved result. Apply `references/local/auto-layout.md` first. For a route that still fails, pick connection sides so the natural corridor is empty and add waypoints only when it is not. Never write edges naively expecting a later viewer fix. Official example diagrams confirm the manual fallback: measured across 133 plain-XML diagrams in `jgraph/drawio-diagrams`, roughly a quarter of edges pin terminals with `exitX/entryX` and 29% carry explicit waypoints.

## Every edge, always

```xml
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;"
        edge="1" parent="1" source="boxA" target="boxB">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

- `source` and `target` reference **shape** cell ids (or the `<object>` wrapper id when one exists). Never point at a text/label cell, and never leave a terminal unset when the shape exists - a dangling end drifts when a human drags things later. Emit all vertices before the edges that reference them; that also puts edges later in document order, on top of fills.
- The `<mxGeometry relative="1" as="geometry" />` child is mandatory; a self-closing edge cell fails silently.
- One `edgeStyle` family per page (all orthogonal, or all straight, or all curved). draw.io's own editor default is `edgeStyle=orthogonalEdgeStyle;rounded=0;jettySize=auto;orthogonalLoop=1;html=1;`; this skill prefers the same with `rounded=1`.
- File each edge at the innermost container that holds **both** endpoints: that container's ID when both ends sit inside it at any nesting depth, and `parent="1"` only when an endpoint is outside every container. Auto-layout reads an edge's coordinates in its parent's frame, so an edge filed further out than its endpoints is laid out in the wrong place. The parent also sets the waypoint frame: page-absolute on the layer, relative to the container when the edge is filed inside one.

## Floating vs fixed terminals

**Floating** (no `exitX/entryX`): draw.io attaches to the nearest perimeter point at render time. Good for exactly one edge between two adjacent shapes with an empty corridor. It self-heals when a human moves a box.

**Fixed** (`exitX`,`exitY`,`entryX`,`entryY`, each 0..1 across the shape's bounding box): the edge leaves and arrives at the exact point you chose.

| Side | exit/entry values |
| --- | --- |
| right middle | `X=1;Y=0.5` |
| left middle | `X=0;Y=0.5` |
| bottom middle | `X=0.5;Y=1` |
| top middle | `X=0.5;Y=0` |
| quarter offsets (parallel edges) | `Y=0.25` / `Y=0.75` (or `X=` on top/bottom) |

Switch from floating to fixed whenever any of these holds:

1. Two or more edges touch the same shape (fan-in/fan-out, request+response).
2. The route must leave from a specific side to keep a corridor clean.
3. The edge connects into or out of a container/swimlane.
4. An exported render showed the edge attaching somewhere surprising.

The fixed point must face the other terminal. `exitX=0` (left side) toward a target on the right forces the route to wrap around the source shape - the layout validator flags this.

## Recipes

- **Left-to-right step:** align the two boxes on the same center-Y, then `exitX=1;exitY=0.5;entryX=0;entryY=0.5`. The edge renders as one straight horizontal line - the most readable connector that exists. Prefer moving a box a few pixels to achieve this over accepting a two-bend elbow.
- **Request/response pair:** give each direction its own corridor so they never overlap: request `exitX=1;exitY=0.25;entryX=0;entryY=0.25`, response `exitX=0;exitY=0.75;entryX=1;entryY=0.75`. Two floating edges between the same shapes render on top of each other (validator warns).
- **Fan-out (1→N):** exit the source at `Y=0.25/0.5/0.75` (one per branch), or exit once from `X=0.5;Y=1` and branch with waypoints in the corridor below.
- **Skip-a-neighbor edge:** the corridor is occupied, so route above or below the row: exit top/bottom, two waypoints in the horizontal corridor, enter top/bottom of the target.

```xml
<mxCell id="skip" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;exitX=0.5;exitY=0;entryX=0.5;entryY=0;"
        edge="1" parent="1" source="a" target="c">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="160" y="150" />
      <mxPoint x="640" y="150" />
    </Array>
  </mxGeometry>
</mxCell>
```

- **Return/feedback loop:** exit the bottom of the last box, run through a dedicated corridor beneath the whole row, enter the bottom of the first box. Never send a return edge back through the middle of the flow.

## Waypoints

`<Array as="points">` inside the edge geometry lists intermediate points in the coordinate space of the edge's **parent** (page-absolute when `parent="1"`). Without an `edgeStyle` they are literal polyline vertices; with `orthogonalEdgeStyle` they are routing hints the orthogonal path snaps through. Place them:

- in reserved corridors (the gaps between rows/columns), never inside a shape;
- at least 20px clear of every shape border, so bends do not kiss boxes;
- axis-aligned with the terminals where possible - each extra bend costs readability.

Before keeping any waypoint, compare the route with the no-waypoint route. If fixed source and target anchors already share an X or Y coordinate and the straight corridor is clear, remove the waypoints. A short sideways excursion that immediately returns to the same axis is a dogleg, not useful routing. Waypoints earn their place only by avoiding a component, separating parallel edges, or occupying a deliberate outer/return corridor.

When connecting a component to a wide semantic strip, decide what the edge means. A relationship to the strip as a whole should be centered on both ends. A relationship to one part of the strip should attach near that part and the strip should be sized/aligned to make the ownership legible. Never use a far-edge attachment plus two bends merely to fill whitespace.

If a route needs more than 3-4 waypoints, the placement is wrong; move boxes until corridors open up.

## Crossings and z-order

- Cells render in document order within a parent: later cells paint on top. Keep the order backgrounds → containers → shapes → edges. An edge that paints across a component body is a routing bug - fix the route, do not reorder to hide it beneath the shape.
- When two edges must cross, mark the crossing: `jumpStyle=arc;jumpSize=6` on the page's edges renders hop marks where they intersect.
- Edge labels sit on straight segments (see `references/local/text-and-labels.md`), never on bends or crossings.

## Terminal hygiene

- Arrowheads must land flat on a shape border, not on a corner: enter at side midpoints or quarter points, never `entryX=0;entryY=0`.
- Non-rectangular shapes need the matching `perimeter` (e.g. `rhombusPerimeter` for decisions, `ellipsePerimeter` for circles), or edges attach to the invisible bounding box and appear to float in space.
- Keep the default `jettySize=auto` so orthogonal edges leave shapes with a perpendicular stub instead of hugging the border.

A one-page working demonstration of every recipe above ships at `assets/edge-routing-patterns.drawio`; open or copy it when a concrete reference beats prose.

## Verify

`python3 scripts/validate_drawio_layout.py <file>.drawio` checks: dangling terminals (error), edges whose approximate route crosses an unrelated component, fixed ports facing away from the other terminal, and same-pair floating edges that will overlap. It also warns when fixed aligned terminals take a clear one/two-waypoint dogleg. Treat each warning as a route to fix; then confirm on the rendered artifact, because static checks approximate the real router.
