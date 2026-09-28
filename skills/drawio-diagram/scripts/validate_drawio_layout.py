#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


# Corner radii of the figure style (tensor, chip, node, tall node, container) and the
# largest radius-to-height ratio it allows; see references/local/figure-style.md.
FIGURE_RADII_U = (2.0, 4.0, 6.0, 8.0, 12.0)
MAX_RADIUS_RATIO = 0.2


@dataclass(frozen=True)
class Box:
    cell_id: str
    parent_id: str | None
    x: float
    y: float
    width: float
    height: float
    style: dict[str, str]
    raw_style: str
    value: str
    is_text: bool
    is_framed: bool
    is_overlap_candidate: bool


@dataclass(frozen=True)
class Edge:
    cell_id: str
    value: str
    source_id: str | None
    target_id: str | None
    style: dict[str, str]
    waypoints: tuple[tuple[float, float], ...]
    source_point: tuple[float, float] | None
    target_point: tuple[float, float] | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate draw.io layout heuristics.",
    )
    parser.add_argument("path", help="Path to a .drawio file")
    parser.add_argument(
        "--min-padding",
        type=float,
        default=16.0,
        help="Minimum padding from a parent border to child boxes",
    )
    return parser.parse_args()


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def parse_style(style: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for token in style.split(";"):
        token = token.strip()
        if not token:
            continue
        if "=" in token:
            key, value = token.split("=", 1)
            result[key] = value
        else:
            result[token] = "1"
    return result


def parse_boxes(root: ET.Element) -> dict[str, Box]:
    boxes: dict[str, Box] = {}
    parent_map = {child: parent for parent in root.iter() for child in parent}
    for cell in root.iter():
        if local_name(cell.tag) != "mxCell":
            continue
        if cell.get("vertex") != "1":
            continue
        geometry = next(
            (child for child in cell if local_name(child.tag) == "mxGeometry"),
            None,
        )
        if geometry is None:
            continue
        x = float(geometry.get("x", "0"))
        y = float(geometry.get("y", "0"))
        width = float(geometry.get("width", "0"))
        height = float(geometry.get("height", "0"))
        style_text = cell.get("style", "")
        style = parse_style(style_text)
        wrapper = parent_map.get(cell)
        is_object_wrapper = wrapper is not None and local_name(wrapper.tag) in {
            "object",
            "UserObject",
        }
        # draw.io identifies a wrapped cell by its <object> id; an inner mxCell id is ignored.
        cell_id = (wrapper.get("id") if is_object_wrapper else None) or cell.get("id")
        if not cell_id:
            continue
        value = cell.get("value", "")
        if is_object_wrapper and not value:
            value = wrapper.get("label", wrapper.get("value", ""))
        is_text = "text" in style or style.get("shape") == "text"
        is_group = "group" in style
        is_background_container = (
            style.get("container") == "1" and style.get("pointerEvents") == "0"
        )
        is_framed = not is_text and not is_group and width > 0 and height > 0
        is_overlap_candidate = is_framed and not is_background_container
        boxes[cell_id] = Box(
            cell_id=cell_id,
            parent_id=cell.get("parent"),
            x=x,
            y=y,
            width=width,
            height=height,
            style=style,
            raw_style=style_text,
            value=value,
            is_text=is_text,
            is_framed=is_framed,
            is_overlap_candidate=is_overlap_candidate,
        )
    return boxes


def parse_edges(root: ET.Element) -> list[Edge]:
    edges: list[Edge] = []
    parent_map = {child: parent for parent in root.iter() for child in parent}
    for cell in root.iter():
        if local_name(cell.tag) != "mxCell":
            continue
        if cell.get("edge") != "1":
            continue
        wrapper = parent_map.get(cell)
        is_object_wrapper = wrapper is not None and local_name(wrapper.tag) in {
            "object",
            "UserObject",
        }
        cell_id = (wrapper.get("id", "") if is_object_wrapper else "") or cell.get("id", "")
        value = cell.get("value", "")
        if is_object_wrapper and not value:
            value = wrapper.get("label", wrapper.get("value", ""))
        geometry = next(
            (child for child in cell if local_name(child.tag) == "mxGeometry"),
            None,
        )
        waypoints: list[tuple[float, float]] = []
        source_point: tuple[float, float] | None = None
        target_point: tuple[float, float] | None = None
        if geometry is not None:
            for child in geometry:
                name = local_name(child.tag)
                if name == "Array" and child.get("as") == "points":
                    for point in child:
                        if local_name(point.tag) == "mxPoint":
                            waypoints.append(
                                (float(point.get("x", "0")), float(point.get("y", "0"))),
                            )
                elif name == "mxPoint" and child.get("as") == "sourcePoint":
                    source_point = (float(child.get("x", "0")), float(child.get("y", "0")))
                elif name == "mxPoint" and child.get("as") == "targetPoint":
                    target_point = (float(child.get("x", "0")), float(child.get("y", "0")))
        edges.append(
            Edge(
                cell_id=cell_id,
                value=value,
                source_id=cell.get("source"),
                target_id=cell.get("target"),
                style=parse_style(cell.get("style", "")),
                waypoints=tuple(waypoints),
                source_point=source_point,
                target_point=target_point,
            ),
        )
    return edges


def absolute_box(box: Box, boxes: dict[str, Box]) -> tuple[float, float, float, float]:
    if not box.parent_id or box.parent_id not in boxes:
        return (box.x, box.y, box.width, box.height)
    parent = boxes[box.parent_id]
    parent_x, parent_y, _, _ = absolute_box(parent, boxes)
    return (parent_x + box.x, parent_y + box.y, box.width, box.height)


def strip_label(value: str) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
    ax1, ay1, aw, ah = a
    bx1, by1, bw, bh = b
    ax2 = ax1 + aw
    ay2 = ay1 + ah
    bx2 = bx1 + bw
    by2 = by1 + bh
    return ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1


def anchor_point(
    box: Box,
    boxes: dict[str, Box],
    style: dict[str, str],
    prefix: str,
) -> tuple[tuple[float, float], bool]:
    """Absolute anchor for an edge terminal.

    Returns the fixed connection point when exitX/exitY (or entryX/entryY) are
    present, otherwise the shape center, plus whether the point was fixed.
    """
    x, y, width, height = absolute_box(box, boxes)
    rel_x = style.get(f"{prefix}X")
    rel_y = style.get(f"{prefix}Y")
    if rel_x is not None and rel_y is not None:
        try:
            px = x + float(rel_x) * width + float(style.get(f"{prefix}Dx", "0") or "0")
            py = y + float(rel_y) * height + float(style.get(f"{prefix}Dy", "0") or "0")
            return ((px, py), True)
        except ValueError:
            pass
    return ((x + width / 2, y + height / 2), False)


def segment_intersects_rect(
    p1: tuple[float, float],
    p2: tuple[float, float],
    rect: tuple[float, float, float, float],
    inset: float = 2.0,
) -> bool:
    """True when segment p1-p2 passes through rect (shrunk by inset)."""
    rx, ry, rw, rh = rect
    x_min, y_min = rx + inset, ry + inset
    x_max, y_max = rx + rw - inset, ry + rh - inset
    if x_min >= x_max or y_min >= y_max:
        return False
    (x1, y1), (x2, y2) = p1, p2
    # Liang-Barsky clipping.
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in (
        (-dx, x1 - x_min),
        (dx, x_max - x1),
        (-dy, y1 - y_min),
        (dy, y_max - y1),
    ):
        if p == 0:
            if q < 0:
                return False
            continue
        t = q / p
        if p < 0:
            if t > t1:
                return False
            t0 = max(t0, t)
        else:
            if t < t0:
                return False
            t1 = min(t1, t)
    return t0 < t1


def route_crosses_rect(
    p1: tuple[float, float],
    p2: tuple[float, float],
    rect: tuple[float, float, float, float],
    orthogonal: bool,
) -> bool:
    """Approximate whether the rendered route between p1 and p2 crosses rect.

    Straight edges use the literal segment. Orthogonal edges are approximated
    by the two candidate L-routes; only when both are blocked is the crossing
    considered likely, since the router can pick whichever corridor is clear.
    """
    if not orthogonal:
        return segment_intersects_rect(p1, p2, rect)
    (x1, y1), (x2, y2) = p1, p2
    corner_hv = (x2, y1)
    corner_vh = (x1, y2)
    hv_blocked = segment_intersects_rect(p1, corner_hv, rect) or segment_intersects_rect(
        corner_hv, p2, rect,
    )
    vh_blocked = segment_intersects_rect(p1, corner_vh, rect) or segment_intersects_rect(
        corner_vh, p2, rect,
    )
    return hv_blocked and vh_blocked


def facing_mismatch(
    style: dict[str, str],
    prefix: str,
    anchor: tuple[float, float],
    other: tuple[float, float],
    tolerance: float = 8.0,
) -> str | None:
    """Detect a fixed port on the side facing away from the other terminal."""
    rel_x = style.get(f"{prefix}X")
    rel_y = style.get(f"{prefix}Y")
    if rel_x is None or rel_y is None:
        return None
    try:
        fx, fy = float(rel_x), float(rel_y)
    except ValueError:
        return None
    dx = other[0] - anchor[0]
    dy = other[1] - anchor[1]
    if fx == 0 and dx > tolerance and abs(dx) >= abs(dy):
        return "left side but the other terminal is to the right"
    if fx == 1 and dx < -tolerance and abs(dx) >= abs(dy):
        return "right side but the other terminal is to the left"
    if fy == 0 and dy > tolerance and abs(dy) > abs(dx):
        return "top side but the other terminal is below"
    if fy == 1 and dy < -tolerance and abs(dy) > abs(dx):
        return "bottom side but the other terminal is above"
    return None


def ancestor_ids(cell_id: str | None, boxes: dict[str, Box]) -> set[str]:
    result: set[str] = set()
    current = cell_id
    while current and current in boxes and current not in result:
        result.add(current)
        current = boxes[current].parent_id
    return result


def route_adds_clear_axis_dogleg(
    start: tuple[float, float],
    end: tuple[float, float],
    waypoints: tuple[tuple[float, float], ...],
    obstacles: list[Box],
    boxes: dict[str, Box],
    skip_ids: set[str],
    tolerance: float = 1.0,
) -> bool:
    """True when a one/two-waypoint detour replaces a clear straight route."""
    if not 1 <= len(waypoints) <= 2:
        return False
    vertical = abs(start[0] - end[0]) <= tolerance
    horizontal = abs(start[1] - end[1]) <= tolerance
    if not vertical and not horizontal:
        return False
    if any(
        obstacle.cell_id not in skip_ids
        and segment_intersects_rect(
            start,
            end,
            absolute_box(obstacle, boxes),
            inset=-1.0,
        )
        for obstacle in obstacles
    ):
        return False
    if vertical:
        return any(abs(point[0] - start[0]) > tolerance for point in waypoints)
    return any(abs(point[1] - start[1]) > tolerance for point in waypoints)


def audit_edges(
    prefix: str,
    boxes: dict[str, Box],
    edges: list[Edge],
    errors: list[str],
    warnings: list[str],
) -> None:
    obstacles = [box for box in boxes.values() if box.is_overlap_candidate]
    pair_count: dict[frozenset[str], list[Edge]] = {}
    for edge in edges:
        if edge.source_id in boxes and edge.target_id in boxes:
            key = frozenset({edge.source_id, edge.target_id})
            if len(key) == 2:
                pair_count.setdefault(key, []).append(edge)

    for edge in edges:
        label = edge.cell_id or "<no id>"
        edge_label = strip_label(edge.value)
        label_background = edge.style.get("labelBackgroundColor", "").lower()
        if edge_label and label_background in {"", "none", "transparent"}:
            warnings.append(
                prefix
                + f"edge {label} label has no opaque background; set"
                " labelBackgroundColor to the canvas/panel fill so the line cannot"
                " show through the text",
            )
        if edge.source_id is None and edge.source_point is None:
            errors.append(
                prefix + f"edge {label} has no source and no explicit sourcePoint",
            )
        if edge.target_id is None and edge.target_point is None:
            errors.append(
                prefix + f"edge {label} has no target and no explicit targetPoint",
            )

        source_box = boxes.get(edge.source_id) if edge.source_id else None
        target_box = boxes.get(edge.target_id) if edge.target_id else None

        if edge.source_id is not None and source_box is None:
            errors.append(
                prefix + f"edge {label} references unknown source {edge.source_id}",
            )
        if edge.target_id is not None and target_box is None:
            errors.append(
                prefix + f"edge {label} references unknown target {edge.target_id}",
            )

        start: tuple[float, float] | None = None
        end: tuple[float, float] | None = None
        start_is_fixed = edge.source_point is not None
        end_is_fixed = edge.target_point is not None
        if source_box is not None:
            start, start_is_fixed = anchor_point(source_box, boxes, edge.style, "exit")
        elif edge.source_point is not None:
            start = edge.source_point
        if target_box is not None:
            end, end_is_fixed = anchor_point(target_box, boxes, edge.style, "entry")
        elif edge.target_point is not None:
            end = edge.target_point

        if start is None or end is None:
            continue

        mismatch = facing_mismatch(edge.style, "exit", start, end)
        if mismatch and not edge.waypoints:
            warnings.append(
                prefix
                + f"edge {label} exits the {mismatch}; the route will wrap around"
                " the source shape - move the port or add waypoints",
            )
        mismatch = facing_mismatch(edge.style, "entry", end, start)
        if mismatch and not edge.waypoints:
            warnings.append(
                prefix
                + f"edge {label} enters the {mismatch}; the route will wrap around"
                " the target shape - move the port or add waypoints",
            )

        skip_ids = ancestor_ids(edge.source_id, boxes) | ancestor_ids(edge.target_id, boxes)
        terminal_pair = frozenset({edge.source_id, edge.target_id})
        has_parallel_edge = len(terminal_pair) == 2 and len(pair_count.get(terminal_pair, [])) > 1
        if (
            start_is_fixed
            and end_is_fixed
            and not has_parallel_edge
            and route_adds_clear_axis_dogleg(
                start,
                end,
                edge.waypoints,
                obstacles,
                boxes,
                skip_ids,
            )
        ):
            warnings.append(
                prefix
                + f"edge {label} adds a dogleg although its terminals align and"
                " the straight corridor is clear; remove the waypoints",
            )
        polyline = [start, *edge.waypoints, end]
        is_orthogonal = "edgeStyle" in edge.style
        crossed: list[str] = []
        for obstacle in obstacles:
            if obstacle.cell_id in skip_ids:
                continue
            rect = absolute_box(obstacle, boxes)
            for seg_start, seg_end in zip(polyline, polyline[1:]):
                if route_crosses_rect(seg_start, seg_end, rect, is_orthogonal):
                    crossed.append(obstacle.cell_id)
                    break
        if crossed:
            detail = ", ".join(crossed[:4])
            warnings.append(
                prefix
                + f"edge {label} likely crosses component(s) {detail}; route around"
                " them with waypoints or different exit/entry sides",
            )

    for key, pair_edges in pair_count.items():
        if len(pair_edges) < 2:
            continue
        loose = [
            edge
            for edge in pair_edges
            if not edge.waypoints
            and "exitX" not in edge.style
            and "entryX" not in edge.style
        ]
        if len(loose) >= 2:
            ids = ", ".join(edge.cell_id or "<no id>" for edge in loose)
            names = " and ".join(sorted(key))
            warnings.append(
                prefix
                + f"edges {ids} between {names} are all floating; they will overlap"
                " - give each its own exitX/exitY and entryX/entryY",
            )


def corner_signature(box: Box) -> str | None:
    if not box.is_framed:
        return None
    if any(
        token in box.style
        for token in ("ellipse", "rhombus", "hexagon", "cylinder", "cloud")
    ):
        return None
    shape = box.style.get("shape", "")
    if shape and shape not in {"label", "rectangle", ""}:
        return None
    if box.style.get("rounded") != "1":
        return "square"
    arc_size = box.style.get("arcSize", "default")
    if box.style.get("absoluteArcSize") == "1":
        # Under absoluteArcSize, arcSize is the corner diameter. Radii on the figure
        # scale differ by kind and height on purpose, so they count as one recipe.
        try:
            radius = float(arc_size) / 2
        except ValueError:
            radius = None
        if radius in FIGURE_RADII_U and radius <= MAX_RADIUS_RATIO * box.height:
            return "rounded:figure-radius-scale"
        return f"rounded:absolute:{arc_size}"
    return f"rounded:default:{arc_size}"


def main() -> int:
    args = parse_args()
    tree = ET.parse(args.path)
    errors: list[str] = []
    warnings: list[str] = []
    root = tree.getroot()
    diagrams = [elem for elem in root if local_name(elem.tag) == "diagram"]

    for diagram in diagrams:
        page_name = diagram.get("name") or diagram.get("id") or "unnamed"
        prefix = f"[{page_name}] "
        graph_model = next(
            (elem for elem in diagram if local_name(elem.tag) == "mxGraphModel"),
            None,
        )
        if graph_model is None:
            errors.append(prefix + "missing mxGraphModel")
            continue
        page_root = next(
            (elem for elem in graph_model if local_name(elem.tag) == "root"),
            None,
        )
        if page_root is None:
            errors.append(prefix + "missing root")
            continue

        boxes = parse_boxes(page_root)
        audit_edges(prefix, boxes, parse_edges(page_root), errors, warnings)
        siblings: dict[str | None, list[Box]] = {}
        for box in boxes.values():
            siblings.setdefault(box.parent_id, []).append(box)

        for parent_id, child_boxes in siblings.items():
            framed = [box for box in child_boxes if box.is_framed]
            overlap_candidates = [box for box in child_boxes if box.is_overlap_candidate]
            for index, left in enumerate(overlap_candidates):
                left_abs = absolute_box(left, boxes)
                for right in overlap_candidates[index + 1 :]:
                    right_abs = absolute_box(right, boxes)
                    if overlap(left_abs, right_abs):
                        errors.append(
                            prefix + f"framed components overlap: {left.cell_id} vs {right.cell_id}",
                        )

            if parent_id in boxes:
                parent = boxes[parent_id]
                if parent.is_framed:
                    header_size = float(parent.style.get("startSize", "0") or "0")
                    for child in framed + [box for box in child_boxes if box.is_text]:
                        max_x = parent.width - args.min_padding
                        max_y = parent.height - args.min_padding
                        min_x = args.min_padding
                        min_y = args.min_padding + header_size
                        if child.x < min_x:
                            errors.append(
                                prefix
                                + f"{child.cell_id} is too close to parent {parent_id} left border",
                            )
                        if child.y < min_y:
                            errors.append(
                                prefix
                                + f"{child.cell_id} is too close to parent {parent_id} top border",
                            )
                        if child.x + child.width > max_x:
                            errors.append(
                                prefix
                                + f"{child.cell_id} exceeds parent {parent_id} right border",
                            )
                        if child.y + child.height > max_y:
                            errors.append(
                                prefix
                                + f"{child.cell_id} exceeds parent {parent_id} bottom border",
                            )

        corner_groups: dict[tuple[str | None, bool], set[str]] = {}
        for box in boxes.values():
            signature = corner_signature(box)
            if signature:
                key = (box.parent_id, box.style.get("container") == "1")
                corner_groups.setdefault(key, set()).add(signature)
        for (parent_id, is_container), signatures in corner_groups.items():
            if len(signatures) > 1:
                role = "containers" if is_container else "peer components"
                scope = parent_id or "page root"
                warnings.append(
                    prefix
                    + f"inconsistent rounded-rectangle settings among {role} under"
                    + f" {scope}: "
                    + ", ".join(sorted(signatures)),
                )

        for box in boxes.values():
            label = strip_label(box.value)
            if not label:
                continue
            if box.is_framed:
                spacing_values = [
                    float(box.style.get("spacingLeft", box.style.get("spacing", "0")) or "0"),
                    float(box.style.get("spacingRight", box.style.get("spacing", "0")) or "0"),
                    float(box.style.get("spacingTop", box.style.get("spacing", "0")) or "0"),
                    float(box.style.get("spacingBottom", box.style.get("spacing", "0")) or "0"),
                ]
                if any(value < 8 for value in spacing_values) and len(label) >= 16:
                    warnings.append(
                        prefix
                        + f"{box.cell_id} label may hug its border; increase spacing or shorten text",
                    )
            if len(label) > 48 and box.width < 260:
                warnings.append(
                    prefix
                    + f"{box.cell_id} label is long for its width; shorten text before widening the box",
                )
            if "rotation=90" in box.raw_style:
                warnings.append(prefix + f"{box.cell_id} uses vertical text rotation")

    for message in warnings:
        print(f"WARNING: {message}", file=sys.stderr)
    for message in errors:
        print(f"ERROR: {message}", file=sys.stderr)

    if errors:
        return 1

    print(f"OK: {Path(args.path).name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
