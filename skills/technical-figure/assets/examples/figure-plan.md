# Figure plan: How a transformer layer is built and adapted

## Claims

| id | section | claim (one sentence the reader should believe after the figure) | shape | picture test | figure |
|---|---|---|---|---|---|
| C1 | Layer structure | Attention and the MLP each read the residual stream through a norm and add their output back through ⊕, and attention writes only through its output projection `W_O`. | components read and write a shared state | structure of more than three named things | `residual-stream` |
| C2 | Mixture of experts | In a mixture-of-experts layer the router picks the top 2 routed experts for each token and supplies the gate weights that scale their outputs, a shared expert always runs, and the weighted sum is added back to the stream. | router selects k of N | branches and a selection on one structure | `moe-block` |
| C3 | Attention variants | Multi-head, grouped-query, and multi-query attention differ only in how many key/value heads the query heads share: one each, one per group, or one for all. | variants of one design differ in one component | alternatives on the same structure | `attention-variants` |
| C4 | Removing a direction | Projecting x onto a unit direction r̂ splits it into (r̂ᵀx) r̂ along r̂ and a remainder orthogonal to r̂; removing the direction keeps only the remainder. | X is a projection of Y | geometry | `projection` |
| C5 | Low-rank adaptation | A low-rank update ΔW = BA has the shape of W but rank at most r, and B and A together hold far fewer entries than W. | a product has this rank | tensor shape | `low-rank-update` |
| C6 | Post-training recipe | The released checkpoint starts from the base checkpoint and passes through supervised fine-tuning and then preference optimization, each reading its own data. | a released artifact came from this recipe | order with inputs | `training-recipe` |
| (none) | Configuration | Hidden size, head count, expert count, and rank used in the examples. | configuration list | fails: a table | prose table |

## Semantic map

| hue or style | meaning in this document | never used for |
|---|---|---|
| blue | a write into the residual stream: the output projection, its edge into ⊕, and the matching equation | reads, selection, weights changed by training |
| vermillion | weights changed by training: trainable factors and the training steps on a recipe's main path | frozen weights, activations, the residual stream |
| magenta | the unit direction r̂ and every vector that lies along it | weights, paths, selection |
| dashed line | control: the router's gate weights | data |
| dashed outline | exists only at run time | not used in this set |
| dotted line | a vector component or correspondence, no arrowhead | flow |
| ghost | context kept for orientation: unselected experts and their reads, data inputs to training, the shared query-head scaffold | removed parts (omitted) |
| full ink versus ghost | selected versus unselected expert | anything carried by hue |

## Conventions

- Direction: model depth bottom to top (`residual-stream`, `moe-block`); head index left to right with query heads above key/value heads (`attention-variants`); product order left to right (`low-rank-update`); training time left to right (`training-recipe`).
- Recurring glyphs: residual stream = vertical spine with a junction dot where a sublayer reads and ⊕ where it writes (in `moe-block` the reads leave the `x` node, because `layout.mjs` cannot branch an edge off the spine); fan-out = one junction dot; vector = arrow from the origin; matrix = rectangle with sides proportional to its dimensions and the dimension symbols outside.
- Names: residual stream, attention, MLP, RMSNorm, `W_O`, `W_in`, `W_out`, heads `h_1` to `h_4`, router, routed experts `E_1` to `E_5`, shared expert `E_s`, gate weights `g_i`, query heads `Q_i`, key/value heads `K_j, V_j`, x, r̂, W, ΔW, B, A, d, k, r, base checkpoint, supervised fine-tuning, SFT checkpoint, preference optimization, released checkpoint, demonstrations, preference pairs.
- Example reused across figures: four attention heads (`residual-stream`, `attention-variants`).
- Theme: light delivered (host not named, so the skill default); dark rendered beside each.

## Storyboard

1. `residual-stream`: spine with side branches. New platform and master figure; the most mechanism-rich figure, so the set's reference.
2. `moe-block`: expert row on the same spine glyph. Zoom into the MLP sublayer, replaced by a mixture of experts; one new idea: selection.
3. `attention-variants`: sibling variants on identical coordinates. Zoom into the attention sublayer's key/value heads; one new idea: sharing.
4. `projection`: annotated exact geometry. New platform (the vector space the stream lives in); one new idea: removing a direction.
5. `low-rank-update`: proportional rectangles. Parallel case of changing weights, now in matrix shape; one new idea: rank.
6. `training-recipe`: lineage graph, left to right. New platform (training time); one new idea: which steps change the weights.

## Alternatives

- Lead figure `residual-stream`: framing A draws the attention internals (four heads fanning out from the normed read, merged by `W_O`) up a column beside the spine; framing B draws attention as one heads box under `W_O` and the MLP as one box. Compared item by item, twice with the order swapped: A wins on difference (the four heads show why `W_O` is the single writer) and consistency (the four heads recur in `attention-variants`), B wins on density, the rest tie. Chosen: A.
- Norm placement: a norm chip inside a filled container disappears (both are surface fill), so the norm is the read edge's operation label instead of a node.
- `moe-block`: ⊗ gates per selected expert were dropped for one weighted-sum box that receives the router's control edge. With op nodes, ELK routed one control edge through the other gate and stacked three arrow tips on the ⊕'s single south port. Five routed experts instead of six, because six made the layout 740u wide and pushed it to the 1080u canvas; no label on the control edge, because an edge label in a vertical layout inserts a layer and scrambles the expert order.
- `training-recipe`: operations on edges, checkpoints as nodes, data joined to the checkpoint it produced. Operations as nodes made the row 836u wide.
