#!/usr/bin/env python3
"""Sync the shared figure style, and the render pipeline eli5-figure borrows from technical-figure, into standalone skill packages."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TF = ROOT / "skills/technical-figure"
ELI5 = ROOT / "skills/eli5-figure"
DRAWIO = ROOT / "skills/drawio-diagram"

# eli5-figure renders on technical-figure's pipeline; vendor it so eli5-figure installs standalone.
PIPELINE_FILES = [
    "scripts/render.mjs",
    "scripts/lint.mjs",
    "scripts/layout.mjs",
    "scripts/sheet.mjs",
    "scripts/measure.mjs",
    "scripts/setup.sh",
    "scripts/package.json",
    "scripts/package-lock.json",
    "references/svg-contract.md",
    "assets/templates/blank.svg",
]
PIPELINE_DIRS = ["scripts/lib"]


def mappings() -> dict[Path, list[Path]]:
    result: dict[Path, list[Path]] = {
        ROOT / "shared/figure-style/tokens.json": [
            TF / "assets/figure-tokens.json",
            DRAWIO / "assets/figure-tokens.json",
            ELI5 / "assets/figure-tokens.json",
        ],
        ROOT / "shared/figure-style/principles.md": [
            DRAWIO / "references/local/figure-principles.md",
            ELI5 / "references/figure-principles.md",
        ],
        ROOT / "shared/figure-style/adapters/drawio-style.md": [
            DRAWIO / "references/local/figure-style.md",
        ],
    }
    for rel in PIPELINE_FILES:
        result[TF / rel] = [ELI5 / rel]
    for rel in PIPELINE_DIRS:
        for source in sorted((TF / rel).rglob("*")):
            if source.is_file() and "__pycache__" not in source.parts:
                result[source] = [ELI5 / source.relative_to(TF)]
    return result


def stale_vendored_files(sources: dict[Path, list[Path]]) -> list[Path]:
    """Files inside vendored pipeline directories that no longer have a source."""
    expected = {target for targets in sources.values() for target in targets}
    stale: list[Path] = []
    for rel in PIPELINE_DIRS:
        for target in sorted((ELI5 / rel).rglob("*")):
            if target.is_file() and "__pycache__" not in target.parts and target not in expected:
                stale.append(target)
    return stale


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if any vendored skill copy differs from its source",
    )
    args = parser.parse_args()

    sources = mappings()
    stale: list[Path] = []
    for source, targets in sources.items():
        source_bytes = source.read_bytes()
        for target in targets:
            if args.check:
                if not target.exists() or target.read_bytes() != source_bytes:
                    stale.append(target)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(source, target)
            if source.stat().st_mode & 0o111:
                target.chmod(target.stat().st_mode | 0o111)

    orphans = stale_vendored_files(sources)
    if args.check:
        stale.extend(orphans)
    else:
        for orphan in orphans:
            orphan.unlink()

    if stale:
        for path in stale:
            print(f"STALE: {path.relative_to(ROOT)}", file=sys.stderr)
        print("Run: python3 scripts/sync_figure_style.py", file=sys.stderr)
        return 1

    verb = "verified" if args.check else "synced"
    print(f"{verb} {sum(len(v) for v in sources.values())} vendored figure-style files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
