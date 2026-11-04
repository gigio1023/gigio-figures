"""Audit chart palettes for color-vision-deficiency separation and mark contrast.

    python3 palette_audit.py                                   # palettes in figure-tokens.json, both themes
    python3 palette_audit.py --theme dark --set categorical
    python3 palette_audit.py --colors "#0072B2" "#D55E00" "#009E73" --bg "#FFFFFF"
    python3 palette_audit.py --json > audit.json

For each palette the audit reports the OKLab difference of every color pair
under normal vision and under simulated protan and deutan vision, and the WCAG
contrast of each color against the background. Differences are Euclidean
distances in OKLab times 100 (written dE below). A pair is adjacent when the
two colors are neighbors in palette order, which is how lines in order and
stacked bars place them; scatter and small multiples can put any two colors
side by side, so they need the all-pairs minimum.

Method, from the published sources:

- sRGB decoding and relative luminance: IEC 61966-2-1 and WCAG 2.2.
- OKLab: Ottosson, "A perceptual color space for image processing" (2020).
- Simulation: the protanomaly and deuteranomaly matrices of Machado, Oliveira,
  and Fernandes (2009) at severity 1.0, which model protanopia and
  deuteranopia, applied to linear RGB and clipped to the gamut.

The floors are the skill's defaults for every token palette, documented in
`references/visual-tokens.md`; flags change them only for a custom check:

- Normal vision, dE 10: five times the OKLab just-noticeable difference of 0.02
  that CSS Color 4 uses for gamut mapping. Thin lines and small dots need
  several times the difference large patches need (Stone, Szafir, and Setlur
  2014), so a categorical pair should clear several JNDs.
- Simulated CVD, dE 8: full severity is the worst case; anomalous trichromats,
  the larger share of readers with color-vision deficiency, see more
  difference than the simulation shows.
- Mark contrast against the background: the tokens' `graphic_contrast_min`
  (3:1, WCAG 2.2 SC 1.4.11).

Exit status: 0 when every check passes, 1 when any fails, 2 on invalid input.
Standard library only, so it runs with a bare `python3` (3.12 or newer).
"""

import argparse
import itertools
import json
import math
import re
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Final, Literal

type Rgb = tuple[float, float, float]  # linear-light sRGB, each channel 0..1
type Lab = tuple[float, float, float]  # OKLab L, a, b
type Matrix = tuple[Rgb, Rgb, Rgb]
type Theme = Literal["light", "dark"]
type PaletteSet = Literal["categorical", "semantic"]

TOKENS_PATH: Final[Path] = Path(__file__).resolve().parents[1] / "assets" / "figure-tokens.json"
THEMES: Final[tuple[Theme, ...]] = ("light", "dark")
PALETTE_SETS: Final[tuple[PaletteSet, ...]] = ("categorical", "semantic")
NORMAL_FLOOR: Final[float] = 10.0
CVD_FLOOR: Final[float] = 8.0
HEX_PATTERN: Final[re.Pattern[str]] = re.compile(r"#?([0-9a-fA-F]{6}|[0-9a-fA-F]{3})")


class Vision(StrEnum):
    """Simulated observer; the values appear in the JSON output."""

    NORMAL = "normal"
    PROTAN = "protan"
    DEUTAN = "deutan"


# Machado, Oliveira, and Fernandes (2009), severity 1.0; rows give the simulated
# linear R, G, B from the input linear R, G, B.
MACHADO_2009: Final[dict[Vision, Matrix]] = {
    Vision.PROTAN: (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    Vision.DEUTAN: (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
}

# Ottosson (2020): linear sRGB to the LMS-like cone responses, then the cube
# roots of those to L, a, b.
OKLAB_TO_LMS: Final[Matrix] = (
    (0.4122214708, 0.5363325363, 0.0514459929),
    (0.2119034982, 0.6806995451, 0.1073969566),
    (0.0883024619, 0.2817188376, 0.6299787005),
)
OKLAB_FROM_LMS_ROOTS: Final[Matrix] = (
    (0.2104542553, 0.7936177850, -0.0040720468),
    (1.9779984951, -2.4285922050, 0.4505937099),
    (0.0259040371, 0.7827717662, -0.8086757660),
)
LUMINANCE_WEIGHTS: Final[Rgb] = (0.2126, 0.7152, 0.0722)  # WCAG relative luminance of linear sRGB


# Dataclasses rather than Pydantic: the script stays standard-library only so
# it runs anywhere the skill is installed, and its records never cross a
# boundary other than its own JSON output.
@dataclass(frozen=True)
class PairDistance:
    """OKLab distance times 100 between two palette colors under one vision."""

    first: str
    second: str
    delta_e: float
    adjacent: bool


@dataclass(frozen=True)
class VisionResult:
    """All pair distances of a palette under one vision, ascending by distance."""

    vision: Vision
    floor: float
    pairs: list[PairDistance]

    @property
    def below_floor(self) -> list[PairDistance]:
        return [pair for pair in self.pairs if pair.delta_e < self.floor]

    def minimum(self, *, adjacent_only: bool) -> PairDistance | None:
        candidates: list[PairDistance] = [p for p in self.pairs if p.adjacent or not adjacent_only]
        return candidates[0] if candidates else None


@dataclass(frozen=True)
class ContrastResult:
    """WCAG contrast ratio of one color against the palette's background."""

    color: str
    ratio: float
    passes: bool


@dataclass(frozen=True)
class PaletteAudit:
    """Every check of one palette on one background."""

    name: str
    background: str
    colors: list[str]
    contrast_min: float
    contrasts: list[ContrastResult]
    visions: list[VisionResult]

    @property
    def passed(self) -> bool:
        return all(c.passes for c in self.contrasts) and not any(v.below_floor for v in self.visions)


def normalize_hex(text: str) -> str:
    """Return `#RRGGBB` in upper case for `#RGB`, `#RRGGBB`, or either without `#`; raise ValueError otherwise."""
    match: re.Match[str] | None = HEX_PATTERN.fullmatch(text.strip())
    if match is None:
        raise ValueError(f"not a hex color: {text!r}")
    digits: str = match.group(1)
    if len(digits) == 3:
        digits = "".join(ch * 2 for ch in digits)
    return f"#{digits.upper()}"


def linear_rgb(hex_color: str) -> Rgb:
    """Decode a normalized `#RRGGBB` to linear-light sRGB with the IEC 61966-2-1 transfer function."""

    def decode(channel: int) -> float:
        value: float = channel / 255
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    return (decode(int(hex_color[1:3], 16)), decode(int(hex_color[3:5], 16)), decode(int(hex_color[5:7], 16)))


def _apply(matrix: Matrix, vector: Rgb) -> Rgb:
    return (
        sum(m * v for m, v in zip(matrix[0], vector, strict=True)),
        sum(m * v for m, v in zip(matrix[1], vector, strict=True)),
        sum(m * v for m, v in zip(matrix[2], vector, strict=True)),
    )


def simulate(rgb: Rgb, vision: Vision) -> Rgb:
    """Linear RGB as seen under `vision`; out-of-gamut results are clipped to 0..1."""
    if vision is Vision.NORMAL:
        return rgb
    simulated: Rgb = _apply(MACHADO_2009[vision], rgb)
    return (
        min(1.0, max(0.0, simulated[0])),
        min(1.0, max(0.0, simulated[1])),
        min(1.0, max(0.0, simulated[2])),
    )


def oklab(rgb: Rgb) -> Lab:
    """OKLab coordinates of a linear sRGB color."""
    lms: Rgb = _apply(OKLAB_TO_LMS, rgb)
    roots: Rgb = (math.cbrt(lms[0]), math.cbrt(lms[1]), math.cbrt(lms[2]))
    return _apply(OKLAB_FROM_LMS_ROOTS, roots)


def delta_e(first: Lab, second: Lab) -> float:
    """Euclidean OKLab distance times 100, so the CSS Color 4 JND of 0.02 reads as 2."""
    return 100 * math.dist(first, second)


def contrast_ratio(first: Rgb, second: Rgb) -> float:
    """WCAG 2.2 contrast ratio of two linear sRGB colors, 1 to 21."""
    lighter: float
    darker: float
    lighter, darker = sorted(
        (sum(w * c for w, c in zip(LUMINANCE_WEIGHTS, color, strict=True)) for color in (first, second)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def audit_palette(
    name: str, colors: Sequence[str], background: str, *, contrast_min: float, normal_floor: float, cvd_floor: float
) -> PaletteAudit:
    """Run every check on normalized `#RRGGBB` colors in palette order."""
    linear: dict[str, Rgb] = {color: linear_rgb(color) for color in [*colors, background]}
    contrasts: list[ContrastResult] = []
    for color in colors:
        ratio: float = contrast_ratio(linear[color], linear[background])
        contrasts.append(ContrastResult(color, round(ratio, 2), ratio >= contrast_min))
    neighbors: set[tuple[int, int]] = {(i, i + 1) for i in range(len(colors) - 1)}
    visions: list[VisionResult] = []
    for vision in Vision:
        lab: list[Lab] = [oklab(simulate(linear[color], vision)) for color in colors]
        pairs: list[PairDistance] = [
            PairDistance(colors[i], colors[j], round(delta_e(lab[i], lab[j]), 1), (i, j) in neighbors)
            for i, j in itertools.combinations(range(len(colors)), 2)
        ]
        pairs.sort(key=lambda pair: pair.delta_e)
        floor: float = normal_floor if vision is Vision.NORMAL else cvd_floor
        visions.append(VisionResult(vision, floor, pairs))
    return PaletteAudit(name, background, list(colors), contrast_min, contrasts, visions)


def token_palettes(
    tokens: dict[str, Any], themes: Sequence[Theme], sets: Sequence[PaletteSet]
) -> list[tuple[str, list[str], str]]:
    """Return (name, colors, background) per theme and set.

    `categorical` is the theme's list in order. `semantic` is the three hue
    strokes followed by the context gray `line`: the colors a chart with a
    focal series uses, where order carries no meaning and the all-pairs
    minimum is the one to read.
    """
    palettes: list[tuple[str, list[str], str]] = []
    for theme in themes:
        spec: dict[str, Any] = tokens["themes"][theme]
        background: str = normalize_hex(spec["bg"])
        for palette_set in sets:
            raw: list[str] = (
                spec["categorical"]
                if palette_set == "categorical"
                else [hue["stroke"] for hue in spec["hues"].values()] + [spec["line"]]
            )
            palettes.append((f"{theme} {palette_set}", [normalize_hex(c) for c in raw], background))
    return palettes


def format_text(audit: PaletteAudit, *, all_pairs: bool) -> str:
    """Human-readable report of one palette audit."""
    count: int = len(audit.colors)
    lines: list[str] = [f"{audit.name}: {count} color{'' if count == 1 else 's'} on {audit.background}"]
    lines.append(f"  contrast against background, marks need {audit.contrast_min:.1f}:1")
    for contrast in audit.contrasts:
        flag: str = "" if contrast.passes else f"  below {audit.contrast_min:.1f}"
        lines.append(f"    {contrast.color}  {contrast.ratio:5.2f}{flag}")
    floors: str = f"floor {audit.visions[0].floor:g} normal, {audit.visions[-1].floor:g} simulated"
    lines.append(f"  OKLab dE x100 ({floors})")
    lines.append(f"    {'vision':<8}{'adjacent min':<26}all-pairs min")
    for result in audit.visions:
        cells: list[str] = []
        for adjacent_only in (True, False):
            pair: PairDistance | None = result.minimum(adjacent_only=adjacent_only)
            low: str = "" if pair is None or pair.delta_e >= result.floor else " low"
            cells.append("-" if pair is None else f"{pair.delta_e:4.1f} {pair.first} {pair.second}{low}")
        lines.append(f"    {result.vision:<8}{cells[0]:<26}{cells[1]}")
    shown: list[tuple[Vision, PairDistance]] = [
        (result.vision, pair)
        for result in audit.visions
        for pair in (result.pairs if all_pairs else result.below_floor)
    ]
    if shown:
        lines.append("  all pairs" if all_pairs else "  pairs below floor")
        for vision, pair in shown:
            where: str = "adjacent" if pair.adjacent else ""
            lines.append(f"    {vision:<8}{pair.delta_e:4.1f}  {pair.first} {pair.second}  {where}".rstrip())
    failed_contrast: int = sum(not c.passes for c in audit.contrasts)
    failed_pairs: int = sum(len(v.below_floor) for v in audit.visions)
    verdict: str = "PASS" if audit.passed else f"FAIL: {failed_contrast} below contrast, {failed_pairs} below floor"
    lines.append(f"  result: {verdict}")
    return "\n".join(lines)


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Audit chart palettes: OKLab separation under normal, protan, and deutan vision, and mark contrast."
    )
    parser.add_argument("--tokens", type=Path, default=TOKENS_PATH, help="figure-tokens.json (default: the skill's)")
    parser.add_argument("--theme", choices=[*THEMES, "all"], default="all", help="token theme to audit")
    parser.add_argument(
        "--set", dest="palette_set", choices=[*PALETTE_SETS, "all"], default="all", help="token palette to audit"
    )
    parser.add_argument("--colors", nargs="+", metavar="HEX", help="audit these colors in order instead of the tokens")
    parser.add_argument("--bg", default="#FFFFFF", metavar="HEX", help="background for --colors (default #FFFFFF)")
    parser.add_argument("--floor", type=float, default=NORMAL_FLOOR, help=f"normal-vision dE floor ({NORMAL_FLOOR:g})")
    parser.add_argument("--cvd-floor", type=float, default=CVD_FLOOR, help=f"simulated-CVD dE floor ({CVD_FLOOR:g})")
    parser.add_argument(
        "--contrast", type=float, help="mark contrast minimum (default: the tokens' graphic_contrast_min)"
    )
    parser.add_argument("--all-pairs", action="store_true", help="list every pair, not only those below a floor")
    parser.add_argument("--json", action="store_true", help="write JSON instead of text")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args: argparse.Namespace = _parse_args(argv)
    try:
        tokens: dict[str, Any] = json.loads(args.tokens.read_text(encoding="utf-8"))
        contrast_min: float = args.contrast if args.contrast is not None else tokens["limits"]["graphic_contrast_min"]
        if args.colors:
            colors: list[str] = [normalize_hex(c) for text in args.colors for c in text.split(",") if c.strip()]
            palettes: list[tuple[str, list[str], str]] = [("custom", colors, normalize_hex(args.bg))]
        else:
            themes: list[Theme] = list(THEMES) if args.theme == "all" else [args.theme]
            sets: list[PaletteSet] = list(PALETTE_SETS) if args.palette_set == "all" else [args.palette_set]
            palettes = token_palettes(tokens, themes, sets)
    except (OSError, ValueError, KeyError) as error:  # unreadable tokens, a bad hex value, or a missing token
        print(f"palette_audit: {error}", file=sys.stderr)
        return 2
    audits: list[PaletteAudit] = [
        audit_palette(name, colors, bg, contrast_min=contrast_min, normal_floor=args.floor, cvd_floor=args.cvd_floor)
        for name, colors, bg in palettes
    ]
    if args.json:
        print(json.dumps([asdict(a) | {"passed": a.passed} for a in audits], indent=2))
    else:
        print("\n\n".join(format_text(a, all_pairs=args.all_pairs) for a in audits))
    return 0 if all(a.passed for a in audits) else 1


if __name__ == "__main__":
    sys.exit(main())
