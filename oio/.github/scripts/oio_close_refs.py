#!/usr/bin/env python3
"""Close OIO issue logs when a merged pull request names them.

The pure helpers in this module parse a pull-request body, rewrite the
Lifecycle Status section, detect lifecycle/state drift, and pick the issues a
scheduled sweep would settle. The CLI talks to GitHub through ``gh`` so the
same script can run from any adopter workflow.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import Iterable

CLOSE_COMMENT_MARKER = "<!-- oio:close-on-merge -->"
ROLLUP_COMMENT_MARKER = "<!-- oio:rollup -->"
SETTLED_STATUSES = {"resolved", "superseded", "obsolete", "wontfix"}
# The sweep's own labels use the `oio:` prefix, which triage does not manage,
# so a triage run never strips them.
READY_LABEL = "oio:ready-to-close"
KEEP_OPEN_LABEL = "oio:keep-open"
SWEEP_PR_LIMIT = 100
OPEN_ISSUES_QUERY = """
query($owner: String!, $name: String!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    issues(states: OPEN, first: 100, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes { number labels(first: 100) { nodes { name } } subIssuesSummary { total completed } }
    }
  }
}
"""
# Pull-request bodies quote examples such as `Closes owner/repo#12` while
# documenting the contract. Those placeholders name no real repository, so a
# close attempt on them only produces a resolution error.
PLACEHOLDER_OWNERS = {"owner", "org", "your-org", "your_org"}
PLACEHOLDER_REPOS = {"repo", "repository", "name", "your-repo", "your_repo"}
CLOSING_PATTERN = re.compile(
    r"\b(?:closes|fixes|resolves)\b\s*:?\s*"
    r"(?:([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+))?\s*#([0-9]+)\b",
    re.IGNORECASE,
)
LIFECYCLE_HEADING = re.compile(r"^###[ \t]+Lifecycle Status[ \t]*(?=\r?$)", re.IGNORECASE | re.MULTILINE)
NEXT_HEADING = re.compile(r"^###[ \t]+", re.MULTILINE)


def _is_placeholder(repo: str) -> bool:
    owner, name = repo.split("/", 1)
    return owner.lower() in PLACEHOLDER_OWNERS or name.lower() in PLACEHOLDER_REPOS


def closing_refs(body: str) -> list[tuple[str | None, int]]:
    """Return the issues a body closes with a native closing verb.

    ``Refs #12`` is a progress link, not a close directive, and is ignored.
    A reference whose repository part is a documented placeholder
    (``owner/repo#12``) is an example, not a directive. Duplicates are
    collapsed while keeping first-seen order.
    """
    refs: list[tuple[str | None, int]] = []
    seen: set[tuple[str | None, int]] = set()
    for match in CLOSING_PATTERN.finditer(body or ""):
        repo = match.group(1)
        if repo is not None and _is_placeholder(repo):
            continue
        key = (repo.lower() if repo else None, int(match.group(2)))
        if key in seen:
            continue
        seen.add(key)
        refs.append((repo, int(match.group(2))))
    return refs


def resolve_lifecycle(body: str) -> str:
    """Set the ``### Lifecycle Status`` section to ``resolved``.

    The section is replaced in place, appended when absent, and the function is
    idempotent so a retried workflow run produces the same body.
    """
    body = body or ""
    newline = "\r\n" if "\r\n" in body else "\n"
    match = LIFECYCLE_HEADING.search(body)
    if match is None:
        return body.rstrip("\r\n") + newline * 2 + "### Lifecycle Status" + newline * 2 + "resolved" + newline
    next_heading = NEXT_HEADING.search(body, match.end())
    if next_heading is None:
        return body[: match.end()] + newline * 2 + "resolved" + newline
    return body[: match.end()] + newline * 2 + "resolved" + newline * 2 + body[next_heading.start() :]


def _label_names(labels: Iterable[object]) -> list[str]:
    names: list[str] = []
    for label in labels or []:
        if isinstance(label, str):
            names.append(label)
        elif isinstance(label, dict):
            name = label.get("name")
            if isinstance(name, str):
                names.append(name)
    return names


def drift_findings(issues: Iterable[dict]) -> list[str]:
    """Report ``status:*`` labels that contradict the GitHub open/closed state."""
    findings: list[str] = []
    for issue in issues:
        number = issue.get("number", "?")
        state = str(issue.get("state", "")).upper()
        statuses = [name.split(":", 1)[1] for name in _label_names(issue.get("labels")) if name.startswith("status:")]
        if not statuses:
            continue
        if state == "CLOSED":
            contradicted = [status for status in statuses if status not in SETTLED_STATUSES]
            if contradicted:
                findings.append(
                    f"issue #{number} is closed but carries {', '.join('status:' + status for status in contradicted)}"
                )
        elif state == "OPEN":
            contradicted = [status for status in statuses if status != "open"]
            if contradicted:
                findings.append(
                    f"issue #{number} is open but carries {', '.join('status:' + status for status in contradicted)}"
                )
    return findings


def sweep_candidates(repo: str, prs: Iterable[dict]) -> list[tuple[str, int, dict]]:
    """Return ``(target repo, issue number, pull request)`` for every closing reference.

    An issue named by several merged pull requests keeps the latest merge, so a
    log reopened after one merge and named again by a later one is still found.
    ``#5`` and ``owner/repo#5`` for the sweep's own repository are one issue.
    """
    latest: dict[tuple[str, int], tuple[str, int, dict]] = {}
    for pr in sorted(prs, key=lambda pr: pr.get("mergedAt") or ""):
        for ref_repo, number in closing_refs(pr.get("body") or ""):
            target = ref_repo or repo
            latest[(target.casefold(), number)] = (target, number, pr)
    return list(latest.values())


def rollup_ready(issues: Iterable[dict]) -> list[dict]:
    """Return open parents whose sub-issues are all closed, except those marked keep-open."""
    ready: list[dict] = []
    for issue in issues:
        summary = issue.get("subIssuesSummary") or {}
        total = summary.get("total") or 0
        if total and summary.get("completed") == total and KEEP_OPEN_LABEL not in _label_names(issue.get("labels")):
            ready.append(issue)
    return ready


def _run(args: list[str], *, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, input=stdin, capture_output=True, text=True, check=False)


def _gh_json(*args: str) -> object:
    result = _run(["gh", *args])
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr.strip()}")
    return json.loads(result.stdout or "null")


def _is_missing_or_forbidden(stderr: str) -> bool:
    lowered = stderr.lower()
    return any(marker in lowered for marker in ("http 403", "http 404", "forbidden", "not found"))


def _ensure_label(repo: str, label: str) -> None:
    result = _run(
        ["gh", "label", "create", label, "--repo", repo, "--color", "5319e7", "--description", "OIO classification: " + label]
    )
    if result.returncode != 0 and "already exists" not in result.stderr.lower():
        raise RuntimeError(f"could not ensure label {label!r} on {repo}: {result.stderr.strip()}")


def _close_issue(repo: str, number: int) -> subprocess.CompletedProcess[str]:
    return _run(["gh", "issue", "close", str(number), "--repo", repo, "--reason", "completed"])


def _comment_once(repo: str, number: int, message: str, marker: str = CLOSE_COMMENT_MARKER) -> None:
    data = _gh_json("issue", "view", str(number), "--repo", repo, "--json", "comments")
    comments = data.get("comments", []) if isinstance(data, dict) else []
    if any(marker in (comment.get("body") or "") for comment in comments):
        return
    result = _run(["gh", "issue", "comment", str(number), "--repo", repo, "--body", f"{marker}\n{message}"])
    if result.returncode != 0:
        raise RuntimeError(f"could not comment on {repo}#{number}: {result.stderr.strip()}")


def _sync_issue(repo: str, number: int, issue: dict, message: str) -> None:
    labels = _label_names(issue.get("labels"))
    other_statuses = [label for label in labels if label.startswith("status:") and label != "status:resolved"]
    edit = ["gh", "issue", "edit", str(number), "--repo", repo, "--add-label", "status:resolved"]
    for label in other_statuses:
        edit.extend(["--remove-label", label])
    result = _run(edit)
    if result.returncode != 0:
        raise RuntimeError(f"could not update labels on {repo}#{number}: {result.stderr.strip()}")
    result = _run(
        ["gh", "issue", "edit", str(number), "--repo", repo, "--body-file", "-"],
        stdin=resolve_lifecycle(issue.get("body") or ""),
    )
    if result.returncode != 0:
        raise RuntimeError(f"could not update the body of {repo}#{number}: {result.stderr.strip()}")
    _comment_once(repo, number, message)


def _read_issue(repo: str, target: str, number: int) -> dict | None:
    """Read a log and ensure ``status:resolved`` exists, or return None to skip it.

    Raises for a same-repository failure; another repository that is missing or
    forbidden only warns, so one inaccessible reference does not fail the run.
    """
    try:
        issue = _gh_json("issue", "view", str(number), "--repo", target, "--json", "state,body,labels")
        if not isinstance(issue, dict):
            raise RuntimeError(f"could not read {target}#{number}")
        _ensure_label(target, "status:resolved")
    except RuntimeError as exc:
        if target.casefold() != repo.casefold() and _is_missing_or_forbidden(str(exc)):
            print(f"WARNING: no access to {target}#{number}; skipping it: {exc}", file=sys.stderr)
            return None
        raise
    return issue


def _settle(repo: str, target: str, number: int, issue: dict, message: str) -> int:
    """Close one log unless it is already closed, then sync its OIO fields. Returns 1 on failure."""
    same_repo = target.casefold() == repo.casefold()
    if str(issue.get("state", "")).upper() == "CLOSED":
        # GitHub's own closing keyword may have closed the log first. Do not
        # issue a second close; still record how it settled.
        print(f"{target}#{number} is already closed; syncing its OIO fields without closing it")
    else:
        close_result = _close_issue(target, number)
        if close_result.returncode != 0:
            if not same_repo and _is_missing_or_forbidden(close_result.stderr):
                print(
                    f"WARNING: cannot close {target}#{number} with the available token; "
                    f"skipping it: {close_result.stderr.strip()}",
                    file=sys.stderr,
                )
                return 0
            print(f"ERROR: could not close {target}#{number}: {close_result.stderr.strip()}", file=sys.stderr)
            return 1
    try:
        _sync_issue(target, number, issue, message)
    except RuntimeError as exc:
        if not same_repo and _is_missing_or_forbidden(str(exc)):
            print(f"WARNING: closed {target}#{number} but could not sync its OIO fields: {exc}", file=sys.stderr)
            return 0
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


def apply_refs(repo: str, pr_url: str) -> int:
    pr = _gh_json("pr", "view", pr_url, "--json", "body,url")
    if not isinstance(pr, dict):
        raise RuntimeError(f"could not read pull request {pr_url}")
    body = pr.get("body") or ""
    url = pr.get("url") or pr_url
    message = f"Closed by {url} on merge. OIO set the Lifecycle Status to `resolved` and applied `status:resolved`."
    failures = 0
    for ref_repo, number in closing_refs(body):
        target = ref_repo or repo
        try:
            issue = _read_issue(repo, target, number)
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            failures += 1
            continue
        if issue is not None:
            failures += _settle(repo, target, number, issue, message)
    return 1 if failures else 0


def _open_issues(repo: str) -> list[dict]:
    owner, name = repo.split("/", 1)
    issues: list[dict] = []
    cursor = None
    while True:
        args = ["api", "graphql", "-f", f"query={OPEN_ISSUES_QUERY}", "-f", f"owner={owner}", "-f", f"name={name}"]
        if cursor:
            args += ["-f", f"cursor={cursor}"]
        data = _gh_json(*args)
        page = data["data"]["repository"]["issues"]
        for node in page["nodes"]:
            issues.append(
                {
                    "number": node["number"],
                    "labels": [label["name"] for label in node["labels"]["nodes"]],
                    "subIssuesSummary": node.get("subIssuesSummary") or {},
                }
            )
        if not page["pageInfo"]["hasNextPage"]:
            return issues
        cursor = page["pageInfo"]["endCursor"]


def _reopen_times(repo: str, number: int) -> list[str]:
    result = _run(
        [
            "gh", "api", f"repos/{repo}/issues/{number}/events", "--paginate",
            "--jq", '.[] | select(.event == "reopened") | .created_at',
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(f"could not read the events of {repo}#{number}: {result.stderr.strip()}")
    return result.stdout.split()


def _set_label(repo: str, number: int, label: str, add: bool) -> None:
    flag = "--add-label" if add else "--remove-label"
    result = _run(["gh", "issue", "edit", str(number), "--repo", repo, flag, label])
    if result.returncode != 0:
        raise RuntimeError(f"could not update labels on {repo}#{number}: {result.stderr.strip()}")


def _sweep_merged(repo: str, open_numbers: set[int], write: bool) -> tuple[int, set[int]]:
    """Close open logs that a merged pull request into the default branch names.

    Returns the failure count and the same-repository numbers it closed (or
    would close), so the rollup does not act on them a second time.
    """
    default = _gh_json("repo", "view", repo, "--json", "defaultBranchRef")["defaultBranchRef"]["name"]
    prs = _gh_json(
        "pr", "list", "--repo", repo, "--state", "merged", "--base", default,
        "--limit", str(SWEEP_PR_LIMIT), "--json", "url,body,mergedAt",
    )
    failures = 0
    settled: set[int] = set()
    for target, number, pr in sweep_candidates(repo, prs if isinstance(prs, list) else []):
        same_repo = target.casefold() == repo.casefold()
        if same_repo and number not in open_numbers:
            continue
        try:
            issue = _read_issue(repo, target, number) if write else _gh_json(
                "issue", "view", str(number), "--repo", target, "--json", "state,body,labels"
            )
            if issue is None or str(issue.get("state", "")).upper() == "CLOSED":
                continue
            if KEEP_OPEN_LABEL in _label_names(issue.get("labels")):
                print(f"skip {target}#{number}: labelled {KEEP_OPEN_LABEL}")
                continue
            # Someone reopening a log after the merge says the merge did not finish it.
            if any(when > pr["mergedAt"] for when in _reopen_times(target, number)):
                print(f"skip {target}#{number}: reopened after {pr['url']} merged")
                continue
        except RuntimeError as exc:
            if not same_repo and _is_missing_or_forbidden(str(exc)):
                print(f"WARNING: no access to {target}#{number}; skipping it: {exc}", file=sys.stderr)
                continue
            print(f"ERROR: {exc}", file=sys.stderr)
            failures += 1
            continue
        print(f"{'' if write else 'would '}close {target}#{number}: named by {pr['url']}, merged {pr['mergedAt']}")
        if same_repo:
            settled.add(number)
        if write:
            message = (
                f"Closed by OIO's close sweep: {pr['url']} names this issue with a closing keyword and merged "
                f"on {pr['mergedAt'][:10]}, but the merge did not close it. OIO set the Lifecycle Status to "
                f"`resolved` and applied `status:resolved`. Reopen it, or add `{KEEP_OPEN_LABEL}`, if it is not done."
            )
            failures += _settle(repo, target, number, issue, message)
    return failures, settled


def _rollup(repo: str, open_issues: list[dict], settled: set[int], write: bool, mode: str) -> int:
    """Label (or close) open parents whose sub-issues are all closed."""
    prefix = "" if write else "would "
    ready = {issue["number"] for issue in rollup_ready(open_issues)}
    failures = 0
    for issue in open_issues:
        number = issue["number"]
        if number in settled:
            continue
        labelled = READY_LABEL in issue["labels"]
        total = (issue.get("subIssuesSummary") or {}).get("total")
        done = "its one sub-issue is closed" if total == 1 else f"all {total} of its sub-issues are closed"
        try:
            if number in ready and mode == "close":
                print(f"{prefix}close parent {repo}#{number}: {done}")
                if write:
                    full = _read_issue(repo, repo, number)
                    message = (
                        f"Closed by OIO's close sweep: {done}. OIO set the Lifecycle Status to `resolved` and "
                        f"applied `status:resolved`. Reopen it, or add `{KEEP_OPEN_LABEL}`, if it is not done."
                    )
                    failures += _settle(repo, repo, number, full, message)
            elif number in ready and not labelled:
                print(f"{prefix}label {repo}#{number} {READY_LABEL}: {done}")
                if write:
                    _ensure_label(repo, READY_LABEL)
                    _set_label(repo, number, READY_LABEL, add=True)
                    _comment_once(
                        repo,
                        number,
                        f"OIO labelled this issue `{READY_LABEL}` because {done}. "
                        f"Close it if it is done, or add `{KEEP_OPEN_LABEL}` to keep it open.",
                        marker=ROLLUP_COMMENT_MARKER,
                    )
            elif labelled and number not in ready:
                print(f"{prefix}remove {READY_LABEL} from {repo}#{number}: it is no longer ready to close")
                if write:
                    _set_label(repo, number, READY_LABEL, add=False)
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            failures += 1
    return failures


def sweep_repo(repo: str, *, write: bool, rollup: str = "label") -> int:
    """Settle what merges left open, then roll up parents whose sub-issues are all closed.

    A merge carried out with the workflow token closes nothing and starts no
    close-on-merge run, so the sweep reads recent merged pull requests instead
    of waiting for a merge event. Without ``write`` it only prints what it
    would do.
    """
    open_issues = _open_issues(repo)
    failures, settled = _sweep_merged(repo, {issue["number"] for issue in open_issues}, write)
    failures += _rollup(repo, open_issues, settled, write, rollup)
    print(f"{'' if write else 'report only: '}sweep of {repo} finished with {failures} failure(s)")
    return 1 if failures else 0


def audit_repo(repo: str) -> int:
    issues = _gh_json("issue", "list", "--repo", repo, "--state", "all", "--limit", "1000", "--json", "number,state,stateReason,labels")
    findings = drift_findings(issues if isinstance(issues, list) else [])
    for finding in findings:
        print(finding)
    print(f"{len(findings)} drift finding(s) in {repo}")
    return 1 if findings else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true", help="close issues named by a merged pull request")
    mode.add_argument("--audit", action="store_true", help="report lifecycle-status drift and exit non-zero on findings")
    mode.add_argument(
        "--sweep",
        action="store_true",
        help="find open issues that merged pull requests name, and parents whose sub-issues are all closed",
    )
    parser.add_argument("--repo", required=True, help="OWNER/REPOSITORY that owns the pull request")
    parser.add_argument("--pr", help="pull-request URL; required with --apply")
    parser.add_argument("--write", action="store_true", help="with --sweep, make the changes instead of only reporting them")
    parser.add_argument(
        "--rollup",
        choices=("label", "close"),
        default="label",
        help=f"with --sweep, add {READY_LABEL} to a finished parent (default) or close it",
    )
    args = parser.parse_args(argv)
    if args.apply and not args.pr:
        parser.error("--pr is required with --apply")
    try:
        if args.audit:
            return audit_repo(args.repo)
        if args.sweep:
            return sweep_repo(args.repo, write=args.write, rollup=args.rollup)
        return apply_refs(args.repo, args.pr)
    except (RuntimeError, json.JSONDecodeError, OSError) as exc:
        print(f"OIO close/audit failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
