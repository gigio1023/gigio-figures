"""Optional editorial chart preset for matplotlib.

Implements the chart language measured from post-2025 openai.com editorial
figures: optional sans title and chip legend, thin ink axes with left/bottom
spines only, no grid, mono numerals, and one accent family per page. Token
values come from the package's vendored editorial design-system snapshot.

Usage:
    import editorial_mpl as ed
    ed.use()                # or ed.use(dark=True)
    fig, ax = plt.subplots(figsize=(8.3, 6.2))
    ...
    ed.mono_ticks(ax); ed.axis_label(ax, "x name", "y name")
    ed.header(fig, "Title", [("series a", ed.BLUE["chip"], ed.BLUE["deep"])])
    ed.save(fig, "chart_name")   # writes chart_name.svg + chart_name.png
"""

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

_TOKENS_PATH = Path(__file__).resolve().parents[1] / "assets" / "editorial-tokens.json"
_TOKENS = json.loads(_TOKENS_PATH.read_text(encoding="utf-8"))
_COLORS = _TOKENS["colors"]

INK = _COLORS["ink"]
CANVAS = _COLORS["canvas"]
GRAY_TEXT = _COLORS["gray_text"]
GRAY_LINE = _COLORS["gray_line"]

# Accent families: light fill / chip / mid / deep. One family per page; a
# second appears only to contrast two systems.
BLUE = _COLORS["blue"]
GREEN = _COLORS["green"]
CORAL = _COLORS["coral"]

# Measured dark-mode series colors (OSWorld chart, dark variant). In dark mode
# prefer chip-step colors or these; mids sink into the dark surface.
DARK_BLUE = _COLORS["dark"]["blue"]
DARK_MAGENTA = _COLORS["dark"]["magenta"]

SANS = _TOKENS["typography"]["sans"]
MONO = _TOKENS["typography"]["mono"]


def use(dark=False):
    """Activate the style. Call before creating figures."""
    ink = _COLORS["dark"]["ink"] if dark else INK
    canvas = _COLORS["dark"]["canvas"] if dark else CANVAS
    mpl.rcParams.update({
        "figure.facecolor": canvas,
        "axes.facecolor": canvas,
        "savefig.facecolor": canvas,
        "svg.fonttype": "none",      # keep text as <text>; fonts via CSS stack
        "font.family": SANS,
        "text.color": ink,
        "axes.edgecolor": ink,
        "axes.labelcolor": ink,
        "axes.linewidth": 1.2,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "xtick.color": ink,
        "ytick.color": ink,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 5,
        "ytick.major.size": 5,
        "xtick.major.width": 1.2,
        "ytick.major.width": 1.2,
        "lines.linewidth": 2.4,
        "legend.frameon": False,
    })


def _ink():
    return mpl.rcParams["text.color"]


def mono_ticks(ax, size=11.5):
    """Tick labels in the mono voice. Call after ticks are final."""
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontfamily(MONO)
        lab.set_fontsize(size)


def axis_label(ax, xlabel=None, ylabel=None, size=11.5):
    """Axis titles: mono UPPERCASE."""
    if xlabel:
        ax.set_xlabel(xlabel.upper(), fontfamily=MONO, fontsize=size, labelpad=10)
    if ylabel:
        ax.set_ylabel(ylabel.upper(), fontfamily=MONO, fontsize=size, labelpad=10)


def header(fig, title=None, entries=(), title_size=17, y=0.955):
    """Optionally draw a title and one row of chip+label legend pairs.

    entries: iterable of (label, chip_facecolor, chip_edgecolor). Labels are
    uppercased mono. Call only when the surrounding artifact does not already
    supply the title or direct labels cannot distinguish the series.
    """
    if title:
        fig.text(0.04, y, title, ha="left", va="top",
                 fontsize=title_size, fontweight="bold", fontfamily=SANS,
                 color=_ink())
    if not entries:
        return
    ly = y - 0.075 if title else y
    x = 0.045
    for label, face, edge in entries:
        fig.add_artist(Line2D([x], [ly], marker="o", markersize=7.5,
                              markerfacecolor=face, markeredgecolor=edge,
                              markeredgewidth=1.4, linestyle="none",
                              transform=fig.transFigure, clip_on=False))
        text = fig.text(x + 0.016, ly, label.upper(), ha="left",
                        va="center_baseline", fontsize=11, fontfamily=MONO,
                        color=_ink())
        fig.canvas.draw()  # measure the label to place the next pair
        bbox = text.get_window_extent()
        x = bbox.transformed(fig.transFigure.inverted()).x1 + 0.045


def direct_label(ax, x, y, text, color, size=12, dx=0, dy=0, ha="left"):
    """Series-colored mono annotation next to a mark. Use sparingly (line
    endpoints, one emphasized value) - never a number on every point."""
    ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points",
                fontfamily=MONO, fontsize=size, color=color, ha=ha,
                va="center_baseline", clip_on=False, annotation_clip=False)


def save(fig, stem, png_dpi=160):
    """Write stem.svg (text preserved) and stem.png (proof render)."""
    fig.savefig(f"{stem}.svg")
    fig.savefig(f"{stem}.png", dpi=png_dpi)
