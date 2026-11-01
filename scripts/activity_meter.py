#!/usr/bin/env python3
"""Count how much each adopter writes to GitHub, so a return to per-task churn shows up (#108).

For every repository in adopters.json (and this one) it reads, through one
GraphQL query per repository, the 100 most recently updated issues and pull
requests with their last 100 comments, and counts what was created in the
window: issues, pull requests and comments, per day on average, plus pull
requests and comments per issue. A repository writing more than
``--warn-per-day`` objects a day is marked.

It only reads. It files nothing and comments nowhere: the weekly workflow puts
the table in its job summary. Busier repositories than 100 updated issues or
pull requests in the window are undercounted, and the table says so.

Usage:
    python scripts/activity_meter.py                  # last 7 days, all adopters
    python scripts/activity_meter.py --days 1 --only pukujan-lab-2/nyc-map-agent
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SELF = "Pukujan/agent-stack-train"
PAGE = 100
QUERY = """query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    issues(first: %(page)d, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes { createdAt comments(last: %(page)d) { nodes { createdAt } } }
    }
    pullRequests(first: %(page)d, orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes { createdAt comments(last: %(page)d) { nodes { createdAt } } }
    }
  }
}""" % {"page": PAGE}


def repositories(only: str | None = None) -> list[str]:
    data = json.loads((ROOT / "adopters.json").read_text(encoding="utf-8"))
    names = [r if isinstance(r, str) else r.get("repository") or r.get("repo") for r in data["repositories"]]
    found = sorted({n for n in names if n} | {SELF})
    return [n for n in found if n == only] if only else found


def fetch(repository: str) -> dict | None:
    owner, name = repository.split("/", 1)
    proc = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}", "-f", f"owner={owner}", "-f", f"name={name}"],
        capture_output=True, text=True, check=False,
    )
    try:
        return json.loads(proc.stdout)["data"]["repository"] if proc.returncode == 0 else None
    except (ValueError, KeyError, TypeError):
        return None


def summarize(repo: dict, since: datetime) -> dict:
    """Counts of what the repository created since ``since``, from one query's answer."""
    def recent(stamp: str) -> bool:
        return datetime.fromisoformat(stamp.replace("Z", "+00:00")) >= since

    out = {"issues": 0, "pulls": 0, "comments": 0, "truncated": False}
    for kind, key in (("issues", "issues"), ("pullRequests", "pulls")):
        nodes = (repo.get(kind) or {}).get("nodes") or []
        out[key] = sum(1 for n in nodes if recent(n["createdAt"]))
        out["comments"] += sum(1 for n in nodes for c in (n.get("comments") or {}).get("nodes") or [] if recent(c["createdAt"]))
        # Every node updated in the window means older ones may be cut off by the page size.
        out["truncated"] |= len(nodes) == PAGE and all(recent(n["createdAt"]) for n in nodes[-1:])
    return out


def table(rows: list[tuple[str, dict | None]], days: int, warn: float) -> str:
    lines = [
        f"## GitHub activity, last {days} day(s)",
        "",
        "| Repository | Issues | Pull requests | Comments | Writes/day | PRs per issue | Comments per issue | |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for name, c in rows:
        if c is None:
            lines.append(f"| {name} | | | | | | | could not read |")
            continue
        total = c["issues"] + c["pulls"] + c["comments"]
        per_day = total / days
        ratio = lambda n: f"{n / c['issues']:.1f}" if c["issues"] else "-"  # noqa: E731
        mark = ("**over** " if per_day > warn else "") + ("(undercounted)" if c["truncated"] else "")
        lines.append(f"| {name} | {c['issues']} | {c['pulls']} | {c['comments']} | {per_day:.1f} | "
                     f"{ratio(c['pulls'])} | {ratio(c['comments'])} | {mark.strip()} |")
    lines += ["", f"Writes are issues + pull requests + comments created. **over**: more than {warn:g} a day (#108)."]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--only")
    parser.add_argument("--warn-per-day", type=float, default=20.0)
    args = parser.parse_args(argv)
    since = datetime.now(timezone.utc) - timedelta(days=args.days)
    rows = []
    for name in repositories(args.only):
        repo = fetch(name)
        rows.append((name, summarize(repo, since) if repo else None))
    sys.stdout.write(table(rows, args.days, args.warn_per_day))
    return 0


if __name__ == "__main__":
    sys.exit(main())
