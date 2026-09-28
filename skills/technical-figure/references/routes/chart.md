# Chart route

Measured data drawn with matplotlib through `scripts/figure_mpl.py`: line charts, bars, dot plots, scatter, distributions, heatmaps, and small multiples. The module reads the same `assets/figure-tokens.json` as the SVG routes, so a chart sits beside a mechanism figure with the same fonts, text sizes, strokes, hues, and canvas width. It renders both themes itself and does not pass through `render.mjs`; the SVG lint does not apply, and the pre-render checks and the visual review below take its place.

## Chart or schematic

Decide by the content, not by the request's noun.

| Content | Route |
| --- | --- |
| Real numbers, many points, true scales (log axes, distributions, time series) | this route |
| Structure with a few illustrative values inside it (a score histogram beside a router, a tensor shape) | the mechanism or grid route |
| 3 to 8 bars of real measurements that may change | this route, so the chart regenerates from the data |
| A decorative sketch of a trend inside a schematic | the schematic route, marked `schematic` in the FigureSpec |

The FigureSpec still applies: the question, the claim, and the one focal series. Sample sizes, seeds, run conditions, and data sources go to the caption.

## Chart by question

Pick from the reader's question, not from the data's shape; "graph" arrives meaning five different charts. Reconsider once while plotting: when the chart fights the data, the question was misread.

| The reader asks | Use | Notes |
| --- | --- | --- |
| How does a measure change over time or along an ordered scale? | Line | Five points or fewer may read better as bars or dots; missing periods stay gaps, never zero |
| Which of a few items is bigger, and by how much? | Bar, sorted | Order by value unless the category order carries meaning; value labels when bars are few |
| Which of many items is bigger? | Horizontal bar or dot plot | Room for long category labels; consider top N plus one "others" row |
| Two measures per item? | Dot plot, grouped bars, or two charts | One y scale; a dual axis is two charts |
| What is the range, spread, or outlier structure? | Histogram, strip plot, or box plot | Show the distribution, not mean-only bars |
| Do two measures move together? | Scatter | Log both axes when spans are wide; label the emphasized point directly |
| How does a quantity distribute over two category dimensions? | Heatmap | One hue's ramp; print values in cells when the grid is small |
| Same measure across many configurations? | Small multiples on one shared scale | The shared scale is what makes the comparison honest |
| What share of a whole? | Stacked bar with two parts, or a 100% bar | A pie only with three slices or fewer, never exploded or 3D |
| Before and after per item? | Slope chart or paired dots | Sort items to reduce crossings |

## Anti-patterns

- Dual y axes: one chart with two scales is two charts.
- 3D effects, exploded pies, donut rings with many segments.
- A truncated bar baseline, or bars on a log axis.
- A number on every point; a rainbow of series colors.
- Mean-only bars where the spread would change the conclusion.
- Stacked areas that cross; the ordering becomes unreadable.

## Design floor

- **Honest scales.** Bars start at zero. A log axis carries dots, never bars, because it has no zero and bar length means nothing. One y scale per chart. Dots and lines may zoom to the data range; bars may not.
- **One focal comparison.** The focal series carries its semantic hue and the emphasis stroke (2.25u); every other series is context in `line` gray at the edge stroke (1.5u) and drawn beneath it. Emphasis may come from the heavier stroke as well as the color, so it survives grayscale.
- **Direct labels over legends.** Name each line at its end and each dot row at its axis; label values only at line ends or on the one emphasized point, never on every point. A legend is allowed only for an encoding that cannot be labeled in place, and holds at most three items.
- **No chart junk.** No title in the canvas (the caption names the chart), no subtitle, takeaway band, source footer, badge, or inset to fill space. No four-sided frame, 3D, shadow, gradient, or background tint. Gridlines are off; a hairline `guide` grid on the value axis is allowed when reading values off that axis is the point, as in a dot plot.
- **Horizontal text.** The y-axis title sits horizontally above the tick labels, never rotated; `axis_titles` places both titles.

## Color and the semantic map

The document's semantic map from `planning.md` assigns each hue one meaning, and a chart follows it: when blue means "proposed method" in the mechanism figures, the proposed method's series is blue in every chart, its end label is set in blue's text color, and no other series in the document's charts uses blue. A chart does not assign hues on its own. When its focal entity has no hue yet, add it to the map; for a standalone chart with no map, blue is the first hue and its meaning is recorded with the chart.

| Situation | Marks | Labels |
| --- | --- | --- |
| The focal series | `fm.focal(hue)`: hue stroke, 2.25u, on top | `hue_name=hue`: hue text color, weight 600 |
| Context series | `fm.context()`: `line` gray, 1.5u | ink-2, weight 400 |
| A second mapped meaning whose contrast with the focus is the claim | `fm.context() \| {"color": fm.hue(second)}`: hue stroke at 1.5u, lighter than the focus | `hue_name=second` |
| A categorical comparison with no focal series | `fm.categorical()` in order, 1.5u; more than seven categories means grouping or splitting | ink-2, or the series color when it passes 4.5:1 |
| Sequential values (heatmap) | `cmap=fm.sequential(hue)`: darker is larger in light, lighter is larger in dark | `ink` near the ramp's fill end, `bg` near its stroke end; check 4.5:1 |

Un-styled series default to context gray, so a hue always appears by choice. Colored area stays small, a focal line or a row of dots, not filled regions. Where overlap itself must show (dense scatter), use a 0.15 to 0.25 alpha fill with an opaque stroke; otherwise no alpha.

## Type and scale

A 720u canvas is a figure 720pt wide, so 1u is 1pt and token sizes pass to matplotlib unchanged. Saving at 144 dpi gives 2 px per u: a 720u chart is a 1440 px PNG, and a 12u tick label is 24 px tall, matching the SVG routes' 2x export. Always create figures with `fm.figure(height_u)` or `fm.figsize(height_u)`; `save` warns when a figure is not 720u or 1080u wide.

| Chart text | Token role | Size and weight | Color |
| --- | --- | --- | --- |
| Tick labels | annotation | 12u, 400 | ink-2 |
| Axis titles | edge label | 12.5u, 400 | ink-2 |
| Direct labels | edge label | 12.5u; 600 when focal (mono stays 500) | ink-2, or the hue's text color |
| Small-multiple panel titles | node label | 14u, 600 | ink |
| Panel letters (a), (b) | panel label | 15u, 600 | ink |

- Pretendard sets Latin and Korean text alike. JetBrains Mono (500) is only for strings that literally appear in code, such as a config key or a function name used as a series name; tick numbers and prose labels stay in Pretendard, and a mono string never contains Hangul.
- Digits are tabular and `ss06` is on. Matplotlib measures text without OpenType features, so the module writes a copy of Pretendard with both baked into its character map (`Pretendard Figure`, about two seconds per weight on first use) instead of setting features at run time.
- Height stays within about 767u (750 CSS px at a 704 px column); `figsize` warns past it. The reference charts use 400u for a line chart and 200u for a four-row dot plot.

## Themes

`fm.render(draw, stem)` calls the drawing function once per theme under `fm.use(theme)` and writes `stem.light.png`, `stem.light.svg`, `stem.dark.png`, and `stem.dark.svg`. The background is baked into every file; the dark render uses the dark palette (brighter hue strokes, lighter ink), not inverted colors. The SVG has text as paths and is sized 720 by height in CSS px, so it is portable but carries one theme; there is no dual-palette SVG for charts. Deliver the theme that matches the host, following the theme policy in `SKILL.md`.

## Module

| Call | Purpose |
| --- | --- |
| `use(theme)` | Register fonts, apply the theme's rcParams |
| `figure(height_u, wide=False, nrows=1, ncols=1, **subplots_kw)` | `plt.subplots` at the canvas width with constrained layout |
| `focal(hue)`, `context()` | Line and marker kwargs for the focal series and for context |
| `hue(name, role)`, `neutral(name)`, `categorical()`, `sequential(hue)` | Theme colors: `role` is `stroke`, `fill`, or `text` |
| `text_style(role, hue_name=None, mono=False)` | Font kwargs for `tick`, `axis`, `label`, `title`, `panel`, `annotation` |
| `label_ends(ax, x, [(y, text, hue or None), ...], mono=False)` | End labels for lines, nudged apart so none overlap |
| `direct_label(ax, x, y, text, hue_name=None, mono=False, dx=6, dy=0)` | One label beside a mark, offsets in u |
| `axis_titles(ax, x=None, y=None)` | x title at the right end below the axis; y title horizontal above the tick labels, or above the panel title in small multiples (set it on the first panel only) |
| `category_axis(ax, labels, axis="y", hues=None, mono=False)` | Categories as direct labels at 0 to n-1, a mapped one in its hue, no spine or tick marks |
| `value_grid(ax, axis)` | Hairline guide grid on the value axis; drops that axis's spine and tick marks |
| `save(fig, stem, theme)`, `render(draw, stem)` | Write the themed PNG and SVG |

A chart script:

```python
import figure_mpl as fm

HUE_MAP: dict[str, fm.HueName] = {"cosine_warmup": "blue"}  # from the document's semantic map
steps, loss = load_user_data()  # values only from the user's files

assert all(len(v) == len(steps) for v in loss.values()), "series do not align"

def draw():
    fig, ax = fm.figure(400)
    for name, values in loss.items():
        ax.plot(steps, values, **(fm.focal(HUE_MAP[name]) if name in HUE_MAP else fm.context()))
    ax.set_ylim(1.7, 3.3)
    fm.axis_titles(ax, x="Training step (thousands)", y="Validation loss")
    fm.label_ends(ax, steps[-1], [(v[-1], n, HUE_MAP.get(n)) for n, v in loss.items()], mono=True)
    return fig

fm.render(draw, "loss")
```

`scripts/example_chart.py` is the working reference: a line chart with one focal series and three context series, and a dot plot with a hairline value grid, a focal value label, mono category labels, and a Korean axis title.

## Commands

```bash
bash scripts/setup.sh --check                                    # fonts present; once per machine
PYTHONPATH=<skill>/scripts uv run --with matplotlib python chart.py
cd scripts && uv run --with matplotlib python example_chart.py /tmp/example-charts
cd scripts && uv run --with matplotlib python -m unittest        # module tests
```

No system matplotlib is assumed; add other dependencies the same way (`--with pandas`). Without the cached fonts the module warns once and falls back to the token stacks' system fonts; text widths then differ and Hangul may be missing on machines without a Korean font, so install the fonts before delivering.

## Non-negotiables

- Data values come from the user or their files; never invent or smooth numbers. Inspect the supplied data before asking. Keep missing values as gaps when that representation is valid; when omitting a series would change the requested comparison, ask about that series while preparing the parts the data supports, and disclose any omitted series rather than dropping it silently.
- Scripts are deterministic: no random numbers, no timestamps in filenames or files. The same data renders to the same bytes.

## Pre-render checks

Catch failures as assertions in the script before the first render, and check the rest by inspection:

- Series align: every series shares the x values or has the frame's length; missing values are counted and each is decided as gap or omission.
- Axis limits cover the data with room for end labels; bar baselines include zero.
- Units are consistent within a series. When one subject appears in several configurations, the measurement basis (effort or mode, per attempt or per full run) is stated in the caption.
- A log axis carries no bars; grouped bars past about three groups per category become a dot plot.
- Every hued series maps to an entry in the document's semantic map.

## Verification

1. The script ran and wrote both themes as PNG and SVG.
2. Both PNGs were opened and judged at the delivery width (the 1440 px render shown at about 704 px): ticks readable, nothing clipped, end labels apart, the focal series read first, the dark render legible.
3. Cold read: from the chart alone, with the caption covered, a reader can state the claim in one sentence. A chart that passes every rule and says nothing fails here.
4. Every number in the chart traces to the user's data.
5. Report `PASSED`, `PASSED WITH FIXES` (what was fixed and rerendered), or `BLOCKED` (which input is missing), with the caption draft and a one-sentence alt text: what is shown and the takeaway.

Rerender after any label or layout correction, and after a data fix rerender every chart drawn from those numbers. Do not add chart types or style variants to prolong the review.

## Accessibility

- Color is never the only channel: the focal series is also heavier, every series is labeled in place, and a second system gets a different dash or marker.
- Blue and vermillion are the pair that stays apart under color-vision deficiency; magenta differs in lightness from both.
- Text meets 4.5:1 against what is under it and meaningful lines 3:1; the theme tokens already satisfy this on the baked background.

## Gotchas

- Constrained layout counts direct labels, so end labels no longer clip at the canvas edge, but `label_ends` draws once to measure the axes. Call it after the limits and the other text are final.
- `bbox_inches="tight"` changes the width and breaks the 1u = 1pt scale. Leave it off; constrained layout already trims the margins.
- `ax.set_ylabel` rotates its text. Use `axis_titles`.
- Setting OpenType features on text at run time misplaces right-aligned and centered numbers, because matplotlib measures without them. The frozen `Pretendard Figure` copy already carries tabular digits.
- A log cost or price axis has no zero, so bar length carries no meaning: plot dots.
- Compare configurations as small multiples on one shared scale (`fm.figure(..., ncols=3, sharey=True)`); a gap smaller than the source's own spread is not a result.
- Matplotlib centers y tick labels on their ascender box, which sets lowercase category names visibly below their dots. `category_axis` centers them on the full box and fixes the ticks so per-label styles hold; numeric ticks keep the default.
