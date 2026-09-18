# Editorial figure principles

Use these rules for the default editorial look across diagram backends.

## Reader before structure

- Treat a diagram as a small document with one communicative job. Before choosing shapes, identify the intended reader, the question the figure must answer, and the context the surrounding document already supplies.
- The default reader is a peer in the domain who lacks only this project's context. Knowledge is not the bottleneck for that reader; the specific structure is. Assume the field's vocabulary, and supply the exact names, mechanisms, and relationships the peer could not reconstruct without the figure. A deliberately simplified figure for a reader outside the field is a separate register, drawn only on explicit request.
- A figure answers its question in a form the peer can verify against the system, not only read. If the visible content restates the caption or the section heading, it is not yet a figure.
- Exact names first. Label a component by the name it carries in code, configuration, or the running system, and add a role on a second line only when the name does not say what the component does. Do not replace a name with a role, and do not hide a name in parentheses behind one. Acronyms the field uses stay as they are; project-private acronyms are expanded once.
- Edges carry mechanism. A connection states what passes, what triggers it, or under which condition it holds whenever the two node names do not make the relation unambiguous. Direction alone is enough only when the names already say it.
- Compress like a dashboard panel, not like a disclosure. The figure's space goes to the names and the mechanism the reader came for. Quantities, timestamps, counts, sample sizes, evidence qualifiers, and provenance are prose beside the figure and enter it only when the question is about them; a limitation stays only next to the one element whose reading it changes, in the fewest words that change it. Stuffing them in to be safe is the opposite failure of abstracting names into roles, and it costs the reader the same attention.
- Source material is evidence. Include a fact when the peer needs it to verify or act on the answer; leave out a fact when it answers a different question. Versions, provenance, and omitted scope belong in prose or file metadata unless the figure is about them.
- Keep one dominant reading path per figure. When the material holds several questions, draw a series of figures at the same depth rather than one abstracted figure.
- Every visible block needs an explicit semantic relationship to the answer. Do not arrange disconnected facts or mini-panels side by side to make the page look substantial; use prose, a table, or a separate figure.
- Complexity the answer needs stays in the figure. Complexity in the source alone does not make it necessary in the figure.

## Content before composition

- Derive the semantic nodes, relationships, groups, and annotations from the reader's question. Do not copy the source inventory wholesale, and do not shrink the inventory to make composition easier.
- Empty space is acceptable. Never add a title, subtitle, legend, caption, callout, rail, strip, badge, icon, inset, or mini-diagram to fill or balance the page, and never write explanatory text above or below the figure unless the figure is standalone and the reader cannot recover the meaning otherwise. Captions, figure numbers, the stated takeaway, and any analogy belong to the surrounding document.
- A supporting element is allowed only when it supplies context the intended reader needs and a direct node or edge label cannot carry. Remove it when the surrounding document already supplies that context.
- Use the simplest familiar shape that expresses each role. Shape variety must encode a real distinction.
- When a figure is hard to scan, fix it in this order: organize (group by real boundary, align peers, order along the reading path, make edge meanings consistent); split into a series of figures at the same depth; move to prose only what answers a different question. Do not abstract nodes into roles, merge components that differ in a relevant way, or delete mechanism to make the figure fit. Grow the canvas downward when needed; never shrink type.

## Visual language

- The rendered figure is the deliverable, not the source. Every label is legible at the delivery size, nothing is clipped, no edge crosses unrelated content, and the geometry is what the source intends. A correct source with a wrong render has failed.
- White canvas, near-black ink, no shadows, and no gradients.
- Use one accent family per figure. A second family is reserved for a real two-system comparison; coral may mark at most one exceptional element.
- Use soft rounded rectangles, thin uniform strokes, and unfilled arrowheads.
- Use a monospace voice for entities, protocols, axes, and technical labels; use a sans-serif voice for human commentary, plain-language figures, or an explicitly required title.
- Keep labels short. One or two lines per component is the normal maximum; the second line is a role or a mechanism, not a sentence.
- Use whitespace and alignment before adding container borders.
- Judge legibility at the intended delivery size, not while zoomed into the source. Every label must remain readable without magnification.

## Identity boundary

This is an independent editorial design language, not OpenAI branding. Never add the OpenAI logo, blossom, or wordmark; never imply affiliation. OpenAI Sans is not included. Use the substitute font stacks in `editorial-tokens.json`.
