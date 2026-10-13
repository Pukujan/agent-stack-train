"""Contributor mode — the third target relationship (issue #247, first slice).

The stack models two relationships to a repository: **owner** (this repository,
dogfooded) and **adopter** (`continuity init` installs into a repository you
administer). Issue #247 names the missing third one: **contributor** — a
repository you do NOT administer, where every install surface would write into
a checkout you have no right to write into.

This module is the pure, standard-library contract layer for the first slice:

- :data:`STACK_PATHS` — the explicit set of paths the stack owns when it
  installs into a repository, derived from each component's own install
  manifest (PCM init templates, OIO installer package files, ACS hotload
  coordination state, CGM content adapter), not from memory.
- :func:`leak_findings` — the leak guard contract: report one finding per
  staged, unstaged, or untracked ``git status`` entry that sits under a
  stack-owned path. "Fails closed" is the caller's contract: a guard that
  cannot run must be reported as a failure, never as a clean result, which is
  why the parser raises on a non-repository or unreadable status.
- :func:`parse_contributor_descriptor` / :func:`render_contributor_descriptor`
  — the task descriptor: the minimal artifact that records which ``owner/repo``
  is being contributed to, the upstream SHA that anchors the task (the one-way
  link — the sidecar references upstream; upstream never references the
  sidecar), and the private sidecar location that holds the task's continuity
  state. Integration is a property of the task, not the checkout: the
  descriptor lives on the owner's side of the boundary, never in the foreign
  repository.

What this slice deliberately does NOT implement (the issue is an explicit
proposal, not a build order): the private sidecar repository itself, the
journal/checkpoint/receipt storage inside it, the coordination database, the
cross-repo index, and the OIO tracker-side sub-gap. Those remain open work
under #247.
"""

from __future__ import annotations

import json
import re

DESCRIPTOR_SCHEMA = "project-continuity.contributor.v1"

#: Upstream anchor kinds a descriptor may record. "pr" is the head SHA of the
#: upstream pull request the work will land through; "commit" is a plain
#: upstream commit SHA. Either way the SHA is upstream's and the sidecar
#: references it — never the reverse.
ANCHOR_KINDS = ("pr", "commit")

#: Paths the stack writes when it installs into a repository its user
#: administers. A contributor checkout must carry none of these in its
#: working-tree status, or stack state is leaking toward an upstream pull
#: request. Entries are repository-relative path prefixes (a directory guards
#: everything under it; a file guards itself and anything under it), each
#: traceable to the component's own install manifest:
#:
#: - PCM (``continuity init`` / docs/TARGET_ADOPTION.md): the continuity
#:   manifest and projections (``.continuity``), the materialized protocol
#:   schemas (``schemas/v1``), and the optional GitHub writing templates
#:   (``.github/ISSUE_TEMPLATE/task.md``, ``.github/pull_request_template.md``).
#: - OIO (``.github/scripts/oio_installer.py`` PACKAGE_FILES): the managed
#:   ``.oio/`` tree, the observational issue form
#:   (``.github/ISSUE_TEMPLATE/observational-issue.yml``), the triage workflow
#:   (``.github/workflows/issue-triage.yml``), and the OIO-managed block
#:   inside ``AGENTS.md``.
#: - ACS (multi-agent-hotload): coordination state committed inside the
#:   working repository (``.coord``) and the adopter root
#:   ``stack-manifest.json``.
#: - CGM: the adopter content adapter (``.content-system``).
#:
#: Entries are deliberately narrow where a foreign repository owns a same-named
#: path: its own ``AGENTS.md``, other ``.github/`` files, and its own
#: ``stack-manifest.json`` (ACS owns the adopter copy, so it stays listed) are
#: untouched unless the exact managed path appears.
STACK_PATHS: tuple[str, ...] = (
    # PCM
    ".continuity",
    "schemas/v1",
    ".github/ISSUE_TEMPLATE/task.md",
    ".github/pull_request_template.md",
    # OIO
    ".oio",
    ".github/ISSUE_TEMPLATE/observational-issue.yml",
    ".github/workflows/issue-triage.yml",
    "AGENTS.md",
    # ACS
    ".coord",
    "stack-manifest.json",
    # CGM
    ".content-system",
)

_GITHUB_REPOSITORY_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
_FULL_SHA_RE = re.compile(r"[0-9a-f]{40}")
_DESCRIPTOR_FIELDS = ("schema", "repository", "anchor_kind", "anchor_sha", "sidecar")

# porcelain v1: two status columns, a space, then the path. "R" entries are
# "old -> new"; the destination is what could land upstream.
_STATUS_LINE_RE = re.compile(r"^(?P<xy>..)\s(?P<path>.+)$")


def stack_path_for(entry_path: str) -> str | None:
    """Return the stack-owned prefix a status entry's path sits under, if any.

    A rename entry is inspected on its destination path. Paths are compared
    as POSIX repository-relative paths with a trailing slash stripped.
    """
    candidate = entry_path.split(" -> ", 1)[-1].strip('"')
    normalized = candidate.rstrip("/")
    for prefix in STACK_PATHS:
        prefix = prefix.rstrip("/")
        if normalized == prefix or normalized.startswith(prefix + "/"):
            return prefix
    return None


def leak_findings(status_porcelain: str) -> list[str]:
    """Report stack-owned paths present in a ``git status --porcelain`` stream.

    One finding is returned for every staged, unstaged, or untracked entry
    whose path sits under a :data:`STACK_PATHS` prefix; an empty list means a
    clean foreign tree. Ignored entries (``!!``) are *not* leaks here — but
    see :func:`ignored_leak_paths`: when a caller asks Git for ignored files
    explicitly, the caller wants them judged too. Unparseable lines are
    treated as leaks rather than skipped — the guard must never turn a
    surprise into silence.
    """
    findings: list[str] = []
    for line in status_porcelain.splitlines():
        if not line:
            continue
        match = _STATUS_LINE_RE.fullmatch(line)
        if match is None:
            findings.append(f"unparseable git status line (treated as a leak): {line!r}")
            continue
        xy = match.group("xy")
        if xy == "!!":
            continue
        entry = match.group("path")
        prefix = stack_path_for(entry)
        if prefix is not None:
            state = "untracked" if xy.startswith("?") else "modified"
            findings.append(f"{entry}: stack-owned path {prefix!r} is {state} in the foreign checkout")
    return findings


def ignored_leak_paths(status_porcelain: str) -> list[tuple[str, str]]:
    """Report stack-owned paths Git reports as ignored (``!!`` entries).

    A stack path inside the foreign repository's ignore list is still stack
    state written into that repository's working tree. The plain guard cannot
    see it, so the CLI runs a second ``--ignored`` pass and routes it here.
    Unparseable lines are reported as leaks with a zero-width prefix marker so
    callers can still surface them.
    """
    paths: list[tuple[str, str]] = []
    for line in status_porcelain.splitlines():
        if not line:
            continue
        match = _STATUS_LINE_RE.fullmatch(line)
        if match is None:
            paths.append((line, ""))
            continue
        if match.group("xy") != "!!":
            continue
        entry = match.group("path")
        prefix = stack_path_for(entry)
        if prefix is not None:
            paths.append((entry, prefix))
    return paths


def validate_descriptor_fields(repository: str, anchor_sha: str, anchor_kind: str, sidecar: str) -> None:
    """Reject descriptor fields the one-way-link contract cannot key on."""
    if _GITHUB_REPOSITORY_RE.fullmatch(repository) is None:
        raise ValueError(f"repository must be an owner/name slug, got: {repository!r}")
    if _FULL_SHA_RE.fullmatch(anchor_sha) is None:
        raise ValueError(f"anchor SHA must be a full 40-character hex commit SHA, got: {anchor_sha!r}")
    if anchor_kind not in ANCHOR_KINDS:
        raise ValueError(f"anchor kind must be one of {ANCHOR_KINDS}, got: {anchor_kind!r}")
    if not sidecar or any(character in sidecar for character in "\r\n"):
        raise ValueError("sidecar location must be a non-empty single-line path")


def render_contributor_descriptor(repository: str, anchor_sha: str, anchor_kind: str, sidecar: str) -> str:
    """Render the canonical descriptor document (sorted keys, LF-terminated)."""
    validate_descriptor_fields(repository, anchor_sha, anchor_kind, sidecar)
    payload = {
        "schema": DESCRIPTOR_SCHEMA,
        "repository": repository,
        "anchor_kind": anchor_kind,
        "anchor_sha": anchor_sha,
        "sidecar": sidecar,
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def parse_contributor_descriptor(text: str) -> dict[str, str]:
    """Parse and validate a descriptor document back into its fields.

    Stale-lookup safety: a malformed, partial, or unknown-schema descriptor
    raises ``ValueError`` rather than returning a plausible-looking record,
    so a sidecar gone stale (upstream force-push, branch delete) fails closed
    instead of resolving to something that merely looks right.
    """
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in contributor descriptor: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("contributor descriptor must be a JSON object")
    unknown = sorted(set(data) - set(_DESCRIPTOR_FIELDS))
    if unknown:
        raise ValueError(f"contributor descriptor has unknown field(s): {', '.join(unknown)}")
    missing = sorted(set(_DESCRIPTOR_FIELDS) - set(data))
    if missing:
        raise ValueError(f"contributor descriptor is missing field(s): {', '.join(missing)}")
    fields: dict[str, str] = {}
    for name in _DESCRIPTOR_FIELDS:
        value = data[name]
        if not isinstance(value, str):
            raise ValueError(f"contributor descriptor field {name!r} must be a string")
        fields[name] = value
    if fields["schema"] != DESCRIPTOR_SCHEMA:
        raise ValueError(f"unsupported descriptor schema: {fields['schema']!r}")
    validate_descriptor_fields(fields["repository"], fields["anchor_sha"], fields["anchor_kind"], fields["sidecar"])
    return fields
