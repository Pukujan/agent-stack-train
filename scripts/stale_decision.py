#!/usr/bin/env python3
"""Stale-decision baseline: does a fresh agent follow a closed issue over a stale status file? (#64)

This repeats PCM's T2 holdout (pcm/docs/plans/PCM-0046-arms-results/): an agent
gets a CURRENT.md that says issue #53 is open with a next action, plus the live
issue, which is closed, and is asked for the current state and next action. In
the original run all five agents reported that the issue was closed and still
recommended the stale action.

Two conditions are staged, five arms each by default:

* ``bare``: the original T2 bundle and prompt, unchanged;
* ``guided``: the same, plus PCM's current GitHub-progression guidance as
  GUIDANCE.md, to measure whether today's stack text changes the answer.

Each answer gets two scores. ``t2-lexical`` is PCM's own scorer
(pcm/tests/traversal_scorer.py), which matches words. ``follows-live`` is a
meaning check made by a separate judge agent that does not see the condition:
pass only if the answer does not recommend the stale action as current and says
the status file is contradicted. The report on the original run found the word
match misleading (its correction 3), so ``follows-live`` is the headline.

Running the arms needs an agent runner, so it happens outside this script:

    python scripts/stale_decision.py stage DIR [--arms 5]
    python scripts/stale_decision.py prompts DIR     # one prompt per arm; save each answer to DIR/<arm>/answer.txt
    python scripts/stale_decision.py judge-prompt DIR  # the blinded judge prompt; save its JSON to DIR/judge.json
    python scripts/stale_decision.py score DIR       # writes DIR/scored.json, prints the tallies
    python scripts/stale_decision.py send DIR        # one Phoenix trace per arm, with both scores

Scoring and sending are pure over the stored files, so they can be rerun
without rerunning any agent.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FX = ROOT / "pcm" / "tests" / "fixtures" / "pcm0046_traversal"
GUIDANCE_SOURCE = ROOT / "pcm" / "AGENTS.md"
CONDITIONS = ("bare", "guided")

sys.path.insert(0, str(ROOT / "pcm" / "tests"))
from traversal_scorer import score_t2  # noqa: E402

BARE_PROMPT = (
    "Here is a repository snapshot: {d}/CURRENT.md (the project's current-state document) and "
    "{d}/issue.json (the live state of the GitHub issue it references). What is the current state and "
    "the next action? Answer in 120 words or fewer, as plain text. Do not read or write anything outside {d}."
)
GUIDED_PROMPT = "Read {d}/GUIDANCE.md and follow it. " + BARE_PROMPT

JUDGE_PROMPT = """You are grading short answers from agents. Each agent saw two files:
- a status document saying issue #{number} is open, with the next action: "{stale}";
- the live issue, which is {state}.

For each answer below, decide three things:
1. recommends_stale: does it recommend doing "{stale}" (or the same thing in other words) as the current next step? Mentioning it only as outdated, already done or no longer valid is not recommending it.
2. states_issue_closed: does it say the issue is closed?
3. flags_contradiction: does it say the status document is wrong, out of date or contradicted by the issue, in any words?

Reply with JSON only, no prose: {{"<id>": {{"recommends_stale": bool, "states_issue_closed": bool, "flags_contradiction": bool, "reason": "<one sentence>"}}, ...}}

{answers}"""


def arms(base: Path) -> list[str]:
    return json.loads((base / "manifest.json").read_text())["arms"]


def guidance_text() -> str:
    text = GUIDANCE_SOURCE.read_text()
    match = re.search(r"<!-- pcm:github-progression:start -->.*?<!-- pcm:github-progression:end -->", text, re.S)
    if not match:
        raise SystemExit(f"no github-progression block in {GUIDANCE_SOURCE}")
    return match.group(0) + "\n"


def stage(base: Path, n: int) -> None:
    issue = json.loads((FX / "t2_issue.json").read_text())
    projection = json.loads((FX / "t2_projection.json").read_text())
    current = ("# Current Repository Checkpoint\n\n## Current projection\n\n"
               f"Leaf #{issue['number']} owns this work. Status: open.\n"
               f"Next action: {projection['next_action']}\n")
    names = []
    for condition in CONDITIONS:
        for i in range(1, n + 1):
            arm = f"{condition}-{i}"
            d = base / arm
            d.mkdir(parents=True, exist_ok=True)
            (d / "CURRENT.md").write_text(current)
            (d / "issue.json").write_text(json.dumps(issue, indent=1) + "\n")
            if condition == "guided":
                (d / "GUIDANCE.md").write_text(guidance_text())
            names.append(arm)
    (base / "manifest.json").write_text(json.dumps(
        {"arms": names, "issue": issue, "projection": projection}, indent=1) + "\n")
    print(f"staged {len(names)} arms under {base}")


def prompt_for(base: Path, arm: str) -> str:
    template = GUIDED_PROMPT if arm.startswith("guided") else BARE_PROMPT
    return template.format(d=base / arm)


def answer(base: Path, arm: str) -> str:
    path = base / arm / "answer.txt"
    return path.read_text().strip() if path.exists() else ""


def blind_ids(base: Path) -> dict[str, str]:
    """A stable shuffled mapping from judge id (A1, A2...) to arm, so the judge never sees the condition."""
    order = sorted(arms(base))
    random.Random(64).shuffle(order)
    return {f"A{i + 1}": arm for i, arm in enumerate(order)}


def redact(text: str) -> str:
    """Hide file paths, which name the arm and so its condition, from the judge."""
    return re.sub(r"(?:\S*/)?(?:bare|guided)-\d+(?:/\S*)?", "<snapshot file>", text)


def judge_prompt(base: Path) -> str:
    manifest = json.loads((base / "manifest.json").read_text())
    blocks = "\n\n".join(f"[{jid}]\n{redact(answer(base, arm))}" for jid, arm in blind_ids(base).items())
    return JUDGE_PROMPT.format(number=manifest["issue"]["number"], state=manifest["issue"]["state"],
                               stale=manifest["projection"]["next_action"], answers=blocks)


def follows_live(verdict: dict | None) -> str:
    if not verdict:
        return "inconclusive"
    return "pass" if not verdict["recommends_stale"] and verdict["flags_contradiction"] else "fail"


def score(base: Path) -> dict:
    manifest = json.loads((base / "manifest.json").read_text())
    judged = {}
    if (base / "judge.json").exists():
        raw = json.loads((base / "judge.json").read_text())
        judged = {arm: raw.get(jid) for jid, arm in blind_ids(base).items()}
    results = {}
    for arm in arms(base):
        text = answer(base, arm)
        lexical = score_t2(text, manifest["issue"], manifest["projection"]) if text else {"verdict": "inconclusive"}
        results[arm] = {"condition": arm.rsplit("-", 1)[0], "answer": text, "t2_lexical": lexical,
                        "judge": judged.get(arm), "follows_live": follows_live(judged.get(arm)) if text else "inconclusive"}
    return results


def tallies(results: dict) -> dict:
    out = {}
    for condition in CONDITIONS:
        rows = [r for r in results.values() if r["condition"] == condition]
        out[condition] = {
            metric: {v: sum(pick(r) == v for r in rows) for v in ("pass", "fail", "inconclusive")}
            for metric, pick in (("follows_live", lambda r: r["follows_live"]),
                                 ("t2_lexical", lambda r: r["t2_lexical"]["verdict"]))}
        out[condition]["recommends_stale"] = sum(bool(r["judge"] and r["judge"]["recommends_stale"]) for r in rows)
        out[condition]["arms"] = len(rows)
    return out


def send(base: Path, model: str) -> str:
    from otlp import Phoenix, Span

    phoenix = Phoenix.from_env(service="stale-decision-baseline")
    if phoenix is None:
        return "Skipped: OCTO_STACK_WS_KEY is not set, so nothing was sent to Phoenix."
    results = json.loads((base / "scored.json").read_text())
    counts = tallies(results)
    root = Span("stale-decision-baseline", {"issue": "#64", "model": model, "arms": len(results),
                                            "counts": json.dumps(counts, sort_keys=True)})
    children = []
    for arm, r in sorted(results.items()):
        span = root.child(f"arm {arm}", {
            "openinference.span.kind": "AGENT", "condition": r["condition"], "model": model,
            "input.value": prompt_for(base, arm), "output.value": r["answer"],
            "t2_lexical.verdict": r["t2_lexical"]["verdict"], "follows_live.verdict": r["follows_live"]})
        children.append((span.end(), r))
    root.end()
    phoenix.send([root] + [s for s, _ in children])
    for span, r in children:
        lexical = r["t2_lexical"]
        failed = [k for k, ok in lexical.get("checks", {}).items() if not ok]
        phoenix.annotate(span, "t2-lexical", label=lexical["verdict"], score=float(lexical["verdict"] == "pass"),
                         explanation="failed: " + ", ".join(failed) if failed else "all word checks passed")
        if r["judge"]:
            phoenix.annotate(span, "follows-live", label=r["follows_live"], score=float(r["follows_live"] == "pass"),
                             explanation=r["judge"].get("reason", ""), kind="LLM",
                             metadata={k: r["judge"][k] for k in ("recommends_stale", "states_issue_closed",
                                                                   "flags_contradiction")})
    return f"sent trace {root.trace_id.hex()} with {len(children)} arms: {phoenix.link()}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=["stage", "prompts", "judge-prompt", "score", "send"])
    parser.add_argument("dir", type=Path)
    parser.add_argument("--arms", type=int, default=5, help="arms per condition (stage)")
    parser.add_argument("--model", default="unknown", help="model the arms ran on (send)")
    args = parser.parse_args(argv)
    base = args.dir.resolve()

    if args.command == "stage":
        stage(base, args.arms)
    elif args.command == "prompts":
        for arm in arms(base):
            print(f"=== {arm}\n{prompt_for(base, arm)}")
    elif args.command == "judge-prompt":
        print(judge_prompt(base))
    elif args.command == "score":
        results = score(base)
        (base / "scored.json").write_text(json.dumps(results, indent=1, sort_keys=True) + "\n")
        print(json.dumps(tallies(results), indent=1))
    else:
        print(send(base, args.model))
    return 0


if __name__ == "__main__":
    sys.exit(main())
