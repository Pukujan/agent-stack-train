"""Property-based tests for the stack guard (claude_guard.py, installed as acs_guard.py), #73.

A property-based test states a rule that must hold for every input, and lets
Hypothesis generate many random inputs (here: git states, session transcripts
and shell commands) to look for one that breaks it. When it finds one, it
shrinks it to the smallest failing case. The hand-picked tests in
``test_claude_guard.py`` check chosen examples; these check combinations.

What each property expects comes from the guard's documented rules (its module
docstring), written out here as small independent oracles, not from calling the
guard's own decision functions:

1. Stop: the hook blocks if and only if some stack checkout the session touched
   (or the project folder) has uncommitted tracked changes, files the session
   wrote that git does not track, unpushed commits, a push without a PCM
   checkpoint, or a pushed branch without an open, ready pull request with
   auto-merge armed; and the reason names every such checkout and no other.
2. Pre-tool: a Bash command that changes GitHub (or commits or pushes) without
   an owning issue is always blocked, and a read-only command never is.
3. Pure helpers: the command splitter and the issue-reference patterns
   round-trip what they parse.

Gaps found: glued short flags (``gh api -XPOST``) and ``gh`` named by its path
passed as reads; they are fixed, with unit tests in ``test_claude_guard.py``.
The rest are strict expected failures at the end of this file, so fixing one
shows up as an unexpected pass: unpushed commits on the default branch, a quoted
separator, command substitution and wrappers, GraphQL from a file, and deleting
comments. The Stop property leaves commits on the default branch out for that
reason.

What these do not cover: the real ``gh`` (pull request lookups are faked, issue
existence is a fixed set), shell features beyond the fragments generated here,
gh subcommands the documented rules do not list (``gh ruleset``, ``gh repo
deploy-key``, ``gh issue close``, ``gh pr merge``), detached HEADs, the session
start hook, and the guard's file-edit rules.

Repositories are real: a template checkout with a bare ``origin`` is built once
per kind and copied for each example, so an example costs a directory copy and
a few git commands.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import tempfile
from pathlib import Path
from random import Random
from unittest import mock

import pytest
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from test_claude_guard import _load, _repo, git, transcript

ISSUES = {"37"}
OWNED_BRANCH = "fix/37-props"
# Building git repositories makes Stop examples cost a few hundred milliseconds; the rest are cheap.
STOP_SETTINGS = settings(
    max_examples=50,
    deadline=None,
    database=None,  # no .hypothesis folder in the checkout
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
SETTINGS = settings(STOP_SETTINGS, max_examples=200)
PRE_TOOL_SETTINGS = settings(STOP_SETTINGS, max_examples=150)  # each check still runs a few git commands


@pytest.fixture(scope="module")
def guard():
    """A private copy of the guard with GitHub faked: issues in ISSUES exist; pull requests come from ``guard.pulls``."""
    mod = _load("claude_guard")
    mod.issue_exists = lambda top, repo, number: number in ISSUES
    mod.pulls = {}  # resolved checkout path -> list of pull requests, or None for "gh failed"
    real_run = mod.run

    def fake_run(args, cwd, timeout=15):
        if args[:3] == ["gh", "pr", "list"]:
            pulls = mod.pulls.get(str(Path(cwd).resolve()), [])
            return (1, "") if pulls is None else (0, json.dumps(pulls))
        return real_run(args, cwd, timeout)

    mod.run = fake_run
    with mock.patch.dict(os.environ):
        os.environ.pop("CLAUDE_PROJECT_DIR", None)
        os.environ.pop("ACS_GUARD", None)
        yield mod


# ---------------------------------------------------------------- 1. stop


@pytest.fixture(scope="module")
def templates(tmp_path_factory):
    """One checkout plus bare origin per kind: stack adopter with and without PCM, and a plain repository."""
    out = {}
    for adopter, pcm in ((True, False), (True, True), (False, False)):
        root = tmp_path_factory.mktemp(f"tpl-{int(adopter)}{int(pcm)}")
        _repo(root, root / "work", adopter=adopter, pcm=pcm)
        out[(adopter, pcm)] = root
    return out


PR_STATES = {
    "none": [],
    "draft": [{"number": 7, "isDraft": True, "autoMergeRequest": None}],
    "no-auto-merge": [{"number": 7, "isDraft": False, "autoMergeRequest": None}],
    "armed": [{"number": 7, "isDraft": False, "autoMergeRequest": {"mergeMethod": "SQUASH"}}],
    "gh-offline": None,
}
COMMITS = ("none", "unpushed", "pushed", "pushed-checkpointed", "ahead-of-upstream")


MOSTLY = st.sampled_from([True, True, True, False])
RARELY = st.sampled_from([False, False, False, True])  # so the pull request states are not always masked


@st.composite
def checkout_state(draw):
    on_task_branch = draw(MOSTLY)
    return {
        "adopter": draw(MOSTLY),
        "pcm": draw(st.booleans()),
        "task_branch": on_task_branch,
        # Commits on the default branch are a separate, known gap (see the expected failures below).
        "commits": draw(st.sampled_from(COMMITS + ("pushed", "pushed-checkpointed"))) if on_task_branch else "none",
        "tracked_change": draw(RARELY),
        "session_file": draw(RARELY),  # an untracked file a Write in the transcript made
        "unrelated_file": draw(st.booleans()),  # an untracked file the session never wrote
        "pr": draw(st.sampled_from(sorted(PR_STATES))),
        "ref": draw(st.sampled_from([None, "write", "cd", "git-C"])),
    }


def clean(**changes) -> dict:
    """A referenced, pushed task branch with an armed pull request, changed as given."""
    base = {"adopter": True, "pcm": False, "task_branch": True, "commits": "pushed", "tracked_change": False,
            "session_file": False, "unrelated_file": False, "pr": "armed", "ref": "cd"}
    return {**base, **changes}


def blocking(s: dict) -> bool:
    """The documented Stop rule for one checkout, written independently of the guard."""
    if not s["adopter"]:
        return False
    if s["tracked_change"] or s["session_file"]:
        return True
    if not s["task_branch"] or s["commits"] == "none":
        return False
    if s["commits"] in ("unpushed", "ahead-of-upstream"):
        return True
    if s["pcm"] and s["commits"] != "pushed-checkpointed":
        return True
    return s["pr"] in ("none", "draft", "no-auto-merge")  # an offline gh is a note, not a block


def commit(work: Path, name: str, message: str = "change") -> None:
    (work / name).write_text(f"{name}\n", encoding="utf-8")
    git("add", name, cwd=work)
    git("commit", "-qm", message, cwd=work)


def build_checkout(templates: dict, s: dict, dest: Path, i: int) -> Path:
    shutil.copytree(templates[(s["adopter"], s["pcm"] and s["adopter"])], dest)
    work = dest / "work"
    git("remote", "set-url", "origin", str(dest / "origin.git"), cwd=work)
    if s["task_branch"]:
        branch = f"fix/37-c{i}"
        git("checkout", "-qb", branch, cwd=work)
        c = s["commits"]
        if c != "none":
            commit(work, f"w{i}.txt")
        if c == "pushed-checkpointed":
            git("commit", "-q", "--allow-empty", "-m", "PCM checkpoint TASK-1: next", cwd=work)
        if c in ("pushed", "pushed-checkpointed", "ahead-of-upstream"):
            git("push", "-qu", "origin", branch, cwd=work)
        if c == "ahead-of-upstream":
            commit(work, f"more{i}.txt")
    if s["tracked_change"]:
        (work / "AGENTS.md").write_text("# Rules\n\nEdited.\n", encoding="utf-8")
    if s["session_file"]:
        (work / f"new_{i}.py").write_text("x = 1\n", encoding="utf-8")
    if s["unrelated_file"]:
        (work / f"scratch_{i}.txt").write_text("mine\n", encoding="utf-8")
    return work


def tool_uses(work: Path, s: dict, i: int) -> list[tuple[str, dict]]:
    uses = []
    if s["session_file"]:
        uses.append(("Write", {"file_path": str(work / f"new_{i}.py"), "content": "x = 1\n"}))
    if s["ref"] == "write":
        uses.append(("Write", {"file_path": str(work / "AGENTS.md"), "content": "# Rules\n"}))
    elif s["ref"] == "cd":
        uses.append(("Bash", {"command": f"cd {shlex.quote(str(work))} && git status"}))
    elif s["ref"] == "git-C":
        uses.append(("Bash", {"command": f"git -C {shlex.quote(str(work))} log --oneline -1; echo done"}))
    return uses


def problem_lines(reason: str, top: str) -> list[str]:
    return [line for line in reason.splitlines() if line.startswith(f"- `{top}`: ") and "Could not check" not in line]


@STOP_SETTINGS
@given(
    states=st.lists(checkout_state(), min_size=1, max_size=3),
    project_is_first=st.booleans(),
    order=st.randoms(use_true_random=False),
)
# Fixed examples every run checks beside the random ones: each pull request state, a missing checkpoint,
# an unpushed commit, and blocking work in a checkout the session never touched.
@example(states=[clean(pr="none")], project_is_first=False, order=Random(0))
@example(states=[clean(pr="draft")], project_is_first=False, order=Random(0))
@example(states=[clean(pr="no-auto-merge")], project_is_first=False, order=Random(0))
@example(states=[clean(pr="gh-offline")], project_is_first=False, order=Random(0))
@example(states=[clean(pcm=True)], project_is_first=False, order=Random(0))
@example(states=[clean(pcm=True, commits="pushed-checkpointed")], project_is_first=False, order=Random(0))
@example(states=[clean(commits="ahead-of-upstream")], project_is_first=False, order=Random(0))
@example(states=[clean(ref=None, tracked_change=True), clean(pr="gh-offline", tracked_change=True)], project_is_first=False, order=Random(0))
def test_stop_blocks_iff_a_touched_checkout_has_work_off_github(guard, templates, states, project_is_first, order):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        scratch = root / "scratch"
        scratch.mkdir()
        project = scratch
        uses: list[tuple[str, dict]] = [("Bash", {"command": "ls -la"})]
        tops, referenced = [], []
        guard.pulls = {}
        for i, s in enumerate(states):
            work = build_checkout(templates, s, root / f"c{i}", i)
            top = git("rev-parse", "--show-toplevel", cwd=work)
            tops.append(top)
            guard.pulls[str(Path(top).resolve())] = PR_STATES[s["pr"]]
            if i == 0 and project_is_first:
                project = work
            mine = tool_uses(work, s, i)
            uses += mine
            referenced.append(bool(mine) or (i == 0 and project_is_first))
        order.shuffle(uses)
        event = {"cwd": str(project), "transcript_path": transcript(root, project, *uses)}

        reason = guard.stop(event)

        expected = [top for top, s, ref in zip(tops, states, referenced) if ref and blocking(s)]
        assert (reason is not None) == bool(expected), (reason, states)
        for top, s, ref in zip(tops, states, referenced):
            if top in expected:
                assert problem_lines(reason, top), (top, reason)
            elif reason is not None:
                assert not problem_lines(reason, top), (top, reason)
                if not ref:
                    assert f"`{top}`" not in reason, (top, reason)


# ---------------------------------------------------------------- 2. pre-tool


@pytest.fixture(scope="module")
def branches(tmp_path_factory):
    """A stack checkout on each kind of branch: the default, owned by an existing issue, a missing issue, none."""
    out = {}
    for name in ("main", OWNED_BRANCH, "feat/99-missing", "feat/no-issue"):
        root = tmp_path_factory.mktemp("pre")
        work = _repo(root, root / "work")
        if name != "main":
            git("checkout", "-qb", name, cwd=work)
        out[name] = work
    return out


# Kinds: "read" never needs an issue; "branch" (commit, push, pull request) needs the branch's owning issue;
# "github" (the documented gh changes) needs the branch's issue or a valid ACS_ISSUE prefix; "never"
# is a change the guard must always block (a pull request that names no issue).
text = st.text(alphabet=st.characters(codec="utf-8", exclude_categories=["Cs", "Cc"]) | st.sampled_from(";&|()\n'\"`$#"),
               max_size=24) | st.sampled_from(["gh variable set X --body y", "a; gh secret delete X", "x && git push"])
quoted = text.map(shlex.quote)

READS = [
    st.just("git status"),
    st.just("git log --oneline -3"),
    st.just("git -C . diff --stat"),
    st.just("cd ."),
    st.just("ls -la"),
    st.just("gh pr view 5 --json state"),
    st.just("gh pr list --state open"),
    st.just("gh issue view 37"),
    st.just("gh variable list"),
    st.just("gh release view v1"),
    st.just("gh api repos/o/r/branches/main/protection"),
    st.just("gh api --paginate repos/o/r/issues --jq '.[].number'"),
    st.just("gh api -X GET repos/o/r/actions/variables -f per_page=100"),
    st.just("gh api --method=get repos/o/r/hooks"),
    st.just("gh api graphql -f query='{ viewer { login } }'"),
    st.just("gh api repos/o/r/issues | jq length"),
    quoted.map(lambda q: f"echo {q}"),
    quoted.map(lambda q: f"gh issue comment 37 --body {q}"),
    quoted.map(lambda q: f"gh api repos/o/r/issues/29/comments -f body={q}"),
    quoted.map(lambda q: f"gh api -X PATCH repos/o/r/issues/comments/5 -f body={q}"),
]
BRANCH_CHANGES = [
    quoted.map(lambda q: f"git commit -m {q}"),
    st.just("git commit -am wip"),
    st.just("git -C . commit -m x"),
    st.just("git push"),
    st.just("git push -u origin HEAD"),
    quoted.map(lambda q: f"gh pr create --title t --body {shlex.quote('Refs #37 ')}{q}"),
]
GITHUB_CHANGES = [
    st.just("gh variable set X --body y"),
    st.just("gh secret delete X"),
    quoted.map(lambda q: f"gh release create v1 --notes {q}"),
    st.just("gh label delete bug --yes"),
    st.just("gh workflow disable ci.yml"),
    st.just("gh repo edit o/r --visibility public"),
    st.just("gh api -X POST repos/o/r/transfer -f new_owner=lab"),
    st.just("gh api repos/o/r/actions/variables -f name=X -f value=y"),
    st.just("gh api --method DELETE repos/o/r/branches/main/protection"),
    st.just("gh api --method=patch repos/o/r -f description=x"),
    st.just("gh api -X PUT repos/o/r/topics -f names=x"),
    st.just("gh api graphql -f query='mutation { x }'"),
    st.just("echo '{}' | \0gh api --input - repos/o/r/hooks"),  # \0 marks where the prefix goes
    st.just("gh api repos/o/r/issues -F title=t"),
    st.just("gh api -XPOST repos/o/r/transfer"),  # short flags take their value glued on, as gh allows
    st.just("gh api -XDELETE repos/o/r/branches/main/protection"),
    st.just("gh api -fname=X -fvalue=y repos/o/r/actions/variables"),
    st.just("/usr/local/bin/gh secret set X --body y"),  # gh named by its path, as git may be
]
NEVER = [quoted.filter(lambda q: not re.search(r"(?i)(refs|closes|fixes|resolves)", q)).map(
    lambda q: f"gh pr create --title t --body {q}")]
ENV_PREFIXES = {  # prefix -> does it name an existing issue
    "": False,
    "ACS_ISSUE=o/r#37 ": True,
    "ACS_ISSUE='o/r#37' ": True,
    "ACS_ISSUE=#37 ": True,
    "ACS_ISSUE=37 ": True,
    "FOO=1 ACS_ISSUE=o/r#37 ": True,
    "ACS_ISSUE=o/r#99 ": False,
    "ACS_ISSUE=nonsense ": False,
    "FOO=1 ": False,
}


@st.composite
def fragment(draw):
    kind = draw(st.sampled_from(["read"] * 6 + ["branch"] * 2 + ["github"] * 3 + ["never"]))
    pool = {"read": READS, "branch": BRANCH_CHANGES, "github": GITHUB_CHANGES, "never": NEVER}[kind]
    prefix = draw(st.sampled_from(sorted(ENV_PREFIXES)))
    body = draw(st.one_of(pool))
    return (body.replace("\0", prefix) if "\0" in body else prefix + body), kind, ENV_PREFIXES[prefix]


JOINERS = st.sampled_from(["; ", " && ", " || ", "\n", " | ", " ;\n"])


@st.composite
def command(draw):
    parts = draw(st.lists(fragment(), min_size=1, max_size=4))
    out = parts[0][0]
    for text_, _, _ in parts[1:]:
        out += draw(JOINERS) + text_
    return out, parts


def unowned(kind: str, env_issue: bool, branch_owned: bool) -> bool:
    if kind == "read":
        return False
    if kind == "never":
        return True
    if kind == "github":
        return not (env_issue or branch_owned)
    return not branch_owned  # commits, pushes and pull requests need the branch's own issue


@PRE_TOOL_SETTINGS
@given(cmd=command(), branch=st.sampled_from(["main", OWNED_BRANCH, "feat/99-missing", "feat/no-issue"]))
def test_pre_tool_blocks_unowned_github_changes_and_never_blocks_reads(guard, branches, cmd, branch):
    text_, parts = cmd
    reason = guard.pre_tool({"tool_name": "Bash", "tool_input": {"command": text_}, "cwd": str(branches[branch])})
    branch_owned = branch == OWNED_BRANCH
    must_block = any(unowned(kind, env, branch_owned) for _, kind, env in parts)
    if must_block:
        assert reason is not None, f"allowed without an owning issue: {text_!r} on {branch}"
    if all(kind == "read" for _, kind, _ in parts):
        assert reason is None, f"read-only command blocked: {text_!r}: {reason}"
    if not must_block:
        assert reason is None, f"owned change blocked: {text_!r} on {branch}: {reason}"


# ---------------------------------------------------------------- 3. pure helpers

WORD = st.text(alphabet=st.characters(codec="utf-8", exclude_categories=["Cs"]), max_size=12)
# A word made only of separator characters reads as a separator even when quoted (a known gap, below).
ARG = WORD.filter(lambda w: not (w and set(w) <= set(";&|()\n")))
NAME = st.from_regex(r"[A-Za-z_][A-Za-z0-9_]{0,8}", fullmatch=True)
PROGRAM = st.from_regex(r"[a-z][a-z0-9_.-]{0,8}", fullmatch=True)


@st.composite
def simple_command(draw):
    env = draw(st.dictionaries(NAME, WORD, max_size=2))
    args = [draw(PROGRAM), *draw(st.lists(ARG, max_size=4))]
    return env, args


@SETTINGS
@given(cmds=st.lists(simple_command(), min_size=1, max_size=4), joiners=st.lists(JOINERS, min_size=3, max_size=3))
def test_segments_round_trip_quoted_simple_commands(guard, cmds, joiners):
    texts = [" ".join([*(f"{k}={shlex.quote(v)}" for k, v in env.items()), *map(shlex.quote, args)]) for env, args in cmds]
    joined = texts[0] + "".join(j + t for j, t in zip(joiners, texts[1:]))
    assert guard.segments_with_env(joined) == cmds
    assert guard.segments(joined) == [args for _, args in cmds]


REPO = st.from_regex(r"[A-Za-z0-9_.-]{1,10}/[A-Za-z0-9_.-]{1,10}", fullmatch=True)
NUMBER = st.integers(min_value=1, max_value=9_999_999)


@SETTINGS
@given(repo=st.none() | REPO, number=NUMBER, hash_=st.booleans())
def test_issue_links_parse_back_to_their_parts(guard, repo, number, hash_):
    ref = f"{repo or ''}{'#' if (hash_ or repo) else ''}{number}"
    m = guard.LINK_RE.match(ref)
    assert m and (m.group(1), int(m.group(2))) == (repo, number)


@SETTINGS
@given(kind=st.from_regex(r"[a-z]{1,8}", fullmatch=True), number=NUMBER,
       slug=st.from_regex(r"[a-z][a-z0-9-]{0,15}", fullmatch=True))
def test_a_branch_named_after_an_issue_yields_that_issue(guard, kind, number, slug):
    m = guard.BRANCH_ISSUE_RE.search(f"{kind}/{number}-{slug}")
    assert m and int(m.group(1)) == number


@SETTINGS
@given(before=st.text(max_size=40), after=st.text(max_size=40), repo=st.none() | REPO, number=NUMBER,
       keyword=st.sampled_from(["Refs", "Closes", "Fixes", "Resolves", "refs", "Closes:"]))
def test_an_issue_reference_is_found_anywhere_in_a_body(guard, before, after, repo, number, keyword):
    assert guard.ISSUE_REF_RE.search(f"{before}\n{keyword} {repo or ''}#{number}\n{after}")


@SETTINGS
@given(args=st.lists(st.from_regex(r"[a-z0-9]{1,6}", fullmatch=True), max_size=4), value=ARG,
       flag=st.sampled_from(["--body", "-b", "--repo"]), glued=st.booleans())
def test_flag_value_reads_both_spellings(guard, args, value, flag, glued):
    spelled = [f"{flag}={value}"] if glued else [flag, value]
    assert guard.flag_value([*args, *spelled, "--tail"], flag) == value


# ---------------------------------------------------------------- known gaps the properties found
# Each is a case where the guard is wrong by its own documented rules. They stay as strict expected
# failures until the guard is fixed, so a fix shows up as an unexpected pass.


def test_stop_blocks_unpushed_commits_on_the_default_branch(guard, templates, tmp_path):
    work = build_checkout(templates, {"adopter": True, "pcm": False, "task_branch": False, "commits": "none",
                                      "tracked_change": False, "session_file": False, "unrelated_file": False}, tmp_path / "c", 0)
    commit(work, "local-only.txt")
    assert guard.stop({"cwd": str(work)})


@pytest.mark.xfail(strict=True, reason="A quoted argument made only of separator characters (`';'`) is read as a "
                   "separator, so the splitter cuts the command there (#73).")
def test_a_quoted_separator_is_an_argument_not_a_separator(guard):
    assert guard.segments("echo ';' done") == [["echo", ";", "done"]]


def _bash(guard, branches, command: str) -> str | None:
    return guard.pre_tool({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(branches["main"])})


@pytest.mark.xfail(strict=True, reason="The splitter reads a quoted `';'` as a separator, so `gh api ';' -X POST ...` "
                   "loses its `gh api` head and passes as a non-gh command (#73).")
def test_a_quoted_separator_cannot_hide_a_github_write(guard, branches):
    assert _bash(guard, branches, "gh api ';' -X POST repos/o/r/transfer")


@pytest.mark.parametrize("command", [
    "echo `gh variable set X --body y`",
    'echo "$(gh variable set X --body y)"',
    "env gh variable set X --body y",
    "command gh variable set X --body y",
])
@pytest.mark.xfail(strict=True, reason="Command substitution inside backticks or double quotes, and wrappers such as "
                   "`env` and `command`, run gh without the guard seeing a command named gh (#73).")
def test_gh_run_through_substitution_or_a_wrapper_is_still_checked(guard, branches, command):
    assert _bash(guard, branches, command)


@pytest.mark.xfail(strict=True, reason="A GraphQL mutation read from a file (`-F query=@file`) is not seen as a "
                   "mutation, so it passes as a read (#73).")
def test_a_graphql_write_read_from_a_file_is_a_change(guard, branches):
    with tempfile.TemporaryDirectory(prefix="q") as tmp:  # a path without the word the guard looks for
        (Path(tmp) / "q.graphql").write_text("mutation { x }\n", encoding="utf-8")
        assert _bash(guard, branches, f"gh api graphql -F query=@{Path(tmp) / 'q.graphql'}")


@pytest.mark.xfail(strict=True, reason="Every method on a comment endpoint passes, so deleting an issue comment (a "
                   "recorded decision) needs no issue; the documented exemption is for recording decisions (#73).")
def test_deleting_a_comment_is_not_recording_a_decision(guard, branches):
    assert _bash(guard, branches, "gh api -X DELETE repos/o/r/issues/comments/5")
