"""Reference charts for the technical-figure chart route; the tests render them too.

    uv run --with matplotlib python example_chart.py [out_dir]

Writes example_line and example_dots as .light/.dark PNG and SVG into
`out_dir` (default: the current directory).

All numbers below are synthetic, typed in by hand to exercise the layout.
They are not measurements of any run.
"""

import math
import sys
from pathlib import Path
from typing import Any, Final

from matplotlib.axes import Axes
from matplotlib.figure import Figure

import figure_mpl as fm

STEPS_K: Final[list[int]] = [0, 2, 4, 6, 8, 10, 12, 14, 16]
LOSS: Final[dict[str, list[float]]] = {
    "cosine_warmup": [3.20, 2.58, 2.24, 2.06, 1.95, 1.88, 1.83, 1.81, 1.80],
    "linear_decay": [3.20, 2.64, 2.36, 2.20, 2.09, 2.01, 1.96, 1.93, 1.91],
    "step_decay": [3.20, 2.67, 2.41, 2.27, 2.14, 2.07, 2.02, 1.99, 1.98],
    "constant": [3.20, 2.70, 2.46, 2.32, 2.23, 2.17, 2.12, 2.09, 2.07],
}
# The document's semantic map gives blue to the proposed schedule; the chart
# reuses it so the schematic and the chart color the same entity the same way.
HUE_MAP: Final[dict[str, fm.HueName]] = {"cosine_warmup": "blue"}
FOCAL: Final[str] = "cosine_warmup"
Y_LIMITS: Final[tuple[float, float]] = (1.7, 3.3)
X_LIMITS: Final[tuple[float, float]] = (1.75, 2.1)

# Pre-render checks: aligned series, no silent gaps, limits that cover the data.
for _name, _values in LOSS.items():
    assert len(_values) == len(STEPS_K), f"{_name} does not align with STEPS_K"
    assert not any(math.isnan(v) for v in _values), f"{_name} has missing values; decide gap or omit"
    assert Y_LIMITS[0] <= min(_values) and max(_values) <= Y_LIMITS[1], f"{_name} falls outside Y_LIMITS"
    assert X_LIMITS[0] <= _values[-1] <= X_LIMITS[1], f"{_name} final value falls outside X_LIMITS"


def draw_line() -> Figure:
    """One focal series in its semantic hue, the rest as context, labeled at their ends."""
    fig: Figure
    ax: Axes
    fig, ax = fm.figure(400)
    for name, values in LOSS.items():
        style: dict[str, Any] = fm.focal(HUE_MAP[name]) if name in HUE_MAP else fm.context()
        ax.plot(STEPS_K, values, **style)
    ax.set_xlim(STEPS_K[0], STEPS_K[-1])
    ax.set_ylim(*Y_LIMITS)
    ax.set_xticks(range(0, 17, 4))
    ax.set_yticks([2.0, 2.5, 3.0])
    fm.axis_titles(ax, x="Training step (thousands)", y="Validation loss")
    fm.label_ends(ax, STEPS_K[-1], [(v[-1], name, HUE_MAP.get(name)) for name, v in LOSS.items()], mono=True)
    return fig


def draw_dots() -> Figure:
    """Final values as a dot plot: sorted, focal dot and label in the hue, hairline grid for reading values."""
    fig: Figure
    ax: Axes
    fig, ax = fm.figure(200)
    ranked: list[tuple[str, float]] = sorted(((n, v[-1]) for n, v in LOSS.items()), key=lambda item: item[1])
    rows: list[int] = list(range(len(ranked)))
    for row, (name, value) in zip(rows, ranked, strict=True):
        style: dict[str, Any] = fm.focal(HUE_MAP[name]) if name in HUE_MAP else fm.context()
        ax.plot([value], [row], "o", **style)
        if name == FOCAL:
            fm.direct_label(ax, value, row, f"{value:.2f}", hue_name=HUE_MAP[name], dx=10)
    fm.category_axis(ax, [name for name, _ in ranked], hues=HUE_MAP, mono=True)  # names are config keys
    ax.set_ylim(len(rows) - 0.5, -0.5)  # best at the top
    ax.set_xlim(*X_LIMITS)
    ax.set_xticks([1.8, 1.9, 2.0, 2.1])
    fm.value_grid(ax, "x")
    fm.axis_titles(ax, x="최종 검증 손실")
    return fig


def main(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    return fm.render(draw_line, out_dir / "example_line") + fm.render(draw_dots, out_dir / "example_dots")


if __name__ == "__main__":
    target: Path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    for path in main(target):
        print(path)
