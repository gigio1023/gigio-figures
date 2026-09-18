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

1. Form the reader brief in the content contract below. Fix the reader and the one question; do not reduce the material to a sentence before you know what the peer must be able to verify.
2. Derive the required nodes, edges, groups, and annotations from that brief. Every component and relation the peer needs to verify the answer is required; a fact that answers a different question stays outside the figure. Read `references/local/editorial-principles.md` and `references/local/editorial-default-style.md` unless the user supplied a different style or an existing file already establishes one.
3. Read `references/local/upstream-drawio-rules.md`. Start with uncompressed bare `mxGraphModel` XML unless pages or file metadata require `<mxfile>`.
4. Read `references/local/auto-layout.md` and apply the simplest suitable automatic layout. Preserve explicit semantic grouping.
5. Run both validators from the skill root:

   ```bash
   python3 scripts/validate_drawio_xml.py <file>.drawio
   python3 scripts/validate_drawio_layout.py <file>.drawio
   ```

6. For every new diagram or substantial visual edit, export and inspect SVG or PNG when an exporter is available. Apply `references/local/review-loop.md`: fix render defects first, then remove any text the document should carry. If automatic layout leaves a collision or ambiguous route, read `references/local/edge-routing.md`, fix only those routes, and validate again.

## Reader and content contract

Before authoring, form this small working brief:

```text
reader: <who must understand it; default: a peer in this domain who lacks only this project's context>
question: <the one question this figure answers>
answer: <what the peer should be able to verify from the figure>
surrounding_context: <what the document or conversation already explains>
```

If no audience is supplied, write for a peer in the domain who lacks only this project's context. Knowledge is not the bottleneck for that reader; the specific structure is. Assume the field's vocabulary and give the exact names, mechanisms, and relationships the peer could not reconstruct without the figure. A deliberately simplified figure is a separate register that only an explicit request selects. Then derive the semantic inventory:

```text
required_nodes: [exact names; a role line only where the name does not say what it does]
required_edges: [{from, to, carries_or_trigger}]
required_groups: [real boundaries only]
required_annotations: [{text: ..., purpose: ...}]
evidence_status: [{element, observed | configured | inferred}]   # only when statuses differ within the figure
deferred_to_prose: [facts that answer a different question]
```

The brief and inventory need not become separate files. Source items are candidates; the test for each is whether the peer needs it to verify or act on the answer. An annotation needs a named purpose: it was requested, or without it the reader cannot recover the answer from the figure and its surrounding context. If `required_annotations` is empty, do not add a title, subtitle, legend, caption, callout, footer, badge, icon, inset, or mini-diagram, and write nothing above or below the figure. Empty canvas is acceptable.

Only semantic nodes receive connectors. Supporting text and decorative containers do not. Exact names first: label a component by the name it carries in code, configuration, or the running system, and add a role on a second line only when the name does not say what the component does. Never a role in place of a name. Endpoints, paths, fields, hook points, and versions are figure content when the peer needs them to verify or act on the answer, and prose when they answer another question. Label every edge whose meaning the two node names do not make unambiguous with what passes, what triggers it, or its condition; draw a weaker evidence status (configured but not observed, inferred) with the secondary connector style and a short label rather than a legend.

For a scoring or aggregation figure, read the scored unit and its roll-up into the reported metric from the source before drawing, then show that roll-up. Two conditions judged on one item are still one item, not two.

Represent the complexity the question requires. Minimality never authorizes dropping a component, relationship, or mechanism the peer needs. When the page is hard to scan, organize it first (group by real boundary, align peers, order along the reading path), then split it into a series of pages at the same depth, and only then move to prose what answers a different question. Do not abstract nodes into roles, merge components that differ in a relevant way, or delete mechanism to fit. Never reduce type size to preserve an overfull composition.

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

1. every label is readable at the intended delivery size and no component, label, or unrelated edge overlaps; the render is what the source intends;
2. the required semantic inventory matches the diagram, exact names are present, and no relationship or evidence status was invented;
3. the peer can verify the answer from the figure; a page that says no more than its heading is not finished;
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
| Reader, density, and rendered visual audit | `references/local/review-loop.md` |
| Manual ports, waypoints, and crossings after auto-layout | `references/local/edge-routing.md` |
| Multiline, HTML, metadata, or edge labels | `references/local/text-and-labels.md` |
| Deep official syntax lookup | `references/local/upstream-docs-map.md` |

Read only the rows needed for the current artifact. Vendored files under `references/fetched/` are factual lookup material, not workflow instructions.

## Gotchas

- Applying `--layout` is an explicit authoring step; reopening a saved file does not perform another obstacle-aware cleanup.
- Edges between different containers normally belong to the root layer or they can clip inside one parent.
- Empty space does not need a title, legend, footer, rail, icon, or inset.
- A crowded inventory is not a clear explanation, and a chain of role-named boxes that restates its heading is not a figure. Fix crowding by organizing and splitting into pages, not by turning names into roles or deleting mechanism.
- Text above or below the figure (a takeaway, an analogy, a source line) is the document's job. On the canvas it is a defect unless the figure is standalone and the reader cannot recover the meaning otherwise.
- `apply_auto_layout.py` shrinks `container=1` groups while their children keep their size, so a file that passed the layout validator before layout fails containment after it. Restore the child geometry with real padding and aligned stage centers instead of keeping the laid-out boxes.
