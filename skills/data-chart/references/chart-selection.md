# Choosing the chart

Pick from the reader's question, not from the data's shape or the request's noun - "graph" arrives meaning five different charts. Reconsider once while plotting: if the chart fights the data, the question was misread.

## Question → chart

| The reader asks... | Use | Notes |
| --- | --- | --- |
| How does a measure change over time or along an ordered scale? | Line | Few points (≤5) may read better as bars or dots; gaps for missing periods, never zero-fill |
| Which of a few items is bigger, by how much? | Bar, sorted | Order by value unless the category order itself carries meaning; direct value labels when counts are few |
| Which of many items is bigger? | Horizontal bar or dot plot | Fits long category labels; consider top-N plus an "others" bar |
| Two measures per item? | Grouped bars, dot plot, or two charts | One y-scale; a dual axis is two charts, not one |
| What is the range, spread, or outlier structure? | Histogram, strip plot, or box plot | Show the distribution, not mean-only bars |
| Do two measures move together? | Scatter | Log both axes when spans are wide; direct-label the emphasized point |
| How does a volume distribute across two category dimensions? | Heatmap | Sequential single-hue ramp; print exact values in cells when the grid is small |
| Same measure across many configurations? | Small multiples on one shared scale | The shared scale is what makes the comparison honest |
| What share of a whole? | Stacked bar (two parts) or 100% bar | A pie only with ≤3 slices where the shares carry the story; never exploded or 3D |
| Before vs after per item? | Slope chart or paired dots | Sort items to reduce line crossings |

## Anti-patterns

- Dual y-axes: one chart, two scales - that is two charts.
- 3D effects, exploded pies, donut rings with many segments.
- A truncated bar baseline, or bars on a log axis.
- A number on every point; rainbow series palettes.
- Mean-only bars where the spread would change the conclusion.
- Stacked areas that cross each other; the ordering becomes unreadable.

## Accessibility

- Color is never the only channel: direct-label series, and give the second system a different dash or marker.
- Check the accent pair under color-vision deficiency. In the preset, blue mid + coral mid passes (ΔE 23.2) only with the coral series dashed or direct-labeled.
- Deliver a one-sentence alt text with every chart - what is shown and the takeaway - even when the embedding document may not render it.
