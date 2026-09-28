# ELI5 figure review

Review the rendered artifact, not only the source, and fix render defects before judging content.

## Render audit

- The lint from `scripts/render.mjs` reports zero errors at the delivery width (a 720u figure in a column of about 704 px unless stated); it is the floor, not the judgment.
- No label is clipped, wraps awkwardly, or touches its border; no arrow crosses unrelated content; arrowheads land on borders, not on text.
- The geometry is what the source intends: the one path reads in order and the single branch is visibly a branch.
- One focal hue on the part the reader must grasp, neutral ink elsewhere, the shared tokens in both themes. No icons, emoji, or drawings of people.

## Truth audit

- Every relation drawn exists in the exact figure or inventory.
- Every merge in the reduction record joins components that share the relation shown; components that differ in that relation are not merged.
- Nothing hidden changes the reader's answer, and each hidden item has its stated reason.
- Where the analogy would imply a false relation, the figure draws the real one and the prose says so.
- The reduction record is complete: kept, merged, hidden, analogy break.

## Reader audit

- Ten-second test: a reader with no domain background, given the figure alone, can say what happens and to whom, in order. When it fails, use fewer concepts or a better analogy, never more words.
- At most five concepts, one path, at most one branch.
- Every arrow says what moves or what happens; no magic box.
- Labels are plain words; an exact name appears only as a second line where the reader will meet it again.
- No talking-down words: "simply", "just", "basically", "magic".

## Negative-space audit

Remove and rerender when any answer is yes:

- Is there anything above or below the figure: an analogy sentence, caption, mapping table, legend, footer, or "in reality" panel?
- Can any element be deleted without changing what the reader takes away?
- Does a label repeat what an arrow already says?

The analogy sentence, the literal mapping, the analogy's limit, and the reduction record belong in the prose beside the figure or in the response.
