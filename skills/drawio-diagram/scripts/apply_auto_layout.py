#!/usr/bin/env python3
"""Apply a draw.io CLI layout and restore portable model attributes."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


MACOS_DRAWIO = Path("/Applications/draw.io.app/Contents/MacOS/draw.io")


def find_drawio() -> str | None:
    configured = os.environ.get("DRAWIO_BIN")
    if configured:
        return configured if os.access(configured, os.X_OK) else None
    discovered = shutil.which("drawio")
    if discovered:
        return discovered
    if MACOS_DRAWIO.is_file() and os.access(MACOS_DRAWIO, os.X_OK):
        return str(MACOS_DRAWIO)
    return None


def graph_models(root: ET.Element) -> list[ET.Element]:
    models = []
    if root.tag.rsplit("}", 1)[-1] == "mxGraphModel":
        models.append(root)
    models.extend(
        element
        for element in root.iter()
        if element is not root and element.tag.rsplit("}", 1)[-1] == "mxGraphModel"
    )
    return models


def read_backgrounds(path: Path) -> list[str | None]:
    """Return each page's model background in page order; the layout rewrite drops it."""
    return [model.get("background") for model in graph_models(ET.parse(path).getroot())]


def restore_adaptive_colors(path: Path, backgrounds: list[str | None] | None = None) -> int:
    """Set adaptiveColors on every model and put back any background the rewrite dropped."""
    tree = ET.parse(path)
    models = graph_models(tree.getroot())
    if not models:
        raise ValueError("draw.io output contains no mxGraphModel")
    for index, model in enumerate(models):
        model.set("adaptiveColors", "auto")
        background = backgrounds[index] if backgrounds and index < len(backgrounds) else None
        if background and not model.get("background"):
            model.set("background", background)
    tree.write(path, encoding="unicode")
    return len(models)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("layout", help="preset name or compact layout JSON array")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"input not found: {args.input}")
    if args.input.resolve() == args.output.resolve():
        parser.error("input and output must differ during layout iteration")
    if not args.output.parent.is_dir():
        parser.error(f"output directory not found: {args.output.parent}")

    try:
        backgrounds = read_backgrounds(args.input)
    except ET.ParseError as exc:
        parser.error(f"input is not uncompressed draw.io XML: {exc}")

    drawio = find_drawio()
    if not drawio:
        print(
            "draw.io CLI not found; install draw.io Desktop or set DRAWIO_BIN",
            file=sys.stderr,
        )
        return 127

    temporary = tempfile.NamedTemporaryFile(
        prefix=f".{args.output.stem}.",
        suffix=".drawio",
        dir=args.output.parent,
        delete=False,
    )
    temporary_path = Path(temporary.name)
    temporary.close()
    temporary_path.unlink()

    try:
        subprocess.run(
            [
                drawio,
                "-x",
                "--layout",
                args.layout,
                "-f",
                "xml",
                "-o",
                str(temporary_path),
                str(args.input),
            ],
            check=True,
        )
        count = restore_adaptive_colors(temporary_path, backgrounds)
        os.replace(temporary_path, args.output)
    except (OSError, ValueError, ET.ParseError, subprocess.CalledProcessError) as exc:
        temporary_path.unlink(missing_ok=True)
        print(f"layout failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"OK: applied {args.layout} and restored adaptiveColors and background"
        f" on {count} model(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
