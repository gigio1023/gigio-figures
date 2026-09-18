# Text and labels

## Contents

- Line breaks and escaping
- Wrapping and fit
- Positioning keys
- Edge labels
- Context and supporting text
- Detail vs compactness
- Fonts

## Line breaks: the #1 text mistake

A literal `\n` inside a `value` attribute is two characters, backslash and n. draw.io renders it as visible `\n` text, not a line break. XML does not interpret backslash escapes.

| You want | Write in the `value` attribute | Requires |
| --- | --- | --- |
| Line break | `&lt;br&gt;` | `html=1` in style (this skill always sets it) |
| Line break (either mode) | `&#xa;` (same character as `&#10;`) | works with `html=0` and `html=1` |
| Literal backslash-n | `\n` | nothing - which is why it is usually a bug |

Standard two-line label:

```xml
<mxCell value="&lt;b&gt;Gateway&lt;/b&gt;&lt;br&gt;routes requests"
        style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
```

## Escaping

HTML inside `value` must be XML-escaped: `<` → `&lt;`, `>` → `&gt;`, `&` → `&amp;`, `"` → `&quot;`. Unescaped `<b>` inside an attribute is malformed XML and the file will not open. A plain `&` in prose (`R&D`) must be `&amp;`.

Text that should *display* angle brackets inside an HTML label needs double escaping - once for HTML, once for XML. A rendered `<<abstract>>` stereotype is written `&amp;lt;&amp;lt;abstract&amp;gt;&amp;gt;` in the attribute.

## Wrapping and fit

- `whiteSpace=wrap` makes long text wrap inside the shape; without it, text stays on one line and overflows. Set it on every framed shape with a label.
- Wrapping is a fallback, not a layout tool: if a label wraps into 3+ lines, shorten the label or widen the box.
- `overflow=hidden` clips instead of overflowing - avoid; clipped words read as missing information.

## Positioning keys (vertices)

- `align` (`left|center|right`) and `verticalAlign` (`top|middle|bottom`) place text inside the shape.
- `labelPosition` / `verticalLabelPosition` place the whole label block relative to the shape - use for icon-style shapes whose label sits below (`verticalLabelPosition=bottom;verticalAlign=top;`).
- `spacing`, `spacingLeft/Right/Top/Bottom` add inner padding; give labeled boxes `spacing=8` or more so text never hugs the border.

## Edge labels

Set `value` on the edge cell. Position with the edge geometry:

```xml
<mxCell id="e1" value="ack" style="edgeStyle=orthogonalEdgeStyle;html=1;labelBackgroundColor=#FFFFFF;" edge="1" parent="1" source="a" target="b">
  <mxGeometry x="-0.4" y="-10" relative="1" as="geometry">
    <mxPoint as="offset" />
  </mxGeometry>
</mxCell>
```

- `x` in -1..1 slides the label along the edge (-1 source, 0 center, 1 target).
- `y` offsets perpendicular to the edge in pixels; use it to lift a label off the line.
- Every edge label needs an opaque `labelBackgroundColor` matching the canvas or containing panel (`#FFFFFF` above). Omitted, `none`, and transparent backgrounds let the connector show through the glyphs. Offset still helps placement, but it does not replace the background.
- Put labels on a straight segment of the route, never on a bend, and keep them out of other shapes' space. Omit a label only when the two shape labels already make the relation unambiguous; otherwise keep it, even on a short edge.
- Keep edge labels to a few words that name what passes, what triggers the edge, or its condition (`ack`, `on failure`, `HTTP 429`, `plaintext to init.h`).

## Context and supporting text

Free-standing text is exceptional. Give each block a named purpose tied to the reader brief before placing it:

- A short title may identify the question when the figure is standalone. Omit it when the surrounding heading already supplies the same context.
- A callout may point to one specific feature that is part of the answer and cannot be labeled directly. It must not become a second narrative.
- A semantic node participates in the model and may receive only relationships the diagram actually asserts.
- Versions, sources, excluded scope, implementation notes, and decorative text belong in surrounding prose or file metadata unless the question is about them.

Delete subtitles, keyword garlands, bottom strips, and explanatory footers that repeat the diagram or compensate for an unclear composition. Do not create a free-standing text region merely because there is room above, below, or beside the main path.

## Detail vs compactness: pick a level deliberately

Choose the detail a domain peer needs to verify the answer:

1. **Exact name** - the name the component carries in code, configuration, or the running system. Default for every component a peer would look up.
2. **Exact name + role** - `&lt;b&gt;Bastion&lt;/b&gt;&lt;br&gt;policy gateway` when the name does not say what the component does. Never the role alone in place of the name.
3. **Structured label** - an HTML `&lt;table&gt;` or `&lt;hr&gt;`-separated shape only when fields or attributes are the subject of the figure.
4. **Hover metadata** - use `<object>` attributes for exact detail that helps future editing but is not needed on the canvas.
5. **Another page** - use a named `<diagram>` page when another required abstraction level deserves its own view.

Move everything else to surrounding prose. A page where most boxes use structured labels is an implementation inventory, not an explanatory figure.

## Fonts

- Use one readable `fontSize` for peer components and, only when required, one larger size for a standalone title. Do not create a tiny caption tier.
- Whole-label bold via `fontStyle=1`; partial bold via `&lt;b&gt;` - never both for the same effect.
- Wide-character scripts (Korean, Japanese, Chinese) run wider than the same letter count in Latin; size boxes for the rendered width, and widen early instead of accepting mid-word breaks.
- Inspect at the intended delivery size. If text needs zoom, reduce content or split the view instead of lowering the font size.
