---
name: drawio-diagram
description: >
  Use when the user explicitly wants a native .drawio artifact, asks to edit an
  existing draw.io file, needs draw.io metadata or pages, or requests draw.io
  export to SVG, PNG, or PDF. Produces editable mxGraph XML with automatic
  layout first, manual routing only when needed, and structural plus rendered
  quality checks. NOT for generic technical diagrams or measured data charts.
---

# Draw.io Diagram

Produce a valid, readable native `.drawio` file. Native XML is the source of truth and remains beside any export. This skill exists for draw.io compatibility and editability; a generic technical diagram belongs to `technical-diagram`.

## Quick path

1. Form the reader brief in the content contract below. Reduce the source to one question and one answer before choosing cells.
2. Derive the required nodes, edges, groups, and annotations from that brief. Read `references/local/editorial-principles.md` and `references/local/editorial-default-style.md` unless the user supplied a different style or an existing file already establishes one.
3. Read `references/local/upstream-drawio-rules.md`. Start with uncompressed bare `mxGraphModel` XML unless pages or file metadata require `<mxfile>`.
4. Read `references/local/auto-layout.md` and apply the simplest suitable automatic layout. Preserve explicit semantic grouping.
5. Run both validators from the skill root:

   ```bash
   python3 scripts/validate_drawio_xml.py <file>.drawio
   python3 scripts/validate_drawio_layout.py <file>.drawio
   ```

6. For every new diagram or substantial visual edit, export and inspect SVG or PNG when an exporter is available. Apply `references/local/review-loop.md`. If automatic layout leaves a collision or ambiguous route, read `references/local/edge-routing.md`, fix only those routes, and validate again.

## Communication and content contract

Before authoring, form this small working brief:

```text
reader: <who must understand it>
question: <the one question this figure answers>
answer: <one sentence the reader should leave with>
surrounding_context: <what the document or conversation already explains>
```

If no audience is supplied, write for a technically literate reader who has no private project context. Then derive the minimum semantic inventory:

```text
required_nodes: [...]
required_edges: [...]
required_groups: [...]
required_annotations: [{text: ..., purpose: ...}]
deferred_to_prose: [...]
```

The brief and inventory need not become separate files. Raw source items are candidates, not requirements. An annotation needs a named purpose: it was requested, or without it the reader cannot recover the answer from the figure and its surrounding context. If `required_annotations` is empty, do not add a title, subtitle, legend, caption, callout, footer, badge, icon, inset, or mini-diagram. Empty canvas is acceptable.

Only semantic nodes receive connectors. Supporting text and decorative containers do not. Prefer reader-facing roles and familiar shapes. If an exact internal name matters, label it as `role (exact name)`. Show endpoints, fields, versions, and implementation steps only when the question is about them.

For a scoring or aggregation figure, read the scored unit and its roll-up into the reported metric from the source before drawing, then show that roll-up. Two conditions judged on one item are still one item, not two.

Represent the complexity needed for the answer, not every available fact. Remove details that answer another question, combine repeated peers only when their distinctions are irrelevant, and split different abstraction levels before enlarging the canvas. Never reduce type size to preserve an overfull composition.

## Native XML baseline

- Include `mxGraphModel` root cells `0` and `1`; use `adaptiveColors="auto"`.
- Use uncompressed XML and stable unique IDs. Do not emit XML comments.
- Emit vertices before edges. Every edge has source and target IDs plus a child `<mxGeometry relative="1" as="geometry" />`.
- Use `html=1;` and XML-escape label HTML. A literal `\n` is not a line break; use `&lt;br&gt;` or `&#xa;`.
- Use `swimlane` or `container=1` only for real grouping. Use `<object>` or `UserObject` only when metadata improves editability.

Read `references/local/text-and-labels.md` only when labels need multiline HTML, edge-label positioning, metadata, or another nontrivial treatment.

## Layout decision

For a bounded edit to an existing file, retain cell IDs, pages, metadata, and unaffected geometry. Apply layout only to the changed region when needed; rebuilding the whole diagram is not a prerequisite for correcting one label or connection.

Automatic layout is the default for new files:

- a linear process: `horizontalFlow` or `verticalFlow`;
- a hierarchy: `horizontalTree` or `verticalTree`;
- nested or routed architecture: explicit ELK JSON, optionally followed by `orthogonalEdge`.

Automatic layout is an explicit authoring step, not a viewer cleanup pass. The saved file must already contain an acceptable layout. Use fixed ports and waypoints only for remaining obstacles, parallel lanes, or return corridors. Never add invisible spacer nodes or supporting bands to manipulate geometry.

## Verification

XML validation is blocking. Treat layout warnings as evidence to inspect and fix; accept one only when the rendered source is still clear and the tradeoff is reported. Validators do not detect every clipped label or visual collision.

Before finishing, confirm:

1. the intended reader can identify the subject and answer without private vocabulary or missing chat context;
2. the required semantic inventory matches the diagram;
3. every label is readable at the intended delivery size and no component, label, or unrelated edge overlaps;
4. the dominant path and secondary paths are distinguishable;
5. every visible element earns its place; and
6. a render was inspected for every new diagram or substantial visual edit, or the missing exporter was reported.

Deliver after these checks pass. Revalidate for a relevant edit or defect; do not add formats or redraw unaffected pages to extend verification.

## Exports

Use an existing draw.io CLI; do not install one for a source-only request:

```bash
drawio -x -f svg -e -b 10 -o <name>.drawio.svg <name>.drawio
drawio -x -f png -e -b 10 --width 3840 -o <name>.drawio.png <name>.drawio
```

Prefer SVG for sharp text. If the exporter is unavailable, deliver the valid `.drawio` source and report that export and visual inspection were unavailable.

## Output

Lead with the artifact created or changed. Report both validator results, the layout route used, and the exact export inspected. Keep `<name>.drawio` beside `<name>.drawio.svg`, `<name>.drawio.png`, or `<name>.drawio.pdf`. Name any accepted warning or unverified rendering.

## Reference router

| Need | Read |
| --- | --- |
| Content and shared appearance invariants | `references/local/editorial-principles.md` |
| draw.io translation of the editorial tokens | `references/local/editorial-default-style.md` |
| Required XML structure and export rules | `references/local/upstream-drawio-rules.md` |
| Automatic layout and current CLI routes | `references/local/auto-layout.md` |
| Communication, density, and rendered visual audit | `references/local/review-loop.md` |
| Manual ports, waypoints, and crossings after auto-layout | `references/local/edge-routing.md` |
| Multiline, HTML, metadata, or edge labels | `references/local/text-and-labels.md` |
| Deep official syntax lookup | `references/local/upstream-docs-map.md` |

Read only the rows needed for the current artifact. Vendored files under `references/fetched/` are factual lookup material, not workflow instructions.

## Gotchas

- Applying `--layout` is an explicit authoring step; reopening a saved file does not perform another obstacle-aware cleanup.
- Edges between different containers normally belong to the root layer or they can clip inside one parent.
- Empty space does not need a title, legend, footer, rail, icon, or inset.
- Do not reproduce every term found in source material. A crowded but complete inventory is not a clear explanation.
- `apply_auto_layout.py` shrinks `container=1` groups while their children keep their size, so a file that passed the layout validator before layout fails containment after it. Restore the child geometry with real padding and aligned stage centers instead of keeping the laid-out boxes.
