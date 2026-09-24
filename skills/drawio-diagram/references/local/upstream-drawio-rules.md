# Upstream draw.io rules (local digest)

This file is the workflow-facing digest the skill enforces. Technical XML and style references from `jgraph/drawio-mcp` (Apache-2.0) are vendored under `references/fetched/` for provenance and exact syntax lookup. Only Markdown prose line wrapping has been adjusted locally in some files; upstream content and code examples remain unchanged.

For an exact XML/style definition, upstream technical facts win. For workflow, layout judgment, model prompting, and verification, this local overlay and `SKILL.md` win; do not inherit rigid grids, reasoning narration, or skipped verification from older vendored agent instructions.

**Known upstream trap:** the "Edge routing & layout passes" section of the vendored `references/fetched/xml-reference.md`, and the "Reasoning budget" and "Edges" sections that tell the model not to add waypoints or fixed ports, assume a drawio-mcp tool call whose `routing: "libavoid"` or `postLayout: "elk"` field runs a pass before anyone sees the result. A `.drawio` file written directly gets neither, and the same section states that draw.io's built-in router has no obstacle avoidance. New files should use the explicit layout routes in `references/local/auto-layout.md`; the saved result must already be acceptable. Use `references/local/edge-routing.md` only for routes that remain ambiguous after that pass. The vendored Claude Code plugin skill also documents a `--layout libavoid` shorthand that hangs on draw.io Desktop 31.4.5; `references/local/auto-layout.md` gives the form that works. The nested-container example in the vendored XML reference still files the `web1` to `web2` edge on the layer although both endpoints sit inside `vpc`; follow the edge-parent rule below, not that example.

**Vendored agent steps that do not apply here:** `references/fetched/claude-code-plugin-drawio-SKILL.md` tells its agent to fetch and follow unpinned `raw.githubusercontent.com/.../main/` references, to open diagrams through an `app.diagrams.net/#create=` URL, to locate draw.io on Windows with `reg.exe` or `powershell.exe -ExecutionPolicy Bypass`, and to delete the source `.drawio` after export. Read that file for syntax facts only. Use the pinned copies under `references/fetched/` instead of fetching `main`, write and export local files through the CLI path in `SKILL.md`, and keep the source file.

## Required XML structure

- Use native `.drawio` XML.
- Prefer a bare `mxGraphModel` for a single-page generated diagram. Wrap it in `mxfile > diagram` when multiple pages, file variables, or metadata require the full document form.
- Include root cells:
  - `id="0"`
  - `id="1" parent="0"`
- Set `adaptiveColors="auto"` on `mxGraphModel`
- **NEVER emit XML comments (`<!-- -->`)** - strictly forbidden; they waste tokens and can cause parse errors
- Use the full `<mxfile>` form when file-level variables or human-editable metadata are useful

## Edge rules

- Every edge `mxCell` must contain `<mxGeometry relative="1" as="geometry" />` as a child element - never self-closing
- Emit all vertices before the edges that reference them
- File each edge at the innermost container that holds both endpoints: `parent="<container_id>"` when both ends sit inside the same container at any nesting depth, and `parent="1"` only when an endpoint is outside every container. Auto-layout reads an edge's coordinates in its parent's frame, so an edge filed further out than its endpoints is laid out in the wrong place
- Connection sides, fixed vs floating terminals, and routing recipes: `references/local/edge-routing.md`
- Use `edgeStyle=orthogonalEdgeStyle` for complex routing with 2+ bends
- Use `edgeStyle=elbowEdgeStyle;elbow=vertical;` for simple 0-1 bend connections
- Use one consistent edge style per diagram type (all orthogonal, all straight, all curved - never mixed)
- Add explicit waypoints when orthogonal routing would create overlap
- Each edge exits and enters as a >=20px straight perpendicular stub
- Bundle fan-out / fan-in edges into a shared trunk before branching

## Container rules

- `swimlane;startSize=30;` for titled panels
- `group;` for invisible grouping (includes `pointerEvents=0` so child connections aren't captured)
- `container=1;pointerEvents=0;` for decorative containers that shouldn't capture connections
- Child cells set `parent="containerId"` and use coordinates relative to the container
- Edges to children inside containers naturally cross the container boundary - this is correct; do not route around it

## Metadata and variables

- `<object>` / `<UserObject>` wrappers can store custom metadata on cells
- `placeholders="1"` on `<object>` enables `%name%` substitution in `label`
- `<mxfile vars='{"project":"Atlas"}'>` can hold file-level variables for reusable templates
- Tags require the `<object>` wrapper; plain `mxCell` cannot have tags

## Export rules

- Keep `.drawio` as the source of truth - **do NOT** delete the source after export (diverges from the upstream Claude Code plugin skill)
- Export only when the draw.io desktop CLI is available
- If export is unavailable, do not fake success; leave the `.drawio` file
- `.drawio.png`, `.drawio.svg`, and `.drawio.pdf` (with `--embed-diagram` / `-e`) carry the diagram XML embedded in the exported file - any of them can be reopened in draw.io to continue editing

## Validation rules

- Run `python3 scripts/validate_drawio_xml.py <file.drawio>` before claiming the XML is valid
- Run `python3 scripts/validate_drawio_layout.py <file.drawio>` before claiming the layout is clean
- When the validators and the eye test disagree, trust the failure mode and fix it instead of arguing with it
