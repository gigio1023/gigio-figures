#!/usr/bin/env python3
"""Validate a generated SVG figure.

Errors fail the check: broken structure, a missing or degenerate viewBox, duplicate ids, and labels that
would render below the minimum size once the figure is scaled to its delivery width. Warnings are
heuristics that deserve a look but do not fail on their own: labels that appear to crowd their box,
colors outside the editorial palette, and corner radii or stroke widths that drift from the tokens.
Pass --strict to turn warnings into failures.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_TARGET_WIDTH = 720.0
DEFAULT_MIN_FONT_PX = 12.0
MIN_LABEL_PADDING_PX = 8.0
SVG_DEFAULT_FONT_PX = 16.0
# Average glyph advance as a fraction of the font size. Monospace Latin runs at 0.6em and sans-serif
# text at roughly 0.52em; Hangul, CJK ideographs, kana, and fullwidth forms take a full em. An
# unknown family is measured as monospace so the estimate errs toward warning.
LATIN_EM_MONO = 0.6
LATIN_EM_SANS = 0.52
WIDE_EM = 1.0
MONO_FAMILY_HINTS = ("mono", "menlo", "courier", "consolas", "code", "monaco")
ALWAYS_ALLOWED_COLORS = {"none", "currentcolor", "transparent", "inherit", "white", "black", "#ffffff", "#000000"}
NON_CONTENT_CONTAINERS = {"defs", "mask", "marker", "clippath", "pattern", "symbol", "metadata", "title", "desc"}
SHAPE_TAGS = {"rect", "path", "line", "polyline", "polygon", "circle", "ellipse"}
HEX_RE = re.compile(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?\b")
RGB_RE = re.compile(r"rgba?\(\s*(\d+)\s*[, ]\s*(\d+)\s*[, ]\s*(\d+)\s*(?:[,/]\s*[\d.]+%?\s*)?\)")
NUMBER_RE = re.compile(r"^\s*(-?(?:\d+\.?\d*|\.\d+))\s*(px|pt|em|rem|%)?\s*$")
FLOAT_RE = re.compile(r"-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?")
TRANSFORM_RE = re.compile(r"(scale|matrix)\s*\(([^)]*)\)")
UNSUPPORTED_SELECTOR_RE = re.compile(r"[\[\]:+~]")


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def local_name(tag: str) -> str:
    """Tag name without namespace, lowercased so camel-case names such as clipPath compare reliably."""
    return tag.rsplit("}", 1)[-1].lower()


def parse_style_attr(style: str | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for chunk in (style or "").split(";"):
        if ":" in chunk:
            key, value = chunk.split(":", 1)
            result[key.strip().lower()] = re.sub(r"\s*!important\s*$", "", value.strip(), flags=re.I)
    return result


def strip_at_rules(css: str) -> str:
    """Drop @font-face, @media, @import, and other at-rules; conditional rules cannot be judged statically."""
    out: list[str] = []
    i = 0
    while i < len(css):
        if css[i] != "@":
            out.append(css[i])
            i += 1
            continue
        depth = 0
        j = i
        while j < len(css):
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
                if depth <= 0:
                    break
            elif css[j] == ";" and depth == 0:
                break
            j += 1
        i = j + 1
    return "".join(out)


def parse_css(css: str) -> list[tuple[list[str], dict[str, str]]]:
    """Return (selectors, declarations) pairs for the simple rules a figure uses."""
    css = css.replace("<![CDATA[", "").replace("]]>", "")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = strip_at_rules(css)
    rules: list[tuple[list[str], dict[str, str]]] = []
    for block in css.split("}"):
        if "{" not in block:
            continue
        selectors, declarations = block.split("{", 1)
        rules.append(([s.strip() for s in selectors.split(",") if s.strip()], parse_style_attr(declarations)))
    return rules


def length_px(value: str | None, *, relative_to: float | None = None) -> float | None:
    """Convert a length to px. Relative units resolve against `relative_to` or are rejected."""
    if value is None:
        return None
    match = NUMBER_RE.match(value)
    if not match:
        return None
    number = float(match.group(1))
    unit = match.group(2)
    if unit == "pt":
        return number * 4 / 3
    if unit in ("em", "rem", "%"):
        if relative_to is None:
            return None
        return number * relative_to / (100 if unit == "%" else 1)
    return number


def first_number(value: str | None) -> float | None:
    if value is None:
        return None
    token = value.replace(",", " ").split()
    return length_px(token[0]) if token else None


def is_wide_char(char: str) -> bool:
    code = ord(char)
    return (
        0x1100 <= code <= 0x11FF
        or 0x2E80 <= code <= 0x9FFF
        or 0xAC00 <= code <= 0xD7A3
        or 0xF900 <= code <= 0xFAFF
        or 0xFF00 <= code <= 0xFF60
        or 0xFFE0 <= code <= 0xFFE6
    )


def latin_em(font_family: str | None) -> float:
    family = (font_family or "").lower()
    if not family or any(hint in family for hint in MONO_FAMILY_HINTS):
        return LATIN_EM_MONO
    return LATIN_EM_SANS


def estimate_width(text: str, font_px: float, font_family: str | None = None) -> float:
    narrow = latin_em(font_family)
    return sum(WIDE_EM if is_wide_char(ch) else narrow for ch in text) * font_px


class StyleResolver:
    """Resolve presentation properties from attributes, inline styles, simple CSS rules, and inheritance."""

    def __init__(self, root: ET.Element) -> None:
        self.parent = {child: parent for parent in root.iter() for child in parent}
        self.rules: list[tuple[list[str], dict[str, str]]] = []
        for element in root.iter():
            if local_name(element.tag) == "style" and element.text:
                self.rules.extend(parse_css(element.text))

    def ancestors(self, element: ET.Element):
        node = self.parent.get(element)
        while node is not None:
            yield node
            node = self.parent.get(node)

    @staticmethod
    def classes(element: ET.Element) -> set[str]:
        return set((element.get("class") or "").split())

    def _simple_match(self, selector: str, element: ET.Element) -> bool:
        for token in re.findall(r"[#.]?[^#.]+", selector):
            if token == "*":
                continue
            if token.startswith("#"):
                if element.get("id") != token[1:]:
                    return False
            elif token.startswith("."):
                if token[1:] not in self.classes(element):
                    return False
            elif token != local_name(element.tag):
                return False
        return True

    @staticmethod
    def specificity(selector: str) -> int:
        types = len([t for t in re.findall(r"[#.]?[^#.\s>]+", selector) if t[0] not in "#." and t != "*"])
        return selector.count("#") * 100 + selector.count(".") * 10 + types

    def matches(self, selector: str, element: ET.Element) -> bool:
        # Attribute, pseudo-class, and sibling selectors are not evaluated; the child combinator is
        # treated as a descendant combinator, which errs toward applying the rule.
        if UNSUPPORTED_SELECTOR_RE.search(selector):
            return False
        parts = selector.replace(">", " ").split()
        if not parts or not self._simple_match(parts[-1], element):
            return False
        remaining = parts[:-1]
        for ancestor in self.ancestors(element):
            if not remaining:
                break
            if self._simple_match(remaining[-1], ancestor):
                remaining.pop()
        return not remaining

    def declared(self, element: ET.Element, prop: str) -> str | None:
        # Cascade order per SVG: inline style, then stylesheet rules, then presentation attributes,
        # which have zero specificity and lose to any matching rule.
        inline = parse_style_attr(element.get("style"))
        if prop in inline:
            return inline[prop]
        best: tuple[int, int, str] | None = None
        for order, (selectors, declarations) in enumerate(self.rules):
            if prop not in declarations:
                continue
            for selector in selectors:
                if self.matches(selector, element):
                    candidate = (self.specificity(selector), order, declarations[prop])
                    if best is None or candidate[:2] > best[:2]:
                        best = candidate
        if best:
            return best[2]
        return element.get(prop)

    def scale_factor(self, element: ET.Element) -> float:
        """Smallest axis scale applied by transforms and nested svg viewports above the element."""
        factor = 1.0
        for node in (element, *self.ancestors(element)):
            if local_name(node.tag) == "svg" and self.parent.get(node) is not None:
                nested_width = length_px(node.get("width"))
                nested_box = FLOAT_RE.findall(node.get("viewBox") or "")
                if nested_width and len(nested_box) == 4 and float(nested_box[2]) > 0:
                    factor *= nested_width / float(nested_box[2])
            for name, args in TRANSFORM_RE.findall(node.get("transform") or ""):
                values = [float(v) for v in FLOAT_RE.findall(args)]
                if name == "scale" and values:
                    sx, sy = values[0], values[1] if len(values) > 1 else values[0]
                    factor *= min(abs(sx), abs(sy))
                elif name == "matrix" and len(values) == 6:
                    a, b, c, d = values[:4]
                    factor *= min((a * a + b * b) ** 0.5, (c * c + d * d) ** 0.5)
        return factor

    def resolve(self, element: ET.Element, prop: str) -> str | None:
        value = self.declared(element, prop)
        if value is not None:
            return value
        for ancestor in self.ancestors(element):
            value = self.declared(ancestor, prop)
            if value is not None:
                return value
        return None

    def inside(self, element: ET.Element, container_names: set[str]) -> bool:
        return any(local_name(a.tag) in container_names for a in self.ancestors(element))


def load_palette(tokens_path: Path) -> tuple[set[str], set[float], set[float]]:
    data = json.loads(tokens_path.read_text(encoding="utf-8"))
    colors: set[str] = set()

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        elif isinstance(node, str):
            for match in HEX_RE.findall(node):
                colors.add(normalize_color(match))

    walk(data.get("colors", data))
    geometry = data.get("geometry", {})
    radii = {0.0}
    for key in ("node_corner_radius_px", "inner_corner_radius_px"):
        if isinstance(geometry.get(key), (int, float)):
            radii.add(float(geometry[key]))
    strokes = {0.0, 1.0}
    for key in ("stroke_width_px", "edge_width_px"):
        if isinstance(geometry.get(key), (int, float)):
            strokes.add(float(geometry[key]))
    return colors, radii, strokes


def normalize_color(value: str) -> str:
    value = value.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        value = "#" + "".join(ch * 2 for ch in value[1:])
    rgb = RGB_RE.fullmatch(value)
    if rgb:
        value = "#" + "".join(f"{min(int(channel), 255):02x}" for channel in rgb.groups())
    return value


def color_to_check(value: str | None) -> str | None:
    """Return the color a viewer will paint, or None when it cannot be checked statically."""
    if value is None:
        return None
    value = value.strip()
    if value.startswith("url("):
        return None
    var = re.fullmatch(r"var\(\s*--[\w-]+\s*(?:,\s*(.+))?\)", value)
    if var:
        return normalize_color(var.group(1)) if var.group(1) else None
    return normalize_color(value)


def check_structure(root: ET.Element, report: Report) -> tuple[float, float, float, float] | None:
    if local_name(root.tag) != "svg":
        report.errors.append("root element is not <svg>")
    raw_view_box = root.get("viewBox")
    view_box: tuple[float, float, float, float] | None = None
    if not raw_view_box:
        report.errors.append("SVG has no viewBox")
    else:
        try:
            values = [float(v) for v in raw_view_box.replace(",", " ").split()]
        except ValueError:
            values = []
        if len(values) != 4 or values[2] <= 0 or values[3] <= 0:
            report.errors.append("viewBox must contain four numbers with positive width and height")
        else:
            view_box = (values[0], values[1], values[2], values[3])
    seen: set[str] = set()
    duplicates: set[str] = set()
    for element in root.iter():
        element_id = element.get("id")
        if element_id:
            if element_id in seen:
                duplicates.add(element_id)
            seen.add(element_id)
    if duplicates:
        report.errors.append(f"duplicate ids: {', '.join(sorted(duplicates))}")
    return view_box


def text_elements(root: ET.Element, resolver: StyleResolver) -> list[ET.Element]:
    return [
        element
        for element in root.iter()
        if local_name(element.tag) == "text" and not resolver.inside(element, NON_CONTENT_CONTAINERS)
    ]


def label_lines(element: ET.Element) -> list[str]:
    spans = [child for child in element if local_name(child.tag) == "tspan"]
    positioned = [span for span in spans if span.get("x") is not None or span.get("dy") is not None]
    if positioned:
        return ["".join(span.itertext()).strip() for span in positioned if "".join(span.itertext()).strip()]
    text = "".join(element.itertext()).strip()
    return [text] if text else []


def font_size_of(element: ET.Element, resolver: StyleResolver) -> float:
    """Resolve the element's font size in px, following inheritance and relative units."""
    chain = [element, *resolver.ancestors(element)]
    size = SVG_DEFAULT_FONT_PX
    for node in reversed(chain):
        declared = resolver.declared(node, "font-size")
        if declared is None:
            continue
        resolved = length_px(declared, relative_to=size)
        if resolved is not None:
            size = resolved
    return size


def smallest_font_size(element: ET.Element, resolver: StyleResolver) -> float:
    """Smallest font size used by the label, counting tspans that set their own size."""
    sizes = [font_size_of(element, resolver)]
    for span in element.iter():
        if span is not element and local_name(span.tag) == "tspan" and "".join(span.itertext()).strip():
            sizes.append(font_size_of(span, resolver))
    return min(sizes)


def check_legibility(
    root: ET.Element,
    resolver: StyleResolver,
    view_box: tuple[float, float, float, float],
    target_width: float,
    min_font_px: float,
    report: Report,
) -> None:
    view_width = view_box[2]
    display_width = target_width
    if target_width > 0:
        # A root width smaller than the viewBox shrinks the figure in any host that honors intrinsic size.
        intrinsic = length_px(root.get("width"))
        if intrinsic is not None and 0 < intrinsic < min(view_width, target_width):
            display_width = intrinsic
            report.notes.append(f"root width attribute {intrinsic:g}px is narrower than the {view_width:g}px viewBox")
    scale = 1.0 if display_width <= 0 or view_width <= display_width else display_width / view_width
    offenders: list[tuple[float, float, str]] = []
    smallest: float | None = None
    for element in text_elements(root, resolver):
        lines = label_lines(element)
        if not lines:
            continue
        size = smallest_font_size(element, resolver) * resolver.scale_factor(element)
        effective = size * scale
        smallest = effective if smallest is None else min(smallest, effective)
        if effective < min_font_px:
            offenders.append((effective, size, lines[0]))
    if scale < 1.0:
        report.notes.append(
            f"canvas is {view_width:g}px wide and will be scaled to {display_width:g}px (x{scale:.2f})"
        )
    if smallest is not None:
        report.notes.append(f"smallest label renders at {smallest:.1f}px")
    if offenders:
        offenders.sort()
        shown = "; ".join(
            f"'{label[:32]}' {size:g}px renders at {effective:.1f}px" for effective, size, label in offenders[:3]
        )
        more = f" (+{len(offenders) - 3} more)" if len(offenders) > 3 else ""
        report.errors.append(
            f"labels below {min_font_px:g}px at {display_width:g}px delivery width: {shown}{more}; "
            "switch the layout engine or direction, shorten labels, or split the figure instead of shrinking type"
        )


def content_rects(root: ET.Element, resolver: StyleResolver, view_width: float) -> list[tuple[float, float, float, float]]:
    rects: list[tuple[float, float, float, float]] = []
    for element in root.iter():
        if local_name(element.tag) != "rect" or resolver.inside(element, NON_CONTENT_CONTAINERS):
            continue
        width = length_px(element.get("width"))
        height = length_px(element.get("height"))
        if width is None or height is None or width >= 0.95 * view_width:
            continue
        x = length_px(element.get("x")) or 0.0
        y = length_px(element.get("y")) or 0.0
        rects.append((x, y, width, height))
    return rects


def check_label_fit(root: ET.Element, resolver: StyleResolver, view_width: float, report: Report) -> None:
    rects = content_rects(root, resolver, view_width)
    crowded: list[str] = []
    for element in text_elements(root, resolver):
        lines = label_lines(element)
        x = first_number(element.get("x"))
        y = first_number(element.get("y"))
        if not lines or x is None or y is None:
            continue
        size = font_size_of(element, resolver)
        family = resolver.resolve(element, "font-family")
        width = max(estimate_width(line, size, family) for line in lines)
        anchor = (resolver.resolve(element, "text-anchor") or "start").strip().lower()
        if anchor == "middle":
            left, right = x - width / 2, x + width / 2
        elif anchor == "end":
            left, right = x - width, x
        else:
            left, right = x, x + width
        containers = [r for r in rects if r[0] <= x <= r[0] + r[2] and r[1] <= y <= r[1] + r[3]]
        if not containers:
            continue
        rx, _, rw, _ = min(containers, key=lambda r: r[2] * r[3])
        padding = min(left - rx, rx + rw - right)
        if padding < MIN_LABEL_PADDING_PX:
            crowded.append(f"'{lines[0][:32]}' (~{width:.0f}px in a {rw:g}px box, {padding:.0f}px to the edge)")
    if crowded:
        report.warnings.append(
            "labels may crowd their box (estimated widths): " + "; ".join(crowded[:4])
            + (f" (+{len(crowded) - 4} more)" if len(crowded) > 4 else "")
        )


def check_tokens(root: ET.Element, resolver: StyleResolver, tokens_path: Path, report: Report) -> None:
    palette, radii, strokes = load_palette(tokens_path)
    allowed = palette | ALWAYS_ALLOWED_COLORS
    off_palette: set[str] = set()
    odd_radii: set[float] = set()
    odd_strokes: set[float] = set()
    generated_by_d2 = root.get("data-d2-version") is not None
    for element in root.iter():
        name = local_name(element.tag)
        if name == "style":
            # D2 emits its whole theme class table; only the colors actually painted matter there.
            if generated_by_d2 or not element.text:
                continue
            for _, declarations in parse_css(element.text):
                for prop in ("fill", "stroke"):
                    color = color_to_check(declarations.get(prop))
                    if color and color not in allowed:
                        off_palette.add(color)
            continue
        inline = parse_style_attr(element.get("style"))
        if not resolver.inside(element, {"mask", "clippath"}):
            # Mask and clip contents are luminance or geometry, never painted color.
            for prop in ("fill", "stroke"):
                color = color_to_check(inline.get(prop, element.get(prop)))
                if color and color not in allowed:
                    off_palette.add(color)
        if name in SHAPE_TAGS and not resolver.inside(element, {"marker", "mask", "clippath", "defs"}):
            stroke_width = length_px(resolver.resolve(element, "stroke-width"))
            if stroke_width is not None and stroke_width not in strokes:
                odd_strokes.add(stroke_width)
        if name == "rect" and not resolver.inside(element, {"marker", "mask", "clippath", "defs"}):
            radius = length_px(resolver.declared(element, "rx"))
            if radius is not None and radius not in radii:
                odd_radii.add(radius)
    if off_palette:
        report.warnings.append("colors outside the editorial palette: " + ", ".join(sorted(off_palette)))
    if odd_radii:
        report.warnings.append(
            "corner radii outside the tokens: " + ", ".join(f"{r:g}" for r in sorted(odd_radii))
            + f" (expected {', '.join(f'{r:g}' for r in sorted(radii))})"
        )
    if odd_strokes:
        report.warnings.append(
            "stroke widths outside the tokens: " + ", ".join(f"{s:g}" for s in sorted(odd_strokes))
            + f" (expected {', '.join(f'{s:g}' for s in sorted(strokes))})"
        )


def validate_svg(
    path: Path,
    *,
    target_width: float = DEFAULT_TARGET_WIDTH,
    min_font_px: float = DEFAULT_MIN_FONT_PX,
    tokens_path: Path | None = None,
) -> Report:
    report = Report()
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        report.errors.append(f"cannot parse SVG: {exc}")
        return report
    view_box = check_structure(root, report)
    if view_box is None:
        return report
    resolver = StyleResolver(root)
    check_legibility(root, resolver, view_box, target_width, min_font_px, report)
    check_label_fit(root, resolver, view_box[2], report)
    if tokens_path is not None:
        try:
            check_tokens(root, resolver, tokens_path, report)
        except (OSError, ValueError) as exc:
            report.errors.append(f"cannot read tokens {tokens_path}: {exc}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("svg", type=Path)
    parser.add_argument(
        "--target-width",
        type=float,
        default=DEFAULT_TARGET_WIDTH,
        help="pixel width the figure will be displayed at; 0 disables the legibility gate (default 720)",
    )
    parser.add_argument(
        "--min-font-px",
        type=float,
        default=DEFAULT_MIN_FONT_PX,
        help="smallest acceptable rendered label size in px (default 12)",
    )
    parser.add_argument("--tokens", type=Path, default=None, help="editorial-tokens.json to check colors and geometry against")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args()

    report = validate_svg(args.svg, target_width=args.target_width, min_font_px=args.min_font_px, tokens_path=args.tokens)
    for warning in report.warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    for error in report.errors:
        print(f"ERROR: {error}", file=sys.stderr)
    failed = bool(report.errors) or (args.strict and bool(report.warnings))
    if failed:
        for note in report.notes:
            print(f"NOTE: {note}", file=sys.stderr)
        return 1
    summary = "; ".join(report.notes) if report.notes else "structure valid"
    print(f"OK: {args.svg} ({summary})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
