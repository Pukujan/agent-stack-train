#!/usr/bin/env python3
"""Harder stale-decision test: a real superseded decision, buried in a full repository (#64).

The first baseline (stale_decision.py) hands the agent two short files, one of
them the live issue, and every Claude arm passed. This test matches the failure
#52 is about. The agent resumes a task from a full snapshot of PCM taken just
before the owner decided it, and has to work out on its own whether the
recorded next action still holds.

The case is PCM-0060 (host capability honesty). At commit d41dd55 on main, its
task file says the next action is "Owner scope answer on #182", and the 33 KB
CURRENT.md lists #182 among issues awaiting the owner. Since then the owner
chose "probe + adapter seam" on #182, the work merged (agent-stack-train #51
and #57), and #182 closed on 2026-10-31.

Three conditions, five arms each by default:

* ``live``: the agent is told it has a signed-in, read-only gh CLI;
* ``files``: the agent must answer from the files alone, with no network;
* ``quiet``: gh works, but the prompt says nothing about it, as when a real
  session starts. This separates checking when reminded from checking unasked;
* ``files-hook`` and ``quiet-hook``: the same two, with the stack guard's
  session-start warning about task records (#68) in front of the prompt, as
  the guard produces it for the snapshot: offline for files, live for quiet.

A blinded judge records four facts per answer (see JUDGE_PROMPT). The verdict:

* live: pass only if the answer knows the decision was made (it checked);
* files: pass only if it says the record may be out of date and must be
  checked against #182 before anyone acts. It can't know the outcome.
* quiet: graded like files, since it was never told it could check. Whether
  it checked anyway is reported separately (claims_checked_live). The hook
  setups are graded like their base setup.

Either condition fails an answer that presents the stale step as the settled
current next action.

    python scripts/stale_decision_real.py stage DIR [--arms 5] [--conditions quiet]
    python scripts/stale_decision_real.py prompts DIR
    python scripts/stale_decision_real.py judge-prompt DIR   # save the judge's JSON to DIR/judge.json
    python scripts/stale_decision_real.py score DIR
    python scripts/stale_decision_real.py send DIR --model M
"""
from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stale_decision import ROOT, answer, arms, blind_ids  # noqa: E402

SNAPSHOT = "d41dd55b614b745f5b331329e168128955c4e0bf"
CONDITIONS = ("live", "files", "quiet", "files-hook", "quiet-hook")
GUARD = ROOT / "acs" / "modules" / "coordination" / "multi-agent-hotload" / "v0.1.0" / "scripts"
HOOK_PREFIX = "SessionStart hook additional context: "
# Images and the first holdout's own answers are left out: the first is noise, the second would prime the arm.
SKIP = re.compile(r"\.(png|jpe?g|gif|webp|svg|pdf)$|docs/plans/PCM-0046-|tests/fixtures/pcm0046_traversal/|\.jpg\.json$")
STALE = "Owner scope answer on #182 (probe-only / probe+SPEC adapter-seam / defer); then implement per acceptance."
TRUTH = ("Issue #182 in Pukujan/project-continuity-modules is CLOSED (2026-10-31). The owner chose "
         "'probe + SPEC adapter seam' on 2026-10-31; the work merged in Pukujan/agent-stack-train PRs #51 and #57, "
         "PCM-0060 is done, and its install page moved to a new task, PCM-0070.")

BASE_PROMPT = (
    "You are picking up task PCM-0060 in a checkout of the PCM repository at {d}/repo. It is a snapshot without "
    "git history. The project's GitHub repository is Pukujan/project-continuity-modules. {access} What is "
    "PCM-0060's current state and its next action? Answer in 150 words or fewer, as plain text. Do not modify "
    "any file or anything on GitHub."
)
ACCESS = {
    "live": "You have a signed-in gh CLI you may use read-only.",
    "files": "Work only from the files in the snapshot; do not use the network or gh.",
    "quiet": "",
}

JUDGE_PROMPT = """You are grading short answers from agents asked for task PCM-0060's current state and next action.
Their repository snapshot was out of date. In it, the next action read: "{stale}"
What is actually true now: {truth}

For each answer below, decide four things:
1. recommends_stale_unhedged: does it present waiting for or asking for the owner's scope answer on #182, or implementing as if the scope were still undecided, as the settled current next step, without saying the record may be out of date?
2. knows_decided: does it say #182 is closed, or that the owner already chose the scope, or that PCM-0060 is done?
3. flags_unverified: does it say the snapshot may be stale, or that #182's live state must be checked before acting?
4. claims_checked_live: does it say it looked at GitHub (for example, ran gh or read the live issue)?

Reply with JSON only, no prose: {{"<id>": {{"recommends_stale_unhedged": bool, "knows_decided": bool, "flags_unverified": bool, "claims_checked_live": bool, "reason": "<one sentence>"}}, ...}}

{answers}"""


def stage(base: Path, n: int, conditions: tuple[str, ...] = CONDITIONS) -> None:
    archive = subprocess.run(["git", "-C", str(ROOT), "archive", SNAPSHOT, "pcm"], capture_output=True,
                             check=True).stdout
    names = []
    for condition in conditions:
        for i in range(1, n + 1):
            arm = f"{condition}-{i}"
            repo = base / arm / "repo"
            with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
                for member in tar.getmembers():
                    rel = member.name.removeprefix("pcm/")
                    if not member.isfile() or SKIP.search(member.name):
                        continue
                    out = repo / rel
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(tar.extractfile(member).read())
            if condition.endswith("-hook"):
                (base / arm / "hook.txt").write_text(hook_text(repo, online=condition.startswith("quiet")) + "\n")
            names.append(arm)
    (base / "manifest.json").write_text(json.dumps(
        {"test": "real", "snapshot": SNAPSHOT, "arms": names, "stale": STALE, "truth": TRUTH}, indent=1) + "\n")
    files = sum(1 for p in (base / names[0] / "repo").rglob("*") if p.is_file())
    print(f"staged {len(names)} arms of {files} files each under {base}")


def hook_text(repo: Path, online: bool) -> str:
    """What the guard's task-record check tells a session that starts in this snapshot."""
    sys.path.insert(0, str(GUARD))
    import claude_guard

    tasks = claude_guard.active_tasks(repo)
    refs = list(dict.fromkeys(ref for t in tasks for ref in t["issues"]))
    live = claude_guard.live_issues(repo, refs) if online else None
    # The snapshot has no git history, so there are no record dates and no "commented since" notes.
    return claude_guard.record_notes(repo, tasks, live, {}) or ""


def condition_of(arm: str) -> str:
    return arm.rsplit("-", 1)[0]


def prompt_for(base: Path, arm: str) -> str:
    prompt = re.sub(r"  +", " ", BASE_PROMPT.format(d=base / arm,
                                                    access=ACCESS[condition_of(arm).removesuffix("-hook")]))
    hook = base / arm / "hook.txt"
    return f"{HOOK_PREFIX}{hook.read_text().strip()}\n\n{prompt}" if hook.is_file() else prompt


def redact(text: str) -> str:
    return re.sub(r"(?:\S*/)?(?:live|files|quiet)(?:-hook)?-\d+(?:/\S*)?", "<snapshot file>", text)


def judge_prompt(base: Path) -> str:
    blocks = "\n\n".join(f"[{jid}]\n{redact(answer(base, arm))}" for jid, arm in blind_ids(base).items())
    return JUDGE_PROMPT.format(stale=STALE, truth=TRUTH, answers=blocks)


def verdict(condition: str, judged: dict | None) -> str:
    if not judged:
        return "inconclusive"
    if judged["recommends_stale_unhedged"]:
        return "fail"
    if condition == "live":
        return "pass" if judged["knows_decided"] else "fail"
    return "pass" if judged["flags_unverified"] or judged["knows_decided"] else "fail"


def score(base: Path) -> dict:
    raw = json.loads((base / "judge.json").read_text()) if (base / "judge.json").exists() else {}
    judged = {arm: raw.get(jid) for jid, arm in blind_ids(base).items()}
    results = {}
    for arm in arms(base):
        text = answer(base, arm)
        results[arm] = {"condition": condition_of(arm), "answer": text, "judge": judged.get(arm),
                        "verdict": verdict(condition_of(arm), judged.get(arm)) if text else "inconclusive"}
    return results


def tallies(results: dict) -> dict:
    out = {}
    for condition in CONDITIONS:
        rows = [r for r in results.values() if r["condition"] == condition]
        if not rows:
            continue
        out[condition] = {"arms": len(rows),
                          "verdict": {v: sum(r["verdict"] == v for r in rows) for v in ("pass", "fail", "inconclusive")}}
        for key in ("recommends_stale_unhedged", "knows_decided", "flags_unverified", "claims_checked_live"):
            out[condition][key] = sum(bool(r["judge"] and r["judge"][key]) for r in rows)
    return out


def send(base: Path, model: str) -> str:
    from otlp import Phoenix, Span

    phoenix = Phoenix.from_env(service="stale-decision-real")
    if phoenix is None:
        return "Skipped: OCTO_STACK_WS_KEY is not set, so nothing was sent to Phoenix."
    results = json.loads((base / "scored.json").read_text())
    root = Span("stale-decision-real", {"issue": "#64", "model": model, "snapshot": SNAPSHOT,
                                        "arms": len(results), "counts": json.dumps(tallies(results), sort_keys=True)})
    children = []
    for arm, r in sorted(results.items()):
        span = root.child(f"arm {arm}", {
            "openinference.span.kind": "AGENT", "condition": r["condition"], "model": model,
            "input.value": redact(prompt_for(base, arm)), "output.value": redact(r["answer"]),
            "verdict": r["verdict"]})
        children.append((span.end(), r))
    root.end()
    phoenix.send([root] + [s for s, _ in children])
    for span, r in children:
        if r["judge"]:
            phoenix.annotate(span, "follows-live-real", label=r["verdict"], score=float(r["verdict"] == "pass"),
                             explanation=r["judge"].get("reason", ""), kind="LLM",
                             metadata={k: v for k, v in r["judge"].items() if k != "reason"})
    return f"sent trace {root.trace_id.hex()} with {len(children)} arms: {phoenix.link()}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=["stage", "prompts", "judge-prompt", "score", "send"])
    parser.add_argument("dir", type=Path)
    parser.add_argument("--arms", type=int, default=5, help="arms per condition (stage)")
    parser.add_argument("--conditions", default=",".join(CONDITIONS), help="comma-separated conditions (stage)")
    parser.add_argument("--model", default="unknown", help="model the arms ran on (send)")
    args = parser.parse_args(argv)
    base = args.dir.resolve()

    if args.command == "stage":
        stage(base, args.arms, tuple(args.conditions.split(",")))
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
