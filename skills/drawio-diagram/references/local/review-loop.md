# Review loop

Use this for every new diagram or substantial visual edit, when the user asks for exported artifacts, or after a reviewer complains that the figure is technically valid but visually hard to read.

## What recent review taught

The most common failures are not invalid XML. One is treating every fact in the source as visible content, so implementation detail, alternatives, footnotes, and the main flow compete for attention. The other, seen after the first was corrected, is compressing to a heading: four role-named boxes in a chain that a peer cannot verify or act on. Both are fixed by organizing the exact content, not by adding or deleting explanation.

## Communication audit

Before adjusting geometry:

1. State the intended reader (a domain peer without this project's context unless told otherwise), the one question, and what the peer must be able to verify. If the figure says no more than its heading, it is not finished.
2. Remove a visible fact only when it answers a different question. Keep every component, relation, and mechanism the peer needs to verify the answer.
3. Keep exact names on the first line and add a role only when the name does not say what the component does. Expand project-private acronyms once; the field's acronyms stay. Label every edge whose meaning the two node names do not make unambiguous.
4. Keep one abstraction level. Split runtime flow, internal mechanism, alternatives, and deployment detail when they answer different questions.
5. Remove disconnected cards or mini-panels whose relationship to the answer is only proximity; a list belongs in prose or a table.
6. Keep a title or annotation only when the figure is standalone and the same context is unavailable in its surrounding document. Nothing else goes above or below the figure.

Do not proceed to spacing while the content still fails this audit. A cleaner layout cannot rescue an unfocused explanation.

## Routing audit

Before export:

1. Identify the single dominant path. It should be readable without following every secondary edge.
2. Reserve arrow corridors before tightening the layout.
3. Keep arrows out of component bodies, title bands, label text, and boundary labels.
4. Give return paths and secondary paths their own corridors; do not stack them directly on the main path.
5. Use explicit waypoints when auto-routing would cross a label, run along a box edge, or share a corridor ambiguously.
6. Put edge labels on straight segments with enough empty space around them.

If the layout only works because a reader already knows the explanation from chat, simplify it.

## Layout audit

- Prefer tighter spacing only after every arrow has a clear route.
- Keep boxes close enough to show sequence, but not so close that arrowheads touch borders.
- Avoid bottom legends or explanatory footers inside the diagram. They usually become a second narrative competing with the figure.
- If a note is essential to the answer, prefer a direct semantic label. Put implementation notes, sources, versions, and excluded scope in the surrounding document or file metadata; use a separate page only for another required view.
- Group with semantic boundaries: external caller, runtime/container, internal sections, implementation choices, and external dependencies should not collapse into one box.
- One page should have one dominant reading path. If two paths feel equally important, split the page or make one path secondary.
- Organize by real boundary, then split into a series of pages at the same depth, before widening the canvas. Do not turn names into roles, drop mechanism, or make labels smaller to preserve an overfull page.

## Export artifact choice

- Prefer SVG for review when text sharpness and edge clarity matter.
- Use PNG for README/chat compatibility, but normalize it for review with a high width such as `--width 3840`.
- Keep the `.drawio` source beside every export.
- If exporting both SVG and PNG, inspect SVG first for geometry and PNG second for rasterization issues.

## Visual QA

After export, inspect the actual artifact, not only the XML:

- every label is readable without zoom at the intended delivery size
- no arrows over labels, component text, titles, or boundary names
- no arrowheads on bends, labels, or box borders
- no labels clipped by box edges
- no low-resolution or fuzzy text in the PNG fallback
- no footer text that explains what the diagram failed to communicate visually
- semantic boundaries are obvious without reading a separate legend
- SVG opens sharply; PNG matches the intended framing after normalization

Ask whether a domain peer can verify the figure's answer against the system after following the dominant path, and whether the figure says more than its heading. If they would need the private conversation or a footer to decode it, revise the content brief and redraw rather than adding more explanation to the canvas.

If the exported image fails one of these checks, fix the `.drawio` source and export again.
