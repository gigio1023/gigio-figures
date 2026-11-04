"""Reference charts for uncertainty in measured results on the technical-figure chart route.

    uv run --with matplotlib python example_uncertainty.py [out_dir]

Writes example_band (accuracy over checkpoints with defined interval bands)
and example_interval (per-task gain with its interval and the raw seeds) as
.light/.dark PNG and SVG into `out_dir` (default: the current directory), and
prints each chart's caption.

All numbers below are synthetic, typed in by hand to exercise the layout.
They are not measurements of any run.
"""

import math
import statistics
import sys
from pathlib import Path
from typing import Final

from matplotlib.axes import Axes
from matplotlib.figure import Figure

import figure_mpl as fm

# Accuracy of two training curricula on one 500-item evaluation set per checkpoint.
CHECKPOINTS_K: Final[list[int]] = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
ITEMS: Final[int] = 500
ACCURACY: Final[dict[str, list[float]]] = {
    "curriculum": [0.412, 0.468, 0.511, 0.547, 0.571, 0.590, 0.604, 0.613, 0.619, 0.622],
    "uniform": [0.405, 0.447, 0.481, 0.507, 0.528, 0.543, 0.554, 0.561, 0.566, 0.569],
}
# Gain of curriculum over uniform in accuracy points, paired by training seed.
GAIN_BY_SEED: Final[dict[str, list[float]]] = {
    "arithmetic": [4.8, 6.1, 5.2, 3.9, 5.6],
    "code repair": [2.1, 0.4, 3.0, 1.2, 2.6],
    "reading": [0.9, -1.2, 1.8, -0.4, 0.6],
    "science QA": [3.3, 2.2, 4.1, 2.9, 3.6],
}
HUE_MAP: Final[dict[str, fm.HueName]] = {"curriculum": "blue"}  # the document's semantic map
Z_95: Final[float] = 1.959964  # standard normal 97.5th percentile
T_95_DF4: Final[float] = 2.776445  # Student t 97.5th percentile, 4 degrees of freedom (5 seeds)
BAND_LIMITS: Final[tuple[float, float]] = (0.34, 0.68)
GAIN_LIMITS: Final[tuple[float, float]] = (-3.0, 8.0)

BAND_DEFINITION: Final[str] = f"95% Wilson interval over {ITEMS} items"
INTERVAL_DEFINITION: Final[str] = "mean and 95% t-interval over 5 seeds"
CAPTIONS: Final[dict[str, str]] = {
    "example_band": f"Accuracy per checkpoint; bands are the {BAND_DEFINITION}, one evaluation run per checkpoint.",
    "example_interval": (
        "Gain of curriculum over uniform per task, paired by seed; dots and lines are the "
        f"{INTERVAL_DEFINITION}, open circles the individual seeds."
    ),
}


def wilson(p: float, n: int) -> tuple[float, float]:
    """95% Wilson score interval of a proportion `p` observed over `n` items."""
    center: float = (p + Z_95**2 / (2 * n)) / (1 + Z_95**2 / n)
    half: float = Z_95 * math.sqrt(p * (1 - p) / n + Z_95**2 / (4 * n**2)) / (1 + Z_95**2 / n)
    return center - half, center + half


def t_interval(values: list[float]) -> tuple[float, float, float]:
    """(mean, low, high) of the 95% t-interval for the mean of five values."""
    mean: float = statistics.mean(values)
    half: float = T_95_DF4 * statistics.stdev(values) / math.sqrt(len(values))
    return mean, mean - half, mean + half


# Pre-render checks: aligned series, one replicate count, limits that cover every interval.
for _name, _values in ACCURACY.items():
    assert len(_values) == len(CHECKPOINTS_K), f"{_name} does not align with CHECKPOINTS_K"
    assert all(BAND_LIMITS[0] <= wilson(v, ITEMS)[0] and wilson(v, ITEMS)[1] <= BAND_LIMITS[1] for v in _values)
for _task, _gains in GAIN_BY_SEED.items():
    assert len(_gains) == 5, f"{_task} needs 5 seeds to match T_95_DF4"
    _, _low, _high = t_interval(_gains)
    assert GAIN_LIMITS[0] <= min(_low, *_gains) and max(_high, *_gains) <= GAIN_LIMITS[1], f"{_task} exceeds limits"


def draw_band() -> Figure:
    """Each series with its defined band behind the opaque line; the focal series in its hue and on top."""
    fig: Figure
    ax: Axes
    fig, ax = fm.figure(400)
    for name, values in ACCURACY.items():
        hue_name: fm.HueName | None = HUE_MAP.get(name)
        bounds: list[tuple[float, float]] = [wilson(v, ITEMS) for v in values]
        fm.band(
            ax,
            CHECKPOINTS_K,
            [low for low, _ in bounds],
            [high for _, high in bounds],
            definition=BAND_DEFINITION,
            hue_name=hue_name,
        )
        ax.plot(CHECKPOINTS_K, values, **(fm.focal(hue_name) if hue_name else fm.context()))
    ax.set_xlim(CHECKPOINTS_K[0], CHECKPOINTS_K[-1])
    ax.set_ylim(*BAND_LIMITS)
    ax.set_xticks(range(4, 21, 4))
    ax.set_yticks([0.4, 0.5, 0.6])
    fm.axis_titles(ax, x="Checkpoint (thousand steps)", y="Accuracy")
    fm.label_ends(
        ax, CHECKPOINTS_K[-1], [(v[-1], name, HUE_MAP.get(name)) for name, v in ACCURACY.items()], mono=True
    )
    return fig


def draw_interval() -> Figure:
    """The difference itself, with its interval and raw seeds, read against a zero reference."""
    fig: Figure
    ax: Axes
    fig, ax = fm.figure(240)
    summary: list[tuple[str, tuple[float, float, float]]] = sorted(
        ((task, t_interval(gains)) for task, gains in GAIN_BY_SEED.items()), key=lambda item: -item[1][0]
    )
    rows: list[int] = list(range(len(summary)))
    ax.axvline(0, color=fm.neutral("line"), linewidth=fm.STROKE["edge_u"], zorder=2)  # no gain: the reference
    fm.interval_dots(
        ax,
        rows,
        [mean for _, (mean, _, _) in summary],
        [(low, high) for _, (_, low, high) in summary],
        definition=INTERVAL_DEFINITION,
        hue_name="blue",
        replicates=[GAIN_BY_SEED[task] for task, _ in summary],
    )
    fm.category_axis(ax, [task for task, _ in summary])
    ax.set_ylim(len(rows) - 0.5, -0.5)  # largest gain at the top; seed strips sit below their dots
    ax.set_xlim(*GAIN_LIMITS)
    ax.set_xticks([-2, 0, 2, 4, 6, 8])
    fm.value_grid(ax, "x")
    fm.axis_titles(ax, x="Gain over uniform (accuracy points)")
    return fig


def main(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    return fm.render(draw_band, out_dir / "example_band") + fm.render(draw_interval, out_dir / "example_interval")


if __name__ == "__main__":
    target: Path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    for path in main(target):
        print(path)
    for stem, caption in CAPTIONS.items():
        print(f"{stem}: {caption}")
