# Automatic layout

Automatic layout is the default starting point for a new diagram whose topology fits a supported layout. Use explicit coordinates and routes when placement carries meaning, a reference layout must be preserved, or the automatic route is unsuitable; a failed trial is not required. The layout is applied explicitly while authoring or exporting; draw.io does not silently repair routes when a saved file is later opened.

## Presets

Choose the simplest preset that matches the topology:

- `horizontalFlow` or `verticalFlow`: linear processes and dominant pipelines
- `horizontalTree` or `verticalTree`: hierarchies and ownership trees
- `radialTree`: genuinely radial relationships
- `organic`: small undirected networks where hierarchy would mislead

With draw.io Desktop 31.4.5 (checked 2026-09-23), the CLI accepts `--layout <name|json>` and applies the layout after opening and before export. Its XML rewrite wraps a bare `mxGraphModel` in `<mxfile>` and drops the `adaptiveColors` and `background` model attributes, so use the bundled wrapper to restore them before validation:

```bash
python3 scripts/apply_auto_layout.py input.drawio laid-out.drawio horizontalFlow
```

Use a new output path during iteration so the semantic input remains available until the laid-out result is verified.

## ELK and obstacle-aware routing

Use explicit JSON for a nested architecture or when the preset leaves poor routes:

```json
[
  {
    "layout": "elkLayered",
    "config": {
      "elk.direction": "RIGHT"
    }
  },
  {
    "layout": "orthogonalEdge"
  }
]
```

Pass the compact JSON array as the wrapper's final argument. `orthogonalEdge` is the obstacle-aware route in the [JSON layout specification](https://www.drawio.com/docs/reference/json-layout-specification/): it keeps every vertex in place and reroutes connectors around them. Write it as a JSON entry: the specification and the vendored upstream plugin skill also describe a `--layout libavoid` shorthand, but on draw.io Desktop 31.4.5 that shorthand hangs until killed, as an unknown layout name does, instead of failing. For containers, a `childLayout` can arrange children before the parent layout is applied. Preserve containment and rerun both validators after layout.

## Explicit routing

Use `edge-routing.md` when a known layout requirement or the rendered result calls for explicit ports or corridors, including when:

- an edge crosses a component or label;
- request and response paths overlap;
- an edge exits from the wrong side;
- a return path has no dedicated corridor; or
- automatic layout obscures a required semantic group.

For a bounded correction, fix the affected route and retain working geometry. For a requested redesign or reference match, adjust the composition as needed while preserving the semantic inventory.
