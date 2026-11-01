"""Tests for the Claude Code guard hooks (claude_guard.py, installed as acs_guard.py).

Each rule runs against a real git repository with a bare ``origin``, so the
guard sees the same branches, upstreams and commits it would in an adopter.
GitHub lookups are stubbed: an issue exists when its number is in ``ISSUES``,
and a branch's open pull requests come from ``guard.pulls`` (default: one with
auto-merge armed; ``None`` means gh failed), and its merged ones from ``guard.merged``.
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
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    mod.pulls = {}
    mod.merged = {}
    mod.auto_merge = "true"
    real_run = mod.run

    def fake_run(args, cwd, timeout=15):
        if args[:3] == ["gh", "pr", "list"]:
            branch = args[args.index("--head") + 1]
            if args[args.index("--state") + 1] == "merged":
                return 0, json.dumps(mod.merged.get(branch, []))
            pulls = mod.pulls.get(branch, [{"number": 7, "isDraft": False, "autoMergeRequest": {"mergeMethod": "SQUASH"}}])
            return (1, "") if pulls is None else (0, json.dumps(pulls))
        if args[:3] == ["gh", "repo", "view"]:
            return (1, "") if mod.auto_merge is None else (0, mod.auto_merge + "\n")
        return real_run(args, cwd, timeout)

    monkeypatch.setattr(mod, "run", fake_run)
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
    for command in ("git commit -m x", "git push -u origin feat/no-issue", "cd . && git commit -am x", "cd .\ngit commit -am x"):
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


def test_github_side_changes_need_an_owning_issue(guard, repo):
    for command in (
        "gh api -X POST repos/o/r/transfer -f new_owner=lab",
        "gh api repos/o/r/actions/variables -f name=X -f value=y",
        "gh api --method DELETE repos/o/r/branches/main/protection",
        "gh api graphql -f query='mutation { x }'",
        "gh repo edit o/r --visibility public",
        "gh variable set X --body y",
        "gh secret delete X",
        "gh release create v1 --notes x",
        "gh label delete bug --yes",
        "gh workflow disable ci.yml",
    ):
        assert "needs an issue log" in bash(guard, repo, command), command


def test_glued_short_flags_and_gh_by_path_are_still_changes(guard, repo):
    # Found by the property tests (#73): gh takes `-XPOST` and `-fname=x`, and gh may be named by its path.
    for command in (
        "gh api -XPOST repos/o/r/transfer",
        "gh api -XDELETE repos/o/r/branches/main/protection",
        "gh api -fname=X -fvalue=y repos/o/r/actions/variables",
        "/usr/local/bin/gh secret set X --body y",
    ):
        assert "needs an issue log" in bash(guard, repo, command), command
    assert bash(guard, repo, "gh api -XGET repos/o/r/hooks") is None
    assert bash(guard, repo, "gh api -HAccept:x repos/o/r/hooks") is None


def test_github_reads_and_decision_records_pass(guard, repo):
    for command in (
        "gh issue comment 37 --body 'line one\nline two; gh variable set X'",
        "gh api repos/o/r/branches/main/protection",
        "gh api --paginate repos/o/r/issues --jq '.[].number'",
        "gh api -X GET repos/o/r/actions/variables -f per_page=100",
        "gh api graphql -f query='{ viewer { login } }'",
        "gh api repos/o/r/issues/29/comments -f body=receipt",
        "gh api -X PATCH repos/o/r/issues/comments/5 -f body=fix",
        "gh variable list",
        "gh release view v1",
        "gh issue comment 37 --body done",
        "gh pr merge 36 --squash",
    ):
        assert bash(guard, repo, command) is None, command


def test_a_github_change_can_name_its_issue_or_use_the_branchs(guard, repo):
    command = "gh variable set X --body y"
    assert bash(guard, repo, f"ACS_ISSUE=o/r#37 {command}") is None
    assert "needs an issue log" in bash(guard, repo, f"ACS_ISSUE=o/r#99 {command}")
    assert "needs an issue log" in bash(guard, repo, f"echo x # note\n{command}")
    git("checkout", "-qb", "fix/37-enforce", cwd=repo)
    assert bash(guard, repo, command) is None


def test_github_changes_from_outside_a_checkout_use_the_project(guard, repo, tmp_path, monkeypatch):
    elsewhere = tmp_path / "scratch"
    elsewhere.mkdir()
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(repo))
    assert "needs an issue log" in bash(guard, elsewhere, "gh variable set X --body y")
    monkeypatch.delenv("CLAUDE_PROJECT_DIR")
    assert bash(guard, elsewhere, "gh variable set X --body y") is None


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


@pytest.fixture
def retry_dir(tmp_path, monkeypatch):
    monkeypatch.setattr("tempfile.tempdir", str(tmp_path / "tmp"))
    (tmp_path / "tmp").mkdir()


def test_stop_blocks_unpushed_commits_even_on_a_retry(guard, repo, retry_dir):
    git("checkout", "-qb", "fix/37-enforce", cwd=repo)
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    git("add", "a.txt", cwd=repo)
    git("commit", "-qm", "change", cwd=repo)
    assert "not on GitHub" in guard.stop({"cwd": str(repo)})
    assert "not on GitHub" in guard.stop({"cwd": str(repo), "stop_hook_active": True, "session_id": "s1"})
    git("push", "-qu", "origin", "fix/37-enforce", cwd=repo)
    assert guard.stop({"cwd": str(repo)}) is None


def test_a_retried_stop_gives_up_after_the_cap(guard, repo, retry_dir, capsys):
    (repo / "AGENTS.md").write_text("edited\n", encoding="utf-8")
    retry = {"cwd": str(repo), "stop_hook_active": True, "session_id": "s2"}
    for _ in range(guard.MAX_STOP_RETRIES):
        assert "uncommitted" in guard.stop(retry)
    assert guard.stop(retry) is None
    assert "after 5 blocked retries" in capsys.readouterr().err
    assert "uncommitted" in guard.stop({**retry, "session_id": "s3"})  # the cap is per session


def test_a_retried_stop_skips_the_pull_request_checks(guard, repo, retry_dir):
    _pushed_branch(repo)
    guard.pulls["fix/37-enforce"] = []
    assert "no open pull request" in guard.stop({"cwd": str(repo)})
    assert guard.stop({"cwd": str(repo), "stop_hook_active": True, "session_id": "s4"}) is None


def test_stop_checks_the_default_branch_for_unpushed_commits(guard, repo):
    git("commit", "-q", "--allow-empty", "-m", "local only", cwd=repo)
    reason = guard.stop({"cwd": str(repo)})
    assert "Branch `main` has 1 commit(s)" in reason and "task branch" in reason


def test_stop_checks_a_branch_the_session_committed_to_then_left(guard, repo, tmp_path):
    started = {"type": "user", "timestamp": "2000-01-01T00:00:00.000Z", "cwd": str(repo)}
    path = tmp_path / "session.jsonl"
    path.write_text(json.dumps(started) + "\n", encoding="utf-8")
    git("checkout", "-qb", "fix/37-enforce", cwd=repo)
    git("commit", "-q", "--allow-empty", "-m", "work", cwd=repo)
    git("switch", "-q", "--detach", "main", cwd=repo)
    assert "Branch `fix/37-enforce` has 1 commit(s)" in guard.stop({"cwd": str(repo), "transcript_path": str(path)})
    # A branch last committed before the session began is someone's old branch, not this session's work.
    path.write_text(json.dumps({**started, "timestamp": "2999-01-01T00:00:00.000Z"}) + "\n", encoding="utf-8")
    assert guard.stop({"cwd": str(repo), "transcript_path": str(path)}) is None


def test_stop_accepts_a_branch_whose_pull_request_merged_at_its_tip(guard, repo):
    _pushed_branch(repo)
    guard.pulls["fix/37-enforce"] = []
    guard.merged["fix/37-enforce"] = [{"headRefOid": "0" * 40}]
    assert "no open pull request" in guard.stop({"cwd": str(repo)})
    guard.merged["fix/37-enforce"] = [{"headRefOid": git("rev-parse", "HEAD", cwd=repo)}]
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


def transcript(tmp_path: Path, cwd: Path, *uses: tuple[str, dict]) -> str:
    """A session transcript (JSONL) with these tool calls, plus a garbled line."""
    path = tmp_path / "session.jsonl"
    lines = [json.dumps({"type": "assistant", "cwd": str(cwd), "message": {"content": [
        {"type": "tool_use", "name": name, "input": tool_input}]}}) for name, tool_input in uses]
    path.write_text("\n".join(["{not json", *lines, ""]), encoding="utf-8")
    return str(path)


def _pushed_branch(repo: Path, branch: str = "fix/37-enforce") -> None:
    git("checkout", "-qb", branch, cwd=repo)
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    git("add", "a.txt", cwd=repo)
    git("commit", "-qm", "change", cwd=repo)
    git("push", "-qu", "origin", branch, cwd=repo)


def test_stop_reports_uncommitted_tracked_changes_on_a_branch_and_on_main(guard, repo):
    (repo / "AGENTS.md").write_text("# Rules\n\nEdited.\n", encoding="utf-8")
    reason = guard.stop({"cwd": str(repo)})
    assert "uncommitted change(s) to tracked files on `main`" in reason and "task branch" in reason
    assert "`AGENTS.md`" in reason and str(repo) in reason
    git("checkout", "-qb", "fix/37-enforce", cwd=repo)
    assert "tracked files on `fix/37-enforce`" in guard.stop({"cwd": str(repo)})
    git("commit", "-qam", "edit", cwd=repo)
    git("push", "-qu", "origin", "fix/37-enforce", cwd=repo)
    assert guard.stop({"cwd": str(repo)}) is None


def test_stop_reports_untracked_files_only_when_the_session_wrote_them(guard, repo, tmp_path):
    (repo / "notes-i-keep.txt").write_text("mine\n", encoding="utf-8")
    assert guard.stop({"cwd": str(repo)}) is None
    (repo / "new.py").write_text("x = 1\n", encoding="utf-8")
    event = {"cwd": str(repo), "transcript_path": transcript(tmp_path, repo, ("Write", {"file_path": "new.py", "content": "x"}))}
    reason = guard.stop(event)
    assert "this session wrote are not in git (`new.py`)" in reason
    assert "notes-i-keep" not in reason


def test_stop_checks_other_checkouts_the_session_worked_in(guard, repo, tmp_path):
    (tmp_path / "second").mkdir()
    (tmp_path / "third").mkdir()
    other = _repo(tmp_path / "second", tmp_path / "second" / "worktree")
    (other / "AGENTS.md").write_text("# Rules\n\nEdited elsewhere.\n", encoding="utf-8")
    plain = _repo(tmp_path / "third", tmp_path / "third" / "plain", adopter=False)
    (plain / "AGENTS.md").write_text("changed\n", encoding="utf-8")
    event = {"cwd": str(repo), "transcript_path": transcript(
        tmp_path, repo,
        ("Bash", {"command": f"cd {other} && git status"}),
        ("Bash", {"command": f"git -C {plain} commit -C HEAD"}),
    )}
    reason = guard.stop(event)
    assert f"`{other}`" in reason and "tracked files on `main`" in reason
    assert str(plain) not in reason
    assert guard.stop({"cwd": str(repo)}) is None  # without the transcript only the project folder counts


def test_stop_reads_a_missing_or_garbled_transcript_as_empty(guard, repo, tmp_path):
    assert guard.stop({"cwd": str(repo), "transcript_path": str(tmp_path / "missing.jsonl")}) is None
    junk = tmp_path / "junk.jsonl"
    junk.write_bytes(b"\xff\xfe[1, 2]\n\"text\"\n{\"message\": \"x\"}\n")
    assert guard.stop({"cwd": str(repo), "transcript_path": str(junk)}) is None


def test_stop_needs_an_open_pull_request_with_auto_merge(guard, repo):
    _pushed_branch(repo)
    assert guard.stop({"cwd": str(repo)}) is None
    guard.pulls["fix/37-enforce"] = []
    assert "no open pull request" in guard.stop({"cwd": str(repo)})
    guard.pulls["fix/37-enforce"] = [{"number": 7, "isDraft": False, "autoMergeRequest": None}]
    assert "gh pr merge 7 --auto --squash" in guard.stop({"cwd": str(repo)})
    guard.pulls["fix/37-enforce"] = [{"number": 7, "isDraft": True, "autoMergeRequest": None}]
    assert "draft" in guard.stop({"cwd": str(repo)})


def test_stop_asks_for_auto_merge_only_where_the_repository_allows_it(guard, repo):
    _pushed_branch(repo)
    guard.pulls["fix/37-enforce"] = [{"number": 7, "isDraft": False, "autoMergeRequest": None}]
    guard.auto_merge = None  # gh could not tell: keep asking, as before
    assert "gh pr merge 7 --auto --squash" in guard.stop({"cwd": str(repo)})
    guard.auto_merge = "false"
    assert guard.stop({"cwd": str(repo)}) is None
    guard.pulls["fix/37-enforce"] = [{"number": 7, "isDraft": True, "autoMergeRequest": None}]
    assert "draft" in guard.stop({"cwd": str(repo)})  # a hand merge still needs a ready pull request
    guard.pulls["fix/37-enforce"] = []
    assert "no open pull request" in guard.stop({"cwd": str(repo)})


def test_stop_does_not_block_on_gh_being_offline_but_says_so(guard, repo):
    _pushed_branch(repo)
    guard.pulls["fix/37-enforce"] = None
    assert guard.stop({"cwd": str(repo)}) is None
    (repo / "a.txt").write_text("b\n", encoding="utf-8")
    reason = guard.stop({"cwd": str(repo)})
    assert "uncommitted" in reason and "Could not check" in reason


def test_stop_main_exits_two_with_every_problem(guard, repo, monkeypatch, capsys):
    import io

    (repo / "AGENTS.md").write_text("edited\n", encoding="utf-8")
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"cwd": str(repo)})))
    assert guard.main(["stop"]) == 2
    assert "uncommitted" in capsys.readouterr().err


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


# ---------------------------------------------------------------- task records vs GitHub (#68)

GATE = "Owner scope answer on #182; then implement."


def add_task(repo: Path, task_id: str = "PCM-0060", issue: int = 182, next_action: str = GATE,
             status: str = "active") -> str:
    meta = {"id": task_id, "issue_url": f"https://github.com/acme/widget/issues/{issue}",
            "next_action": next_action, "status": status}
    path = repo / "tasks" / f"TASK-{task_id}.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text(f"# TASK-{task_id}\n\n<!-- continuity:task {json.dumps(meta)} -->\n", encoding="utf-8")
    git("add", "-A", cwd=repo)
    git("commit", "-qm", f"record {task_id}", cwd=repo)
    git("push", "-q", "origin", "main", cwd=repo)
    return path.relative_to(repo).as_posix()


def issue(state="OPEN", closed=None, comment_at=None, body="Owner: probe plus seam."):
    last = {"createdAt": comment_at, "body": body, "author": {"login": "owner"}} if comment_at else None
    return {"state": state, "closed_at": closed, "last_comment": last}


def recorded_at(repo: Path, rel: str) -> str:
    return git("log", "-1", "--format=%cI", "--", rel, cwd=repo)


def later(repo: Path, rel: str, minutes: int) -> str:
    from datetime import datetime, timedelta, timezone
    stamp = datetime.fromisoformat(recorded_at(repo, rel)) + timedelta(minutes=minutes)
    return stamp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stub_live(guard, monkeypatch, live):
    seen = []
    monkeypatch.setattr(guard, "live_issues", lambda top, refs: seen.append(refs) or live)
    return seen


def test_a_closed_issue_marks_its_record_out_of_date(guard, repo, monkeypatch):
    rel = add_task(repo)
    stub_live(guard, monkeypatch, {("acme/widget", 182): issue("CLOSED", "2026-10-31T23:34:13Z")})
    context = guard.session_start({"cwd": str(repo), "source": "startup"})
    assert "acme/widget#182 closed on 2026-10-31" in context
    assert rel in context and GATE in context and "out of date" in context


def test_an_issue_the_next_action_names_is_checked_too(guard, repo, monkeypatch):
    add_task(repo, issue=200, next_action="Wait for acme/widget#182, then ship.")
    seen = stub_live(guard, monkeypatch, {("acme/widget", 200): issue(),
                                          ("acme/widget", 182): issue("CLOSED", "2026-10-31T00:00:00Z")})
    context = guard.check_records(repo)
    assert seen == [[("acme/widget", 200), ("acme/widget", 182)]]
    assert "depends on acme/widget#182, which closed on 2026-10-31" in context


def test_a_later_comment_is_news_but_a_receipt_or_same_session_note_is_not(guard, repo, monkeypatch):
    rel = add_task(repo)
    stub_live(guard, monkeypatch, {("acme/widget", 182): issue(comment_at=later(repo, rel, 90))})
    assert "has a comment from owner" in guard.check_records(repo)
    stub_live(guard, monkeypatch, {("acme/widget", 182): issue(comment_at=later(repo, rel, 5))})
    assert guard.check_records(repo) is None
    receipt = issue(comment_at=later(repo, rel, 90), body="<!-- pcm:receipt-v2 request-id=x --> done")
    stub_live(guard, monkeypatch, {("acme/widget", 182): receipt})
    assert guard.check_records(repo) is None


def test_open_issues_with_nothing_new_stay_quiet(guard, repo, monkeypatch):
    add_task(repo)
    add_task(repo, task_id="PCM-0001", issue=1, status="done")
    seen = stub_live(guard, monkeypatch, {("acme/widget", 182): issue()})
    assert guard.session_start({"cwd": str(repo), "source": "startup"}) is None
    assert seen == [[("acme/widget", 182)]]  # the finished task is not checked


def test_when_github_cant_be_reached_the_records_are_marked_unverified(guard, repo, monkeypatch):
    add_task(repo)
    stub_live(guard, monkeypatch, None)
    context = guard.check_records(repo)
    assert "Could not reach GitHub" in context and "PCM-0060" in context and "unverified" in context


def test_no_task_records_means_no_github_call(guard, repo, monkeypatch):
    seen = stub_live(guard, monkeypatch, {})
    assert guard.check_records(repo) is None and seen == []


def test_the_query_reads_partial_answers_and_treats_no_answer_as_unreachable(guard, repo, monkeypatch):
    refs = [("acme/widget", 182), ("acme/widget", 9)]
    answer = {"data": {"i0": {"issueOrPullRequest": {"state": "CLOSED", "closedAt": "2026-10-31T00:00:00Z",
                                                     "comments": {"nodes": []}}}, "i1": None}}
    monkeypatch.setattr(guard, "run", lambda args, cwd, timeout=15: (1, json.dumps(answer)))
    assert guard.live_issues(repo, refs) == {refs[0]: issue("CLOSED", "2026-10-31T00:00:00Z")}
    monkeypatch.setattr(guard, "run", lambda args, cwd, timeout=15: (127, "timed out"))
    assert guard.live_issues(repo, refs) is None


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


# ---------------------------------------------------------------- other harnesses (#83)


def _main(guard, monkeypatch, argv, event) -> int:
    import io

    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(event)))
    return guard.main(argv)


def test_codex_pre_tool_blocks_with_exit_two_and_stop_answers_in_json(guard, repo, monkeypatch, capsys):
    commit = {"tool_name": "Bash", "tool_input": {"command": "git commit -m x"}, "cwd": str(repo)}
    assert _main(guard, monkeypatch, ["--harness", "codex", "pre-tool"], commit) == 2
    assert "[stack guard]" in capsys.readouterr().err
    (repo / "AGENTS.md").write_text("edited\n", encoding="utf-8")
    assert _main(guard, monkeypatch, ["--harness", "codex", "stop"], {"cwd": str(repo), "stop_hook_active": False}) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["decision"] == "block" and "uncommitted" in out["reason"]


def test_cursor_shell_command_is_checked_and_always_answered(guard, repo, monkeypatch, capsys):
    shell = {"command": "git commit -m x", "cwd": str(repo), "conversation_id": "c1", "workspace_roots": [str(repo)]}
    assert _main(guard, monkeypatch, ["--harness", "cursor", "pre-tool"], shell) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["permission"] == "deny" and "[stack guard]" in out["agent_message"]
    assert _main(guard, monkeypatch, ["--harness", "cursor", "pre-tool"], {**shell, "command": "ls"}) == 0
    assert json.loads(capsys.readouterr().out) == {"permission": "allow"}
    monkeypatch.setenv("ACS_GUARD", "off")
    assert _main(guard, monkeypatch, ["--harness", "cursor", "pre-tool"], shell) == 0
    assert json.loads(capsys.readouterr().out) == {"permission": "allow"}


def test_cursor_stop_finds_the_project_without_a_cwd_and_follows_up(guard, repo, monkeypatch, capsys):
    (repo / "AGENTS.md").write_text("edited\n", encoding="utf-8")
    monkeypatch.setenv("CURSOR_PROJECT_DIR", str(repo))
    assert _main(guard, monkeypatch, ["--harness", "cursor", "stop"], {"status": "completed", "loop_count": 0}) == 0
    assert "uncommitted" in json.loads(capsys.readouterr().out)["followup_message"]
    event = guard.normalize("cursor", "stop", {"loop_count": 2, "workspace_roots": ["/w"], "conversation_id": "c"})
    assert event["stop_hook_active"] is True and event["session_id"] == "c"


def test_gemini_tools_map_to_the_checks_and_deny_in_json(guard, repo, monkeypatch, capsys):
    shell = {"tool_name": "run_shell_command", "tool_input": {"command": "git commit -m x"}, "cwd": str(repo)}
    assert _main(guard, monkeypatch, ["--harness", "gemini", "pre-tool"], shell) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["decision"] == "deny" and "[stack guard]" in out["reason"]
    edit = guard.normalize("gemini", "pre-tool", {"tool_name": "write_file", "tool_input": {"file_path": "x"}})
    assert edit["tool_name"] == "Write"
    assert _main(guard, monkeypatch, ["--harness", "gemini", "pre-tool"], {**shell, "tool_input": {"command": "ls"}}) == 0
    assert capsys.readouterr().out == ""


def test_session_start_context_goes_in_each_harness_field(guard, capsys):
    assert guard.answer("cursor", "session-start", "note") == 0
    assert json.loads(capsys.readouterr().out) == {"additional_context": "note"}
    for harness in ("claude", "codex", "gemini"):
        guard.answer(harness, "session-start", "note")
        assert json.loads(capsys.readouterr().out)["hookSpecificOutput"]["additionalContext"] == "note"


def test_claude_and_codex_events_pass_through_unchanged(guard):
    event = {"tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": "/x"}
    assert guard.normalize("claude", "pre-tool", event) is event
    assert guard.normalize("codex", "pre-tool", event) is event


def test_an_unknown_harness_is_refused(guard, capsys):
    assert guard.main(["--harness", "vim", "pre-tool"]) == 2
    assert "unknown harness" in capsys.readouterr().err


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


def test_harness_hook_files_keep_the_adopters_entries_and_are_idempotent(tmp_path):
    bridge = _load("claude_bridge")
    mine = {"type": "command", "command": "./mine.sh"}
    seeds = {
        bridge.CODEX_HOOKS_REL: {"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [mine]}]}},
        bridge.CURSOR_HOOKS_REL: {"version": 1, "hooks": {"beforeShellExecution": [{"command": "./mine.sh"}]}},
        bridge.GEMINI_SETTINGS_REL: {"theme": "dark", "context": {"fileName": "GEMINI.md"},
                                     "hooks": {"BeforeTool": [{"matcher": "read_file", "hooks": [mine]}]}},
    }
    for rel, seed in seeds.items():
        (tmp_path / rel).parent.mkdir(parents=True)
        (tmp_path / rel).write_text(json.dumps(seed), encoding="utf-8")
    for rel, plan in bridge.HARNESS_PLANS:
        data = plan(tmp_path)
        (tmp_path / rel).write_bytes(data)
        assert plan(tmp_path) is None, rel
    codex = json.loads((tmp_path / bridge.CODEX_HOOKS_REL).read_text())
    assert codex["hooks"]["PreToolUse"][0]["hooks"][0] == mine
    assert "--harness codex pre-tool" in codex["hooks"]["PreToolUse"][1]["hooks"][0]["command"]
    assert set(codex["hooks"]) == {"SessionStart", "PreToolUse", "Stop"}
    cursor = json.loads((tmp_path / bridge.CURSOR_HOOKS_REL).read_text())
    assert cursor["version"] == 1 and cursor["hooks"]["beforeShellExecution"][0] == {"command": "./mine.sh"}
    assert cursor["hooks"]["stop"][0]["loop_limit"] == 5
    gemini = json.loads((tmp_path / bridge.GEMINI_SETTINGS_REL).read_text())
    assert gemini["theme"] == "dark" and gemini["context"]["fileName"] == ["GEMINI.md", "AGENTS.md"]
    assert gemini["hooks"]["BeforeTool"][0]["matcher"] == "read_file"
    assert set(gemini["hooks"]) == {"SessionStart", "BeforeTool", "AfterAgent"}


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
    for rel, plan in bridge.HARNESS_PLANS:
        assert (adopter / rel).is_file() and plan(adopter) is None
