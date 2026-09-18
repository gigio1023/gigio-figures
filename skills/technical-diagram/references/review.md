# Diagram review

Review the rendered artifact, not only the source. Fix render defects before judging content; a figure that says the right thing but renders wrong has failed.

## Render audit

- At the delivery width (720px unless the document says otherwise), every label renders at 12px or more. `scripts/validate_svg.py --target-width` computes the scaled size and is the floor, not the judgment; a label can pass the floor and still be hard to read.
- Labels fit without clipping, awkward wrapping, or touching borders; the validator's crowding warning marks labels with less than 8px inside their box.
- Edges do not cross unrelated nodes, labels, or container titles, and arrowheads land on borders, not on text.
- Parallel and return paths remain distinguishable, and the geometry is what the source intends: nothing moved, hidden, or overlapped by the layout engine.
- One accent family is used consistently and color is not the only distinction.
- Shapes, strokes, arrowheads, and typography match the bundled editorial principles.

## Reader audit

- State the intended reader, the question, and what the reader must be able to verify before judging the composition. The default reader is a peer in the domain who lacks only this project's context; only an explicit request changes that.
- Apply the heading test: if the visible content says no more than the caption or the section heading would, the figure is not finished. A four-box chain of role names fails here.
- Check every visible fact against the question. Remove a fact only when it answers a different question; keep every component, relation, and mechanism the peer needs to verify or act on the answer.
- Exact names are on the first line; a role appears on a second line only when the name does not say what the component does. No name has been replaced by a role or pushed into parentheses behind one. Project-private acronyms are expanded once; the field's acronyms stay.
- Every edge whose meaning the two node names do not make unambiguous carries a label: what passes, what triggers it, or its condition.
- Where evidence status differs within the figure, the weaker status (configured but not observed, inferred) uses the secondary connection style and a short label, and no legend was added.
- Keep one dominant reading path. When the material holds several questions, the fix is a series of figures at the same depth, not one abstracted figure.
- Remove disconnected cards or mini-panels whose relationship to the answer is only proximity. Use prose or a table when the content is a list rather than a topology.
- Use a title or other supporting annotation only when the figure is standalone and that context is unavailable elsewhere. It must not restate the diagram or explain a composition that remains unclear.

## Semantic audit

- Every required node exists once with an unambiguous label.
- Every required relationship exists with the correct direction and, where needed, its mechanism.
- Containers express real ownership or boundaries; they are not decoration.
- External systems, implementation choices, and internal components remain distinguishable.
- No relationship, category, conclusion, evidence status, or provenance was invented.

## Density audit

When the figure is hard to scan, fix it in this order:

1. Organize: group by real boundary, align peers, order nodes along the reading path, and make edge meanings consistent.
2. Split into a series of figures at the same depth: an overview and one figure per mechanism, each complete for its question.
3. Move to prose only what answers a different question: versions, provenance, alternatives, scope.

Do not abstract nodes into roles, merge components that differ in a relevant way, shorten a name into a description, or delete an edge label to make the figure fit. Grow the canvas downward; never make type smaller or the canvas wider than the delivery width.

When the figure fails the delivery-width gate instead, follow the fix order in SKILL.md under "Delivery size": layout engine, then direction, then labels and splitting, then spacing.

## Negative-space audit

Remove and rerender when any answer is yes:

- Is there any text above or below the diagram (a takeaway, an analogy, a source line, a caption) that the surrounding document could carry?
- Can a title, legend, caption, callout, badge, icon, inset, or mini-diagram be deleted without changing the required meaning?
- Does a note repeat a node or edge label?
- Was any element added solely to center, fill, or balance empty space?
- Can a legend be replaced by direct labels?
- Is a footer, source line, excluded-scope list, or alternatives panel carrying material that belongs in the surrounding document?

Empty space is not a defect. Fix an unclear composition by moving, grouping, or splitting existing semantic content before adding anything new, and never by removing the names or mechanism the peer needs.
