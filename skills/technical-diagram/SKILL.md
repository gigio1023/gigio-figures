---
name: technical-diagram
description: >
  Use when the user wants a technical diagram, architecture figure, system map, process flow, or box-and-arrow schematic without requiring a native editor format. Draws for a domain peer by default: exact names, mechanism on the edges, and the full topology the question needs, in a restrained editorial style, authored as D2 source with ELK layout or as direct SVG from a bundled template, routed by where the figure will be shown and whether a D2 renderer is installed, and checked for legibility at the delivery width. NOT for native .drawio files, Mermaid-only output, measured data charts, image generation, or a deliberately simplified figure for readers outside the field (eli5-figure, on explicit request).
---

# Technical Diagram

Produce the accurate technical figure a peer can verify, drawn so it stays readable where it will actually be shown. Two routes produce the same editorial look from the same tokens: a semantic D2 source laid out by ELK, and direct SVG authored from the bundled template. SVG is the deliverable on both routes. Keep the source beside the render so the figure remains reproducible without a GUI.

## Quick path

1. Form the reader brief in the content contract below, including the delivery width. Fix the reader and the one question; do not reduce the material to a sentence before you know what the peer must be able to verify.
2. Derive the required nodes, edges, groups, and annotations from that brief. Every component and relation the peer needs to verify the answer is required; a fact that answers a different question stays outside the figure.
3. Read `references/editorial-principles.md`. Choose the route with the table in "Route decision", then read `references/d2-authoring.md` or `references/direct-svg.md`.
4. D2 route: copy `assets/editorial-theme.d2` beside the new source, import it, author only the semantic structure, format with `d2 fmt <file>.d2`, and render:

   ```bash
   bash scripts/render_d2.sh <file>.d2 <file>.svg
   ```

   Direct SVG route: start from `assets/direct-svg-template.svg`, replace the nodes and connections, and validate:

   ```bash
   python3 scripts/validate_svg.py --target-width 720 --tokens assets/editorial-tokens.json <file>.svg
   ```

5. Inspect the rendered figure, not only the source. When the available viewer cannot display SVG, make a PNG proof: `D2_PNG_PROOF=1` with the render script on D2 v0.9.0 or newer, or `qlmanage -t -s 1440 -o <dir> <file>.svg` on macOS. Apply `references/review.md`: fix render defects first, remove any text the document should carry, and render again after each fix.

## Reader and content contract

Before authoring, form this small working brief:

```text
reader: <who must understand it; default: a peer in this domain who lacks only this project's context>
question: <the one question this figure answers>
answer: <what the peer should be able to verify from the figure>
surrounding_context: <what the document or conversation already explains>
delivery_width: <px the figure will be shown at; 720 unless the document says otherwise>
```

If no audience is supplied, write for a peer in the domain who lacks only this project's context. Knowledge is not the bottleneck for that reader; the specific structure is. Assume the field's vocabulary and give the exact names, mechanisms, and relationships the peer could not reconstruct without the figure. Only an explicit request for a simplified figure changes the register, and that request belongs to `eli5-figure`. If no delivery width is supplied, assume 720px, which is a Notion page body and a single-column document; a wide desktop report may state 1180px or more. Then derive the semantic inventory:

```text
required_nodes: [exact names; a role line only where the name does not say what it does]
required_edges: [{from, to, carries_or_trigger}]
required_groups: [real boundaries only]
required_annotations: [{text: ..., purpose: ...}]
deferred_to_prose: [facts that answer a different question, and every count, timestamp, or qualifier]
```

Infer the brief from the request and supplied material; it is a working aid, not a questionnaire to send before drawing. Ask only when a missing relation or conflicting fact would change the answer, and continue the supported parts.

The brief and inventory need not become separate files. They are the comparison set for the finished source. Source items are candidates; the test for each is whether the peer needs it to verify or act on the answer. An annotation needs a named purpose: it was requested, or without it the reader cannot recover the answer from the figure and its surrounding context. If `required_annotations` is empty, add no title, subtitle, legend, caption, callout, footer, badge, icon, or mini-diagram, and write nothing above or below the figure. Captions, figure numbers, and the stated takeaway belong to the surrounding document.

Exact names first. Label a component by the name it carries in code, configuration, or the running system; add a role on a second line only when the name does not say what the component does. Do not replace a name with a role, and do not hide a name in parentheses behind one. Acronyms the field uses stay; project-private acronyms are expanded once. Endpoints, file paths, field names, hook points, and versions are figure content when the peer needs them to verify or act on the answer, and prose when they answer another question.

Edges carry mechanism. Label a connection with what passes, what triggers it, or the condition under which it holds whenever the two node names do not make the relation unambiguous. An unlabeled arrow between a hook and a destination hides exactly what the peer came for. Keep the label to the mechanism itself: `encrypt, JSON, HTTP` is a mechanism; `configured, receipt not observed` is a caveat and belongs in prose.

Compress like a dashboard panel, not like a disclosure. The figure's space goes to names and mechanism. Quantities, timestamps, counts, sample sizes, evidence qualifiers, and provenance are prose beside the figure unless the question is about them: `plaintext log` is content, `plaintext log, 12 rows` is a disclosure. When an unconfirmed relation would mislead if drawn plainly, draw it in the secondary connection style and let the prose say why, or leave it out; do not write the hedge on the edge. This is the opposite failure of abstracting names into roles, and it costs the reader the same attention.

Represent the complexity the question requires. Minimality never authorizes dropping a component, relationship, or mechanism the peer needs. When the figure is hard to scan, organize it first (group by real boundary, align peers, order along the reading path, make edge meanings consistent), then split it into a series of figures at the same depth, and only then move to prose what answers a different question. Do not abstract nodes into roles, merge components that differ in a relevant way, or delete mechanism to make the figure fit. Grow the canvas downward; never reduce type size.

## Route decision

| Situation | Route |
| --- | --- |
| The figure is inlined into an HTML document that supplies its own fonts and color tokens | Direct SVG |
| The figure ships as a standalone file that must carry its own look (Notion upload, README, Slack) and `d2` is installed | D2 |
| An existing SVG must be edited, the user asks for SVG source, or the composition needs geometry D2 cannot express | Direct SVG |
| `d2` is not installed | Direct SVG. Do not install D2 silently. If the user explicitly asked for D2 source, write the valid `.d2` and report that the render is unverified. |

D2 buys automatic layout and fonts subsetted into the file, which matters when the SVG must look the same on every viewer. Direct SVG buys exact control over width and corridors, inheritance of the document's fonts, and CSS color tokens, which matters inside a styled document. Both routes read `assets/editorial-tokens.json`, and a figure may move from one route to the other without changing its content.

## Delivery size

A figure wider than its column is scaled down by the host, and the labels shrink with it. Keep the canvas no wider than the delivery width. When it must be wider, the smallest label still has to render at 12px or more after scaling; `scripts/validate_svg.py --target-width` computes this and fails the figure otherwise, and the render script applies it with `DELIVERY_WIDTH` (default 720, `0` to disable).

Fix a failing figure in this order: on the D2 route switch the engine with `D2_LAYOUT=tala`, then switch to `direction: down` or stack rows, shorten labels without dropping names, put fewer nodes in a row or split the figure into a series, and only then tighten layout spacing. Grow the canvas downward, never sideways past the delivery width, and never shrink type.

## Korean and bilingual labels

Korean labels use a sans stack (Pretendard, Apple SD Gothic Neo, Noto Sans KR); monospace Korean faces are rare and a mono Latin word inside a sans Korean label reads as two voices, so keep one voice per label. On the direct SVG route the template's `ko` class does this. On the D2 route the embedded fonts have no Hangul, so the viewer's fonts draw the glyphs and the boxes come out wider than the text; for a standalone file that must look identical everywhere, pass a Hangul-capable TTF through `D2_FONT_MONO` so D2 embeds it (macOS system fonts need a fontTools re-save first; see `references/d2-authoring.md`). Bilingual variants keep the same geometry where the estimated label widths allow it; the translation itself follows the document's glossary.

## Style boundary

The editorial theme preserves the visual language established by this package, but semantic clarity wins over exact imitation. D2 approximates a 1.2px stroke with an integer width and uses an unfilled triangle rather than the exact small V-shaped arrowhead, and the theme turns off D2's default bold shape labels and italic connection labels. Do not compensate with SVG decoration or a second visual system. Use direct SVG when exact geometry is part of the request.

## Verification

The render script checks D2 formatting, validates D2 syntax, renders with the selected engine (ELK by default, TALA with `D2_LAYOUT=tala`) and 16px outer padding, and runs `scripts/validate_svg.py`, which checks the SVG root, viewBox, and ids, fails labels that render below 12px at the delivery width, and warns about labels that crowd their box, colors outside the palette, and corner radii or stroke widths that drift from the tokens. Neither step proves that the figure is readable or true.

Before finishing, confirm all five, in this order:

1. **Render:** at the delivery width every label is legible, nothing is clipped, no edge crosses unrelated content, and the geometry is what the source intends. A figure that says the right thing but renders wrong has failed.
2. **Meaning:** every required node, edge, direction, group, and annotation is present, and no relationship was invented.
3. **Verifiability:** the peer can check the answer against the system from this figure. If the visible content only restates the caption or section heading, the figure is not finished.
4. **Communication:** the peer can identify the subject and follow the reading path without the chat context; exact names are present and any project-private acronym is expanded once.
5. **Minimality:** every visible element changes the reader's understanding; no count, timestamp, or qualifier sits in a label that the prose should carry, and nothing is written above or below the figure.

When these checks and any required project checks pass, deliver. Repeat the affected checks after a semantic or layout fix; do not keep rerendering for equally valid aesthetic alternatives.

## Output

Lead with the artifacts created. Report the route taken, the delivery width assumed, the D2 validation and SVG validation results including the smallest rendered label size, the layout engine, and whether the render was visually inspected. Keep the source (`<name>.d2` with `editorial-theme.d2`, or the hand-authored `<name>.svg`) and the render together. Name any missing renderer, unverified visual result, accepted validator warning, accepted layout defect, and any fact deferred to prose.

## Reference router

| Need | Read or run |
| --- | --- |
| Default content and appearance rules | `references/editorial-principles.md` |
| D2 syntax, classes, delivery width, fonts, and known limits | `references/d2-authoring.md` |
| Direct SVG structure, layout recipe, tokens, fonts, embedding | `references/direct-svg.md` |
| Reader, semantic, visual, and negative-space audit | `references/review.md` |
| Deterministic D2-to-SVG render with the legibility gate (`D2_LAYOUT`, `DELIVERY_WIDTH`, `D2_PNG_PROOF`) | execute `scripts/render_d2.sh` |
| Standalone SVG check (structure, legibility, tokens) | execute `scripts/validate_svg.py` |
| Starting point for a hand-authored figure | `assets/direct-svg-template.svg` |
| A deliberately simple figure for a reader outside the field, on explicit request | the `eli5-figure` skill, which reduces this skill's exact figure |

Read only the route needed for the current artifact.

## Gotchas

- A successful D2 render does not prove that labels, crossings, or semantic grouping are readable; inspect the SVG or a PNG proof.
- Horizontal ELK layouts are wide. The bundled four-node example renders 1027px wide at default spacing, which puts its 12px edge labels at about 8.4px and its 14px node labels at 9.8px in a 720px column; the validator catches it. `D2_LAYOUT=tala` renders the same source 647px wide and `direction: down` 389px wide.
- macOS system fonts such as `AppleGothic.ttf` fail D2's font embedding with a checksum error. Re-save the TTF with fontTools, or use a distributed TTF such as Pretendard, which was not exercised in the verification run.
- D2 draws shape labels bold and connection labels italic unless told otherwise. The theme sets `bold: false` and `italic: false`; a hand-written class must repeat them.
- Hangul is not in D2's embedded fonts. Without a supplied TTF the glyphs depend on the viewer and the boxes run wide.
- The main source must keep `editorial-theme.d2` beside it. A missing relative import loses both portability and the shared style.
- The render script refuses an unformatted source; run `d2 fmt` first.
- Apply `entity` to technical nodes and `flow` to ordinary connections; the default D2 theme is intentionally not the style contract.
- Do not turn an awkward automatic layout into an excuse for a title, legend, spacer node, or decorative container. Fix the existing geometry, change direction, or use the direct SVG route.
- A crowded inventory is not a clear explanation, and a four-box chain that restates its heading is not a figure. Fix crowding by organizing and splitting into a series, not by turning names into roles or deleting the mechanism. Field case: an incident figure reduced to `PAM login -> credential hook -> destination` lost the hook point, the intercepted calls, and the plaintext log path, the three things a security peer needed. The redraw then overshot with `12 rows` and `receipt not observed` in the labels; those are prose.
- Text above or below the figure (a takeaway, an analogy, a source line) is the document's job. Inside the SVG it is a defect unless the figure is standalone and the reader cannot recover the meaning otherwise.
