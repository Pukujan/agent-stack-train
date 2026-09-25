#!/usr/bin/env python3.12
"""PCM-0046 arm scorer harness (pre-registered; pure functions over stored artifacts).

Artifacts live under /tmp/pcm0046-arms/results/:
  T1-<n>.diff        unified diff of seeded task file (before -> participant result)
  T2-<n>.answer.txt  participant answer text
  T3-<n>.message.txt participant commit message
  T4-<n>.tree/       participant's final tree directory
  T4-<n>.answer.txt  participant's yes/no sentence (recorded; T4 grades the tree)

Run: python3.12 docs/plans/PCM-0046-arm-scorer.py [results-dir]   (default /tmp/pcm0046-arms/results)
"""
import difflib
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]  # repo root; script lives in docs/plans/
sys.path.insert(0, str(REPO / "tests"))
from traversal_scorer import score_t1, score_t2, score_t3, score_t4  # noqa: E402

FX = REPO / "tests" / "fixtures" / "pcm0046_traversal"
RES = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/pcm0046-arms/results")


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


def main() -> int:
    issue_state = json.loads(FX.joinpath("t2_issue.json").read_text())
    projection = json.loads(FX.joinpath("t2_projection.json").read_text())
    out = {}
    for n in range(1, 6):
        out[f"T1-{n}"] = score_t1(RES.joinpath(f"T1-{n}.diff").read_text())
        out[f"T2-{n}"] = score_t2(RES.joinpath(f"T2-{n}.answer.txt").read_text(), issue_state, projection)
        out[f"T3-{n}"] = score_t3(RES.joinpath(f"T3-{n}.message.txt").read_text(), intent=False)
        out[f"T4-{n}"] = score_t4(tree_snapshot(RES / f"T4-{n}.tree"))
    tally = {}
    for b in ("T1", "T2", "T3", "T4"):
        vs = [out[f"{b}-{n}"]["verdict"] for n in range(1, 6)]
        tally[b] = {
            "pass": vs.count("pass"),
            "fail": vs.count("fail"),
            "inconclusive": vs.count("inconclusive"),
            "meets_4of5": vs.count("pass") >= 4,
        }
    print(json.dumps({"arms": {k: v["verdict"] for k, v in out.items()}, "tally": tally}, indent=1))
    payload = json.dumps({"arms": out, "tally": tally}, indent=1)
    RES.joinpath("scored.json").write_text(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
