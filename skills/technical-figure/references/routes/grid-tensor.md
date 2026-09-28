# Grid and tensor route

Token × layer grids, attention masks, matrices, tensor shapes, bit fields, layer strips, and candidate grids. These figures need no graph layout: every coordinate follows from an index, a cell size, and a gap.

## Rules

- **Coordinates from arithmetic.** x = x0 + col × (cell + gap), y = y0 + row × (cell + gap). Cells are 16 to 28u with 2 to 4u gaps; choose the size so the grid fits the canvas and the labels stay at token size.
- **Axes carry meaning and a direction.** Positions left to right; depth bottom to top in mechanism figures; layer index left to right in data grids. Label each axis once, at its end, with its name; label indices only where the claim refers to them (first, last, a marked index).
- **Cells encode one thing.** `cell on` with a hue for selected or active cells; `band` behind a range of rows or columns for a region (a layer type, a stage); ghost for excluded or future positions. A grid of empty cells that encode nothing is a table drawn badly.
- **Arrows only where information moves.** In a token × layer grid, attention reads draw from earlier positions into the current one; MLP steps stay within a column.
- **Repeating units get a bracket**, labeled with the repetition count when the count is the claim, otherwise `N×` beside the bracket.

## Tensor shapes and products

- Draw each matrix as a rectangle whose sides are proportional to its dimensions, using one scale per figure; when one dimension dwarfs the others, break the long side with a gap and say so in the caption.
- Place factors in multiplication order with ⊗ or juxtaposition, the result after an equals sign.
- Dimension labels sit outside the sides (`d_model` along the height, `d_ff` along the width), in `ta` with `data-tex`.
- A rank-one product shows as a column times a row; the column in the hue when it is the direction the claim is about.

## Precision and bit fields

- A number format is a strip of fields (sign, exponent, mantissa) with widths proportional to bit counts and one hue per field kind reused for every format in the figure.
- Formats compared on range sit on one shared number line.
- Block or tile scaling shows the tile boundaries on the matrix and one swatch per scale factor, repeated identically across panels.

## Authoring

Generate the SVG from a short script with contract classes (`cell`, `band`, `guide`, `edge`, text classes), then run `scripts/render.mjs`. Keep indices and sizes as named variables so a change of example regenerates the figure.
