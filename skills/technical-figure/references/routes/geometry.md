# Geometry route

Vectors, projections, subspaces, angles, decision boundaries, and other figures where distance and angle carry meaning. The space is metric: a reader measures it with their eyes, so the geometry must be computed, not sketched.

## Rules

- **Compute coordinates from the actual values.** Pick concrete vectors (for example x = (3, 2) and a unit direction r̂ = (1, 0)), compute every derived point in code, and map data coordinates to canvas coordinates with one scale for both axes (1:1 aspect). Record the example values in the FigureSpec.
- **Exact or schematic, and say which.** An exact figure may carry ticks and coordinate labels. A schematic figure (a high-dimensional idea drawn in 2D) carries no ticks, numeric labels, or right-angle marks that would look like measurements; the caption says it is schematic.
- **The reference direction is an axis.** Align the direction the claim is about with a canvas axis so its components read as horizontal and vertical.
- **Reserved hue for the direction.** The direction and anything that lies along it (its projection, a component along it) take the hue the semantic map assigns to that direction. The complement is neutral ink; derived components are dotted.
- **Right-angle marks** where orthogonality is the claim, 8u squares in ink-2.
- **Label at the tip.** Vector labels sit just beyond the arrow tip on the side away from other vectors; projection labels sit beside the segment's midpoint. Use `data-tex` for every symbol.
- **Separate overlapping objects.** When a unit vector lies along its own projection, offset one of them by 6u perpendicular or draw the unit vector heavier and shorter, so the tip does not read as a tick mark.
- **Crop to content.** Axes extend a little past the data; the canvas does not reserve empty quadrants. Empty margins shrink everything when the host scales the figure to the column.

## Build-up panels

When one operation applies to several vectors (projecting every column of a matrix), draw (a) one vector in detail and (b) three vectors moving to the complement plane, in the same axes and scale, with before in ghost and after in ink.

## Authoring

Write a short script (Python or JavaScript) that computes the points and emits the SVG with contract classes: `guide` for axes and ticks, `edge` with `data-arrow="end"` for vectors, `edge emph` with the hue for the direction, `leader` for dotted components, `ta` for tick labels, `t` or `tl` with `data-tex` for symbols. Then run `scripts/render.mjs`. Keep the script beside the figure so the values can change without redrawing.

For plotted functions or data-driven geometry (a loss surface slice, a point cloud from real activations), use the chart route with the same tokens.
