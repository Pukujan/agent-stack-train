"""Metamorphic tests for the GitHub cadence (#108).

A cadence verdict has no oracle to compare against, but it has relations that
must hold whatever the exact numbers are. Each test changes the input in a way
that must not change the verdict, or must change it in one known direction:

* MR1 harness: the same situation, sent in each harness's own hook shape,
  gets the same verdict from Claude Code, Codex, Cursor, Gemini, WorkBuddy and
  DeepSeek Harness.
* MR2 splitting: the same change split into any number of commits under the
  limit gets the same verdict, and once a split blocks, every finer one does.
* MR3 scaling: multiplying the limits and the work by the same factor keeps
  the verdict; so does moving the branch's age and the age limit together.
* MR4 checkpoints: adding checkpoint commits never moves a branch toward its
  limit.
* MR5 spelling: the same polling command written differently gets the same
  verdict, and a sleep's unit is the same as its value in seconds.
* MR6 adopter shape: a PCM adopter, a plain adopter, the stack repository
  itself and an adopter with a changed seat file get the same verdict.

GitHub is stubbed as in ``test_claude_guard.py``; the git repositories are real.
"""

from __future__ import annotations

import io
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from test_claude_guard import _repo as _plain_repo, git, guard, repo, retry_dir  # noqa: F401  (fixtures)

HARNESSES = ("claude", "codex", "cursor", "gemini", "workbuddy", "dsh")
BRANCH = "fix/37-enforce"


# ---------------------------------------------------------------- helpers


def _repo(root: Path, checkout: Path, **shape) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    return _plain_repo(root, checkout, **shape)


def limits(repo: Path, **values: int) -> None:
    (repo / ".coord").mkdir(exist_ok=True)
    (repo / ".coord" / "cadence.json").write_text(json.dumps(values), encoding="utf-8")


def commit(repo: Path, name: str, lines: int, subject: str = "change", hours_ago: float = 0) -> None:
    (repo / name).write_text("".join(f"{name} {i}\n" for i in range(lines)), encoding="utf-8")
    git("add", name, cwd=repo)
    when = (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%S+0000")
    env = {**os.environ, "GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when}
    import subprocess

    subprocess.run(["git", "commit", "-qm", subject], cwd=repo, check=True, env=env)


def branch_with(repo: Path, commits: int, lines: int, hours_ago: float = 0, pcm: bool = False) -> None:
    """A pushed task branch whose work is ``lines`` lines in ``commits`` commits, and no pull request."""
    git("checkout", "-qb", BRANCH, cwd=repo)
    per = [lines // commits + (1 if i < lines % commits else 0) for i in range(commits)]
    for i, n in enumerate(per):
        commit(repo, f"f{i}.txt", n, hours_ago=hours_ago)
    if pcm:
        git("commit", "-q", "--allow-empty", "-m", "PCM checkpoint TASK-1: next", cwd=repo)
    git("push", "-qu", "origin", BRANCH, cwd=repo)


def stop_blocks(guard, repo: Path) -> bool:  # noqa: F811
    guard.pulls[BRANCH] = []
    return guard.stop({"cwd": str(repo)}) is not None


def native(harness: str, hook: str, repo: Path, command: str | None = None) -> dict:
    """The hook input each harness sends, for one stop or one shell command."""
    session = str(uuid.uuid4())  # a fresh session, so no earlier block makes this a retry
    if hook == "pre-tool":
        if harness == "cursor":
            return {"command": command, "cwd": str(repo), "conversation_id": session, "workspace_roots": [str(repo)]}
        tool = {"gemini": "run_shell_command", "dsh": "bash"}.get(harness, "Bash")
        return {"tool_name": tool, "tool_input": {"command": command}, "cwd": str(repo), "session_id": session}
    if harness == "cursor":
        return {"status": "completed", "loop_count": 0, "conversation_id": session, "workspace_roots": [str(repo)]}
    return {"cwd": str(repo), "session_id": session, "stop_hook_active": False}


def verdict(guard, monkeypatch, capsys, harness: str, hook: str, event: dict) -> bool:  # noqa: F811
    """True when the harness was told to block, read from its own answer format."""
    capsys.readouterr()
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(event)))
    code = guard.main(["--harness", harness, hook])
    out = capsys.readouterr().out.strip()
    if code == 2:
        return True
    answer = json.loads(out) if out else {}
    return answer.get("decision") in ("block", "deny") or answer.get("permission") == "deny" or "followup_message" in answer


# ---------------------------------------------------------------- MR1 harness


STOP_CASES = {
    "small pushed branch": (dict(commits=1, lines=5), False),
    "branch past the commit limit": (dict(commits=3, lines=5), True),
    "branch past the line limit": (dict(commits=1, lines=50), True),
}


@pytest.mark.parametrize("case", sorted(STOP_CASES))
def test_mr1_every_harness_gets_the_same_stop_verdict(guard, repo, monkeypatch, capsys, retry_dir, case):  # noqa: F811
    work, expected = STOP_CASES[case]
    limits(repo, pr_after_commits=3, pr_after_lines=40)
    branch_with(repo, **work)
    guard.pulls[BRANCH] = []
    monkeypatch.setenv("CURSOR_PROJECT_DIR", str(repo))
    seen = {h: verdict(guard, monkeypatch, capsys, h, "stop", native(h, "stop", repo)) for h in HARNESSES}
    assert seen == {h: expected for h in HARNESSES}


POLLS = {
    "until loop, 15 seconds": ('until [ "$(gh pr view 7 --json state -q .state)" = MERGED ]; do sleep 15; done', True),
    "until loop, 60 seconds": ('until [ "$(gh pr view 7 --json state -q .state)" = MERGED ]; do sleep 60; done', False),
    "gh run watch default": ("gh run watch 123", True),
    "gh run watch slow": ("gh run watch 123 --interval 90", False),
    "a single read": ("gh pr view 7", False),
    "a batch read over repositories": ("for r in a/b c/d; do gh pr list -R $r; done", False),
}


@pytest.mark.parametrize("case", sorted(POLLS))
def test_mr1_every_harness_gets_the_same_polling_verdict(guard, repo, monkeypatch, capsys, case):  # noqa: F811
    command, expected = POLLS[case]
    seen = {h: verdict(guard, monkeypatch, capsys, h, "pre-tool", native(h, "pre-tool", repo, command)) for h in HARNESSES}
    assert seen == {h: expected for h in HARNESSES}


# ---------------------------------------------------------------- MR2 splitting


def test_mr2_splitting_the_same_change_keeps_the_verdict_until_the_limit(guard, tmp_path):  # noqa: F811
    blocked = []
    for n in range(1, 7):
        repo = _repo(tmp_path / str(n), tmp_path / str(n) / "widget")
        limits(repo, pr_after_commits=4, pr_after_lines=10_000)
        branch_with(repo, commits=n, lines=24)
        blocked.append(stop_blocks(guard, repo))
    assert blocked == [False, False, False, True, True, True]  # same change; only the split crosses the limit
    assert all(b or not a for a, b in zip(blocked, blocked[1:]))  # once it blocks, a finer split blocks too


# ---------------------------------------------------------------- MR3 scaling


@pytest.mark.parametrize("commits,lines", [(1, 10), (2, 30), (3, 10), (1, 45), (2, 20)])
def test_mr3_scaling_limits_and_work_together_keeps_the_verdict(guard, tmp_path, commits, lines):  # noqa: F811
    seen = []
    for k in (1, 2, 3):
        root = tmp_path / str(k)
        repo = _repo(root, root / "widget")
        limits(repo, pr_after_commits=3 * k, pr_after_lines=40 * k)
        branch_with(repo, commits=commits * k, lines=lines * k)
        seen.append(stop_blocks(guard, repo))
    assert len(set(seen)) == 1, seen


@pytest.mark.parametrize("age,limit", [(10, 24), (30, 24), (30, 48), (60, 48)])
def test_mr3_moving_age_and_age_limit_together_keeps_the_verdict(guard, tmp_path, age, limit):  # noqa: F811
    seen = []
    for k in (1, 2):
        root = tmp_path / str(k)
        repo = _repo(root, root / "widget")
        limits(repo, pr_after_hours=limit * k)
        branch_with(repo, commits=1, lines=3, hours_ago=age * k)
        seen.append(stop_blocks(guard, repo))
    assert seen == [age >= limit] * 2


# ---------------------------------------------------------------- MR4 checkpoints


def test_mr4_checkpoint_commits_never_count_toward_the_limit(guard, tmp_path):  # noqa: F811
    for checkpoints in (0, 1, 5):
        root = tmp_path / str(checkpoints)
        repo = _repo(root, root / "widget", pcm=True)
        limits(repo, pr_after_commits=3)
        branch_with(repo, commits=2, lines=4)
        for i in range(checkpoints):
            git("commit", "-q", "--allow-empty", "-m", f"PCM checkpoint TASK-1: step {i}", cwd=repo)
        if not checkpoints:
            git("commit", "-q", "--allow-empty", "-m", "PCM checkpoint TASK-1: next", cwd=repo)
        git("push", "-q", cwd=repo)
        assert guard.branch_size(repo, "main")[0] == 2
        assert not stop_blocks(guard, repo)


# ---------------------------------------------------------------- MR5 spelling


SAME_POLL = [
    'until [ "$(gh run list --limit 1 --json status -q .[0].status)" = completed ]; do sleep 15; done',
    'until [ "$(gh run list --limit 1 --json status -q .[0].status)" = completed ]\ndo\n  sleep 15\ndone',
    'while [ "$(gh run list --limit 1 --json status -q .[0].status)" != completed ]; do sleep 15; done',
    'until   [ "$(/opt/homebrew/bin/gh run list --limit 1 --json status -q .[0].status)" = completed ];do sleep 15s;done',
    "for i in $(seq 40); do gh run list --limit 1; sleep 15; done",
    "watch -n 15 gh run list --limit 1",
    "gh run watch 9 -i 15",
    "gh pr checks 7 --watch --interval 15",
]


def test_mr5_spellings_of_one_poll_get_one_verdict(guard, repo):  # noqa: F811
    assert {guard.poll_interval(c) for c in SAME_POLL} == {15.0}
    assert all(guard.check_bash(c, repo) for c in SAME_POLL)
    slow = [c.replace("15s", "60s").replace("15", "60") for c in SAME_POLL]
    assert {guard.poll_interval(c) for c in slow} == {60.0}
    assert not any(guard.check_bash(c, repo) for c in slow)


def test_mr5_a_sleeps_unit_equals_its_seconds(guard):  # noqa: F811
    loop = 'until gh pr view 7 --json state -q .state | grep -q MERGED; do sleep {}; done'
    assert guard.poll_interval(loop.format("1m")) == guard.poll_interval(loop.format("60")) == 60
    assert guard.poll_interval(loop.format("0.5m")) == guard.poll_interval(loop.format("30s")) == 30


def test_mr5_the_poll_limit_moves_with_the_adopters_setting(guard, repo):  # noqa: F811
    command = "gh run watch 9 --interval 30"
    assert guard.check_bash(command, repo)
    limits(repo, min_poll_seconds=30)
    assert guard.check_bash(command, repo) is None
    limits(repo, min_poll_seconds=31)
    assert guard.check_bash(command, repo)


# ---------------------------------------------------------------- MR6 adopter shape


def shaped(tmp_path: Path, shape: str) -> Path:
    root = tmp_path / shape
    repo = _repo(root, root / "widget", pcm=shape == "pcm adopter")
    if shape == "stack repository":
        (repo / ".coord" / "hotload.lock.json").unlink()
        (repo / "stack-releases.json").write_text("{}\n", encoding="utf-8")
    if shape == "seat changed":
        (repo / ".coord" / "boss_claim.json").write_text("{}\n", encoding="utf-8")
    git("add", "-A", cwd=repo)
    git("commit", "-q", "--allow-empty", "-m", "shape", cwd=repo)
    git("push", "-q", "origin", "main", cwd=repo)
    if shape == "seat changed":
        (repo / ".coord" / "boss_claim.json").write_text('{"seat": "dsh@air"}\n', encoding="utf-8")
    return repo


@pytest.mark.parametrize("commits,lines", [(1, 5), (3, 5), (1, 50)])
def test_mr6_every_adopter_shape_gets_the_same_verdict(guard, tmp_path, commits, lines):  # noqa: F811
    seen = {}
    for shape in ("plain adopter", "pcm adopter", "stack repository", "seat changed"):
        repo = shaped(tmp_path, shape)
        limits(repo, pr_after_commits=3, pr_after_lines=40)
        branch_with(repo, commits=commits, lines=lines, pcm=shape == "pcm adopter")
        seen[shape] = stop_blocks(guard, repo)
    assert len(set(seen.values())) == 1, seen


# ---------------------------------------------------------------- the settings themselves


def test_bad_settings_fall_back_to_the_defaults(guard, repo):  # noqa: F811
    assert guard.cadence(repo) == guard.CADENCE_DEFAULTS
    (repo / ".coord" / "cadence.json").write_text("{not json", encoding="utf-8")
    assert guard.cadence(repo) == guard.CADENCE_DEFAULTS
    limits(repo, pr_after_commits=0, pr_after_lines=True, pr_after_hours="2", min_poll_seconds=-5)
    assert guard.cadence(repo) == guard.CADENCE_DEFAULTS
    limits(repo, pr_after_commits=5)
    assert guard.cadence(repo) == {**guard.CADENCE_DEFAULTS, "pr_after_commits": 5}


def test_session_start_names_pushed_branches_past_the_limit_with_no_pull_request(guard, repo, monkeypatch):  # noqa: F811
    limits(repo, pr_after_commits=1)
    branch_with(repo, commits=1, lines=2)
    git("switch", "-q", "main", cwd=repo)
    asked = []
    real = guard.run

    def fake(args, cwd, timeout=15):
        if args[:5] == ["gh", "pr", "list", "--state", "all"]:
            asked.append(args)
            return 0, json.dumps([])
        return real(args, cwd, timeout)

    monkeypatch.setattr(guard, "run", fake)
    context = guard.session_start({"cwd": str(repo), "source": "startup"})
    assert "past the cadence limit" in context and BRANCH in context and len(asked) == 1
    monkeypatch.setattr(guard, "run", lambda args, cwd, timeout=15: (0, json.dumps([{"headRefName": BRANCH}]))
                        if args[:5] == ["gh", "pr", "list", "--state", "all"] else real(args, cwd, timeout))
    assert "past the cadence limit" not in guard.session_start({"cwd": str(repo), "source": "startup"})


def test_session_start_leaves_branches_older_than_the_recent_window_alone(guard, repo, monkeypatch):  # noqa: F811
    limits(repo, pr_after_commits=1)
    branch_with(repo, commits=1, lines=2, hours_ago=24 * (guard.OVERDUE_RECENT_DAYS + 1))
    git("switch", "-q", "main", cwd=repo)
    real = guard.run
    asked = []
    monkeypatch.setattr(guard, "run", lambda args, cwd, timeout=15: (asked.append(args), (0, "[]"))[1]
                        if args[:5] == ["gh", "pr", "list", "--state", "all"] else real(args, cwd, timeout))
    assert guard.overdue_branches(repo, "main") == [] and asked == []  # not even a GitHub call
