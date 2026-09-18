#!/usr/bin/env python3
"""Sync the shared editorial design system, and the render tooling eli5-figure borrows from technical-diagram, into standalone skill packages."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAPPINGS = {
    ROOT / "shared/editorial-style/tokens.json": [
        ROOT / "skills/technical-diagram/assets/editorial-tokens.json",
        ROOT / "skills/drawio-diagram/assets/editorial-tokens.json",
        ROOT / "skills/data-chart/assets/editorial-tokens.json",
        ROOT / "skills/eli5-figure/assets/editorial-tokens.json",
    ],
    ROOT / "shared/editorial-style/principles.md": [
        ROOT / "skills/technical-diagram/references/editorial-principles.md",
        ROOT / "skills/drawio-diagram/references/local/editorial-principles.md",
        ROOT / "skills/eli5-figure/references/editorial-principles.md",
    ],
    ROOT / "shared/editorial-style/adapters/d2-theme.d2": [
        ROOT / "skills/technical-diagram/assets/editorial-theme.d2",
    ],
    ROOT / "shared/editorial-style/adapters/drawio-style.md": [
        ROOT / "skills/drawio-diagram/references/local/editorial-default-style.md",
    ],
    ROOT / "shared/editorial-style/adapters/d2-eli5-theme.d2": [
        ROOT / "skills/eli5-figure/assets/eli5-theme.d2",
    ],
    # eli5-figure renders on technical-diagram's routes; vendor the wrapper, validator, and template so it installs standalone.
    ROOT / "skills/technical-diagram/scripts/render_d2.sh": [
        ROOT / "skills/eli5-figure/scripts/render_d2.sh",
    ],
    ROOT / "skills/technical-diagram/scripts/validate_svg.py": [
        ROOT / "skills/eli5-figure/scripts/validate_svg.py",
    ],
    ROOT / "skills/technical-diagram/assets/direct-svg-template.svg": [
        ROOT / "skills/eli5-figure/assets/direct-svg-template.svg",
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if any vendored skill copy differs from the shared source",
    )
    args = parser.parse_args()

    stale: list[Path] = []
    for source, targets in MAPPINGS.items():
        source_bytes = source.read_bytes()
        for target in targets:
            if args.check:
                if not target.exists() or target.read_bytes() != source_bytes:
                    stale.append(target)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(source, target)

    if stale:
        for path in stale:
            print(f"STALE: {path.relative_to(ROOT)}", file=sys.stderr)
        print("Run: python3 scripts/sync_editorial_style.py", file=sys.stderr)
        return 1

    verb = "verified" if args.check else "synced"
    print(f"{verb} {sum(len(v) for v in MAPPINGS.values())} editorial style copies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
