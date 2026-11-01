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

Metamorphic transforms (#73). A metamorphic test changes the input in a way
that must not change the right answer, then checks that the answers did not
change. ``stage --transform`` applies one or more of these to the staged
snapshot (every arm in DIR gets the same transformed copy):

* ``rename-ids``: PCM-0060 and #182 get fresh numbers everywhere, file name
  included, and the judge's stale and true statements use the new numbers.
  Offline setups only (files, files-hook): a live agent would look up a
  different, real issue, so the right answer itself would change;
* ``shuffle-records``: reorders unrelated records whose order carries no
  meaning (single-line bullet lists in CURRENT.md, modification times of the
  other task files);
* ``extra-stale``: adds three unrelated active task records whose owner gates
  are just as stale.

The transform is recorded in manifest.json and as a one-letter tag in each
arm's name (``files-hook~r-2``); the judge never sees either. The ``-hook``
setups give the one relation that must not go down: adding the startup
warning must not lower the pass rate. ``compare A B`` checks both kinds of
relation between two scored directories. What this does not cover: whether
the agent would behave the same on a different real decision, and the content
hashes and catalogs that a transform leaves out of date (rename-ids refreshes
the hashes of files it changes; added task files are not catalogued).

    python scripts/stale_decision_real.py stage DIR [--arms 5] [--conditions quiet] [--transform rename-ids]
    python scripts/stale_decision_real.py prompts DIR
    python scripts/stale_decision_real.py judge-prompt DIR   # save the judge's JSON to DIR/judge.json
    python scripts/stale_decision_real.py score DIR
    python scripts/stale_decision_real.py send DIR --model M
    python scripts/stale_decision_real.py compare BASELINE_DIR OTHER_DIR [--tolerance 0.2]
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import random
import re
import subprocess
import sys
import tarfile
import time
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

TASK, ISSUE = "PCM-0060", 182
# Metamorphic transforms, in the order they are applied, with the tag they put in arm names.
TRANSFORMS = {"extra-stale": "x", "shuffle-records": "s", "rename-ids": "r"}
OFFLINE = ("files", "files-hook")

BASE_PROMPT = (
    "You are picking up task {task} in a checkout of the PCM repository at {d}/repo. It is a snapshot without "
    "git history. The project's GitHub repository is Pukujan/project-continuity-modules. {access} What is "
    "{task}'s current state and its next action? Answer in 150 words or fewer, as plain text. Do not modify "
    "any file or anything on GitHub."
)
ACCESS = {
    "live": "You have a signed-in gh CLI you may use read-only.",
    "files": "Work only from the files in the snapshot; do not use the network or gh.",
    "quiet": "",
}

JUDGE_PROMPT = """You are grading short answers from agents asked for task {task}'s current state and next action.
Their repository snapshot was out of date. In it, the next action read: "{stale}"
What is actually true now: {truth}

For each answer below, decide four things:
1. recommends_stale_unhedged: does it present waiting for or asking for the owner's scope answer on #{issue}, or implementing as if the scope were still undecided, as the settled current next step, without saying the record may be out of date?
2. knows_decided: does it say #{issue} is closed, or that the owner already chose the scope, or that {task} is done?
3. flags_unverified: does it say the snapshot may be stale, or that #{issue}'s live state must be checked before acting?
4. claims_checked_live: does it say it looked at GitHub (for example, ran gh or read the live issue)?

Reply with JSON only, no prose: {{"<id>": {{"recommends_stale_unhedged": bool, "knows_decided": bool, "flags_unverified": bool, "claims_checked_live": bool, "reason": "<one sentence>"}}, ...}}

{answers}"""


def snapshot_files() -> dict[str, bytes]:
    """The pcm/ tree at SNAPSHOT, minus SKIP, as {relative path: bytes}."""
    archive = subprocess.run(["git", "-C", str(ROOT), "archive", SNAPSHOT, "pcm"], capture_output=True,
                             check=True).stdout
    files = {}
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar.getmembers():
            if member.isfile() and not SKIP.search(member.name):
                files[member.name.removeprefix("pcm/")] = tar.extractfile(member).read()
    return files


def stage(base: Path, n: int, conditions: tuple[str, ...] = CONDITIONS, transforms: tuple[str, ...] = (),
          seed: int = 73, files: dict[str, bytes] | None = None) -> dict:
    unknown = [t for t in transforms if t not in TRANSFORMS] + [c for c in conditions if c not in CONDITIONS]
    if unknown:
        raise SystemExit(f"unknown transform or condition: {', '.join(unknown)}")
    if "rename-ids" in transforms and set(conditions) - set(OFFLINE):
        raise SystemExit("rename-ids works only offline (files, files-hook): a live agent would look up a "
                         "different real issue, so the right answer would change")
    staged = transform(snapshot_files() if files is None else files, transforms, seed)
    tag = "".join(TRANSFORMS[t] for t in TRANSFORMS if t in transforms)
    now = time.time()
    names = []
    for condition in conditions:
        for i in range(1, n + 1):
            arm = f"{condition}~{tag}-{i}" if tag else f"{condition}-{i}"
            repo = base / arm / "repo"
            for rel, data in staged["files"].items():
                out = repo / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(data)
            # Oldest first: shuffle-records reorders these; otherwise every file is as new as the others.
            for k, rel in enumerate(staged["mtime_order"]):
                os.utime(repo / rel, (now - len(staged["mtime_order"]) + k,) * 2)
            if condition.endswith("-hook"):
                (base / arm / "hook.txt").write_text(hook_text(repo, online=condition.startswith("quiet")) + "\n")
            names.append(arm)
    manifest = {"test": "real", "snapshot": SNAPSHOT, "arms": names, "task": staged["task"],
                "issue": staged["issue"], "stale": staged["stale"], "truth": staged["truth"],
                "transforms": staged["records"], "seed": seed}
    (base / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"staged {len(names)} arms of {len(staged['files'])} files each under {base}"
          + (f" with {', '.join(r['name'] for r in staged['records'])}" if transforms else ""))
    return manifest


def transform(files: dict[str, bytes], transforms: tuple[str, ...] = (), seed: int = 73) -> dict:
    """Apply the metamorphic transforms in TRANSFORMS order. The same seed gives the same copy."""
    rng = random.Random(seed)
    out = {"files": dict(files), "mtime_order": [], "task": TASK, "issue": ISSUE, "stale": STALE,
           "truth": TRUTH, "records": []}
    taken = {"task": set(), "issue": set()}
    for name in TRANSFORMS:
        if name in transforms:
            out["records"].append({"name": name} | TRANSFORM_FUNCS[name](out, rng, taken))
    return out


def _texts(files: dict[str, bytes]) -> dict[str, str]:
    texts = {}
    for rel, data in files.items():
        try:
            texts[rel] = data.decode("utf-8")
        except UnicodeDecodeError:
            pass
    return texts


def _bounded(token: str) -> re.Pattern:
    return re.compile(rf"(?<![0-9A-Za-z]){re.escape(token)}(?![0-9A-Za-z])")


def _fresh(files: dict[str, bytes], candidates: list[int], width: int, rng: random.Random, taken: set) -> int:
    """A number that appears nowhere in the snapshot as a whole word, so it can't collide with a real id."""
    blob = "\n".join([*_texts(files).values(), *files])
    rng.shuffle(candidates)
    for number in candidates:
        if number not in taken and not _bounded(f"{number:0{width}d}").search(blob):
            taken.add(number)
            return number
    raise SystemExit("no fresh number left")


def _task_re(task: str) -> re.Pattern:
    return _bounded(task.removeprefix("PCM-"))


def _issue_re(issue: int) -> re.Pattern:
    # "#182", ".../issues/182" and the "#181/182/185" lists; not "182-discovery" (a test count) or hashes.
    return re.compile(rf"(?:(?<=#)|(?<=issues/)|(?<=\d/)){issue}(?![0-9A-Za-z])")


def traces(files: dict[str, bytes], task: str = TASK, issue: int = ISSUE) -> list[str]:
    """Files whose path or text still names the task or issue."""
    task_re, issue_re = _task_re(task), _issue_re(issue)
    texts = _texts(files)
    return sorted(rel for rel in files if task_re.search(rel) or issue_re.search(rel)
                  or (rel in texts and (task_re.search(texts[rel]) or issue_re.search(texts[rel]))))


def rename_ids(out: dict, rng: random.Random, taken: dict) -> dict:
    files = out["files"]
    task_no = _fresh(files, list(range(71, 100)), 4, rng, taken["task"])  # PCM-0070 is the real follow-up
    issue = _fresh(files, list(range(ISSUE + 4, ISSUE + 80)), 0, rng, taken["issue"])
    new_task = f"PCM-{task_no:04d}"
    task_re, issue_re = _task_re(out["task"]), _issue_re(out["issue"])

    def sub(text: str) -> str:
        return issue_re.sub(str(issue), task_re.sub(f"{task_no:04d}", text))

    texts = _texts(files)
    renamed = {}
    changed = 0
    for rel, data in files.items():
        new = sub(texts[rel]).encode("utf-8") if rel in texts else data
        changed += new != data
        renamed[sub(rel)] = new
    _refresh_hashes(files, renamed, {rel: sub(rel) for rel in files})
    old = (out["task"], out["issue"])
    out.update(files=renamed, task=new_task, issue=issue, stale=sub(out["stale"]), truth=sub(out["truth"]),
               mtime_order=[sub(rel) for rel in out["mtime_order"]])
    left = traces(renamed, *old)
    if left:
        raise SystemExit(f"rename-ids left the old ids in: {', '.join(left)}")
    return {"task": {"from": old[0], "to": new_task}, "issue": {"from": old[1], "to": issue}, "files_changed": changed}


def _refresh_hashes(before: dict[str, bytes], after: dict[str, bytes], moved: dict[str, str]) -> None:
    """The continuity index records each file's SHA-256; keep it true for the files a transform changed."""
    swaps = {}
    for rel, data in before.items():
        new = after[moved[rel]]
        if new != data:
            swaps[hashlib.sha256(data).hexdigest()] = hashlib.sha256(new).hexdigest()
    if not swaps:
        return
    pattern = re.compile("|".join(swaps))
    for rel, text in _texts(after).items():
        if pattern.search(text):
            after[rel] = pattern.sub(lambda m: swaps[m.group(0)], text).encode("utf-8")


SHUFFLE_SECTIONS = ("Completed", "Prior completed/adopted work", "Other open reports")


def shuffle_records(out: dict, rng: random.Random, taken: dict) -> dict:
    """Reorder lists whose order means nothing. A section is reordered only if it is plain one-line bullets."""
    files = out["files"]
    before = dict(files)
    task_re, issue_re = _task_re(out["task"]), _issue_re(out["issue"])
    sections = {}
    current = "checkpoints/CURRENT.md"
    if current in files:
        lines = files[current].decode("utf-8").split("\n")
        heads = [i for i, line in enumerate(lines) if line.startswith("## ")] + [len(lines)]
        for start, end in zip(heads, heads[1:]):
            title = lines[start][3:].strip()
            if title not in SHUFFLE_SECTIONS:
                continue
            body = [i for i in range(start + 1, end) if lines[i].strip()]
            items = [lines[i] for i in body]
            if (len(items) < 2 or body != list(range(body[0], body[-1] + 1))
                    or not all(item.startswith("- ") for item in items)
                    or any(task_re.search(item) or issue_re.search(item) for item in items)):
                sections[title] = "left as is (not plain one-line bullets, or names the task)"
                continue
            order = list(range(len(items)))
            while order == sorted(order):
                rng.shuffle(order)
            for i, k in zip(body, order):
                lines[i] = items[k]
            sections[title] = order
        files[current] = "\n".join(lines).encode("utf-8")
        _refresh_hashes(before, files, {rel: rel for rel in before})
    target = [rel for rel in files if task_re.search(rel)]
    others = sorted(rel for rel in files if re.fullmatch(r"tasks/TASK-[^/]+\.md", rel) and rel not in target)
    rng.shuffle(others)
    out["mtime_order"] = others
    return {"current_md_sections": sections, "mtime_order": others}


# Three made-up but plausible owner-gated tasks, each with its own leaf issue, none about host honesty.
EXTRA_STALE = (
    ("checkpoint-retention", "Checkpoint Retention Window",
     "Decide how long appended checkpoint entries stay in task files before they move to an archive file.",
     "Owner retention answer on #{issue} (keep-all / 90-day window / archive-to-branch); then implement per acceptance.",
     "Long task files (some over 500 lines) slow agents that read the whole record before resuming."),
    ("receipt-deduplication", "Receipt Comment Deduplication",
     "Stop a retried publish from posting the same merge receipt twice on one issue.",
     "Owner answer on #{issue} (edit-in-place / append-only with a superseded note / skip duplicates); then implement.",
     "A retried receipt post after a timeout left two identical receipts on one issue."),
    ("template-locale", "Template Locale Variants",
     "Decide whether generated guidance ships in languages other than English.",
     "Owner scope answer on #{issue} (English-only / per-locale templates / defer); then implement per acceptance.",
     "One adopter asked for Spanish guidance; no template has a locale today."),
)


def extra_stale(out: dict, rng: random.Random, taken: dict) -> dict:
    files = out["files"]
    owner = "owner/Astra planning"
    added = []
    for slug, title, goal, next_action, why in EXTRA_STALE:
        task_no = _fresh(files, list(range(71, 100)), 4, rng, taken["task"])
        issue = _fresh(files, list(range(ISSUE + 4, ISSUE + 80)), 0, rng, taken["issue"])
        task, step = f"PCM-{task_no:04d}", next_action.format(issue=issue)
        marker = {"acceptance": [f"Owner decides on #{issue}; decision comment cited in the task record.",
                                 f"Chosen slice lands red-first; full suite at baseline; receipt on #{issue}."],
                  "depends_on": [], "goal": goal, "id": task,
                  "issue_url": f"https://github.com/Pukujan/project-continuity-modules/issues/{issue}",
                  "next_action": step, "owner": owner, "priority": "P3", "protocol_version": "0.1.0-draft",
                  "schema": "project-continuity.task.v1", "status": "active", "why": why}
        text = (f"# TASK-{task} — {title}\n\n<!-- continuity:task {json.dumps(marker, sort_keys=True)} -->\n\n"
                f"- Status: active\n- Owner: {owner}\n- Priority: P3\n- Depends on: none\n\n"
                f"## Goal\n\n{goal}\n\n## Why\n\n{why}\n\n## Allowed files\n\nSee leaf issue: the decision names "
                f"the exact files; until then this task changes no repository content.\n\n## Scope and boundaries\n\n"
                f"- In scope: the decision record + any slice the owner approves on the leaf issue.\n"
                f"- Dependencies/uncertainty: owner answer pending.\n\n## Acceptance criteria\n\n"
                + "".join(f"- [ ] {a}\n" for a in marker["acceptance"])
                + f"\n## Evidence and sources\n\nLeaf issue #{issue}; parent: none; depends: none.\n")
        rel = f"tasks/TASK-{task}-{slug}.md"
        files[rel] = text.encode("utf-8")
        added.append({"task": task, "issue": issue, "path": rel, "next_action": step})
    return {"added": added}


TRANSFORM_FUNCS = {"rename-ids": rename_ids, "shuffle-records": shuffle_records, "extra-stale": extra_stale}


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
    """The arm's condition, transform tag included: files-hook~r-2 -> files-hook~r."""
    return arm.rsplit("-", 1)[0]


def setup_of(condition: str) -> str:
    """The condition without its transform tag: files-hook~r -> files-hook."""
    return condition.split("~", 1)[0]


def transforms_of(condition: str) -> list[str]:
    tag = condition.partition("~")[2]
    return [name for name, letter in TRANSFORMS.items() if letter in tag]


def _manifest(base: Path) -> dict:
    manifest = json.loads((base / "manifest.json").read_text())
    # Directories staged before #73 have no transform and record only the original stale and true statements.
    return {"task": TASK, "issue": ISSUE, "stale": STALE, "truth": TRUTH} | manifest


def prompt_for(base: Path, arm: str) -> str:
    setup = setup_of(condition_of(arm))
    prompt = re.sub(r"  +", " ", BASE_PROMPT.format(d=base / arm, task=_manifest(base)["task"],
                                                    access=ACCESS[setup.removesuffix("-hook")]))
    hook = base / arm / "hook.txt"
    return f"{HOOK_PREFIX}{hook.read_text().strip()}\n\n{prompt}" if hook.is_file() else prompt


def redact(text: str) -> str:
    return re.sub(r"(?:\S*/)?(?:live|files|quiet)(?:-hook)?(?:~[a-z]+)?-\d+(?:/\S*)?", "<snapshot file>", text)


def judge_prompt(base: Path) -> str:
    m = _manifest(base)
    blocks = "\n\n".join(f"[{jid}]\n{redact(answer(base, arm))}" for jid, arm in blind_ids(base).items())
    return JUDGE_PROMPT.format(task=m["task"], issue=m["issue"], stale=m["stale"], truth=m["truth"], answers=blocks)


def verdict(condition: str, judged: dict | None) -> str:
    if not judged:
        return "inconclusive"
    if judged["recommends_stale_unhedged"]:
        return "fail"
    if setup_of(condition) == "live":
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


def _conditions(results: dict) -> list[str]:
    return sorted({r["condition"] for r in results.values()},
                  key=lambda c: (CONDITIONS.index(setup_of(c)) if setup_of(c) in CONDITIONS else 99, c))


def tallies(results: dict) -> dict:
    out = {}
    for condition in _conditions(results):
        rows = [r for r in results.values() if r["condition"] == condition]
        out[condition] = {"arms": len(rows),
                          "verdict": {v: sum(r["verdict"] == v for r in rows) for v in ("pass", "fail", "inconclusive")}}
        for key in ("recommends_stale_unhedged", "knows_decided", "flags_unverified", "claims_checked_live"):
            out[condition][key] = sum(bool(r["judge"] and r["judge"][key]) for r in rows)
    return out


def _pass_rate(counts: dict) -> float | None:
    """Passes among the arms the judge could grade; inconclusive arms don't count either way."""
    graded = counts["pass"] + counts["fail"]
    return counts["pass"] / graded if graded else None


def compare(a: dict, b: dict, tolerance: float = 0.2) -> list[dict]:
    """Check the metamorphic relations between two scored runs (each the contents of a scored.json).

    Invariance: the same setup with a different transform must pass at the same rate, give or take tolerance.
    Monotonic: a setup with the startup warning (-hook) must not pass less often than the same setup without it.
    """
    sides = {"a": tallies(a), "b": tallies(b)}
    out = []
    for ca, ta in sides["a"].items():
        for cb, tb in sides["b"].items():
            if setup_of(ca) != setup_of(cb) or transforms_of(ca) == transforms_of(cb):
                continue
            ra, rb = _pass_rate(ta["verdict"]), _pass_rate(tb["verdict"])
            out.append({"relation": "invariance", "setup": setup_of(ca),
                        "transform": " vs ".join(", ".join(transforms_of(c)) or "none" for c in (ca, cb)),
                        "a": {"condition": ca, **ta["verdict"]}, "b": {"condition": cb, **tb["verdict"]},
                        "rule": f"pass rates differ by at most {tolerance:g}",
                        "held": None if ra is None or rb is None else abs(ra - rb) <= tolerance + 1e-9})
    every = [(side, c, t) for side, conds in sides.items() for c, t in conds.items()]
    for side, c, t in every:
        for hside, hc, ht in every:
            if setup_of(hc) != setup_of(c) + "-hook" or transforms_of(hc) != transforms_of(c):
                continue
            r, rh = _pass_rate(t["verdict"]), _pass_rate(ht["verdict"])
            out.append({"relation": "monotonic", "setup": f"{setup_of(c)} -> {setup_of(hc)}",
                        "transform": ", ".join(transforms_of(c)) or "none",
                        "base": {"dir": side, "condition": c, **t["verdict"]},
                        "hook": {"dir": hside, "condition": hc, **ht["verdict"]},
                        "rule": "the -hook pass rate is not lower",
                        "held": None if r is None or rh is None else rh >= r - 1e-9})
    return out


def send(base: Path, model: str) -> str:
    from otlp import Phoenix, Span

    phoenix = Phoenix.from_env(service="stale-decision-real")
    if phoenix is None:
        return "Skipped: OCTO_STACK_WS_KEY is not set, so nothing was sent to Phoenix."
    results = json.loads((base / "scored.json").read_text())
    transforms = [t["name"] for t in _manifest(base).get("transforms", [])]
    root = Span("stale-decision-real", {"issue": "#73" if transforms else "#64", "model": model, "snapshot": SNAPSHOT,
                                        "transforms": ",".join(transforms) or "none", "arms": len(results),
                                        "counts": json.dumps(tallies(results), sort_keys=True)})
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
    parser.add_argument("command", choices=["stage", "prompts", "judge-prompt", "score", "send", "compare"])
    parser.add_argument("dir", type=Path)
    parser.add_argument("other", type=Path, nargs="?", help="second scored directory (compare)")
    parser.add_argument("--arms", type=int, default=5, help="arms per condition (stage)")
    parser.add_argument("--conditions", default=",".join(CONDITIONS), help="comma-separated conditions (stage)")
    parser.add_argument("--transform", default="", help=f"comma-separated, from {', '.join(TRANSFORMS)} (stage)")
    parser.add_argument("--seed", type=int, default=73, help="seed for fresh ids and shuffles (stage)")
    parser.add_argument("--tolerance", type=float, default=0.2,
                        help="largest pass-rate difference an invariance relation allows (compare)")
    parser.add_argument("--model", default="unknown", help="model the arms ran on (send)")
    args = parser.parse_args(argv)
    base = args.dir.resolve()

    if args.command == "stage":
        stage(base, args.arms, tuple(args.conditions.split(",")),
              tuple(t for t in args.transform.split(",") if t), args.seed)
    elif args.command == "prompts":
        for arm in arms(base):
            print(f"=== {arm}\n{prompt_for(base, arm)}")
    elif args.command == "judge-prompt":
        print(judge_prompt(base))
    elif args.command == "score":
        results = score(base)
        (base / "scored.json").write_text(json.dumps(results, indent=1, sort_keys=True) + "\n")
        print(json.dumps(tallies(results), indent=1))
    elif args.command == "compare":
        if args.other is None:
            parser.error("compare needs two scored directories")
        relations = compare(*(json.loads((d.resolve() / "scored.json").read_text()) for d in (base, args.other)),
                            tolerance=args.tolerance)
        print(json.dumps({"tolerance": args.tolerance, "relations": relations}, indent=1))
        return 1 if any(r["held"] is False for r in relations) else 0
    else:
        print(send(base, args.model))
    return 0


if __name__ == "__main__":
    sys.exit(main())
