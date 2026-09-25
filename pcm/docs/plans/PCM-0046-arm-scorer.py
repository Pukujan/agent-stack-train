#!/usr/bin/env python3.12
"""PCM-0046 arm capture + scoring harness (pre-registered; amendment 9).

Modes:
  capture <arms-root> <results-dir>   build T1/T1b whole-file diffs (n=10**9)
                                      and T4 tree snapshots from arm roots.
  score <results-dir>                 grade stored artifacts with the merged
                                      scorer; candidate + baseline tallies.

T2/T3/T3b answer/message files are written by the parent from arm results:
  results/T2-<n>.answer.txt, results/T3-<n>.message.txt, results/T3b-<n>.message.txt
  results/T1b-<n>.diff is produced by capture from the T1b roots.
Rescoring is a pure function over stored artifacts; it never reruns arms.

Run from the repo root (score imports tests/traversal_scorer.py).
"""
from __future__ import annotations

import difflib
import hashlib
import json
import pathlib
import shutil
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
FX = REPO / "tests" / "fixtures" / "pcm0046_traversal"


def whole_file_diff(before: str, after: str) -> str:
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile="a/tasks/TASK-PCM-SEED.md",
            tofile="b/tasks/TASK-PCM-SEED.md",
            n=10**9,
        )
    )


def tree_snapshot(tree: pathlib.Path) -> dict:
    files = {}
    for p in sorted(tree.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(tree))
            try:
                files[rel] = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                files[rel] = f"<binary {hashlib.sha256(p.read_bytes()).hexdigest()}>"
    return {"files": files}


def capture(arms: pathlib.Path, results: pathlib.Path) -> int:
    results.mkdir(parents=True, exist_ok=True)
    base = (FX / "t1_task_before.md").read_text()
    for prefix in ("T1", "T1b"):
        for n in range(1, 6):
            edited = arms / f"{prefix}-{n}" / "TASK-PCM-SEED.md"
            if not edited.is_file():
                print(f"MISSING: {edited}")
                continue
            (results / f"{prefix}-{n}.diff").write_text(whole_file_diff(base, edited.read_text()))
    for n in range(1, 6):
        src = arms / f"T4-{n}" / "tree"
        if not src.is_dir():
            print(f"MISSING: {src}")
            continue
        dst = results / f"T4-{n}.tree"
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)
    print(f"CAPTURED to {results}")
    return 0


def score_dir(results: pathlib.Path) -> int:
    from tests.traversal_scorer import score_t1, score_t2, score_t3, score_t4

    issue_state = json.loads((FX / "t2_issue.json").read_text())
    projection = json.loads((FX / "t2_projection.json").read_text())
    out: dict[str, dict] = {}
    for n in range(1, 6):
        for key, path in (
            (f"T1-{n}", results / f"T1-{n}.diff"),
            (f"T1b-{n}", results / f"T1b-{n}.diff"),
        ):
            if path.is_file():
                out[key] = score_t1(path.read_text())
        for key, path in (
            (f"T2-{n}", results / f"T2-{n}.answer.txt"),
            (f"T3-{n}", results / f"T3-{n}.message.txt"),
            (f"T3b-{n}", results / f"T3b-{n}.message.txt"),
        ):
            if path.is_file():
                if key.startswith("T2"):
                    out[key] = score_t2(path.read_text(), issue_state, projection)
                else:
                    out[key] = score_t3(path.read_text(), intent=False)
        tree = results / f"T4-{n}.tree"
        if tree.is_dir():
            out[f"T4-{n}"] = score_t4(tree_snapshot(tree))
    behaviors = ["T1", "T2", "T3", "T4", "T1b", "T3b"]
    tally = {}
    for b in behaviors:
        vs = [out[f"{b}-{n}"]["verdict"] for n in range(1, 6) if f"{b}-{n}" in out]
        if not vs:
            continue
        tally[b] = {
            "arms": len(vs),
            "pass": vs.count("pass"),
            "fail": vs.count("fail"),
            "inconclusive": vs.count("inconclusive"),
            "meets_4of5": vs.count("pass") >= 4,
        }
    print(json.dumps({"arms": {k: v["verdict"] for k, v in out.items()}, "tally": tally}, indent=1))
    (results / "scored.json").write_text(json.dumps({"arms": out, "tally": tally}, indent=1))
    return 0


def main() -> int:
    if len(sys.argv) >= 4 and sys.argv[1] == "capture":
        return capture(pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3]))
    if len(sys.argv) >= 3 and sys.argv[1] == "score":
        return score_dir(pathlib.Path(sys.argv[2]))
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
