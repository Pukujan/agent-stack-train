"""Tests for the Claude Code guard hooks (claude_guard.py, installed as acs_guard.py).

Each rule runs against a real git repository with a bare ``origin``, so the
guard sees the same branches, upstreams and commits it would in an adopter.
GitHub lookups are stubbed: an issue exists when its number is in ``ISSUES``.
"""

from __future__ import annotations

import json
import subprocess
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

from conftest import MODULE_ROOT

ISSUES = {"37"}
FORM = """body:
  - type: textarea
    id: summary
    attributes:
      label: Summary
    validations:
      required: false
  - type: dropdown
    id: issue_type
    attributes:
      label: Issue Type
    validations:
      required: true
  - type: dropdown
    id: lifecycle_status
    attributes:
      label: Lifecycle Status
    validations:
      required: true
"""


def _load(name: str):
    spec = spec_from_file_location(name, MODULE_ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def guard(monkeypatch):
    mod = _load("claude_guard")
    monkeypatch.setattr(mod, "issue_exists", lambda top, repo, number: number in ISSUES)
    monkeypatch.delenv("ACS_GUARD", raising=False)
    return mod


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def _repo(tmp_path: Path, checkout: Path, *, adopter: bool = True, pcm: bool = False) -> Path:
    bare = tmp_path / "origin.git"
    git("init", "--bare", "-b", "main", str(bare), cwd=tmp_path)
    checkout.mkdir(parents=True)
    git("init", "-b", "main", cwd=checkout)
    git("config", "user.email", "t@example.com", cwd=checkout)
    git("config", "user.name", "t", cwd=checkout)
    (checkout / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
    if adopter:
        (checkout / ".coord").mkdir()
        (checkout / ".coord" / "hotload.lock.json").write_text("{}\n", encoding="utf-8")
        (checkout / ".github" / "ISSUE_TEMPLATE").mkdir(parents=True)
        (checkout / ".github" / "ISSUE_TEMPLATE" / "observational-issue.yml").write_text(FORM, encoding="utf-8")
    if pcm:
        (checkout / "checkpoints").mkdir()
        (checkout / "checkpoints" / "CURRENT.md").write_text("# Current\n", encoding="utf-8")
    git("add", "-A", cwd=checkout)
    git("commit", "-qm", "init", cwd=checkout)
    git("remote", "add", "origin", str(bare), cwd=checkout)
    git("push", "-q", "origin", "main", cwd=checkout)
    git("remote", "set-head", "origin", "main", cwd=checkout)
    return checkout


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return _repo(tmp_path, tmp_path / "widget")


def bash(guard, repo: Path, command: str) -> str | None:
    return guard.pre_tool({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(repo)})


# ---------------------------------------------------------------- owning issue, default branch


def test_commit_on_the_default_branch_is_blocked(guard, repo):
    assert "default branch" in bash(guard, repo, "git commit -m x")


def test_work_on_a_branch_without_an_owning_issue_is_blocked(guard, repo):
    git("checkout", "-qb", "feat/no-issue", cwd=repo)
    for command in ("git commit -m x", "git push -u origin feat/no-issue", "cd . && git commit -am x"):
        assert "no owning issue" in bash(guard, repo, command), command


def test_a_branch_named_after_an_existing_issue_passes_and_is_cached(guard, repo):
    git("checkout", "-qb", "fix/37-enforce", cwd=repo)
    assert bash(guard, repo, "git commit -m x") is None
    assert git("config", "--get", "branch.fix/37-enforce.acs-issue", cwd=repo) == "#37"


def test_a_branch_named_after_a_missing_issue_is_blocked(guard, repo):
    git("checkout", "-qb", "fix/99-nope", cwd=repo)
    assert "no owning issue" in bash(guard, repo, "git commit -m x")


def test_link_records_the_owning_issue(guard, repo, monkeypatch):
    git("checkout", "-qb", "feat/linked", cwd=repo)
    monkeypatch.chdir(repo)
    assert guard.main(["link", "99"]) == 1
    assert guard.main(["link", "37"]) == 0
    assert bash(guard, repo, "git commit -m x") is None


def test_pushes_to_the_default_branch_and_force_pushes_are_blocked(guard, repo):
    git("checkout", "-qb", "fix/37-enforce", cwd=repo)
    assert "default branch" in bash(guard, repo, "git push origin HEAD:main")
    assert "default branch" in bash(guard, repo, "git push origin fix/37-enforce:refs/heads/main")
    assert "force" in bash(guard, repo, "git push --force-with-lease origin fix/37-enforce")
    assert bash(guard, repo, "git push -u origin fix/37-enforce") is None


def test_a_plain_push_from_the_default_branch_is_blocked(guard, repo):
    assert "default branch" in bash(guard, repo, "git push")


# ---------------------------------------------------------------- worktrees


def test_worktrees_inside_the_checkout_are_blocked(guard, repo):
    for path in (".claude/worktrees/x", ".worktrees/x", "../widget-x"):
        assert "worktrees go only at" in bash(guard, repo, f"git worktree add -b t {path}"), path


def test_worktrees_in_the_pcm_project_folder_pass(guard, tmp_path):
    main = _repo(tmp_path, tmp_path / "widget" / "main")
    assert bash(guard, main, "git worktree add -b t ../worktrees/TASK-1") is None
    assert "worktrees go only at" in bash(guard, main, "git worktree add -b t ../other/TASK-1")


def test_worktree_tools_are_blocked(guard, repo):
    event = {"cwd": str(repo)}
    assert guard.pre_tool({**event, "tool_name": "EnterWorktree", "tool_input": {}})
    assert guard.pre_tool({**event, "tool_name": "Agent", "tool_input": {"isolation": "worktree"}})
    assert guard.pre_tool({**event, "tool_name": "Agent", "tool_input": {"prompt": "x"}}) is None


# ---------------------------------------------------------------- issue logs and pull requests


def test_issue_logs_must_have_the_forms_required_headings(guard, repo, tmp_path):
    prose = tmp_path / "prose.md"
    prose.write_text("Something broke.\n", encoding="utf-8")
    good = tmp_path / "good.md"
    good.write_text("### Summary\n\nx\n\n### Issue Type\n\nobservational\n\n### Lifecycle Status\n\nopen\n", encoding="utf-8")
    assert "Issue Type" in bash(guard, repo, f"gh issue create --title t --body-file {prose}")
    assert "--body-file" in bash(guard, repo, "gh issue create --title t")
    assert bash(guard, repo, f"gh issue create --title t --body-file {good}") is None


def test_pull_requests_must_name_their_owning_issue(guard, repo):
    git("checkout", "-qb", "fix/37-enforce", cwd=repo)
    assert "Refs #N" in bash(guard, repo, "gh pr create --fill")
    assert "Refs #N" in bash(guard, repo, "gh pr create --title t --body 'no issue here'")
    assert bash(guard, repo, "gh pr create --title t --body 'Refs #37'") is None


def test_edits_that_remove_the_guard_are_blocked(guard, repo):
    settings = str(repo / ".claude" / "settings.json")
    event = {"cwd": str(repo)}
    assert guard.pre_tool({**event, "tool_name": "Write", "tool_input": {"file_path": settings, "content": "{}"}})
    assert guard.pre_tool({**event, "tool_name": "Edit", "tool_input": {
        "file_path": settings, "old_string": "python3 acs_guard.py stop", "new_string": ""}})
    assert guard.pre_tool({**event, "tool_name": "Edit", "tool_input": {
        "file_path": str(repo / ".claude" / "hooks" / "acs_guard.py"), "old_string": "a", "new_string": "b"}})
    assert guard.pre_tool({**event, "tool_name": "Edit", "tool_input": {
        "file_path": str(repo / "README.md"), "old_string": "a", "new_string": "b"}}) is None


# ---------------------------------------------------------------- stop


def test_stop_blocks_unpushed_commits_then_lets_the_retry_through(guard, repo):
    git("checkout", "-qb", "fix/37-enforce", cwd=repo)
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    git("add", "a.txt", cwd=repo)
    git("commit", "-qm", "change", cwd=repo)
    assert "not on GitHub" in guard.stop({"cwd": str(repo)})
    assert guard.stop({"cwd": str(repo), "stop_hook_active": True}) is None
    git("push", "-qu", "origin", "fix/37-enforce", cwd=repo)
    assert guard.stop({"cwd": str(repo)}) is None


def test_stop_needs_a_pcm_checkpoint_after_the_last_change(guard, tmp_path):
    repo = _repo(tmp_path, tmp_path / "widget", pcm=True)
    git("checkout", "-qb", "fix/37-enforce", cwd=repo)
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    git("add", "a.txt", cwd=repo)
    git("commit", "-qm", "change", cwd=repo)
    git("push", "-qu", "origin", "fix/37-enforce", cwd=repo)
    assert "checkpoint" in guard.stop({"cwd": str(repo)})
    git("commit", "-q", "--allow-empty", "-m", "PCM checkpoint TASK-1: next", cwd=repo)
    git("push", "-q", cwd=repo)
    assert guard.stop({"cwd": str(repo)}) is None


# ---------------------------------------------------------------- session start


def test_session_start_hands_over_the_default_branchs_rules(guard, repo, tmp_path):
    other = tmp_path / "other"
    git("clone", "-q", str(tmp_path / "origin.git"), str(other), cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=other)
    git("config", "user.name", "t", cwd=other)
    (other / "AGENTS.md").write_text("# Rules\n\nNew rule.\n", encoding="utf-8")
    git("commit", "-qam", "new rule", cwd=other)
    git("push", "-q", "origin", "main", cwd=other)
    git("checkout", "-qb", "old-branch", cwd=repo)
    context = guard.session_start({"cwd": str(repo), "source": "startup"})
    assert "not `main`" in context
    assert "1 commit(s) behind" in context
    assert "New rule." in context
    assert "compacted" in guard.session_start({"cwd": str(repo), "source": "compact"})


def test_session_start_is_quiet_on_a_current_default_branch(guard, repo):
    assert guard.session_start({"cwd": str(repo), "source": "startup"}) is None


# ---------------------------------------------------------------- scope and switch


def test_the_guard_ignores_repositories_that_do_not_adopt_the_stack(guard, tmp_path):
    repo = _repo(tmp_path, tmp_path / "plain", adopter=False)
    assert bash(guard, repo, "git commit -m x") is None
    assert bash(guard, repo, "git push origin HEAD:main") is None
    assert guard.pre_tool({"cwd": str(repo), "tool_name": "EnterWorktree", "tool_input": {}}) is None


def test_main_exits_two_with_the_reason_and_honours_acs_guard_off(guard, repo, monkeypatch, capsys):
    import io

    event = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git commit -m x"}, "cwd": str(repo)})
    monkeypatch.setattr("sys.stdin", io.StringIO(event))
    assert guard.main(["pre-tool"]) == 2
    assert "[stack guard]" in capsys.readouterr().err
    monkeypatch.setenv("ACS_GUARD", "off")
    monkeypatch.setattr("sys.stdin", io.StringIO(event))
    assert guard.main(["pre-tool"]) == 0


# ---------------------------------------------------------------- install


def test_settings_merge_keeps_the_adopters_hooks_and_is_idempotent(tmp_path):
    bridge = _load("claude_bridge")
    own = {"permissions": {"allow": ["Bash(ls)"]}, "hooks": {"PreToolUse": [
        {"matcher": "Bash", "hooks": [{"type": "command", "command": "python3 mine.py"}]}]}}
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps(own), encoding="utf-8")
    data = bridge.plan_settings(tmp_path)
    (tmp_path / ".claude" / "settings.json").write_bytes(data)
    merged = json.loads(data)
    assert merged["permissions"] == own["permissions"]
    assert merged["hooks"]["PreToolUse"][0]["hooks"][0]["command"] == "python3 mine.py"
    assert set(merged["hooks"]) == {"SessionStart", "PreToolUse", "Stop"}
    assert bridge.plan_settings(tmp_path) is None


def test_check_guard_flags_missing_and_stale_copies(tmp_path):
    bridge = _load("claude_bridge")
    assert len(bridge.check_guard(tmp_path)) == 4
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    (tmp_path / bridge.GUARD_REL).write_bytes(bridge.plan_guard(tmp_path))
    (tmp_path / bridge.SETTINGS_REL).write_bytes(bridge.plan_settings(tmp_path))
    assert bridge.check_guard(tmp_path) == []
    (tmp_path / bridge.GUARD_REL).write_text("# edited\n", encoding="utf-8")
    assert "differs" in bridge.check_guard(tmp_path)[0]


def test_install_writes_the_guard(installer, make_stack, make_adopter, stub_externals, run_args):
    stub_externals()
    adopter = make_adopter()
    assert installer.run(run_args(make_stack(), adopter)) == 0
    bridge = installer.claude_bridge
    assert (adopter / bridge.GUARD_REL).is_file()
    assert bridge.check_guard(adopter) == []
