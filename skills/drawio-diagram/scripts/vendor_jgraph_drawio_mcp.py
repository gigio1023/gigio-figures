#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


REPO = "jgraph/drawio-mcp"
USER_AGENT = "drawio-agent-skill/1.0"
ROOT = Path(__file__).resolve().parents[1]
FETCH_ROOT = ROOT / "references" / "fetched"
MANIFEST_PATH = FETCH_ROOT / "vendor-manifest.json"
FILES = {
    "shared/xml-reference.md": "xml-reference.md",
    "shared/style-reference.md": "style-reference.md",
    "shared/mermaid-reference.md": "mermaid-reference.md",
    "shared/mxfile.xsd": "mxfile.xsd",
    "plugins/claude-code/README.md": "claude-code-plugin-README.md",
    "plugins/claude-code/skills/drawio/SKILL.md": "claude-code-plugin-drawio-SKILL.md",
}


def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read()


def resolve_commit(repo: str, ref: str) -> str:
    url = f"https://api.github.com/repos/{repo}/commits/{ref}"
    try:
        payload = fetch_bytes(url)
        data = json.loads(payload.decode("utf-8"))
        sha = data.get("sha")
        if isinstance(sha, str) and sha:
            return sha
    except (HTTPError, OSError, json.JSONDecodeError):
        pass
    return ref


def vendor_file(repo: str, ref: str, upstream_path: str, local_name: str) -> dict[str, str]:
    raw_url = f"https://raw.githubusercontent.com/{repo}/{ref}/{upstream_path}"
    data = fetch_bytes(raw_url)
    output_path = FETCH_ROOT / local_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    return {
        "upstream_path": upstream_path,
        "raw_url": raw_url,
        "local_path": str(output_path.relative_to(ROOT)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch upstream drawio-mcp files into stable local files in this repo.",
    )
    parser.add_argument("--repo", default=REPO, help="GitHub repo in owner/name form")
    parser.add_argument("--ref", default="main", help="Git ref, branch, tag, or commit")
    args = parser.parse_args()

    resolved_commit = resolve_commit(args.repo, args.ref)
    records = [
        vendor_file(args.repo, args.ref, upstream_path, local_name)
        for upstream_path, local_name in FILES.items()
    ]
    manifest = {
        "repo": args.repo,
        "requested_ref": args.ref,
        "resolved_commit": resolved_commit,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": records,
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(MANIFEST_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
