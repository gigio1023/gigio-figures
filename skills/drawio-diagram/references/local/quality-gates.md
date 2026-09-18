# Quality gates

This file turns repeated review pain into hard finishing gates.

## Meaning

- The figure answers one stated question for one intended reader, a domain peer without this project's context unless told otherwise, in a form that reader can verify. A chain of boxes that restates the heading fails this gate. Do not mix separate questions on one page; draw a series.
- Exact names first; add a role on a second line only when the name does not say what the component does. Never a role in place of a name. Expand project-private acronyms once; keep the paths, endpoints, and fields the peer needs to verify or act, and move the rest to prose.
- Every edge whose meaning the two node names do not make unambiguous carries a label: what passes, what triggers it, or its condition, and nothing more. A hedge, count, or timestamp in a label is a defect; it belongs in prose.
- Do not mix implementation choices and external dependencies in one box.
- Preserve semantic boundaries: callers, runtime/container, internal sections, implementation choices, and external dependencies are separate roles unless the user explicitly wants them merged.
- If a label is not unambiguously correct, simplify it. Prefer `response` over a narrower word unless the narrower word is exact.
- Prefer a specific label (`A2A interface`, `Runtime layer`) over a vague one (`options and tools`); when the component has a name, the name comes first and the specific role is the second line.

## Layout

- No framed component may overlap another framed component.
- Keep at least `16px` inner padding in ordinary boxes.
- Keep at least `24px` padding from a container border to child components.
- Children must stay fully inside their parent.
- If a swimlane has a header, children must stay below the header band.
- Tight layout is acceptable only after arrows have dedicated corridors and labels still breathe.
- If a layout feels crowded, organize by real boundary, then split the page into a series at the same depth, before widening the canvas. Do not shorten a name into a role.
- Avoid bottom legends or explanatory footers that restate the diagram. Prefer direct semantic labels, surrounding prose or metadata, or a separate page for another required view.
- Remove decorative keyword garlands. If a top/bottom band is meaningful, state whether it is a caption, legend, constraint, ownership boundary, or semantic rail and align it to the content it governs.

## Text

- Do not use vertical text for main labels.
- Component labels should usually fit in one or two lines.
- Avoid paragraphs inside boxes.
- Every label must remain readable without zoom at the intended delivery size.
- Do not lower font size to preserve an overfull page; reduce content or split the view.
- If text comes close to the border, add spacing before resizing the box.
- If the same type of component repeats, keep font size, alignment, and padding consistent.

## Arrows

- There must be one visually dominant path.
- Secondary arrows should use a quieter corridor.
- Put edge labels on straight segments, not on bends.
- Give every edge label an opaque background matching the surface behind it.
- If the orchestrator and interface can be aligned for a straight request/response pair, do that.
- If fixed terminals already align and the straight corridor is clear, remove waypoints that introduce a dogleg.
- Do not let arrows or arrowheads sit on top of labels, component bodies, titles, boundary names, or box borders.
- If auto-routing crosses text or components, add waypoints or move boxes before accepting the route.

## Shape consistency

- Use one rounded-rectangle recipe per page.
- Under the editorial default style, the node recipe is `rounded=1;absoluteArcSize=1;arcSize=32;` (absolute arcSize renders at half its value). For other styles' small-radius boxes, prefer `rounded=1;absoluteArcSize=1;arcSize=12;`.
- Do not mix heavily rounded boxes with lightly rounded boxes unless the distinction carries meaning.

## Verification

Before finishing, run:

```bash
python3 scripts/validate_drawio_xml.py path/to/file.drawio
python3 scripts/validate_drawio_layout.py path/to/file.drawio
```

If either validator complains, fix the diagram or explicitly accept the tradeoff in the final response.

When an export is part of the deliverable, inspect the exported SVG or high-resolution PNG before finishing. The validators are necessary but not sufficient for visual quality.

When the editorial default style is active, also spot-check the export against its tokens: soft ~16px corners, two text voices, thin open arrowheads, one accent family, no shadows. Style drift is a finishing defect even when every validator passes.
