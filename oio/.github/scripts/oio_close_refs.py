#!/usr/bin/env python3
"""Close OIO issue logs when a merged pull request names them.

The pure helpers in this module parse a pull-request body, rewrite the
Lifecycle Status section, and detect lifecycle/state drift. The CLI talks to
GitHub through ``gh`` so the same script can run from any adopter workflow.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import Iterable

CLOSE_COMMENT_MARKER = "<!-- oio:close-on-merge -->"
SETTLED_STATUSES = {"resolved", "superseded", "obsolete", "wontfix"}
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


def _comment_once(repo: str, number: int, pr_url: str) -> None:
    data = _gh_json("issue", "view", str(number), "--repo", repo, "--json", "comments")
    comments = data.get("comments", []) if isinstance(data, dict) else []
    if any(CLOSE_COMMENT_MARKER in (comment.get("body") or "") for comment in comments):
        return
    body = (
        f"{CLOSE_COMMENT_MARKER}\n"
        f"Closed by {pr_url} on merge. OIO set the Lifecycle Status to `resolved` and applied `status:resolved`."
    )
    result = _run(["gh", "issue", "comment", str(number), "--repo", repo, "--body", body])
    if result.returncode != 0:
        raise RuntimeError(f"could not comment on {repo}#{number}: {result.stderr.strip()}")


def _sync_issue(repo: str, number: int, issue: dict, pr_url: str) -> None:
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
    _comment_once(repo, number, pr_url)


def apply_refs(repo: str, pr_url: str) -> int:
    pr = _gh_json("pr", "view", pr_url, "--json", "body,url")
    if not isinstance(pr, dict):
        raise RuntimeError(f"could not read pull request {pr_url}")
    body = pr.get("body") or ""
    url = pr.get("url") or pr_url
    failures = 0
    for ref_repo, number in closing_refs(body):
        target = ref_repo or repo
        same_repo = target.casefold() == repo.casefold()
        try:
            issue = _gh_json("issue", "view", str(number), "--repo", target, "--json", "state,body,labels")
            if not isinstance(issue, dict):
                raise RuntimeError(f"could not read {target}#{number}")
            already_closed = str(issue.get("state", "")).upper() == "CLOSED"
            _ensure_label(target, "status:resolved")
        except RuntimeError as exc:
            if not same_repo and _is_missing_or_forbidden(str(exc)):
                print(f"WARNING: no access to {target}#{number}; skipping it: {exc}", file=sys.stderr)
                continue
            print(f"ERROR: {exc}", file=sys.stderr)
            failures += 1
            continue
        if already_closed:
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
                    continue
                print(f"ERROR: could not close {target}#{number}: {close_result.stderr.strip()}", file=sys.stderr)
                failures += 1
                continue
        try:
            _sync_issue(target, number, issue, url)
        except RuntimeError as exc:
            if not same_repo and _is_missing_or_forbidden(str(exc)):
                print(f"WARNING: closed {target}#{number} but could not sync its OIO fields: {exc}", file=sys.stderr)
                continue
            print(f"ERROR: {exc}", file=sys.stderr)
            failures += 1
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
    parser.add_argument("--repo", required=True, help="OWNER/REPOSITORY that owns the pull request")
    parser.add_argument("--pr", help="pull-request URL; required with --apply")
    args = parser.parse_args(argv)
    if args.apply and not args.pr:
        parser.error("--pr is required with --apply")
    try:
        if args.audit:
            return audit_repo(args.repo)
        return apply_refs(args.repo, args.pr)
    except (RuntimeError, json.JSONDecodeError, OSError) as exc:
        print(f"OIO close/audit failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
