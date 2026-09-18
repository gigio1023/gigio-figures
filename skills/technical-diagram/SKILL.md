---
name: technical-diagram
description: >
  Draw a technical diagram, architecture figure, system map, process flow, or box-and-arrow schematic as a compact editorial SVG for a domain peer: exact names, mechanism on the edges, the topology the question needs, legible at the delivery width. Use for any diagram request that does not name a native format. NOT for native .drawio files (drawio-diagram), Mermaid-only output, measured data charts (data-chart), image generation, or a deliberately simplified figure for readers outside the field (eli5-figure, explicit request only).
---

# Technical Diagram

Produce the accurate technical figure a peer can verify, drawn so it stays readable where it will be shown. Two routes give the same editorial look from the same tokens: a semantic D2 source laid out by ELK, and direct SVG from the bundled template. SVG is the deliverable on both routes; keep the source beside the render so the figure is reproducible without a GUI.

## Quick path

1. Form the reader brief and semantic inventory below. Fix the reader and the one question before choosing nodes; every component and relation the peer needs to verify the answer is required.
2. Read `references/editorial-principles.md`, choose the route in "Route decision", then read `references/d2-authoring.md` or `references/direct-svg.md`.
3. D2 route: copy `assets/editorial-theme.d2` beside the source, import it, author only the semantic structure, run `d2 fmt <file>.d2`, then render and gate:

   ```bash
   bash scripts/render_d2.sh <file>.d2 <file>.svg
   ```

   Direct SVG route: start from `assets/direct-svg-template.svg`, replace the nodes and connections, and gate:

   ```bash
   python3 scripts/validate_svg.py --target-width 720 --tokens assets/editorial-tokens.json <file>.svg
   ```

   Run both from the skill directory; the scripts resolve their own assets.

4. Inspect the render, not only the source. Without an SVG viewer, make a PNG proof: `D2_PNG_PROOF=1` with the render script on D2 v0.9.0 or newer, or `qlmanage -t -s 1440 -o <dir> <file>.svg` on macOS. Apply `references/review.md`, fix render defects first and content second, and render again after each fix.

## Reader and content contract

Form this working brief before authoring. It is the comparison set for the finished source, not a questionnaire: infer it from the request and material, ask only when a missing relation or conflicting fact would change the answer, and continue the supported parts meanwhile.

```text
reader: <default: a peer in this domain who lacks only this project's context>
question: <the one question this figure answers>
answer: <what the peer should be able to verify from the figure>
surrounding_context: <what the document or conversation already explains>
delivery_width: <px; 720 unless the document says otherwise (Notion body, single column); a wide report may state 1180>
required_nodes: [exact names; a role on a second line only where the name does not say what it does]
required_edges: [{from, to, what passes or what triggers it}]
required_groups: [real boundaries only]
required_annotations: [{text, purpose}]   # empty means no title, legend, caption, callout, footer, badge, icon, or inset
deferred_to_prose: [facts that answer a different question; every count, timestamp, and qualifier]
```

The reader is a peer: knowledge is not their bottleneck, this project's structure is. Assume the field's vocabulary and supply the exact names, mechanisms, and relationships they could not reconstruct without the figure. Only an explicit request for a simplified figure changes the register, and that request is `eli5-figure`'s job.

Three content rules do most of the work; `references/editorial-principles.md` holds the full set.

- **Exact names first.** Label a component by the name it carries in code, configuration, or the running system; add a role on a second line only when the name does not say what it does. Never a role in place of a name. Paths, endpoints, fields, and hook points are content when the peer needs them to verify or act on the answer.
- **Edges carry mechanism.** Label a connection with what passes, what triggers it, or its condition whenever the two node names leave the relation ambiguous, and keep the label to the mechanism. `encrypt, JSON, HTTP` is mechanism; `configured, receipt not observed` is a caveat for the prose.
- **Compress like a dashboard panel, not a disclosure.** Quantities, timestamps, counts, sample sizes, evidence qualifiers, and provenance are prose beside the figure unless the question is about them. If an unconfirmed relation would mislead when drawn plainly, use the secondary connection style and let the prose say why, or leave it out.

When the figure is hard to scan: organize (group by real boundary, align peers, order along the reading path, make edge meanings consistent), then split into a series of figures at the same depth, then move to prose only what answers a different question. Do not abstract nodes into roles, merge components that differ in a relevant way, or delete mechanism to fit. Grow the canvas downward; never shrink type.

## Route decision

| Situation | Route |
| --- | --- |
| The figure is inlined into an HTML document that supplies its own fonts and color tokens | Direct SVG |
| The figure ships as a standalone file that must carry its own look (Notion upload, README, Slack) and `d2` is installed | D2 |
| An existing SVG must be edited, the user asks for SVG source, or the composition needs geometry D2 cannot express | Direct SVG |
| `d2` is not installed | Direct SVG. Do not install D2 silently. If the user explicitly asked for D2 source, write the valid `.d2` and report that the render is unverified. |

D2 buys automatic layout and fonts subsetted into the file, which matters when the SVG must look the same on every viewer. Direct SVG buys exact geometry, the document's fonts, and CSS color tokens, which matters inside a styled document. Both routes read `assets/editorial-tokens.json`, and a figure may move between routes without changing content. To edit an existing SVG, change only the affected groups and keep ids and untouched geometry; do not regenerate the file.

## Delivery size and labels

A figure wider than its column is scaled down by the host and its labels shrink with it. Keep the canvas no wider than the delivery width; when it must be wider, the smallest label still has to render at 12px or more after scaling. `scripts/validate_svg.py --target-width` computes this and fails the figure otherwise; the render script applies it through `DELIVERY_WIDTH` (default 720, `0` disables). Fix a failing figure in this order: on the D2 route switch the engine with `D2_LAYOUT=tala`, then `direction: down` or stacked rows, then shorter labels without dropped names and fewer nodes per row or a series, and only then tighter spacing. Never widen past the delivery width and never shrink type.

Korean labels use a sans stack and one voice per label; a mono Latin word inside a sans Korean label reads as two voices. On the D2 route the embedded fonts have no Hangul, so a standalone file needs a Hangul-capable TTF passed through `D2_FONT_MONO`; the font caveats are in `references/d2-authoring.md`. The D2 theme approximates the tokens (integer stroke, unfilled triangle arrowhead, bold and italic turned off); do not compensate with SVG decoration, and use direct SVG when exact geometry is part of the request.

## Verification

The render script formats, validates, renders, and runs the SVG gate, which fails labels under 12px at the delivery width and warns on crowding, off-palette colors, and token drift. Neither proves that the figure is readable or true. Confirm, in this order:

1. **Render:** at the delivery width every label is legible, nothing is clipped, no edge crosses unrelated content, and the geometry is what the source intends. A figure that says the right thing but renders wrong has failed.
2. **Meaning:** every required node, edge, direction, group, and annotation is present, and no relationship was invented.
3. **Verifiability:** the peer can check the answer against the system from this figure. If the visible content only restates the caption or section heading, the figure is not finished.
4. **Communication:** the peer can identify the subject and follow the reading path without the chat context; project-private acronyms are expanded once.
5. **Minimality:** every visible element changes the reader's understanding, no count, timestamp, or qualifier sits in a label, and nothing is written above or below the figure.

When these and any required project checks pass, deliver. Repeat only the affected checks after a fix; do not rerender for equally valid aesthetic alternatives.

## Output

Lead with the artifacts created. Report the route, the delivery width assumed, the validation results including the smallest rendered label size, the layout engine, and whether the render was visually inspected. Name any missing renderer, unverified render, accepted warning or layout defect, and fact deferred to prose. Keep the source (`<name>.d2` with `editorial-theme.d2`, or the hand-authored `<name>.svg`) beside the render.

## Reference router

| Need | Read or run |
| --- | --- |
| Full content and appearance rules | `references/editorial-principles.md` |
| D2 syntax, classes, layout engines and measured widths, fonts, Hangul, known limits | `references/d2-authoring.md` |
| Direct SVG structure, layout recipe, tokens, fonts, embedding | `references/direct-svg.md` |
| Render, reader, semantic, density, and negative-space audit | `references/review.md` |
| D2 render with the legibility gate (`D2_LAYOUT`, `DELIVERY_WIDTH`, `D2_PNG_PROOF`) | execute `scripts/render_d2.sh` |
| Standalone SVG check (structure, legibility, tokens) | execute `scripts/validate_svg.py` |
| Starting point for a hand-authored figure | `assets/direct-svg-template.svg` |
| A deliberately simple figure for a reader outside the field, on explicit request | the `eli5-figure` skill, which reduces this skill's exact figure |

Read only the route needed for the current artifact.

## Gotchas

- A successful render does not prove that labels, crossings, or grouping are readable; inspect the SVG or a PNG proof.
- The main source must keep `editorial-theme.d2` beside it, and the render script refuses an unformatted source. Apply `entity` to technical nodes and `flow` to connections; D2's default theme is not the style contract.
- Horizontal ELK rows are wide: the bundled four-node example is 1027px at default spacing and fails the 720px gate, TALA renders it at 647px and `direction: down` at 389px. Follow the fix order above before touching spacing.
- An awkward automatic layout is not a reason for a title, legend, spacer node, or decorative container. Fix the geometry, change direction, or use direct SVG.
- A crowded inventory is not a clear explanation, and a chain of role-named boxes that restates its heading is not a figure. Field case: `PAM login -> credential hook -> destination` lost the hook point, the intercepted calls, and the plaintext log path; the redraw then overshot with `12 rows` and `receipt not observed` in the labels, which are prose.
- Text above or below the figure is the document's job. Inside the SVG it is a defect unless the figure is standalone and the meaning is otherwise unrecoverable.
