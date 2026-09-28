"""Matplotlib style for the technical-figure chart route.

Charts share the design tokens of every other technical-figure route
(`assets/figure-tokens.json`): Pretendard for Latin and Korean text, JetBrains
Mono only for literal code identifiers, the theme palettes, the stroke scale,
and the 720u canvas.

Scale: a figure is `canvas_width_u / 72` inches wide, so its width in points
equals its width in u and 1u is 1pt. Saving at `72 * export_scale` dpi then
gives `export_scale` pixels per u: a 720u figure becomes a 1440 px PNG in which
a 12u tick label is 24 px tall, the same as the SVG routes' 2x export. Token
sizes and strokes therefore pass to matplotlib unchanged as points.

Usage:

    import figure_mpl as fm

    def draw() -> Figure:
        fig, ax = fm.figure(400)
        ax.plot(x, y_other, **fm.context())
        ax.plot(x, y_ours, **fm.focal("blue"))
        fm.label_ends(ax, x[-1], [(y_ours[-1], "ours", "blue"), (y_other[-1], "baseline", None)])
        fm.axis_titles(ax, x="Step", y="Loss")
        return fig

    fm.render(draw, "loss")  # loss.light.png/.svg and loss.dark.png/.svg
"""

import json
import logging
import os
import re
import warnings
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, Final, Literal, TypedDict

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler
from fontTools.ttLib import TTFont  # a matplotlib dependency
from fontTools.ttLib.tables import otTables
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.backend_bases import RendererBase
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.text import Annotation, Text
from matplotlib.transforms import Bbox

type Theme = Literal["light", "dark"]
type HueName = Literal["blue", "vermillion", "magenta"]
type HueRole = Literal["stroke", "fill", "text"]
type Neutral = Literal["bg", "surface", "ink", "ink_2", "line", "guide"]
type TextRole = Literal["tick", "axis", "label", "title", "panel", "annotation"]
type Axis = Literal["x", "y"]


# TypedDict rather than Pydantic: the chart route runs under
# `uv run --with matplotlib` with no other dependency, and these types only name
# the JSON shape that figure-tokens.json already fixes.
class HueTokens(TypedDict):
    stroke: str
    fill: str
    text: str


class ThemeTokens(TypedDict):
    bg: str
    surface: str
    ink: str
    ink_2: str
    line: str
    guide: str
    hues: dict[str, HueTokens]
    categorical: list[str]


class TypeTokens(TypedDict):
    size_u: float
    weight: int
    color: Neutral


TOKENS_PATH: Final[Path] = Path(__file__).resolve().parents[1] / "assets" / "figure-tokens.json"
TOKENS: Final[dict[str, Any]] = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))  # raw JSON

THEMES: Final[tuple[Theme, ...]] = ("light", "dark")
CANVAS_U: Final[float] = TOKENS["units"]["canvas_width_u"]
WIDE_CANVAS_U: Final[float] = TOKENS["units"]["wide_canvas_width_u"]
EXPORT_SCALE: Final[int] = TOKENS["units"]["export_scale"]
PT_PER_U: Final[float] = 1.0  # figure width in pt == canvas width in u (see module docstring)
DPI: Final[float] = 72 * EXPORT_SCALE / PT_PER_U
# The height budget is given in CSS px at the delivery width; convert it to u.
MAX_HEIGHT_U: Final[float] = (
    TOKENS["units"]["max_height_css_px"] * CANVAS_U / TOKENS["units"]["delivery_width_css_px"]
)

STROKE: Final[dict[str, float]] = {k: v for k, v in TOKENS["stroke"].items() if k.endswith("_u") and k != "allowed_u"}

# Chart text roles mapped onto the shared type roles, so a tick label is the
# same size as an SVG annotation and a direct label the same as an edge label.
_ROLE_TYPE: Final[dict[TextRole, str]] = {
    "tick": "annotation",  # 12u, 400, ink_2
    "axis": "edge_label",  # 12.5u, 400, ink_2
    "label": "edge_label",  # direct labels; a focal label takes the hue text color and weight 600
    "title": "node_label",  # small-multiple panel titles, 14u, 600, ink
    "panel": "panel_label",  # (a), (b), 15u, 600, ink
    "annotation": "annotation",
}
TYPE: Final[dict[str, TypeTokens]] = {name: TOKENS["type"][name] for name in _ROLE_TYPE.values()}
_EMPHASIS_WEIGHT: Final[int] = TOKENS["type"]["node_label"]["weight"]
_MONO_WEIGHT: Final[int] = TOKENS["type"]["node_label"]["mono_weight"]

FONT_FILES: Final[tuple[str, ...]] = (
    "Pretendard-Regular.otf",
    "Pretendard-SemiBold.otf",
    "JetBrainsMono-Regular.ttf",
    "JetBrainsMono-Medium.ttf",
)
SANS_FAMILY: Final[str] = TOKENS["fonts"]["sans"]["family"]
MONO_FAMILY: Final[str] = TOKENS["fonts"]["mono"]["family"]
# Registered name of the Pretendard copy with features baked in; a distinct
# name keeps a system-installed Pretendard from being picked instead.
FIGURE_SANS_FAMILY: Final[str] = f"{SANS_FAMILY} Figure"
# tnum first: Pretendard's ss06 lookup runs before tnum and leaves its 4, 6,
# and 9 proportional, but ss06 does map the tabular digits to tabular
# high-legibility forms. This order yields evenly spaced digits throughout.
FROZEN_FEATURES: Final[tuple[str, ...]] = ("tnum", *re.findall(r'"(\w{4})"', TOKENS["fonts"]["sans"]["features"]))

_active: Theme = "light"
_fonts_registered: bool = False
_sans: list[str] = ["DejaVu Sans"]
_mono: list[str] = ["DejaVu Sans Mono"]


def font_dir() -> Path:
    """Return the directory `scripts/setup.sh` downloads the OFL fonts into."""
    root: str = os.environ.get("TECHNICAL_FIGURE_CACHE") or ""
    if not root:
        cache: Path = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
        root = str(cache / "technical-figure")
    return Path(root) / "fonts"


def _freeze_features(source: Path) -> Path:
    """Return a copy of a Pretendard file whose default glyphs already carry FROZEN_FEATURES.

    Matplotlib 3.11 draws with OpenType features but measures text without
    them, so a runtime `tnum` shifts right-aligned and centered numbers by up
    to a third of an em. Writing the single substitutions into the character
    map instead makes tabular, high-legibility digits the defaults, and layout
    and drawing agree. The copy is written once beside the font cache (about
    two seconds per weight) and reused while it is newer than its source.
    """
    name: str = source.name.replace(SANS_FAMILY, FIGURE_SANS_FAMILY.replace(" ", ""))
    target: Path = source.parent.parent / "matplotlib" / name
    if target.is_file() and target.stat().st_mtime >= source.stat().st_mtime:
        return target
    font: TTFont = TTFont(source)
    gsub: otTables.GSUB = font["GSUB"].table
    for tag in FROZEN_FEATURES:
        indices: list[int] = sorted({
            index
            for record in gsub.FeatureList.FeatureRecord
            if record.FeatureTag == tag
            for index in record.Feature.LookupListIndex
        })
        for index in indices:
            lookup: otTables.Lookup = gsub.LookupList.Lookup[index]
            mapping: dict[str, str] = {}
            for subtable in lookup.SubTable:
                inner: otTables.SingleSubst = subtable.ExtSubTable if lookup.LookupType == 7 else subtable
                mapping.update(getattr(inner, "mapping", {}))  # single substitutions; others do not apply to digits
            for cmap in font["cmap"].tables:
                cmap.cmap = {code: mapping.get(glyph, glyph) for code, glyph in cmap.cmap.items()}
    for record in font["name"].names:
        if record.nameID in (1, 16):  # family names; FreeType reports ID 16 when present
            record.string = record.toUnicode().replace(SANS_FAMILY, FIGURE_SANS_FAMILY)
    target.parent.mkdir(parents=True, exist_ok=True)
    font.save(target)
    return target


def _register_fonts() -> None:
    """Register the cached fonts once and resolve the family stacks.

    Missing files produce one warning; text then falls back along the token
    stacks to whatever the system has, which changes widths, loses tabular
    digits, and may lose Hangul coverage on machines without a Korean font.
    """
    global _fonts_registered, _sans, _mono
    if _fonts_registered:
        return
    directory: Path = font_dir()
    missing: list[str] = []
    for name in FONT_FILES:
        path: Path = directory / name
        if not path.is_file():
            missing.append(name)
            continue
        if name.startswith(SANS_FAMILY):
            path = _freeze_features(path)
        font_manager.fontManager.addfont(str(path))
    if missing:
        warnings.warn(
            f"technical-figure fonts missing from {directory}: {', '.join(missing)}. "
            "Falling back to system fonts; run scripts/setup.sh to install Pretendard and JetBrains Mono.",
            RuntimeWarning,
            stacklevel=3,
        )
        # One warning is enough; matplotlib would otherwise log every weight
        # it substitutes along the fallback stack.
        logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    available: set[str] = {entry.name for entry in font_manager.fontManager.ttflist}
    if FIGURE_SANS_FAMILY in available:
        _sans = [FIGURE_SANS_FAMILY]
    else:
        _sans = [f for f in TOKENS["fonts"]["sans"]["stack"] if f in available] + ["DejaVu Sans"]
    if MONO_FAMILY in available:
        _mono = [MONO_FAMILY]
    else:
        _mono = [f for f in TOKENS["fonts"]["mono"]["stack"] if f in available] + ["DejaVu Sans Mono"]
    _fonts_registered = True


def _theme(theme: Theme | None = None) -> ThemeTokens:
    return TOKENS["themes"][theme or _active]


def neutral(name: Neutral, theme: Theme | None = None) -> str:
    """Neutral color of the active (or given) theme: bg, surface, ink, ink_2, line, guide."""
    return _theme(theme)[name]


def hue(name: HueName, role: HueRole = "stroke", theme: Theme | None = None) -> str:
    """Semantic hue: `stroke` for marks, `fill` for areas, `text` for labels in that hue."""
    return _theme(theme)["hues"][name][role]


def categorical(theme: Theme | None = None) -> list[str]:
    """The theme's categorical palette, to be used in order, only when no series is focal."""
    return list(_theme(theme)["categorical"])


def sequential(name: HueName, theme: Theme | None = None) -> LinearSegmentedColormap:
    """Single-hue ramp from the hue's fill to its stroke, for heatmaps."""
    colors: list[str] = [hue(name, "fill", theme), hue(name, "stroke", theme)]
    return LinearSegmentedColormap.from_list(f"{name}-{theme or _active}", colors)


def size_pt(size_u: float) -> float:
    """Token size in u to matplotlib points."""
    return size_u * PT_PER_U


def use(theme: Theme = "light") -> None:
    """Activate a theme for figures created afterwards. Colors are baked at draw time."""
    global _active
    _register_fonts()
    _active = theme
    t: ThemeTokens = _theme(theme)
    unit: float = TOKENS["spacing_u"]["unit"] * PT_PER_U
    margin_in: float = TOKENS["spacing_u"]["canvas_margin"] * PT_PER_U / 72
    guide_pt: float = STROKE["guide_u"] * PT_PER_U
    tick: TypeTokens = TYPE[_ROLE_TYPE["tick"]]
    axis: TypeTokens = TYPE[_ROLE_TYPE["axis"]]
    title: TypeTokens = TYPE[_ROLE_TYPE["title"]]
    mpl.rcParams.update({
        # Background baked into every export; a transparent PNG loses dark lines on a dark page.
        "figure.facecolor": t["bg"],
        "axes.facecolor": t["bg"],
        "savefig.facecolor": t["bg"],
        "savefig.transparent": False,
        "savefig.dpi": DPI,
        "savefig.bbox": "standard",  # "tight" would change the width and break the u scale
        "figure.dpi": DPI,
        "figure.constrained_layout.use": True,
        "figure.constrained_layout.w_pad": margin_in,
        "figure.constrained_layout.h_pad": margin_in,
        "svg.fonttype": "path",
        "svg.hashsalt": "technical-figure",
        "font.family": _sans,
        "font.size": size_pt(tick["size_u"]),
        "text.color": t["ink"],
        # Frame layer, lighter than any series: guide spines on two sides, no grid unless asked for.
        "axes.edgecolor": t["guide"],
        "axes.linewidth": guide_pt,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "axes.axisbelow": True,
        "grid.color": t["guide"],
        "grid.linewidth": guide_pt,
        "axes.labelsize": size_pt(axis["size_u"]),
        "axes.labelweight": axis["weight"],
        "axes.labelcolor": t[axis["color"]],
        "axes.labelpad": 2 * unit,
        "axes.titlesize": size_pt(title["size_u"]),
        "axes.titleweight": title["weight"],
        "axes.titlecolor": t[title["color"]],
        "axes.titlelocation": "left",
        "axes.titlepad": 3 * unit,
        # Un-styled series default to context gray; a hue is always a deliberate choice.
        "axes.prop_cycle": cycler(color=[t["line"]]),
        "lines.linewidth": STROKE["edge_u"] * PT_PER_U,
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        "lines.dash_capstyle": "round",
        "lines.scale_dashes": False,  # dash patterns stay in u, not multiples of the stroke
        "lines.dashed_pattern": [float(v) * PT_PER_U for v in TOKENS["dash"]["dashed"].split()],
        "lines.dotted_pattern": [float(v) * PT_PER_U for v in TOKENS["dash"]["dotted"].split()],
        "lines.markersize": 2 * unit,
        "lines.markeredgewidth": 0,
        "legend.frameon": False,
        "legend.fontsize": size_pt(axis["size_u"]),
        "legend.labelcolor": t["ink_2"],
        "xtick.labelsize": size_pt(tick["size_u"]),
        "ytick.labelsize": size_pt(tick["size_u"]),
        "xtick.labelcolor": t[tick["color"]],
        "ytick.labelcolor": t[tick["color"]],
        "xtick.color": t["guide"],
        "ytick.color": t["guide"],
        "xtick.major.size": unit,
        "ytick.major.size": unit,
        "xtick.major.width": guide_pt,
        "ytick.major.width": guide_pt,
        "xtick.major.pad": unit,
        "ytick.major.pad": unit,
    })


def figsize(height_u: float, *, wide: bool = False) -> tuple[float, float]:
    """Figure size in inches for a canvas of 720u (1080u when `wide`) by `height_u`."""
    if height_u > MAX_HEIGHT_U:
        warnings.warn(
            f"height {height_u:.0f}u exceeds the {MAX_HEIGHT_U:.0f}u screen budget; split or rearrange the chart",
            stacklevel=2,
        )
    width_u: float = WIDE_CANVAS_U if wide else CANVAS_U
    return width_u * PT_PER_U / 72, height_u * PT_PER_U / 72


def figure(
    height_u: float = 400, *, wide: bool = False, nrows: int = 1, ncols: int = 1, **kwargs: Any
) -> tuple[Figure, Any]:
    """`plt.subplots` at the canvas width with constrained layout; returns (fig, axes)."""
    return plt.subplots(nrows, ncols, figsize=figsize(height_u, wide=wide), layout="constrained", **kwargs)


def focal(name: HueName) -> dict[str, Any]:
    """Line or marker kwargs for the one focal series: hue stroke, emphasis width, drawn on top."""
    return {"color": hue(name), "linewidth": STROKE["emphasis_u"] * PT_PER_U, "zorder": 3}


def context() -> dict[str, Any]:
    """Line or marker kwargs for a context series: `line` gray at the edge width."""
    return {"color": neutral("line"), "linewidth": STROKE["edge_u"] * PT_PER_U, "zorder": 2}


def text_style(role: TextRole = "label", *, hue_name: HueName | None = None, mono: bool = False) -> dict[str, Any]:
    """Font kwargs for a text role; `hue_name` marks a focal label, `mono` a literal code identifier."""
    spec: TypeTokens = TYPE[_ROLE_TYPE[role]]
    style: dict[str, Any] = {
        "fontsize": size_pt(spec["size_u"]),
        "fontweight": spec["weight"],
        "color": neutral(spec["color"]),
        "fontfamily": _sans,
    }
    if hue_name is not None:
        style["color"] = hue(hue_name, "text")
        style["fontweight"] = _EMPHASIS_WEIGHT
    if mono:
        style["fontfamily"] = _mono
        style["fontweight"] = _MONO_WEIGHT
    return style


def direct_label(
    ax: Axes,
    x: float,
    y: float,
    text: str,
    *,
    hue_name: HueName | None = None,
    mono: bool = False,
    dx: float = 6,
    dy: float = 0,
    ha: Literal["left", "center", "right"] = "left",
    va: Literal["center", "bottom", "top", "baseline"] = "center",
) -> Annotation:
    """Label a mark in place, offset by (dx, dy) in u. Constrained layout keeps it inside the canvas."""
    return ax.annotate(
        text,
        (x, y),
        xytext=(dx * PT_PER_U, dy * PT_PER_U),
        textcoords="offset points",
        ha=ha,
        va=va,
        annotation_clip=False,
        **text_style("label", hue_name=hue_name, mono=mono),
    )


def _spread(positions: Sequence[float], gap: float) -> list[float]:
    """Place sorted positions at least `gap` apart, each crowded cluster centered on its members' mean."""
    clusters: list[list[float]] = []
    for p in positions:
        clusters.append([p])
        while len(clusters) > 1:
            below: list[float] = clusters[-2]
            above: list[float] = clusters[-1]
            below_top: float = sum(below) / len(below) + (len(below) - 1) * gap / 2
            above_bottom: float = sum(above) / len(above) - (len(above) - 1) * gap / 2
            if above_bottom - below_top >= gap:
                break
            clusters[-2:] = [below + above]
    placed: list[float] = []
    for cluster in clusters:
        start: float = sum(cluster) / len(cluster) - (len(cluster) - 1) * gap / 2
        placed.extend(start + i * gap for i in range(len(cluster)))
    return placed


def label_ends(
    ax: Axes,
    x: float,
    labels: Sequence[tuple[float, str, HueName | None]],
    *,
    mono: bool = False,
    gap_u: float = 16,
    dx: float = 6,
) -> list[Annotation]:
    """Direct-label line endpoints at `x`, nudging labels apart vertically so none overlap.

    `labels` holds (y, text, hue or None). Call after the axis limits are final:
    the nudge converts data to points from the laid-out axes height.
    """
    fig: Figure | None = ax.get_figure(root=True)
    if fig is None:
        raise ValueError("label_ends needs axes that belong to a figure")
    fig.canvas.draw()  # settle constrained layout so the axes height is final
    y0: float
    y1: float
    y0, y1 = ax.get_ylim()
    height_pt: float = ax.get_window_extent().height * 72 / fig.dpi
    points: list[float] = [(y - y0) / (y1 - y0) * height_pt for y, _, _ in labels]
    order: list[int] = sorted(range(len(labels)), key=lambda i: points[i])
    placed: list[float] = _spread([points[i] for i in order], gap_u * PT_PER_U)
    annotations: list[Annotation] = []
    for i, target in zip(order, placed, strict=True):
        y, text, hue_name = labels[i]
        dy_u: float = (target - points[i]) / PT_PER_U
        annotations.append(direct_label(ax, x, y, text, hue_name=hue_name, mono=mono, dx=dx, dy=dy_u))
    return annotations


def axis_titles(ax: Axes, x: str | None = None, y: str | None = None) -> None:
    """Axis titles without rotated text: x at the right end below the axis, y horizontal above its tick labels."""
    if x is not None:
        ax.set_xlabel(x, loc="right")
    if y is not None:
        ax.set_ylabel("")

        def tick_label_box(renderer: RendererBase) -> Bbox:
            box: Bbox | None = ax.yaxis.get_tightbbox(renderer)
            return box if box is not None else ax.bbox

        def decorations_box(renderer: RendererBase) -> Bbox:
            # Axes, ticks, and title only (no child artists, which include this label):
            # with a panel title the y title becomes a row-level unit label above it.
            box: Bbox | None = ax.get_tightbbox(renderer, bbox_extra_artists=[])
            return box if box is not None else ax.bbox

        ax.annotate(
            y,
            xy=(0, 1),
            xycoords=(tick_label_box, decorations_box),
            xytext=(0, TOKENS["spacing_u"]["unit"] * 2 * PT_PER_U),
            textcoords="offset points",
            ha="left",
            va="bottom",
            annotation_clip=False,
            **text_style("axis"),
        )


def category_axis(
    ax: Axes, labels: Sequence[str], *, axis: Axis = "y", hues: Mapping[str, HueName] | None = None, mono: bool = False
) -> None:
    """Put categories at 0..n-1 on `axis`, labeled as direct labels (a mapped one in its hue), without spine or ticks.

    Words are centered on their full box: matplotlib's default `center_baseline`
    centers the ascender box and sets lowercase labels visibly low.
    """
    positions: list[int] = list(range(len(labels)))
    if axis == "y":
        ax.set_yticks(positions, labels)
        texts: list[Text] = ax.get_yticklabels()
    else:
        ax.set_xticks(positions, labels)
        texts = ax.get_xticklabels()
    ax.spines["left" if axis == "y" else "bottom"].set_visible(False)
    ax.tick_params(axis=axis, length=0)
    for text, label in zip(texts, labels, strict=True):
        text.set(**text_style("label", hue_name=(hues or {}).get(label), mono=mono))
        if axis == "y":
            text.set_verticalalignment("center")


def value_grid(ax: Axes, axis: Axis = "y") -> None:
    """Hairline guide grid for charts whose point is reading values off `axis`; drops that axis's spine and ticks."""
    ax.grid(True, axis=axis, color=neutral("guide"), linewidth=STROKE["guide_u"] * PT_PER_U)
    ax.set_axisbelow(True)
    ax.spines["left" if axis == "y" else "bottom"].set_visible(False)
    ax.tick_params(axis=axis, length=0)


def _check_width(fig: Figure) -> None:
    width_u: float = fig.get_figwidth() * 72 / PT_PER_U
    if min(abs(width_u - CANVAS_U), abs(width_u - WIDE_CANVAS_U)) > 0.5:
        warnings.warn(
            f"figure is {width_u:.0f}u wide, not {CANVAS_U:.0f}u or {WIDE_CANVAS_U:.0f}u; "
            "text will not render at the token sizes. Use figure() or figsize().",
            stacklevel=3,
        )


def save(fig: Figure, stem: str | Path, theme: Theme | None = None) -> tuple[Path, Path]:
    """Write `stem.<theme>.png` (2x, background baked in) and `stem.<theme>.svg` (text as paths).

    Save under the same `use()` theme the figure was drawn with.
    """
    theme = theme or _active
    _check_width(fig)
    bg: str = neutral("bg", theme)
    png: Path = Path(f"{stem}.{theme}.png")
    svg: Path = Path(f"{stem}.{theme}.svg")
    fig.savefig(png, dpi=DPI, facecolor=bg, edgecolor=bg, transparent=False)
    fig.savefig(svg, facecolor=bg, edgecolor=bg, transparent=False, metadata={"Date": None})
    # Matplotlib sizes the SVG in pt (720pt displays as 960 CSS px); use px so 1u is 1 CSS px.
    source: str = svg.read_text(encoding="utf-8")
    root_in_px: str = re.sub(
        r"<svg\b[^>]*>", lambda m: re.sub(r'="([\d.]+)pt"', r'="\1"', m.group(0)), source, count=1
    )
    svg.write_text(root_in_px, encoding="utf-8")
    return png, svg


def render(draw: Callable[[], Figure], stem: str | Path, themes: Iterable[Theme] = THEMES) -> list[Path]:
    """Call `draw` once per theme under `use(theme)` and save each figure; returns the written paths."""
    paths: list[Path] = []
    for theme in themes:
        use(theme)
        fig: Figure = draw()
        paths.extend(save(fig, stem, theme))
        plt.close(fig)
    return paths
