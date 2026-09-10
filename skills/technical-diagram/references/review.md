# Diagram review

Review the rendered artifact, not only the source.

## Communication audit

- State the intended reader, the question, and the one-sentence answer before judging the composition. If the figure has two unrelated answers, split it or choose the one the request prioritizes.
- Check every visible fact against the answer. Source facts that merely prove research happened belong in prose, metadata, or a separate figure.
- Replace private names with reader-facing roles. Keep an exact internal name in parentheses only when knowing that identity changes the answer. Expand acronyms once; remove code identifiers that do not matter to the question.
- Keep a single abstraction level. A runtime path, internal algorithm, alternatives list, and deployment inventory should not compete on one canvas.
- Remove disconnected cards or mini-panels whose relationship to the answer is only proximity. Use prose or a table when the content is a list rather than a topology.
- Use a title or other supporting annotation only when the figure is standalone and that context is unavailable elsewhere. It must not restate the diagram or explain a composition that remains unclear.

## Semantic audit

- Every required node exists once with an unambiguous label.
- Every required relationship exists with the correct direction.
- Containers express real ownership or boundaries; they are not decoration.
- External systems, implementation choices, and internal components remain distinguishable.
- No relationship, category, conclusion, or provenance was invented.

## Visual audit

- The dominant reading path is obvious without the surrounding conversation.
- At the delivery width (720px unless the document says otherwise), every label renders at 12px or more. `scripts/validate_svg.py --target-width` computes the scaled size and is the floor, not the judgment; a label can pass the floor and still be hard to read.
- Labels fit without clipping, awkward wrapping, or touching borders; the validator's crowding warning marks labels with less than 8px inside their box.
- Edges do not cross unrelated nodes, labels, or container titles.
- Parallel and return paths remain distinguishable.
- One accent family is used consistently and color is not the only distinction.
- Shapes, strokes, arrowheads, and typography match the bundled editorial principles.

## Density audit

When the figure is hard to scan, fix it in this order:

1. Remove content that answers another question.
2. Replace implementation detail with a role-first label.
3. Combine repeated peers only when they have the same relevant relationship.
4. Move versions, provenance, exact endpoints, and field names outside the figure unless they are the subject.
5. Split by abstraction level.

Change the layout direction or tighten spacing before enlarging the canvas, and do not make type smaller or the canvas wider than the delivery width before exhausting these options.

## Negative-space audit

Remove and rerender when any answer is yes:

- Is there unrequested text or a decorative region above or below the diagram?
- Can a title, legend, caption, callout, badge, icon, inset, or mini-diagram be deleted without changing the required meaning?
- Does a note repeat a node or edge label?
- Was any element added solely to center, fill, or balance empty space?
- Can a legend be replaced by direct labels?
- Is a footer, source line, excluded-scope list, or alternatives panel carrying material that belongs in the surrounding document?

Empty space is not a defect. Fix an unclear composition by moving, grouping, or shortening existing semantic content before adding anything new.
