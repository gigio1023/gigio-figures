---
name: technical-diagram
description: >
  Use when the user wants a technical diagram, architecture figure, system map, process flow, or box-and-arrow schematic without requiring a native editor format. Produces a compact SVG figure in a restrained editorial style, authored as D2 source with ELK layout or as direct SVG from a bundled template, routed by where the figure will be shown and whether a D2 renderer is installed, and checked for legibility at the delivery width. NOT for native .drawio files, Mermaid-only output, measured data charts, or image generation.
---

# Technical Diagram

Produce the smallest accurate technical figure that stays readable where it will actually be shown. Two routes produce the same editorial look from the same tokens: a semantic D2 source laid out by ELK, and direct SVG authored from the bundled template. SVG is the deliverable on both routes. Keep the source beside the render so the figure remains reproducible without a GUI.

## Quick path

1. Form the reader brief in the content contract below, including the delivery width. Reduce the source to one question and one answer before choosing nodes.
2. Derive the required nodes, edges, groups, and annotations from that brief. Source facts that do not support the answer stay outside the figure.
3. Read `references/editorial-principles.md`. Choose the route with the table in "Route decision", then read `references/d2-authoring.md` or `references/direct-svg.md`.
4. D2 route: copy `assets/editorial-theme.d2` beside the new source, import it, author only the semantic structure, format with `d2 fmt <file>.d2`, and render:

   ```bash
   bash scripts/render_d2.sh <file>.d2 <file>.svg
   ```

   Direct SVG route: start from `assets/direct-svg-template.svg`, replace the nodes and connections, and validate:

   ```bash
   python3 scripts/validate_svg.py --target-width 720 --tokens assets/editorial-tokens.json <file>.svg
   ```

5. Inspect the rendered figure, not only the source. When the available viewer cannot display SVG, make a PNG proof: `D2_PNG_PROOF=1` with the render script on D2 v0.9.0 or newer, or `qlmanage -t -s 1440 -o <dir> <file>.svg` on macOS. Apply `references/review.md`, remove any unrequired content, and render again after each fix.

## Communication and content contract

Before authoring, form this small working brief:

```text
reader: <who must understand it>
question: <the one question this figure answers>
answer: <one sentence the reader should leave with>
surrounding_context: <what the document or conversation already explains>
delivery_width: <px the figure will be shown at; 720 unless the document says otherwise>
```

If no audience is supplied, write for a technically literate reader who has no private project context. If no delivery width is supplied, assume 720px, which is a Notion page body and a single-column document; a wide desktop report may state 1180px or more. Then derive the semantic inventory:

```text
required_nodes: [...]
required_edges: [...]
required_groups: [...]
required_annotations: [{text: ..., purpose: ...}]
deferred_to_prose: [...]
```

Infer the brief from the request and supplied material; it is a working aid, not a questionnaire to send before drawing. Ask only when a missing relation or conflicting fact would change the answer, and continue the supported parts.

The brief and inventory need not become separate files. They are the comparison set for the finished source. Raw source items are candidates, not requirements. An annotation needs a named purpose: it was requested, or without it the reader cannot recover the answer from the figure and its surrounding context. If `required_annotations` is empty, add no title, subtitle, legend, caption, callout, footer, badge, icon, or mini-diagram. Captions, figure numbers, and the stated takeaway belong to the surrounding document.

Use reader-facing roles instead of unexplained internal terms. If an exact name matters, introduce it as `role (exact name)` rather than making the reader infer the role. Show endpoints, field names, versions, and implementation steps only when the question is specifically about them.

Represent real complexity when the request requires it. Minimality never authorizes dropping a component or relationship needed for the answer. Remove details that answer another question, combine repeated peers only when their differences are irrelevant, and split by abstraction level when one page is too dense. Shorten role-first labels and simplify grouping before enlarging the canvas; never reduce type size to preserve an overfull composition.

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

Fix a failing figure in this order: on the D2 route switch the engine with `D2_LAYOUT=tala`, then switch to `direction: down` or stack rows, shorten role-first labels, put fewer nodes in a row or split the figure, and only then tighten layout spacing. Grow the canvas downward, never sideways past the delivery width, and never shrink type.

## Korean and bilingual labels

Korean labels use a sans stack (Pretendard, Apple SD Gothic Neo, Noto Sans KR); monospace Korean faces are rare and a mono Latin word inside a sans Korean label reads as two voices, so keep one voice per label. On the direct SVG route the template's `ko` class does this. On the D2 route the embedded fonts have no Hangul, so the viewer's fonts draw the glyphs and the boxes come out wider than the text; for a standalone file that must look identical everywhere, pass a Hangul-capable TTF through `D2_FONT_MONO` so D2 embeds it (macOS system fonts need a fontTools re-save first; see `references/d2-authoring.md`). Bilingual variants keep the same geometry where the estimated label widths allow it; the translation itself follows the document's glossary.

## Style boundary

The editorial theme preserves the visual language established by this package, but semantic clarity wins over exact imitation. D2 approximates a 1.2px stroke with an integer width and uses an unfilled triangle rather than the exact small V-shaped arrowhead, and the theme turns off D2's default bold shape labels and italic connection labels. Do not compensate with SVG decoration or a second visual system. Use direct SVG when exact geometry is part of the request.

## Verification

The render script checks D2 formatting, validates D2 syntax, renders with the selected engine (ELK by default, TALA with `D2_LAYOUT=tala`) and 16px outer padding, and runs `scripts/validate_svg.py`, which checks the SVG root, viewBox, and ids, fails labels that render below 12px at the delivery width, and warns about labels that crowd their box, colors outside the palette, and corner radii or stroke widths that drift from the tokens. Neither step proves that the figure is readable.

Before finishing, confirm all four:

1. **Communication:** the intended reader can identify the subject and the one-sentence answer without private vocabulary or missing chat context.
2. **Meaning:** every required node, edge, direction, group, and annotation is present and no relationship was invented.
3. **Render:** at the delivery width, every label is readable, no edge crosses unrelated content, and the dominant reading path is obvious.
4. **Minimality:** every visible element changes the reader's understanding; empty top, bottom, or side space remains empty.

When these checks and any required project checks pass, deliver. Repeat the affected checks after a semantic or layout fix; do not keep rerendering for equally valid aesthetic alternatives.

## Output

Lead with the artifacts created. Report the route taken, the delivery width assumed, the D2 validation and SVG validation results including the smallest rendered label size, the layout engine, and whether the render was visually inspected. Keep the source (`<name>.d2` with `editorial-theme.d2`, or the hand-authored `<name>.svg`) and the render together. Name any missing renderer, unverified visual result, accepted validator warning, or accepted layout defect.

## Reference router

| Need | Read or run |
| --- | --- |
| Default content and appearance rules | `references/editorial-principles.md` |
| D2 syntax, classes, delivery width, fonts, and known limits | `references/d2-authoring.md` |
| Direct SVG structure, layout recipe, tokens, fonts, embedding | `references/direct-svg.md` |
| Semantic, visual, and negative-space audit | `references/review.md` |
| Deterministic D2-to-SVG render with the legibility gate (`D2_LAYOUT`, `DELIVERY_WIDTH`, `D2_PNG_PROOF`) | execute `scripts/render_d2.sh` |
| Standalone SVG check (structure, legibility, tokens) | execute `scripts/validate_svg.py` |
| Starting point for a hand-authored figure | `assets/direct-svg-template.svg` |

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
- Do not reproduce every term found in source material. A crowded but complete inventory is not a clear explanation.
