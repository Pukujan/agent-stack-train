#!/usr/bin/env python3.12
"""PCM-0046 v2 arm bundle generator (pre-registered; amendment 4).

Builds fully isolated per-arm roots under the given base (default
/tmp/pcm0046-arms-v2). Each root contains ONLY that arm's files; rubric and
expected verdicts never enter any arm root. Run from the repo root:

    python3.12 docs/plans/PCM-0046-arm-bundles.py [base-dir]
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
FX = REPO / "tests" / "fixtures" / "pcm0046_traversal"


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/pcm0046-arms-v2")
    guidance_c = (REPO / "docs" / "plans" / "PCM-0046-guidance-candidate.md").read_text()
    guidance_b = (REPO / "docs" / "plans" / "PCM-0046-guidance-baseline.md").read_text()
    projection = json.loads((FX / "t2_projection.json").read_text())
    issue = json.loads((FX / "t2_issue.json").read_text())
    stale_tree = json.loads((FX / "t4_snapshot_stale_doc.json").read_text())["files"]
    manifest: dict[str, list[str]] = {}
    for n in range(1, 6):
        t1 = base / f"T1-{n}"
        write(t1 / "TASK-PCM-SEED.md", (FX / "t1_task_before.md").read_text())
        write(t1 / "GUIDANCE.md", guidance_c)
        manifest[f"T1-{n}"] = sorted(p.relative_to(t1).as_posix() for p in t1.rglob("*") if p.is_file())

        t1b = base / f"T1b-{n}"
        write(t1b / "TASK-PCM-SEED.md", (FX / "t1_task_before.md").read_text())
        write(t1b / "GUIDANCE.md", guidance_b)
        manifest[f"T1b-{n}"] = sorted(p.relative_to(t1b).as_posix() for p in t1b.rglob("*") if p.is_file())

        t2 = base / f"T2-{n}"
        cur = (
            "# Current Repository Checkpoint\n\n"
            "## Current projection\n\n"
            f"Leaf #{issue['number']} owns this work. Status: open.\n"
            f"Next action: {projection['next_action']}\n"
        )
        write(t2 / "CURRENT.md", cur)
        write(t2 / "issue.json", json.dumps(issue, indent=1) + "\n")
        manifest[f"T2-{n}"] = sorted(p.relative_to(t2).as_posix() for p in t2.rglob("*") if p.is_file())

        t3 = base / f"T3-{n}"
        write(t3 / "GUIDANCE.md", guidance_c)
        manifest[f"T3-{n}"] = ["GUIDANCE.md"]
        t3b = base / f"T3b-{n}"
        write(t3b / "GUIDANCE.md", guidance_b)
        manifest[f"T3b-{n}"] = ["GUIDANCE.md"]

        t4 = base / f"T4-{n}"
        for rel, content in stale_tree.items():
            write(t4 / "tree" / rel, content)
        manifest[f"T4-{n}"] = sorted(
            p.relative_to(t4).as_posix() for p in (t4 / "tree").rglob("*") if p.is_file()
        )
    write(base / "manifest.json", json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    digest = hashlib.sha256((base / "manifest.json").read_bytes()).hexdigest()
    print(f"STAGED: {base} manifest-sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
