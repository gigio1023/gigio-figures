# Visual grammar

The grammar decides what each mark means. Tokens decide how the marks look; this file decides which mark to use. Most crude figures break one of the first three sections: everything drawn at the same weight, one color carrying many meanings, or one line style carrying many relations.

## Emphasis and layering

- **Salience follows importance.** The heaviest visual weight (hue, emphasis stroke, size) goes to the claim's subject, one to three elements at most. The document's central object, such as a residual stream or a request path, must never be the weakest line in its own figure.
- **Three layers of weight.** Claim path: hue and 2.25u stroke. Context structure: ink at 1.5u edges and 1.25u gray outlines. Frame (containers, guides, axes, dividers): surface fills and 1.0u guide lines. Edges are darker than node outlines so mechanism reads before boxes.
- **Ghost, do not delete.** Elements outside the claim keep their position in `ghost` style so the reader can orient; deleting them moves everything and breaks comparison with other figures.
- **Smallest effective difference.** Make every distinction as light as it can be while still visible. Frames are lighter than content; a second accent is heavier than the context but lighter than the focus.
- **One focal hue per figure by default.** The focal element takes the hue its meaning has in the semantic map. When its meaning is not in the map, it is emphasized in ink (`box focus` or `edge emph` without a hue class) and the context is ghosted; do not invent a hue for it. A second hue appears only when the contrast between two meanings is itself the claim, and then both come from the map.

## Semantic map

- Each hue has one meaning for the whole document: blue, vermillion, and magenta, assigned in the plan. The same hue colors the element, its edge, any symbol in the equations, and the matching word when the prose colors it.
- Neutral means "not the subject": ink for structure, gray for context, surface for frames.
- A meaning not in the map does not get a hue. Use position, a label, or a glyph.
- Charts in the document use the same map for the same entities.
- Color is never the only channel. Every hued distinction also shows as position, stroke, dash, marker shape, or label, so the figure survives grayscale and color-vision deficiency.

## Relations and line styles

At most three relation kinds per figure; more means the figure answers several questions and should be split.

| Relation | Sentence it reads as | Mark |
|---|---|---|
| Data or artifact flow | A's output is read by B | `edge`: solid, arrowhead at the consumer |
| Residual write | B's output is added to the stream | `edge` into an `op` ⊕ on the `spine`; hue when it is the claim |
| Control | A decides B's selection, weights, or parameters | `edge control`: dashed, entering from a side different from the data path |
| Derivation | process A produces artifact B | solid edge from an operation node to an artifact node; operations and artifacts look different |
| Lineage | B starts from A | reuse the same node, or a thin edge labeled `init` |
| Order | A then B | placement alone; add arrows only where order is not obvious |
| Feedback | B's result returns to A | one return edge in a consistent rotation, labeled with its exit condition |
| Correspondence, zoom | this panel details that element | `leader`: dotted, no arrowhead |
| Causal effect | A changes B | not an arrow: show before and after, or put the measured effect in the caption |
| Identity | A and B are the same object | one node, not two |

- Every edge must read as "A [verb] B". When the verb is not obvious from the two names and the line style, label the edge with the verb or the payload.
- Parallel fan-out (copy to all), exclusive choice (one of), and loops look different: fan-out branches from one junction dot; exclusive choice groups the alternatives under a bracket labeled with the condition; loops sit inside a scope box that states what repeats.
- Junction dots only where a line really splits or merges. Crossings without a dot are not connections; avoid crossings first (crossings hurt comprehension more than bends or asymmetry).

## Shapes mean kinds

Keep one shape per kind of thing for the document and define any shape that is not obvious once, in the first figure's caption or a small legend.

| Kind | Shape |
|---|---|
| Component, module, function | `box` |
| Artifact, checkpoint, dataset | `box` with a second line naming its type, or a `chip` when small |
| Operator (add, multiply, subtract) | `op` circle with ⊕, ⊗, ⊖ |
| Vector | strip of 3 to 6 `cell`s |
| Matrix, token × layer grid | grid of `cell`s |
| Distribution, score | small bar histogram |
| Tag, dtype, verdict | `chip`; when one figure holds both input chips and verdict chips, keep them apart by position and give the verdicts a hue or a caption-defined variant |
| Region of an axis (layer type, stage) | `band` |

## Containers

- A container means one thing: a module scope, a repetition, a zoom panel, or a condition. Pick one style per meaning and keep it across the document.
- Every container has a name, placed at its top left outside edge corridors. A container without a name is decoration.
- Arrows end at nodes, not at container borders. An arrow to a border reads as "to every member".
- Do not wrap a single element in a container, and do not draw a border and a fill for the same container.

## Text

- Labels sit next to what they name, closer to it than to anything else. Prefer direct labels to legends; a legend holds at most three items and only for encodings that cannot be labeled in place.
- One family per hierarchy level. Node titles in the sans; identifiers that literally appear in code in mono, preferably as their own line. Never mix mono and Hangul in one string.
- All text horizontal. Rotate the layout, not the words.
- Math through `data-tex`, with the same symbols as the prose.
- No sentences in the canvas except the annotation layer, which holds names and mechanism in the fewest words that change the reading, in `ta` beside the content with a thin leader when it cannot sit adjacent.

## Zoom, locator, inset

- A zoom panel details one element shown elsewhere: dotted `leader` from the element to the panel, the panel titled with the element's identifier, its background a lighter tint of the element or plain `zoom` outline.
- After the document's first full overview, repeat the overview only as a small ghosted locator with the region marked, not at full size.
- An inset that shows an operation geometrically (a projection, a block-scale tile) is content, not decoration; place it beside the step it explains and never over another element.

## Never in the canvas

- A title or subtitle (the caption names the figure), a footer, a source line, a takeaway band.
- Counts, sample sizes, timestamps, hedges, configuration lists; they go to the caption or a table.
- Logos, mascots, emoji, clip art, or icons that do not encode a kind defined in a legend.
- 3D, perspective, drop shadows, glow, gradients (a gradient may encode a sequential value in a chart), transparent backgrounds.
- Bullet lists inside boxes.
- Decoration to fill space: empty space may stay empty.

## Sources

- Bertin, Semiology of Graphics (1967); Mackinlay, ACM TOG 5(2) 1986; Cleveland and McGill, JASA 79(387) 1984; Munzner, Visualization Analysis and Design (2014): channels, expressiveness and effectiveness, eyes beat memory.
- Tufte, Envisioning Information (1990), Visual Explanations (1997), Beautiful Evidence (2006): layering and separation, smallest effective difference, small multiples, the ambiguity of links and arrows.
- Larkin and Simon, Cognitive Science 11 (1987): diagrams work by indexing information by location.
- Tversky, Morrison, Bétrancourt, IJHCS 57 (2002): congruence and apprehension. Tversky, TopiCS 3(3) (2011): arrows carry many meanings. Heiser and Tversky, Cognitive Science 30 (2006): arrows invite functional readings.
- Moody, IEEE TSE 35(6) (2009): semiotic clarity, symbol overload, perceptual discriminability, graphic economy, cognitive integration.
- Palmer (1992), Palmer and Rock (1994): common region and uniform connectedness. Harel, CACM 31(5) (1988): enclosure as set containment.
- Gleicher et al., Information Visualization 10(4) (2011) and Gleicher (2018): juxtaposition, superposition, explicit encoding; comparison as targets and actions.
- Mayer (2017): coherence, signaling, spatial contiguity. Kalyuga et al. (2003): expertise reversal, why peer figures should not carry novice explanations.
- Purchase (1997): edge crossings harm comprehension most among layout aesthetics.
- Marshall, Freitas, Jay, arXiv 2008.12566 (2022): neural-network system diagrams; well-cited authors separate flow kinds with different arrows.
- OMG BPMN 2.0.2: separate marks for sequence flow, message flow, association, exclusive and parallel gateways.
- The emphasis, ghost, delta-highlight, and sibling-variant rules also rest on direct inspection of published figures from Anthropic, OpenAI, Google DeepMind, Meta, DeepSeek, Qwen, MiniMax, and independent explainers; see `exemplars.md`.
