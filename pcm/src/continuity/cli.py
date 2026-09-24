from __future__ import annotations

import argparse
import difflib
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import uuid
from collections.abc import Callable, Iterator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import quote

from . import __version__

PROTOCOL_VERSION = "0.1.0-draft"
CONTINUITY_RECORDS_POLICY_MARKER = (
    '<!-- pcm:policy {"id":"continuity-records","policy_version":"1.2.0","protocol_version":"0.1.0-draft"} -->'
)
GITHUB_PROGRESSION_GUIDANCE = """<!-- pcm:github-progression:start -->
## GitHub-owned progression

GitHub Issues are required for PCM-governed project work and own task scope, acceptance, priority, ownership, dependencies, lifecycle and durable project progression. Merged default-branch history owns accepted code and normative/domain documents; PR checks and merge records own delivery facts. Checked-in PROJECT/CURRENT/TASK/checkpoint/handoff documents are mandatory versioned projections for task state, not a parallel authority. Local files, registries, context packs and chat are ephemeral execution aids. Domain-document ownership stays with the target project.

Every issue progress update MUST link the leaf child issue that owns the work, its parent ancestry and dependencies (or explicitly none). A top-level deliverable identifies itself as the leaf and says parent: none. Create one child per independently deliverable scope, never one per comment. Record task ID, primary writer and branch on the issue before creating its repository projection. Re-read live issues and relevant source revisions before resuming; the issue verifier checks identity/status, not semantic agreement.

Authorized owner/user direction can revise intent: record it on the owning GitHub issue with a correction/supersession link before dependent work. It cannot alter observed CI/merge facts or waive required gates. Stale projections yield to their field's authority. If direction, ownership or evidence conflicts remain unresolved, pause affected work and record uncertainty; continue independent safe work. One primary writer owns each task branch/checkpoint stream. Coordinate shared-document edits through linked issues/PRs, re-read the current base and reconcile concurrent changes; never force-push or overwrite another writer. Issue prose is not an atomic lock.

Label observed results, repository/external evidence, agent reports and inference separately. Preserve contradictory evidence with source/revision and mark conclusions disputed or unknown until resolved. Append correction/supersession evidence; never rewrite checkpoint history. An upstream correction MUST identify affected descendants and assumptions on their issues; pause, re-plan and revalidate dependent work before resuming. Follow explicit parent/dependency links within the affected scope; cycles or unknown lineage block affected claims. No graph database, local canonical ledger or autonomous polling agent is required.

Before every push, synchronize relevant docs and task/checkpoint projections, CURRENT/HANDOFF when affected, and reviewed catalog/generated index. Record leaf/parent/dependency links, source issue/comment revision, as-of status, evidence, blockers and next action. Commit product/docs first; `continuity checkpoint` then commits and synchronously pushes the checkpoint with a stable request ID. After every successful push, manually publish a leaf issue receipt keyed by request ID and exact pushed SHA, linking changed docs/checkpoint, PR, tests and pending gates; add a linked parent progression update. Retry a missing receipt without another checkpoint/push; inspect for the same key before posting. Automatic issue-comment synchronization is not implemented.

Required CI and GitHub auto-merge are mandatory. Verify protection, required reviews/checks on the exact current-base or merge-queue candidate, and auto-merge; missing, failed, skipped, stale or unverified gates fail closed: no completion or cleanup. After CI/merge, append the exact check results, PR/merge SHA and live issue status to the leaf and link the parent update; fetch and verify accepted history. Reconcile material doc/status corrections in a new synchronized increment. Receipt-only transitions need no recursive doc commit: docs retain an explicit as-of/pending state and point to the live issue. Never label local-only or merely pushed work delivered. Preserve unsafe resources and keep incomplete issues open.
<!-- pcm:github-progression:end -->"""

GITHUB_ISSUE_LIFECYCLE_GUIDANCE = (
    "When a GitHub issue reference appears in a pull-request description or commit message, use a supported issue-closing keyword only when merging should complete that issue. "
    "GitHub treats `close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves`, and `resolved` followed by an issue reference as a close directive; negation does not cancel it. "
    "For progress-only work, link with `Refs #<number>` or the GitHub sidebar. After each merge, verify the live issue state before changing task status. "
    "See [GitHub's issue-linking rules](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue)."
)
CONFIG_SCHEMA = "project-continuity.config.v1"
MARKER_RE = re.compile(r"<!--\s*continuity:(?P<kind>[a-z-]+)\s+(?P<payload>\{.*\})\s*-->")
TASK_FILE_RE = re.compile(r"^TASK-(?P<prefix>[A-Z][A-Z0-9]*)-(?P<num>\d{4})(?:-(?P<slug>[a-z0-9-]+))?\.md$")
TASK_ID_RE = re.compile(r"^(?P<prefix>[A-Z][A-Z0-9]*)-(?P<num>\d{4})$")
CHECKPOINT_HEADING_RE = re.compile(r"^###\s+.+$")
SECTION_NAMES = ("Completed:", "Evidence:", "Decisions:", "Changed:", "Blocked/uncertain:", "Next:")

SCHEMA_FILES = {
    "config": "config.schema.json",
    "project": "project.schema.json",
    "current": "current.schema.json",
    "task": "task.schema.json",
    "checkpoint": "checkpoint.schema.json",
    "checkpoint-operation": "checkpoint-operation.schema.json",
    "context-pack": "context-pack.schema.json",
    "documents": "documents.schema.json",
    "recovery": "recovery.schema.json",
}

WORKSPACE_MODES = {"managed-worktrees", "single-checkout"}
WORKSPACE_SCHEMA: dict[str, Any] = {
    "additionalProperties": False,
    "properties": {"mode": {"enum": sorted(WORKSPACE_MODES), "type": "string"}},
    "required": ["mode"],
    "type": "object",
}

BUILTIN_SCHEMAS = {
    "config": {
        "$id": "https://project-continuity.dev/schema/v1/config.schema.json",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "additionalProperties": False,
        "properties": {
            "canonical": {
                "additionalProperties": False,
                "properties": {
                    "current": {"minLength": 1, "type": "string"},
                    "project": {"minLength": 1, "type": "string"},
                    "tasks": {"minLength": 1, "type": "string"},
                },
                "required": ["project", "current", "tasks"],
                "type": "object",
            },
            "profile": {"enum": ["minimal", "software"], "type": "string"},
            "protocol": {"const": "project-continuity"},
            "protocol_version": {"minLength": 1, "type": "string"},
            "schema": {"const": "project-continuity.config.v1"},
            "schema_dir": {"const": "schemas/v1"},
            "task_prefix": {"pattern": "^[A-Z][A-Z0-9]*$", "type": "string"},
            "trackers": {
                "additionalProperties": False,
                "properties": {"beads": {"type": "boolean"}, "github": {"type": "boolean"}},
                "required": ["github", "beads"],
                "type": "object",
            },
        },
        "required": [
            "schema",
            "protocol",
            "protocol_version",
            "profile",
            "task_prefix",
            "canonical",
            "schema_dir",
            "trackers",
        ],
        "title": "Project Continuity Config v1",
        "type": "object",
    },
    "project": {
        "$id": "https://project-continuity.dev/schema/v1/project.schema.json",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "additionalProperties": False,
        "properties": {
            "id": {"pattern": "^[a-z0-9][a-z0-9-]*$", "type": "string"},
            "protocol_version": {"minLength": 1, "type": "string"},
            "schema": {"const": "project-continuity.project.v1"},
            "title": {"minLength": 1, "type": "string"},
        },
        "required": ["schema", "protocol_version", "id", "title"],
        "title": "Project metadata v1",
        "type": "object",
    },
    "current": {
        "$id": "https://project-continuity.dev/schema/v1/current.schema.json",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "additionalProperties": False,
        "properties": {
            "active_task": {"pattern": "^[A-Z][A-Z0-9]*-[0-9]{4}$", "type": ["string", "null"]},
            "active_task_file": {"minLength": 1, "type": ["string", "null"]},
            "protocol_version": {"minLength": 1, "type": "string"},
            "schema": {"const": "project-continuity.current.v1"},
        },
        "required": ["schema", "protocol_version", "active_task", "active_task_file"],
        "title": "Current checkpoint metadata v1",
        "type": "object",
    },
    "task": {
        "$id": "https://project-continuity.dev/schema/v1/task.schema.json",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "additionalProperties": False,
        "properties": {
            "acceptance": {"items": {"minLength": 1, "type": "string"}, "minItems": 1, "type": "array"},
            "depends_on": {"items": {"minLength": 1, "type": "string"}, "type": "array"},
            "goal": {"minLength": 1, "type": "string"},
            "id": {"pattern": "^[A-Z][A-Z0-9]*-[0-9]{4}$", "type": "string"},
            "issue_url": {"format": "uri", "pattern": "^https://github\\.com/[^/]+/[^/]+/issues/[1-9][0-9]*$", "type": "string"},
            "next_action": {"minLength": 1, "type": "string"},
            "owner": {"minLength": 1, "type": "string"},
            "priority": {"minLength": 1, "type": "string"},
            "protocol_version": {"minLength": 1, "type": "string"},
            "schema": {"const": "project-continuity.task.v1"},
            "status": {"enum": ["queued", "active", "blocked", "completed", "cancelled"], "type": "string"},
            "why": {"minLength": 1, "type": "string"},
        },
        "required": [
            "schema",
            "protocol_version",
            "id",
            "status",
            "owner",
            "priority",
            "depends_on",
            "goal",
            "why",
            "acceptance",
            "next_action",
        ],
        "title": "Task metadata v1",
        "type": "object",
    },
    "checkpoint": {
        "$id": "https://project-continuity.dev/schema/v1/checkpoint.schema.json",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "additionalProperties": False,
        "properties": {
            "agent": {"minLength": 1, "type": "string"},
            "blocked": {"items": {"minLength": 1, "type": "string"}, "type": "array"},
            "changed": {"items": {"minLength": 1, "type": "string"}, "minItems": 1, "type": "array"},
            "completed": {"items": {"minLength": 1, "type": "string"}, "minItems": 1, "type": "array"},
            "decisions": {"items": {"minLength": 1, "type": "string"}, "minItems": 1, "type": "array"},
            "evidence": {"items": {"minLength": 1, "type": "string"}, "minItems": 1, "type": "array"},
            "next_action": {"minLength": 1, "type": "string"},
            "protocol_version": {"minLength": 1, "type": "string"},
            "schema": {"const": "project-continuity.checkpoint.v1"},
            "task_id": {"pattern": "^[A-Z][A-Z0-9]*-[0-9]{4}$", "type": "string"},
            "timestamp": {"minLength": 1, "type": "string"},
        },
        "required": [
            "schema",
            "protocol_version",
            "task_id",
            "timestamp",
            "agent",
            "completed",
            "evidence",
            "decisions",
            "changed",
            "blocked",
            "next_action",
        ],
        "title": "Checkpoint metadata v1",
        "type": "object",
    },
    "checkpoint-operation": {
        "$id": "https://project-continuity.dev/schema/v1/checkpoint-operation.schema.json",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "additionalProperties": False,
        "properties": {
            "payload_sha256": {"pattern": "^[a-f0-9]{64}$", "type": "string"},
            "request_id": {"pattern": "^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$", "type": "string"},
            "schema": {"const": "project-continuity.checkpoint-operation.v1"},
            "task_id": {"pattern": "^[A-Z][A-Z0-9]*-[0-9]{4}$", "type": "string"},
        },
        "required": ["schema", "task_id", "request_id", "payload_sha256"],
        "title": "Checkpoint operation identity v1",
        "type": "object",
    },
    "context-pack": {
        "$id": "https://project-continuity.dev/schema/v1/context-pack.schema.json",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "additionalProperties": False,
        "properties": {
            "commit": {"minLength": 1, "type": "string"},
            "generated_at": {"minLength": 1, "type": "string"},
            "protocol_version": {"minLength": 1, "type": "string"},
            "ref": {"minLength": 1, "type": "string"},
            "repository": {"minLength": 1, "type": "string"},
            "schema": {"const": "project-continuity.context-pack.v1"},
            "sources": {"items": {"minLength": 1, "type": "string"}, "minItems": 3, "type": "array"},
            "task_id": {"pattern": "^[A-Z][A-Z0-9]*-[0-9]{4}$", "type": "string"},
        },
        "required": ["schema", "protocol_version", "repository", "ref", "commit", "task_id", "generated_at", "sources"],
        "title": "Context pack metadata v1",
        "type": "object",
    },
    "documents": {
        "$id": "https://project-continuity.dev/schema/v1/documents.schema.json",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "additionalProperties": False,
        "properties": {
            "documents": {
                "items": {
                    "additionalProperties": False,
                    "properties": {
                        "id": {"pattern": "^[a-z0-9][a-z0-9._-]*$", "type": "string"},
                        "keywords": {"items": {"minLength": 1, "type": "string"}, "type": "array"},
                        "path": {"minLength": 1, "type": "string"},
                        "related": {"items": {"minLength": 1, "type": "string"}, "type": "array"},
                        "reviewed_commit": {"pattern": "^(uncommitted|[a-f0-9]{40,64})$", "type": "string"},
                        "reviewed_sha256": {"pattern": "^[a-f0-9]{64}$", "type": "string"},
                        "summary": {"minLength": 1, "type": "string"},
                        "tasks": {"items": {"pattern": "^[A-Z][A-Z0-9]*-[0-9]{4}$", "type": "string"}, "type": "array"},
                        "title": {"minLength": 1, "type": "string"},
                    },
                    "required": [
                        "id",
                        "path",
                        "title",
                        "summary",
                        "keywords",
                        "related",
                        "tasks",
                        "reviewed_commit",
                        "reviewed_sha256",
                    ],
                    "type": "object",
                },
                "type": "array",
            },
            "schema": {"const": "project-continuity.documents.v1"},
        },
        "required": ["schema", "documents"],
        "title": "Continuity document inventory v1",
        "type": "object",
    },
}


_config_properties = BUILTIN_SCHEMAS["config"].get("properties")
if isinstance(_config_properties, dict):
    _config_properties["workspace"] = WORKSPACE_SCHEMA

BUILTIN_SCHEMAS["recovery"] = {
    "$id": "https://project-continuity.dev/schema/v1/recovery.schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "additionalProperties": False,
    "properties": {
        "schema": {"const": "project-continuity.recovery.v1"},
        "protocol_version": {"minLength": 1, "type": "string"},
        "project_id": {"minLength": 1, "type": "string"},
        "task_id": {"pattern": "^[A-Z][A-Z0-9]*-[0-9]{4}$", "type": "string"},
        "canonical_root": {"minLength": 1, "type": "string"},
        "canonical_task": {"minLength": 1, "type": "string"},
        "repository": {"minLength": 1, "type": "string"},
        "ref": {"minLength": 1, "type": "string"},
        "commit": {"minLength": 1, "type": "string"},
        "recorded_at": {"minLength": 1, "type": "string"},
        "status": {"enum": ["pending-reconciliation", "reconciled"], "type": "string"},
        "checkpoint": {"type": "object"},
        "reconciled_at": {"minLength": 1, "type": "string"},
    },
    "required": [
        "schema",
        "protocol_version",
        "project_id",
        "task_id",
        "canonical_root",
        "canonical_task",
        "repository",
        "ref",
        "commit",
        "recorded_at",
        "status",
        "checkpoint",
    ],
    "title": "Continuity recovery receipt v1",
    "type": "object",
}


class ContinuityError(Exception):
    pass


class CanonicalUnavailable(ContinuityError):
    """Canonical continuity state cannot be read or written right now."""


@dataclass(frozen=True)
class GitWorktree:
    path: str
    branch: str | None
    locked: bool = False


def _json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def marker(kind: str, metadata: dict[str, Any]) -> str:
    return f"<!-- continuity:{kind} {_json(metadata)} -->"


def extract_marker(text: str, kind: str) -> dict[str, Any] | None:
    for line in text.splitlines():
        match = MARKER_RE.fullmatch(line.strip())
        if match and match.group("kind") == kind:
            try:
                value = json.loads(match.group("payload"))
            except json.JSONDecodeError as exc:
                raise ContinuityError(f"invalid JSON metadata for {kind}: {exc}") from exc
            if not isinstance(value, dict):
                raise ContinuityError(f"{kind} metadata must be a JSON object")
            return value
    return None


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContinuityError(f"missing file: {path}") from exc
    except OSError as exc:
        raise CanonicalUnavailable(f"file unavailable: {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ContinuityError(f"invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContinuityError(f"JSON object required: {path}")
    return value


def load_config(root: Path) -> dict[str, Any]:
    return load_json(root / ".continuity" / "config.json")


def schema_dir(root: Path) -> Path:
    return root / "schemas" / "v1"


def load_schema(root: Path, kind: str) -> dict[str, Any]:
    path = schema_dir(root) / SCHEMA_FILES[kind]
    if path.exists():
        schema = load_json(path)
        if kind == "config":
            # Existing v1 repositories can retain their checked-in schema and
            # still adopt this optional, backward-compatible policy field.
            properties = schema.setdefault("properties", {})
            if isinstance(properties, dict) and "workspace" not in properties:
                properties["workspace"] = WORKSPACE_SCHEMA
        return schema
    return BUILTIN_SCHEMAS[kind]


def validate_schema(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected = schema.get("type")
    if expected:
        types = [expected] if isinstance(expected, str) else expected
        type_map = {
            "object": dict,
            "array": list,
            "string": str,
            "boolean": bool,
            "integer": int,
            "null": type(None),
        }
        if not any(
            isinstance(instance, type_map[t]) and not (t == "integer" and isinstance(instance, bool)) for t in types
        ):
            errors.append(f"{path}: expected type {types}, got {type(instance).__name__}")
            return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']!r}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: string shorter than {schema['minLength']}")
        if "pattern" in schema and re.fullmatch(schema["pattern"], instance) is None:
            errors.append(f"{path}: does not match pattern {schema['pattern']!r}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: requires at least {schema['minItems']} items")
        item_schema = schema.get("items")
        if item_schema:
            for index, value in enumerate(instance):
                errors.extend(validate_schema(value, item_schema, f"{path}[{index}]"))

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required key {key!r}")
        props = schema.get("properties", {})
        for key, value in instance.items():
            if key in props:
                errors.extend(validate_schema(value, props[key], f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected key {key!r}")
    return errors


def write_file_no_overwrite(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing == content:
            return "unchanged"
        raise ContinuityError(f"refusing to overwrite existing content: {path}")
    path.write_text(content, encoding="utf-8")
    return "created"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ContinuityError("slug must contain at least one alphanumeric character")
    return slug


def project_template(name: str) -> str:
    meta = {
        "schema": "project-continuity.project.v1",
        "protocol_version": PROTOCOL_VERSION,
        "id": slugify(name),
        "title": name,
    }
    return (
        f"# {name} — Project Contract\n\n"
        f"{marker('project', meta)}\n\n"
        f"{GITHUB_PROGRESSION_GUIDANCE}\n\n"
        "## Main goal\n\nDescribe the durable project goal.\n\n"
        "## Why\n\nExplain why the project exists.\n\n"
        "## Scope\n\nDescribe what is in scope.\n\n"
        "## Non-goals\n\nDescribe what is explicitly out of scope.\n\n"
        "## Definition of success\n\nDescribe durable success criteria.\n"
    )


def current_template(prefix: str) -> str:
    meta = {
        "schema": "project-continuity.current.v1",
        "protocol_version": PROTOCOL_VERSION,
        "active_task": None,
        "active_task_file": None,
    }
    return (
        "# Current Repository Checkpoint\n\n"
        f"{marker('current', meta)}\n\n"
        "This is an as-of projection; live GitHub issues own progression. Link the owning leaf, parent ancestry and dependencies for active work.\n\n"
        "## Program state\n\nPhase: bootstrap.\n\n"
        "## Completed\n\n- continuity protocol initialized.\n\n"
        "## Active\n\n- none.\n\n"
        "## Queued\n\n- create the first bounded task.\n\n"
        "## Blockers\n\nNone known.\n\n"
        "## Next atomic action\n\n"
        f"Create or identify the GitHub issue, record its {prefix} task/branch identity, then create the task projection with `continuity task new --issue <URL>`.\n"
    )


def workspace_policy_text(workspace_mode: str) -> str:
    if workspace_mode == "single-checkout":
        return (
            "## Workspace mode: single checkout\n\n"
            "Use the main checkout for sequential work. Do not create clones or linked worktrees. "
            "This is the strictest and simplest option when parallel isolation is not needed.\n\n"
        )
    return (
        "## Workspace mode: managed task worktrees\n\n"
        "The Git repository, remote, and task history stay canonical; the main checkout remains the permanent home base. "
        "Use it for sequential work. Create a linked worktree only when parallel work or isolation is actually useful, "
        "at `<canonical-root>/pcm/worktree/<TASK-ID>`. Use one per independent active task, not one per session or agent; "
        "a new session continuing that task resumes the same tree. Do not create sibling clones or arbitrary worktree paths.\n\n"
        "Before creating a tree, PCM checks Git's registered worktrees and the private per-device workspace registry. "
        "Register existing checkouts on other drives with `continuity workspace register --root <checkout>`. One clean, unlocked match for the same remote/task/ref is reused; a dirty, locked, conflicting, or ambiguous match stops before creation. PCM does not scan drives. Registry paths are local-only and must never be copied into issues, commits, PRs, or handoffs.\n\n"
        "After the task is pushed, required CI passes, its pull request is merged into the remote default branch, and its task record is complete, run `continuity worktree remove <TASK-ID>`. "
        "Removal verifies the GitHub PR, required checks, and merged commit; it refuses locked/pinned, dirty, untracked, unpublished, unmerged, or unverifiable work. For a short audit hold, record the reason, expected release date, private workspace ID, and unlock/remove next action in the completed task's checkpoint, then lock it with `git worktree lock --reason \"<reason; release YYYY-MM-DD>\" <path>`. The lock makes normal cleanup refuse the tree and is not a cleanup exemption. When the audit ends, return to the permanent checkout, run `git worktree unlock <path>`, then `continuity worktree remove <TASK-ID>` to complete verified cleanup. For other Git hosts without a verified CI adapter, it leaves the tree in place. Never force-remove it. Keep unfinished or user-modified work for recovery.\n\n"
        "Linked worktrees share the repository's Git object store; they are not full repository clones. Reuse package-manager download/build caches and installed runtimes where supported. "
        "Keep mutable `node_modules` and `.venv` environments separate when lockfiles or interpreters differ; store dependency changes in tracked manifests/lockfiles or patch files, not as hidden edits inside an installed environment. "
        "Remove the task worktree after verified merge and completion.\n\n"
    )


def handoff_template(workspace_mode: str) -> str:
    return (
        "# Current Handoff\n\n"
        "Start from repository state, not prior chat history.\n\n"
        "## Read order\n\n"
        "1. `PROJECT.md`\n"
        "2. `AGENTS.md` when present\n"
        "3. `checkpoints/CURRENT.md`\n"
        "4. the active task named by CURRENT\n"
        "5. the minimum relevant specification/design document\n\n"
        "Before editing a GitHub task, run `continuity issue verify <TASK-ID>` and confirm the live issue is open and matches the task.\n\n"
        "## Authority\n\nGitHub Issues are authoritative for task scope, priority, ownership, dependencies, acceptance, and lifecycle; "
        "the linked task file is a compact working cache. Merged default-branch history is authoritative for accepted code. "
        "PR checks and merge evidence are authoritative for delivery. Chat and context packs are derived. Before resuming, "
        "verify the linked issue and read current GitHub status.\n\n"
        + GITHUB_ISSUE_LIFECYCLE_GUIDANCE
        + "\n\n"
        + GITHUB_PROGRESSION_GUIDANCE
        + "\n\n"
        + workspace_policy_text(workspace_mode)
        + "## Finding earlier project documents\n\n"
        "When `.continuity/documents.json` is present, it is the machine-readable inventory and `docs/CONTINUITY_INDEX.md` is its generated human view. Every fresh session or task takeover/resumption must consult the inventory before choosing its next action, not only before writing a document: run `git fetch origin`, then use `continuity docs find \"<issue title and task-objective terms>\" --task <TASK-ID>` and read matching records and their declared neighbors. The search is deterministic metadata search, not semantic whole-repository search. `continuity validate` checks the generated view; use `continuity docs render` to refresh its freshness labels after source edits. A `NEEDS_REVIEW` result preserves historical evidence but says not to rely on it without checking the current file.\n\n"
        + "## Continuity records\n\n"
        f"{CONTINUITY_RECORDS_POLICY_MARKER}\n\n"
        "Write continuity issues, updates, pull requests, and project-state documents so a fresh reader can understand the problem, human outcome, scope, evidence, and next action. Cite external claims and link repository claims to a revision or CI result. Include reproduction detail only when needed to verify the claim. Keep PR openings skimmable; link long logs. Do not claim automatic tracker synchronization or chat capture unless implemented and tested.\n\n"
        "## Degraded continuity\n\n"
        "Execution safety and existing authorization outrank continuity bookkeeping. If a canonical continuity file is temporarily unavailable, do not stop safe work, repair storage just to force a checkpoint, or ask again for an already-authorized host/worktree. Use an authorized alternate checkout and run `continuity checkpoint <TASK-ID> --root <canonical-root> --recovery-root <alternate-root> ...` to write a JSON recovery receipt under `.continuity/recovery/`; do not create an ad-hoc Markdown checkpoint or replace the alternate task file. Reconcile it into the canonical task with `continuity recovery reconcile --root <canonical-root> --file <receipt>` when writable. The repository/task lineage is authoritative; a physical path is not.\n\n"
        "Normal checkpointing is a delivery operation, not a local note: commit the product change first, then run `continuity checkpoint`. The command prints a `REQUEST_ID`, commits the canonical checkpoint and synchronously pushes the task branch to `origin`; if interrupted, rerun with the same `--request-id` to avoid a duplicate (changed payload with the same ID is rejected). Open or update a PR after pushing. GitHub CI and auto-merge then run asynchronously and wait for required reviews/checks and any merge queue. Confirm the merge before marking the task complete or removing its worktree.\n"
    )


def agents_template(workspace_mode: str) -> str:
    return (
        "# Agent Operating Contract\n\n"
        "## Start\n\n"
        "Read PROJECT → CURRENT → active TASK → minimum relevant spec before editing.\n\n"
        "For GitHub repositories, verify the live linked issue with `continuity issue verify <TASK-ID>` before resuming; the issue owns task scope and lifecycle, merged default-branch history owns accepted code, and PR checks/merge records own delivery. Resolve discrepancies from the issue before editing.\n\n"
        + GITHUB_ISSUE_LIFECYCLE_GUIDANCE
        + "\n\n"
        + GITHUB_PROGRESSION_GUIDANCE
        + "\n\n"
        "Store checkout roots only in the private per-device registry with `continuity workspace register --root <checkout>`. Before creating a worktree, inspect registered roots and Git's worktree list. Reuse one clean, unlocked matching task branch; stop on dirty, locked, conflicting, or ambiguous matches. Do not scan drives or copy absolute paths into shared handoffs.\n\n"
        "## Scope\n\n"
        "Work only inside the active bounded task. Split or revise the task before materially expanding scope.\n\n"
        + workspace_policy_text(workspace_mode)
        + "## Continuity records\n\n"
        f"{CONTINUITY_RECORDS_POLICY_MARKER}\n\n"
        "For continuity issues, progress updates, pull requests, and project-state documents, explain the human problem and outcome first, then scope, status, linked evidence, and one next action. Cite external claims and tie repository claims to a revision, issue, PR, or CI result. Record reproduction details only when needed. Keep PR openings skimmable; link long logs. Preserve existing project ownership outside continuity. Do not claim automatic tracker synchronization or chat capture unless implemented and tested.\n\n"
        + "## Checkpoint\n\n"
        "Before stopping after meaningful work, append completed work, exact evidence, decisions, changed paths, blockers, and one next atomic action.\n\n"
        "If canonical continuity state is temporarily unavailable, treat that as degraded continuity rather than an execution blocker: keep safe authorized work moving, use an already-authorized alternate checkout/host, and run `continuity checkpoint <TASK-ID> --root <canonical-root> --recovery-root <alternate-root> --agent <name> --completed <work> --evidence <result> --next <next-action>` to write the JSON recovery receipt under `.continuity/recovery/`. Do not write an ad-hoc checkpoint under `checkpoints/`, replace the alternate task file, treat a physical worktree as project identity, repair storage merely to write a checkpoint, or request redundant permission. Reconcile later with `continuity recovery reconcile --root <canonical-root> --file <receipt>`.\n\n"
        "For a normal checkpoint, commit the product change first and then run `continuity checkpoint`; it prints a stable `REQUEST_ID`, commits, and synchronously pushes the checkpoint to the task branch. If interrupted, retry with the same `--request-id`; the same payload is a no-op and a different payload is rejected. Open or update a PR after pushing. GitHub CI and auto-merge then run asynchronously, gated by required reviews/checks and any merge queue. Confirm the merge before marking complete or removing the worktree.\n\n"
        "If `.continuity/documents.json` exists, every fresh session or task takeover/resumption must consult it before deciding the next action, not only before writing documentation. Run `git fetch origin`, then `continuity docs find \"<issue title and task-objective terms>\" --task <TASK-ID>`; read the returned matches and declared neighbors before deciding that prior work is missing or creating/replacing a document. Investigate `NEEDS_REVIEW`/`REMOTE_UNKNOWN` before relying on old evidence. The generated human view is checked by `continuity validate`.\n"
    )


def github_issue_template() -> str:
    return """---
name: Continuity task
about: Record an actionable continuity outcome with clear evidence
title: "Continuity: [human outcome]"
labels: ""
assignees: ""
---

## Problem and consequence

Who or what is affected, and what becomes harder, unsafe, or impossible?

## Desired result

What observable result would resolve the problem?

## Scope and boundaries

What is included, what is not, and what dependencies or uncertainty matter?

## How we will know

List observable acceptance checks proportionate to the outcome.

## Evidence and sources

Link relevant repository state at a revision. Cite direct sources for external factual claims.

## Reproduction (only when needed)

Record the starting revision, relevant inputs/configuration, runtime, exact command or prompt, observed result, and limitations.

## Continuity links

- Leaf owning issue, parent ancestry and dependencies (or explicitly none):
- Task ID, primary writer, branch and linked repository projection:
- Related issues or PRs:
- Current owner and next action:

This template records context; it does not automatically synchronize this issue with repository tasks, pull requests, or checkpoints.
""" + "\n" + GITHUB_PROGRESSION_GUIDANCE + "\n"


def github_pr_template() -> str:
    return f"""{GITHUB_ISSUE_LIFECYCLE_GUIDANCE}

## Human outcome

What changed for the person or project?

## Change and scope

Summarize the change and important boundaries.

## Verification

List focused commands and observed results. Link the CI run; do not paste full logs.

## Evidence and provenance (when relevant)

- Task ID and leaf owning issue, parent ancestry and dependencies (or explicitly none):
- Starting revision, inputs, or source:
- Direct citations or reproducible artifact:
- What remains unknown:

<details>
<summary>Reproduction details or extended technical notes (only when useful)</summary>

Add exact commands, configuration, inputs, results, and limitations here when they are needed to verify the claim.

</details>

## Continuity closeout

- Docs/task/checkpoint/catalog/index synchronized before push; as-of status and source issue revision:
- Request ID / exact pushed SHA / leaf receipt and parent update:
- Required CI on exact candidate / mandatory auto-merge / verified merge and live issue status:
- One next action or explicit completion:

This template records context; it does not automatically synchronize this pull request with issues or checkpoints.
""" + "\n" + GITHUB_PROGRESSION_GUIDANCE + "\n"


def readme_template(name: str) -> str:
    return (
        f"# {name}\n\n"
        "This repository uses Project Continuity Protocol.\n\n"
        "Point a fresh agent/session to `HANDOFF.md`; it contains the cold-start read order.\n"
        f"\n{GITHUB_PROGRESSION_GUIDANCE}\n"
    )


def init_repo(
    root: Path,
    profile: str,
    name: str,
    prefix: str,
    github_templates: bool = False,
    workspace_mode: str | None = None,
    github_authority: bool | None = None,
) -> list[str]:
    if profile not in {"minimal", "software"}:
        raise ContinuityError(f"unsupported profile: {profile}")
    prefix = prefix.upper()
    if re.fullmatch(r"[A-Z][A-Z0-9]*", prefix) is None:
        raise ContinuityError("task prefix must match [A-Z][A-Z0-9]*")
    workspace_mode = workspace_mode or "managed-worktrees"
    if workspace_mode not in WORKSPACE_MODES:
        raise ContinuityError(f"unsupported workspace mode: {workspace_mode}")
    remote = git_value(root, ["remote", "get-url", "origin"], fallback="")
    github_authority = github_repository(remote) is not None if github_authority is None else github_authority
    config = {
        "schema": CONFIG_SCHEMA,
        "protocol": "project-continuity",
        "protocol_version": PROTOCOL_VERSION,
        "profile": profile,
        "task_prefix": prefix,
        "canonical": {
            "project": "PROJECT.md",
            "current": "checkpoints/CURRENT.md",
            "tasks": "tasks",
        },
        "schema_dir": "schemas/v1",
        "trackers": {"github": github_authority, "beads": False},
        "workspace": {"mode": workspace_mode},
    }

    planned = {
        ".continuity/config.json": json.dumps(config, indent=2, sort_keys=True) + "\n",
        "PROJECT.md": project_template(name),
        "checkpoints/CURRENT.md": current_template(prefix),
        "HANDOFF.md": handoff_template(workspace_mode),
    }
    for kind, filename in SCHEMA_FILES.items():
        planned[f"schemas/v1/{filename}"] = json.dumps(BUILTIN_SCHEMAS[kind], indent=2, sort_keys=True) + "\n"
    if profile == "software":
        planned["AGENTS.md"] = agents_template(workspace_mode)
        planned["README.md"] = readme_template(name)
    if github_templates:
        planned[".github/ISSUE_TEMPLATE/task.md"] = github_issue_template()
        planned[".github/pull_request_template.md"] = github_pr_template()

    conflicts = [
        rel
        for rel, content in planned.items()
        if (root / rel).exists() and (root / rel).read_text(encoding="utf-8") != content
    ]
    if conflicts:
        joined = ", ".join(sorted(conflicts))
        raise ContinuityError(f"initialization conflicts; no files written: {joined}")

    results = []
    for rel, content in sorted(planned.items()):
        state = write_file_no_overwrite(root / rel, content)
        results.append(f"{state}: {rel}")
    (root / "tasks").mkdir(parents=True, exist_ok=True)
    (root / ".continuity" / "packs").mkdir(parents=True, exist_ok=True)
    return results


def task_files(root: Path, config: dict[str, Any]) -> list[Path]:
    directory = root / config["canonical"]["tasks"]
    return sorted(directory.glob("TASK-*.md")) if directory.exists() else []


def task_metadata(path: Path) -> dict[str, Any] | None:
    try:
        return extract_marker(path.read_text(encoding="utf-8"), "task")
    except OSError as exc:
        raise CanonicalUnavailable(f"canonical task unavailable: {path}: {exc}") from exc


def find_task(root: Path, config: dict[str, Any], task_id: str) -> Path:
    for path in task_files(root, config):
        if path.name.startswith(f"TASK-{task_id}-") or path.name == f"TASK-{task_id}.md":
            return path
        meta = task_metadata(path)
        if meta and meta.get("id") == task_id:
            return path
    raise ContinuityError(f"task not found: {task_id}")


def next_task_id(root: Path, config: dict[str, Any]) -> str:
    prefix = config["task_prefix"]
    highest = 0
    for path in task_files(root, config):
        match = TASK_FILE_RE.match(path.name)
        if match and match.group("prefix") == prefix:
            highest = max(highest, int(match.group("num")))
    return f"{prefix}-{highest + 1:04d}"


def task_new(root: Path, slug: str, goal: str, why: str, owner: str, priority: str, issue_url: str | None = None) -> Path:
    config = load_config(root)
    if config.get("trackers", {}).get("github") and not issue_url:
        raise ContinuityError("GitHub-authoritative repositories require --issue URL when creating a task")
    if issue_url:
        issue_repo, _ = validate_github_issue_url(issue_url)
        origin = github_repository(git_value(root, ["remote", "get-url", "origin"], fallback=""))
        if origin and origin.casefold() != issue_repo.casefold():
            raise ContinuityError(f"issue belongs to {issue_repo}, but this checkout is {origin}")
    task_id = next_task_id(root, config)
    slug = slugify(slug)
    tasks_dir: str = config["canonical"]["tasks"]
    path = root / tasks_dir / f"TASK-{task_id}-{slug}.md"
    meta = {
        "schema": "project-continuity.task.v1",
        "protocol_version": config["protocol_version"],
        "id": task_id,
        **({"issue_url": issue_url} if issue_url else {}),
        "status": "active",
        "owner": owner,
        "priority": priority,
        "depends_on": [],
        "goal": goal,
        "why": why,
        "acceptance": ["replace this with observable, task-specific acceptance checks"],
        "next_action": "define scope and observable acceptance checks, then begin bounded work",
    }
    content = (
        f"# TASK-{task_id} — {slug.replace('-', ' ').title()}\n\n"
        f"{marker('task', meta)}\n\n"
        f"- Status: active\n- Owner: {owner}\n- Priority: {priority}\n- Depends on: none\n\n"
        f"## Goal\n\n{goal}\n\n## Why\n\n{why}\n\n"
        "## Allowed files\n\n- define bounded paths before implementation.\n\n"
        "## Human outcome\n\nDescribe what becomes easier, safer, clearer, or possible when this task is complete.\n\n"
        "## Scope and boundaries\n\n- In scope:\n- Out of scope:\n- Dependencies/uncertainty:\n\n"
        "## Acceptance criteria\n\n- [ ] state observable, task-specific outcomes.\n\n"
        "## Evidence and sources\n\nLink repository state at a revision and cite external factual claims directly. Record commands and results for claims that need verification.\n\n"
        "## Reproduction details (only when needed)\n\nStarting revision, material inputs/configuration, runtime, exact command or prompt, observed result, and limitations.\n\n"
        "## Related records\n\n- Required leaf owning issue, parent ancestry and dependencies (or explicitly none):\n- Primary writer / branch / source issue revision / as-of status:\n- Related PR/CI evidence and push receipt (request ID / SHA):\n\n"
        "## Checkpoint log\n\n"
        "No checkpoints yet.\n\n"
        "## Handoff\n\n"
        "Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.\n"
    )
    write_file_no_overwrite(path, content)
    return path


def validate_checkpoint_structure(root: Path, task_path: Path, text: str) -> list[str]:
    errors: list[str] = []
    request_ids: set[str] = set()
    if "## Checkpoint log" not in text:
        return [f"{task_path}: missing '## Checkpoint log'"]
    log = text.split("## Checkpoint log", 1)[1]
    if "## Handoff" in log:
        log = log.split("## Handoff", 1)[0]
    entries = []
    current: list[str] = []
    for line in log.splitlines():
        if CHECKPOINT_HEADING_RE.match(line):
            if current:
                entries.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        entries.append(current)
    for index, entry in enumerate(entries, 1):
        body = "\n".join(entry)
        meta = extract_marker(body, "checkpoint")
        required_sections = (
            SECTION_NAMES
            if meta is not None
            else ("Completed:", "Evidence:", "Decisions:", "Blocked/uncertain:", "Next:")
        )
        missing = [name for name in required_sections if name not in body]
        if missing:
            errors.append(f"{task_path}: checkpoint {index} missing sections: {', '.join(missing)}")
        if meta is not None:
            for err in validate_schema(meta, load_schema(root, "checkpoint")):
                errors.append(f"{task_path}: checkpoint {index}: {err}")
        operation = extract_marker(body, "checkpoint-operation")
        if operation is not None:
            for err in validate_schema(operation, load_schema(root, "checkpoint-operation")):
                errors.append(f"{task_path}: checkpoint {index} operation: {err}")
            request_id = operation.get("request_id")
            if isinstance(request_id, str):
                if request_id in request_ids:
                    errors.append(f"{task_path}: duplicate checkpoint request ID: {request_id}")
                request_ids.add(request_id)
            if meta is None:
                errors.append(f"{task_path}: checkpoint {index} has an operation ID but no checkpoint metadata")
            else:
                if operation.get("task_id") != meta.get("task_id"):
                    errors.append(f"{task_path}: checkpoint {index} operation task ID does not match checkpoint")
                if operation.get("payload_sha256") != checkpoint_payload_sha256(meta):
                    errors.append(f"{task_path}: checkpoint {index} payload digest does not match checkpoint content")
    return errors


DOCUMENT_CATALOG_PATH = ".continuity/documents.json"
DOCUMENT_INDEX_PATH = "docs/CONTINUITY_INDEX.md"


def document_path(root: Path, value: str) -> Path:
    if "\\" in value or "\n" in value or "\r" in value:
        raise ContinuityError(f"document paths must use single-line repository-relative forward slashes: {value}")
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ContinuityError(f"document path must stay inside the repository: {value}")
    normalized = relative.as_posix()
    if normalized != value:
        raise ContinuityError(f"document path must be normalized and repository-relative: {value}")
    if normalized in {DOCUMENT_CATALOG_PATH, DOCUMENT_INDEX_PATH}:
        raise ContinuityError(f"the inventory and generated view cannot index themselves: {value}")
    resolved_root = root.resolve()
    candidate = resolved_root / Path(*relative.parts)
    if candidate.is_symlink():
        raise ContinuityError(f"indexed document paths cannot be symlinks: {value}")
    resolved = candidate.resolve()
    if not resolved.is_relative_to(resolved_root):
        raise ContinuityError(f"document path escapes the repository through a symlink: {value}")
    return resolved


def managed_output_path(root: Path, rel: str) -> Path:
    resolved_root = root.resolve()
    candidate = resolved_root / Path(*PurePosixPath(rel).parts)
    resolved = candidate.resolve()
    if not resolved.is_relative_to(resolved_root):
        raise ContinuityError(f"managed document output escapes the repository: {rel}")
    return candidate


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_document_bytes(value: bytes) -> str:
    try:
        text = value.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContinuityError("indexed documents must be UTF-8 text") from exc
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    return sha256_bytes(normalized)


def document_sha256(root: Path, record: dict[str, Any]) -> str | None:
    try:
        return sha256_document_bytes(document_path(root, record["path"]).read_bytes())
    except (ContinuityError, OSError, KeyError, TypeError):
        return None


def document_review_commit(root: Path, rel_path: str, source: Path) -> str:
    head = git_value(root, ["rev-parse", "HEAD"], "uncommitted")
    if head == "uncommitted":
        return "uncommitted"
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "show", f"{head}:{rel_path}"],
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "uncommitted"
    return head if sha256_document_bytes(result.stdout) == sha256_document_bytes(source.read_bytes()) else "uncommitted"


def remote_tracking_head(root: Path) -> tuple[str, str] | None:
    ref = git_value(root, ["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"], "")
    if not ref:
        return None
    commit = git_value(root, ["rev-parse", ref], "")
    return (ref, commit) if commit else None


def remote_document_hashes(root: Path, remote_ref: str, paths: list[str]) -> dict[str, str | None] | None:
    unique_paths = list(dict.fromkeys(paths))
    if not unique_paths:
        return {}
    requests = "".join(f"{remote_ref}:{path}\n" for path in unique_paths).encode("utf-8")
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "cat-file", "--batch"],
            input=requests,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None

    snapshots: dict[str, str | None] = {}
    content = result.stdout
    cursor = 0
    for rel_path in unique_paths:
        header_end = content.find(b"\n", cursor)
        if header_end < 0:
            return None
        header = content[cursor:header_end].split()
        cursor = header_end + 1
        if len(header) == 2 and header[1] == b"missing":
            snapshots[rel_path] = None
            continue
        if len(header) != 3 or header[1] != b"blob":
            return None
        try:
            size = int(header[2])
        except ValueError:
            return None
        end = cursor + size
        if end >= len(content) or content[end : end + 1] != b"\n":
            return None
        try:
            snapshots[rel_path] = sha256_document_bytes(content[cursor:end])
        except ContinuityError:
            snapshots[rel_path] = None
        cursor = end + 1
    if cursor != len(content):
        return None
    return snapshots


def document_freshness(
    root: Path,
    record: dict[str, Any],
    include_remote: bool = False,
    remote_hashes: dict[str, str | None] | None = None,
) -> tuple[str, str | None]:
    current = document_sha256(root, record)
    if current is None:
        return "MISSING", None
    reviewed = record.get("reviewed_sha256")
    if current != reviewed:
        return "NEEDS_REVIEW", current
    if include_remote:
        if remote_hashes is None or record["path"] not in remote_hashes:
            return "REMOTE_UNKNOWN", current
        remote_hash = remote_hashes[record["path"]]
        if remote_hash is None:
            return "NEEDS_REVIEW", None
        if remote_hash != reviewed:
            return "NEEDS_REVIEW", remote_hash
    return "CURRENT", current


def load_document_catalog(root: Path) -> dict[str, Any]:
    path = managed_output_path(root, DOCUMENT_CATALOG_PATH)
    catalog = load_json(path)
    errors = validate_schema(catalog, load_schema(root, "documents"))
    if errors:
        raise ContinuityError(f"{path}: " + "; ".join(errors))
    return catalog


def validate_document_catalog_data(
    root: Path,
    catalog: dict[str, Any],
    known_task_ids: set[str],
    verify_source_paths: set[str] | None = None,
) -> list[str]:
    errors = [f"{root / DOCUMENT_CATALOG_PATH}: {e}" for e in validate_schema(catalog, load_schema(root, "documents"))]
    if errors:
        return errors
    documents = catalog["documents"]
    ids: set[str] = set()
    paths: dict[str, str] = {}
    for record in documents:
        doc_id = record["id"]
        rel = record["path"]
        for field in ("keywords", "related", "tasks"):
            values = record[field]
            if len(values) != len(set(values)):
                errors.append(f"{root / DOCUMENT_CATALOG_PATH}: document {doc_id} has duplicate {field}")
        if doc_id in ids:
            errors.append(f"{root / DOCUMENT_CATALOG_PATH}: duplicate document ID: {doc_id}")
        ids.add(doc_id)
        if rel in paths:
            errors.append(f"{root / DOCUMENT_CATALOG_PATH}: document path is assigned to both {paths[rel]} and {doc_id}: {rel}")
        paths[rel] = doc_id
        verify_source = verify_source_paths is None or rel in verify_source_paths
        if verify_source:
            try:
                source = document_path(root, rel)
            except ContinuityError as exc:
                errors.append(str(exc))
                continue
            if not source.is_file():
                errors.append(f"{root / DOCUMENT_CATALOG_PATH}: document source is missing: {rel}")
        else:
            relative_path = PurePosixPath(rel)
            if (
                relative_path.is_absolute()
                or ".." in relative_path.parts
                or not relative_path.parts
                or relative_path.as_posix() != rel
                or rel in {DOCUMENT_CATALOG_PATH, DOCUMENT_INDEX_PATH}
            ):
                errors.append(f"{root / DOCUMENT_CATALOG_PATH}: invalid repository-relative document path: {rel}")
        for task_id in record["tasks"]:
            if task_id not in known_task_ids:
                errors.append(f"{root / DOCUMENT_CATALOG_PATH}: document {doc_id} references unknown task {task_id}")
    for record in documents:
        for related_id in record["related"]:
            if related_id not in ids:
                errors.append(f"{root / DOCUMENT_CATALOG_PATH}: document {record['id']} references unknown neighbor {related_id}")
            if related_id == record["id"]:
                errors.append(f"{root / DOCUMENT_CATALOG_PATH}: document cannot be related to itself: {related_id}")
    return errors


def _plain_text(value: str) -> str:
    return " ".join(value.replace("|", "\\|").split())


def render_document_index(root: Path, catalog: dict[str, Any]) -> str:
    catalog_digest = hashlib.sha256(_json(catalog).encode("utf-8")).hexdigest()
    lines = [
        "# Continuity Document Index",
        "",
        marker(
            "documents-index",
            {"schema": "project-continuity.documents-index.v1", "catalog_sha256": catalog_digest},
        ),
        "",
        f"> Generated from `{DOCUMENT_CATALOG_PATH}`. Edit the JSON inventory, then run `continuity docs render`; do not edit this view directly.",
        "> Freshness below compares local file bytes; after `git fetch origin`, use `continuity docs find` for cached remote freshness.",
        "",
    ]
    documents = sorted(catalog.get("documents", []), key=lambda record: record.get("id", ""))
    if not documents:
        lines.extend(["No documents are registered yet.", ""])
    for record in documents:
        freshness, current_hash = document_freshness(root, record)
        lines.extend(
            [
                f"## {_plain_text(record['title'])} (`{record['id']}`)",
                "",
                f"- File: [`{record['path']}`](../{quote(record['path'], safe='/-._~')})",
                f"- Local content status: **{freshness}**",
                f"- Last reviewed at commit: `{record['reviewed_commit']}`",
                f"- Reviewed SHA-256: `{record['reviewed_sha256']}`",
                f"- Current SHA-256: `{current_hash or 'unavailable'}`",
                f"- Summary: {_plain_text(record['summary'])}",
                f"- Search terms: {', '.join(f'`{_plain_text(term)}`' for term in sorted(record['keywords'])) or 'none'}",
                f"- Neighboring records: {', '.join(f'`{item}`' for item in sorted(record['related'])) or 'none'}",
                f"- Task associations: {', '.join(f'`{item}`' for item in sorted(record['tasks'])) or 'none'}",
                "",
            ]
        )
    return "\n".join(lines)


def document_task_ids(root: Path, config: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for task_path in task_files(root, config):
        meta = task_metadata(task_path)
        if meta and isinstance(meta.get("id"), str):
            result.add(meta["id"])
    return result


def write_document_catalog(root: Path, catalog: dict[str, Any], known_task_ids: set[str]) -> None:
    errors = validate_document_catalog_data(root, catalog, known_task_ids)
    if errors:
        raise ContinuityError("document inventory is invalid: " + "; ".join(errors))
    normalized = {"schema": "project-continuity.documents.v1", "documents": sorted(catalog["documents"], key=lambda item: item["id"])}
    content = json.dumps(normalized, indent=2, sort_keys=True) + "\n"
    catalog_path = managed_output_path(root, DOCUMENT_CATALOG_PATH)
    view_path = managed_output_path(root, DOCUMENT_INDEX_PATH)
    try:
        catalog_path.parent.mkdir(parents=True, exist_ok=True)
        view_path.parent.mkdir(parents=True, exist_ok=True)
        catalog_path.write_text(content, encoding="utf-8")
        view_path.write_text(render_document_index(root, normalized), encoding="utf-8")
    except OSError as exc:
        raise ContinuityError(f"cannot update document inventory/view: {exc}") from exc


def initialize_document_catalog(root: Path) -> tuple[Path, Path]:
    catalog_path = managed_output_path(root, DOCUMENT_CATALOG_PATH)
    view_path = managed_output_path(root, DOCUMENT_INDEX_PATH)
    if not catalog_path.exists():
        if view_path.exists():
            raise ContinuityError(f"refusing to replace existing human document index without its inventory: {view_path}")
        catalog = {"schema": "project-continuity.documents.v1", "documents": []}
        write_document_catalog(root, catalog, document_task_ids(root, load_config(root)))
    else:
        catalog = load_document_catalog(root)
        write_document_catalog(root, catalog, document_task_ids(root, load_config(root)))
    return catalog_path, view_path


def upsert_document(
    root: Path,
    doc_id: str,
    rel_path: str,
    title: str,
    summary: str,
    keywords: list[str],
    related: list[str],
    tasks: list[str],
) -> dict[str, Any]:
    if re.fullmatch(r"[a-z0-9][a-z0-9._-]*", doc_id) is None:
        raise ContinuityError("document ID must use lowercase letters, digits, '.', '_' or '-' and start alphanumeric")
    source = document_path(root, rel_path)
    if not source.is_file():
        raise ContinuityError(f"document source does not exist: {rel_path}")
    catalog = load_document_catalog(root)
    records = catalog["documents"]
    existing = next((record for record in records if record["id"] == doc_id), None)
    if existing and existing["path"] != PurePosixPath(rel_path).as_posix():
        raise ContinuityError(f"document ID {doc_id!r} already owns path {existing['path']!r}; IDs cannot be reassigned")
    record = {
        "id": doc_id,
        "path": PurePosixPath(rel_path).as_posix(),
        "title": title,
        "summary": summary,
        "keywords": sorted(set(keywords)),
        "related": sorted(set(related)),
        "tasks": sorted(set(tasks)),
        "reviewed_commit": existing["reviewed_commit"] if existing else document_review_commit(root, rel_path, source),
        "reviewed_sha256": existing["reviewed_sha256"] if existing else sha256_document_bytes(source.read_bytes()),
    }
    updated = [item for item in records if item["id"] != doc_id] + [record]
    catalog["documents"] = updated
    config = load_config(root)
    write_document_catalog(root, catalog, document_task_ids(root, config))
    return {str(key): value for key, value in record.items()}


def refresh_document(root: Path, doc_id: str) -> dict[str, Any]:
    catalog = load_document_catalog(root)
    record = next((item for item in catalog["documents"] if item["id"] == doc_id), None)
    if record is None:
        raise ContinuityError(f"document ID not found: {doc_id}")
    source = document_path(root, record["path"])
    if not source.is_file():
        raise ContinuityError(f"document source does not exist: {record['path']}")
    record["reviewed_sha256"] = sha256_document_bytes(source.read_bytes())
    record["reviewed_commit"] = document_review_commit(root, record["path"], source)
    write_document_catalog(root, catalog, document_task_ids(root, load_config(root)))
    return {str(key): value for key, value in record.items()}


def document_neighbors(catalog: dict[str, Any], doc_id: str) -> list[dict[str, Any]]:
    records = catalog["documents"]
    by_id = {record["id"]: record for record in records}
    neighbor_ids = {
        record["id"]
        for record in records
        if doc_id in record["related"] or record["id"] in by_id[doc_id]["related"]
    }
    neighbor_ids.discard(doc_id)
    return [by_id[item] for item in sorted(neighbor_ids)]


def search_document_catalog(
    root: Path, catalog: dict[str, Any], query: str, task_id: str | None = None
) -> list[tuple[int, dict[str, Any]]]:
    terms = sorted(set(re.findall(r"[a-z0-9][a-z0-9._-]*", query.casefold())))
    if not terms:
        raise ContinuityError("document search query must contain letters or numbers")
    records = catalog["documents"]
    eligible_ids: set[str] | None = None
    if task_id:
        eligible_ids = {record["id"] for record in records if task_id in record["tasks"]}
        for direct_id in list(eligible_ids):
            eligible_ids.update(record["id"] for record in document_neighbors(catalog, direct_id))
    matches: list[tuple[int, dict[str, Any]]] = []
    for record in records:
        if eligible_ids is not None and record["id"] not in eligible_ids:
            continue
        fields = [
            (record["title"].casefold(), 5),
            (" ".join(record["keywords"]).casefold(), 4),
            (record["summary"].casefold(), 2),
            ((record["path"] + " " + record["id"]).casefold(), 1),
        ]
        score = sum(weight for term in terms for value, weight in fields if term in value)
        if score:
            matches.append((score, record))
    return sorted(matches, key=lambda item: (-item[0], item[1]["id"]))


def validate_document_catalog(root: Path, known_task_ids: set[str]) -> list[str]:
    try:
        catalog_path = managed_output_path(root, DOCUMENT_CATALOG_PATH)
        view_path = managed_output_path(root, DOCUMENT_INDEX_PATH)
    except ContinuityError as exc:
        return [str(exc)]
    if not catalog_path.exists():
        return [f"{view_path}: generated document index exists without {catalog_path}"] if view_path.exists() else []
    try:
        catalog = load_document_catalog(root)
    except ContinuityError as exc:
        return [str(exc)]
    errors = validate_document_catalog_data(root, catalog, known_task_ids)
    try:
        rendered = render_document_index(root, catalog)
        actual = view_path.read_text(encoding="utf-8")
    except OSError as exc:
        return errors + [f"generated document index unavailable: {view_path}: {exc}"]
    if actual != rendered:
        detail = "\n".join(
            list(
                difflib.unified_diff(
                    actual.splitlines(),
                    rendered.splitlines(),
                    fromfile="checked-in index",
                    tofile="expected index",
                    lineterm="",
                )
            )[:14]
        )
        errors.append(
            f"generated document index is out of date: run `continuity docs render --root {root}`"
            + (f"\n{detail}" if detail else "")
        )
    return errors


def context_documents_for_task(catalog: dict[str, Any], task_id: str) -> list[dict[str, Any]]:
    direct = {record["id"] for record in catalog["documents"] if task_id in record["tasks"]}
    selected = set(direct)
    for doc_id in direct:
        selected.update(record["id"] for record in document_neighbors(catalog, doc_id))
    return [record for record in sorted(catalog["documents"], key=lambda item: item["id"]) if record["id"] in selected]


def validate_single_checkout(root: Path) -> list[str]:
    """Enforce one canonical Git checkout without changing Git state."""
    root = root.resolve()
    if not (root / ".git").exists():
        return []

    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=root,
            capture_output=True,
            check=True,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        return [f"could not inspect registered Git worktrees: {exc}"]

    worktrees = [line.removeprefix("worktree ") for line in result.stdout.splitlines() if line.startswith("worktree ")]

    def normalize(path: str | Path) -> str:
        return str(Path(path).resolve()).replace("\\", "/").casefold()

    if len(worktrees) != 1 or normalize(worktrees[0]) != normalize(root):
        found = ", ".join(worktrees) if worktrees else "none"
        return [(f"single-checkout mode requires exactly one registered Git worktree at {root}; found: {found}")]
    return []


def parse_git_worktrees(output: str) -> list[GitWorktree]:
    entries: list[GitWorktree] = []
    path: str | None = None
    branch: str | None = None
    locked = False
    for line in [*output.splitlines(), ""]:
        if not line:
            if path is not None:
                entries.append(GitWorktree(path, branch, locked))
            path = None
            branch = None
            locked = False
        elif line.startswith("worktree "):
            if path is not None:
                entries.append(GitWorktree(path, branch, locked))
            path = line.removeprefix("worktree ")
            branch = None
            locked = False
        elif line.startswith("branch "):
            branch = line.removeprefix("branch ")
        elif line == "locked" or line.startswith("locked "):
            locked = True
    return entries


def branch_for_task(task_path: Path) -> str:
    return f"task/{task_path.stem.removeprefix('TASK-')}"


def validate_managed_worktrees(root: Path, config: dict[str, Any]) -> list[str]:
    root = root.resolve()
    if not (root / ".git").exists():
        return []
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "worktree", "list", "--porcelain"],
            capture_output=True,
            check=True,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        return [f"could not inspect registered Git worktrees: {exc}"]

    entries = parse_git_worktrees(result.stdout)
    if not entries:
        return ["Git reported no registered worktrees for the managed repository"]
    canonical_root = Path(entries[0].path).resolve()
    errors: list[str] = []
    for entry in entries[1:]:
        path = Path(entry.path).resolve()
        try:
            relative = path.relative_to(canonical_root)
        except ValueError:
            errors.append(f"managed worktree is outside the canonical checkout: {path}")
            continue
        if len(relative.parts) != 3 or relative.parts[:2] != ("pcm", "worktree"):
            errors.append(f"additional worktree must be under pcm/worktree/<TASK-ID> in the canonical checkout: {path}")
            continue
        task_id = relative.parts[2]
        if TASK_ID_RE.fullmatch(task_id) is None:
            errors.append(f"managed worktree directory must be a task ID, got: {relative.parts[2]}")
            continue
        try:
            task_path = find_task(canonical_root, config, task_id)
        except ContinuityError as exc:
            errors.append(f"{path}: {exc}")
            continue
        meta = task_metadata(task_path)
        if meta is None or meta.get("id") != task_id:
            errors.append(f"{path}: task file does not identify {task_id}")
            continue
        if meta.get("status") not in {"active", "blocked"}:
            errors.append(f"{path}: task {task_id} is finished; remove its managed worktree after merge")
        expected_branch = branch_for_task(task_path)
        if entry.branch != f"refs/heads/{expected_branch}":
            errors.append(f"{path}: expected task branch {expected_branch}, found {entry.branch or 'detached HEAD'}")
    return errors


def validate_workspace_layout(root: Path, config: dict[str, Any]) -> list[str]:
    workspace = config.get("workspace")
    mode = workspace.get("mode", "single-checkout") if isinstance(workspace, dict) else "single-checkout"
    if mode == "single-checkout":
        return validate_single_checkout(root)
    if mode == "managed-worktrees":
        return validate_managed_worktrees(root, config)
    return [f"unsupported workspace mode: {mode}"]


def validate_repo(root: Path) -> list[str]:
    errors: list[str] = []
    config_path = root / ".continuity" / "config.json"
    try:
        config = load_json(config_path)
    except ContinuityError as exc:
        return [str(exc)]

    if "workspace_mode" in config:
        return [
            (
                f"{config_path}: unsupported legacy key 'workspace_mode'; "
                "migration required: use `workspace: {mode: single-checkout}` or "
                "`workspace: {mode: managed-worktrees}` in .continuity/config.json. "
                "Validation does not modify configuration."
            )
        ]

    try:
        config_errors = [f"{config_path}: {e}" for e in validate_schema(config, load_schema(root, "config"))]
        errors.extend(config_errors)
    except ContinuityError as exc:
        errors.append(str(exc))
        return sorted(set(errors))

    # Invalid config is a terminal structural error. Do not index required
    # keys after schema validation has already established that they are absent.
    if config_errors:
        return sorted(set(errors))

    errors.extend(validate_workspace_layout(root, config))
    remote = git_value(root, ["remote", "get-url", "origin"], fallback="")
    if github_repository(remote) and not config.get("trackers", {}).get("github"):
        errors.append(f"{config_path}: GitHub repositories must set trackers.github=true to enable issue authority")

    canonical = config.get("canonical", {})
    project_path = root / canonical.get("project", "PROJECT.md")
    current_path = root / canonical.get("current", "checkpoints/CURRENT.md")

    for kind, path in (("project", project_path), ("current", current_path)):
        if not path.exists():
            errors.append(f"missing canonical {kind}: {path}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"canonical {kind} unavailable: {path}: {exc}")
            continue
        try:
            meta = extract_marker(text, kind)
        except ContinuityError as exc:
            errors.append(f"{path}: {exc}")
            continue
        if meta is None:
            errors.append(f"{path}: missing continuity:{kind} metadata marker")
            continue
        try:
            errors.extend(f"{path}: {e}" for e in validate_schema(meta, load_schema(root, kind)))
        except ContinuityError as exc:
            errors.append(str(exc))
            continue
        if meta.get("protocol_version") != config.get("protocol_version"):
            errors.append(f"{path}: protocol_version does not match config")

    current_meta = None
    if current_path.exists():
        with suppress(ContinuityError, OSError):
            current_meta = extract_marker(current_path.read_text(encoding="utf-8"), "current")

    tasks_by_id: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in task_files(root, config):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"canonical task unavailable: {path}: {exc}")
            continue
        try:
            meta = extract_marker(text, "task")
        except ContinuityError as exc:
            errors.append(f"{path}: {exc}")
            continue
        if meta is None:
            errors.append(f"{path}: missing continuity:task metadata marker")
            continue
        try:
            errors.extend(f"{path}: {e}" for e in validate_schema(meta, load_schema(root, "task")))
        except ContinuityError as exc:
            errors.append(str(exc))
            continue
        task_id = meta.get("id")
        if not isinstance(task_id, str):
            continue
        if not task_id.startswith(config["task_prefix"] + "-"):
            errors.append(f"{path}: task id prefix does not match configured task_prefix")
        if task_id in tasks_by_id:
            errors.append(f"duplicate task id: {task_id}")
        else:
            tasks_by_id[task_id] = (path, meta)
        if meta.get("protocol_version") != config.get("protocol_version"):
            errors.append(f"{path}: protocol_version does not match config")
        if meta.get("next_action", "").strip() == "":
            errors.append(f"{path}: next_action must be non-empty")
        if (
            config.get("trackers", {}).get("github")
            and current_meta
            and meta.get("id") == current_meta.get("active_task")
        ):
            issue_url = meta.get("issue_url")
            if not isinstance(issue_url, str):
                errors.append(f"{path}: active task in a GitHub-authoritative repository requires issue_url")
            else:
                try:
                    issue_repo, _ = validate_github_issue_url(issue_url)
                    remote = git_value(root, ["remote", "get-url", "origin"], fallback="")
                    repository = github_repository(remote)
                    if repository and repository.casefold() != issue_repo.casefold():
                        errors.append(f"{path}: issue_url repository {issue_repo} does not match origin {repository}")
                except ContinuityError as exc:
                    errors.append(f"{path}: {exc}")
        errors.extend(validate_checkpoint_structure(root, path, text))

    for _task_id, (path, meta) in tasks_by_id.items():
        for dep in meta.get("depends_on", []):
            if dep.startswith("external:"):
                continue
            if dep not in tasks_by_id:
                errors.append(f"{path}: dependency does not resolve: {dep}")

    errors.extend(validate_document_catalog(root, set(tasks_by_id)))

    if current_meta:
        active_id = current_meta.get("active_task")
        active_file = current_meta.get("active_task_file")
        if (active_id is None) != (active_file is None):
            errors.append(f"{current_path}: active_task and active_task_file must both be null or both set")
        if active_id is not None and isinstance(active_id, str) and isinstance(active_file, str):
            target = root / active_file
            if not target.exists():
                errors.append(f"{current_path}: active task file does not exist: {active_file}")
            elif active_id not in tasks_by_id:
                errors.append(f"{current_path}: active task id not found in task metadata: {active_id}")
            else:
                task_path, task_meta = tasks_by_id[active_id]
                if task_path.resolve() != target.resolve():
                    errors.append(f"{current_path}: active_task_file does not match task {active_id}")
                if task_meta.get("status") != "active":
                    errors.append(f"{current_path}: active task {active_id} has status {task_meta.get('status')!r}")
        for task_id, (_, task_meta) in tasks_by_id.items():
            if task_meta.get("status") == "completed" and active_id == task_id:
                errors.append(f"{current_path}: completed task cannot be active: {task_id}")

    packs_dir = root / ".continuity" / "packs"
    if packs_dir.exists():
        for pack in sorted(packs_dir.glob("*.md")):
            try:
                meta = extract_marker(pack.read_text(encoding="utf-8"), "context-pack")
            except OSError as exc:
                errors.append(f"context pack unavailable: {pack}: {exc}")
                continue
            except ContinuityError as exc:
                errors.append(f"{pack}: {exc}")
                continue
            if meta is None:
                errors.append(f"{pack}: missing continuity:context-pack metadata marker")
            else:
                try:
                    errors.extend(f"{pack}: {e}" for e in validate_schema(meta, load_schema(root, "context-pack")))
                except ContinuityError as exc:
                    errors.append(str(exc))
    recovery_dir = root / ".continuity" / "recovery"
    if recovery_dir.exists():
        for receipt_path in sorted(recovery_dir.glob("*.json")):
            try:
                receipt = load_json(receipt_path)
                errors.extend(
                    f"{receipt_path}: {error}" for error in validate_schema(receipt, load_schema(root, "recovery"))
                )
            except ContinuityError as exc:
                errors.append(f"{receipt_path}: {exc}")
    return sorted(set(errors))


def preflight_repo(root: Path) -> tuple[str, list[str]]:
    """Classify an explicit target root before an agent relies on PCM state."""
    root = root.resolve()
    if not root.exists():
        return "MISSING_ROOT", [f"target root does not exist: {root}"]
    if not root.is_dir():
        return "INVALID_ROOT", [f"target root is not a directory: {root}"]

    project_path = root / "PROJECT.md"
    if project_path.exists():
        try:
            project_meta = extract_marker(project_path.read_text(encoding="utf-8"), "project")
        except (ContinuityError, OSError):
            project_meta = None
        if project_meta and project_meta.get("id") == "project-continuity-modules":
            return "HELPER_REPOSITORY", [
                (
                    "this root is the Project Continuity Modules helper repository; "
                    "another project's continuity state must live in that target repository"
                )
            ]

    config_path = root / ".continuity" / "config.json"
    if not config_path.exists():
        return "NOT_ADOPTED", [
            (
                "missing .continuity/config.json; initialize a fresh target or follow "
                "the mature-repository overlay procedure before relying on PCM state"
            )
        ]

    errors = validate_repo(root)
    if errors:
        if any("unavailable" in error.lower() or "permission denied" in error.lower() for error in errors):
            return "DEGRADED_TARGET", errors
        return "INVALID_TARGET", errors
    return "TARGET_VALID", []


def checkpoint_metadata(
    config: dict[str, Any],
    task_id: str,
    agent: str,
    timestamp: str,
    completed: list[str],
    evidence: list[str],
    decisions: list[str],
    changed: list[str],
    blocked: list[str],
    next_action: str,
) -> dict[str, Any]:
    return {
        "schema": "project-continuity.checkpoint.v1",
        "protocol_version": config["protocol_version"],
        "task_id": task_id,
        "timestamp": timestamp,
        "agent": agent,
        "completed": completed,
        "evidence": evidence,
        "decisions": decisions,
        "changed": changed,
        "blocked": blocked,
        "next_action": next_action,
    }


def checkpoint_payload_sha256(meta: dict[str, Any]) -> str:
    """Hash the requested checkpoint content, excluding its first-write timestamp."""
    payload = {
        key: meta[key]
        for key in (
            "protocol_version",
            "task_id",
            "agent",
            "completed",
            "evidence",
            "decisions",
            "changed",
            "blocked",
            "next_action",
        )
    }
    return hashlib.sha256(_json(payload).encode("utf-8")).hexdigest()


def checkpoint_operation_metadata(meta: dict[str, Any], request_id: str) -> dict[str, str]:
    return {
        "schema": "project-continuity.checkpoint-operation.v1",
        "task_id": meta["task_id"],
        "request_id": request_id,
        "payload_sha256": checkpoint_payload_sha256(meta),
    }


def checkpoint_records(text: str) -> list[tuple[dict[str, Any] | None, dict[str, Any] | None]]:
    if "## Checkpoint log" not in text:
        return []
    log = text.split("## Checkpoint log", 1)[1]
    if "## Handoff" in log:
        log = log.split("## Handoff", 1)[0]
    entries: list[list[str]] = []
    current: list[str] = []
    for line in log.splitlines():
        if CHECKPOINT_HEADING_RE.match(line):
            if current:
                entries.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        entries.append(current)
    return [
        (extract_marker("\n".join(entry), "checkpoint"), extract_marker("\n".join(entry), "checkpoint-operation"))
        for entry in entries
    ]


def checkpoint_addition(meta: dict[str, Any], request_id: str) -> str:
    human_time = meta["timestamp"].replace("T", " ").replace("Z", " UTC")
    operation = checkpoint_operation_metadata(meta, request_id)
    return "\n".join(
        [
            "",
            f"### {human_time} — {meta['agent']}",
            "",
            marker("checkpoint", meta),
            marker("checkpoint-operation", operation),
            "",
            "Completed:",
            *[f"- {item}" for item in meta["completed"]],
            "",
            "Evidence:",
            *[f"- {item}" for item in meta["evidence"]],
            "",
            "Decisions:",
            *[f"- {item}" for item in meta["decisions"]],
            "",
            "Changed:",
            *[f"- {item}" for item in meta["changed"]],
            "",
            "Blocked/uncertain:",
            *[f"- {item}" for item in (meta["blocked"] or ["none"])],
            "",
            "Next:",
            f"- {meta['next_action']}",
            "",
        ]
    )


def recovery_path(recovery_root: Path, task_id: str, request_id: str) -> Path:
    safe_request_id = re.sub(r"[^0-9A-Za-z._-]", "-", request_id)
    request_hash = hashlib.sha256(request_id.encode("utf-8")).hexdigest()[:12]
    return recovery_root / ".continuity" / "recovery" / f"{task_id}-{safe_request_id}-{request_hash}.json"


def write_recovery_checkpoint(
    recovery_root: Path,
    canonical_root: Path,
    config: dict[str, Any],
    task_id: str,
    agent: str,
    timestamp: str,
    completed: list[str],
    evidence: list[str],
    decisions: list[str],
    changed: list[str],
    blocked: list[str],
    next_action: str,
    canonical_task: str,
    request_id: str,
) -> Path:
    recovery_root = recovery_root.resolve()
    canonical_root = canonical_root.resolve()
    if recovery_root == canonical_root:
        raise ContinuityError("recovery root must be a different authorized checkout or host")

    checkpoint = checkpoint_metadata(
        config,
        task_id,
        agent,
        timestamp,
        completed,
        evidence,
        decisions,
        changed,
        blocked,
        next_action,
    )
    operation = checkpoint_operation_metadata(checkpoint, request_id)
    checkpoint["request_id"] = operation["request_id"]
    checkpoint["payload_sha256"] = operation["payload_sha256"]
    project_id = recovery_root.name
    project_path = recovery_root / config["canonical"]["project"]
    try:
        project_meta = extract_marker(project_path.read_text(encoding="utf-8"), "project")
    except (ContinuityError, OSError):
        project_meta = None
    if project_meta and isinstance(project_meta.get("id"), str):
        project_id = project_meta["id"]

    receipt = {
        "schema": "project-continuity.recovery.v1",
        "protocol_version": config["protocol_version"],
        "project_id": project_id,
        "task_id": task_id,
        "canonical_root": str(canonical_root),
        "canonical_task": canonical_task,
        "repository": git_value(canonical_root, ["config", "--get", "remote.origin.url"], project_id),
        "ref": git_value(canonical_root, ["rev-parse", "--abbrev-ref", "HEAD"], "unknown"),
        "commit": git_value(canonical_root, ["rev-parse", "HEAD"], "unknown"),
        "recorded_at": timestamp,
        "status": "pending-reconciliation",
        "checkpoint": checkpoint,
    }
    path = recovery_path(recovery_root, task_id, request_id)
    content = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            existing = load_json(path)
            existing_checkpoint = existing.get("checkpoint", {})
            if (
                not isinstance(existing_checkpoint, dict)
                or existing_checkpoint.get("request_id") != request_id
                or existing_checkpoint.get("payload_sha256") != operation["payload_sha256"]
            ):
                raise ContinuityError(f"recovery request ID {request_id!r} was reused with different content")
            return path
        write_file_no_overwrite(path, content)
    except OSError as exc:
        raise ContinuityError(f"cannot write recovery receipt: {path}: {exc}") from exc
    return path


def checkpoint_task(
    root: Path,
    task_id: str,
    agent: str,
    timestamp: str,
    completed: list[str],
    evidence: list[str],
    decisions: list[str],
    changed: list[str],
    blocked: list[str],
    next_action: str,
    recovery_root: Path | None = None,
    request_id: str | None = None,
) -> Path:
    if request_id is None:
        request_id = uuid.uuid4().hex
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", request_id):
        raise ContinuityError("checkpoint request ID must be 1-128 safe ASCII letters, digits, '.', '_', ':' or '-'")
    config: dict[str, Any] | None = None
    canonical_task = f"tasks/TASK-{task_id}.md"
    try:
        config = load_config(root)
        path = find_task(root, config, task_id)
        canonical_task = path.relative_to(root).as_posix()
        try:
            original = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise CanonicalUnavailable(f"canonical task unavailable: {path}: {exc}") from exc
        meta = checkpoint_metadata(
            config,
            task_id,
            agent,
            timestamp,
            completed,
            evidence,
            decisions,
            changed,
            blocked,
            next_action,
        )
        operation = checkpoint_operation_metadata(meta, request_id)
        for prior_meta, prior_operation in checkpoint_records(original):
            if not prior_operation or prior_operation.get("request_id") != request_id:
                continue
            if prior_meta is None or prior_operation.get("payload_sha256") != operation["payload_sha256"]:
                raise ContinuityError(f"checkpoint request ID {request_id!r} was reused with different checkpoint payload")
            return path
        addition = checkpoint_addition(meta, request_id)
        if "## Handoff" in original:
            before, after = original.split("## Handoff", 1)
            new_text = before.rstrip() + "\n" + addition + "\n## Handoff" + after
        else:
            new_text = original.rstrip() + "\n" + addition
        if not new_text.startswith(original.split("## Handoff", 1)[0].rstrip()):
            raise ContinuityError("checkpoint append invariant failed")
        try:
            path.write_text(new_text, encoding="utf-8")
        except OSError as exc:
            raise CanonicalUnavailable(f"cannot write canonical checkpoint: {path}: {exc}") from exc
        return path
    except CanonicalUnavailable:
        if recovery_root is None:
            raise
        if config is None:
            config = load_config(recovery_root)
        return write_recovery_checkpoint(
            recovery_root,
            root,
            config,
            task_id,
            agent,
            timestamp,
            completed,
            evidence,
            decisions,
            changed,
            blocked,
            next_action,
            canonical_task,
            request_id,
        )


def reconcile_recovery(root: Path, receipt_path: Path) -> Path:
    receipt = load_json(receipt_path)
    if receipt.get("schema") != "project-continuity.recovery.v1":
        raise ContinuityError(f"invalid recovery receipt schema: {receipt_path}")
    checkpoint = receipt.get("checkpoint")
    if not isinstance(checkpoint, dict):
        raise ContinuityError(f"recovery receipt has no checkpoint: {receipt_path}")
    task_id = checkpoint.get("task_id")
    required = (
        "task_id",
        "agent",
        "timestamp",
        "completed",
        "evidence",
        "decisions",
        "changed",
        "blocked",
        "next_action",
    )
    if not all(key in checkpoint for key in required) or not isinstance(task_id, str):
        raise ContinuityError(f"recovery receipt checkpoint is incomplete: {receipt_path}")
    request_id = checkpoint.get("request_id")
    if receipt.get("status") == "reconciled" and not isinstance(request_id, str):
        raise ContinuityError(f"legacy recovery receipt is already reconciled: {receipt_path}")
    output = checkpoint_task(
        root,
        task_id,
        checkpoint["agent"],
        checkpoint["timestamp"],
        checkpoint["completed"],
        checkpoint["evidence"],
        checkpoint["decisions"],
        checkpoint["changed"],
        checkpoint["blocked"],
        checkpoint["next_action"],
        request_id=request_id if isinstance(request_id, str) else None,
    )
    if receipt.get("status") == "reconciled":
        return output
    receipt["status"] = "reconciled"
    receipt["reconciled_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    try:
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as exc:
        raise ContinuityError(f"checkpoint reconciled but receipt could not be updated: {receipt_path}: {exc}") from exc
    return output


def git_value(root: Path, args: list[str], fallback: str | None = None) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        value = proc.stdout.strip()
        if value:
            return value
    except (OSError, subprocess.CalledProcessError):
        pass
    if fallback is not None:
        return fallback
    raise ContinuityError(f"git provenance unavailable for: {' '.join(args)}")


def git_run(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError as exc:
        raise ContinuityError("git is required for checkpoint publishing") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "git command failed").strip()
        raise ContinuityError(f"git {' '.join(args)} failed: {detail}") from exc


def canonical_worktree_root(root: Path) -> Path:
    root = root.resolve()
    entries = parse_git_worktrees(git_run(root, ["worktree", "list", "--porcelain"]).stdout)
    if not entries:
        raise ContinuityError("Git reported no worktree for this repository")
    primary = Path(entries[0].path).resolve()
    if root != primary:
        raise ContinuityError(
            f"run this command from the canonical checkout {primary}; a task worktree is not the project identity"
        )
    git_value(root, ["remote", "get-url", "origin"])
    return primary


def task_for_worktree(root: Path, task_id: str, config: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    if TASK_ID_RE.fullmatch(task_id) is None:
        raise ContinuityError(f"invalid task ID: {task_id}")
    task_path = find_task(root, config, task_id)
    meta = task_metadata(task_path)
    if meta is None or meta.get("id") != task_id:
        raise ContinuityError(f"task metadata does not identify {task_id}: {task_path}")
    return task_path, meta


def workspace_mode(config: dict[str, Any]) -> str:
    workspace = config.get("workspace")
    if workspace is None:
        return "single-checkout"
    if not isinstance(workspace, dict):
        raise ContinuityError("workspace configuration must be an object")
    mode = workspace.get("mode")
    if not isinstance(mode, str) or mode not in WORKSPACE_MODES:
        raise ContinuityError(f"unsupported workspace mode: {mode}")
    return mode


def worktree_inventory(root: Path) -> list[GitWorktree]:
    return parse_git_worktrees(git_run(root, ["worktree", "list", "--porcelain"]).stdout)


def local_workspace_registry_path() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
    return base / "project-continuity" / "workspaces.json"


def local_workspace_roots() -> list[Path]:
    registry_path = local_workspace_registry_path()
    if not registry_path.exists():
        return []
    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContinuityError(f"private workspace registry cannot be read: {exc}") from exc
    roots = data.get("roots") if isinstance(data, dict) else None
    if not isinstance(roots, list) or any(not isinstance(item, str) for item in roots):
        raise ContinuityError("private workspace registry has an invalid roots list")
    return [Path(item).expanduser().resolve() for item in roots]


def register_local_workspace(root: Path) -> Path:
    root = root.resolve()
    git_value(root, ["remote", "get-url", "origin"])
    # Normalize linked-worktree input to this clone's permanent checkout.
    entries = worktree_inventory(root)
    if not entries:
        raise ContinuityError("Git reported no checkout to register")
    permanent = Path(entries[0].path).resolve()
    registry_path = local_workspace_registry_path()
    current = local_workspace_roots()
    if permanent not in current:
        current.append(permanent)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps({"version": 1, "roots": sorted(str(item) for item in current)}, indent=2) + "\n", encoding="utf-8")
    if os.name != "nt":
        os.chmod(registry_path.parent, 0o700)
        os.chmod(registry_path, 0o600)
    return permanent


def managed_worktree_path(root: Path, task_id: str) -> Path:
    root = root.resolve()
    for parent in (root / "pcm", root / "pcm" / "worktree"):
        if parent.is_symlink():
            raise ContinuityError(f"refusing to use a symlink in the managed worktree path: {parent}")
        if parent.exists() and not parent.is_dir():
            raise ContinuityError(f"managed worktree path component is not a directory: {parent}")
    path = root / "pcm" / "worktree" / task_id
    if not path.resolve(strict=False).is_relative_to(root):
        raise ContinuityError(f"managed worktree path escapes the canonical checkout: {path}")
    return path


def ensure_managed_worktree_ignored(root: Path) -> None:
    raw_path = git_value(root, ["rev-parse", "--git-path", "info/exclude"])
    exclude = Path(raw_path)
    if not exclude.is_absolute():
        exclude = root / exclude
    try:
        content = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
        if "/pcm/worktree/" not in content.splitlines():
            updated = content.rstrip("\r\n")
            if updated:
                updated += "\n"
            updated += "# PCM managed task worktrees\n/pcm/worktree/\n"
            exclude.parent.mkdir(parents=True, exist_ok=True)
            exclude.write_text(updated, encoding="utf-8")
    except OSError as exc:
        raise ContinuityError(f"could not configure the local managed-worktree ignore: {exc}") from exc


def github_repository(remote: str) -> str | None:
    match = re.fullmatch(
        r"(?:https://github\.com/|ssh://git@github\.com/|git@github\.com:)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?",
        remote,
    )
    return match.group(1) if match else None


def validate_github_issue_url(url: str) -> tuple[str, str]:
    match = re.fullmatch(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/issues/([1-9][0-9]*)", url)
    if not match:
        raise ContinuityError("issue must be a canonical GitHub issue URL: https://github.com/OWNER/REPO/issues/NUMBER")
    return f"{match.group(1)}/{match.group(2)}", match.group(3)


def verify_task_issue(root: Path, task_id: str) -> dict[str, str]:
    config = load_config(root)
    task_path, meta = task_for_worktree(root, task_id, config)
    issue_url = meta.get("issue_url")
    if not isinstance(issue_url, str):
        raise ContinuityError(f"task {task_id} has no authoritative GitHub issue URL: {task_path}")
    repository, number = validate_github_issue_url(issue_url)
    remote = git_value(root, ["remote", "get-url", "origin"])
    expected_repo = github_repository(remote)
    if expected_repo and expected_repo.casefold() != repository.casefold():
        raise ContinuityError(f"task issue belongs to {repository}, but this checkout is {expected_repo}")
    result = run_external(["gh", "issue", "view", number, "--repo", repository, "--json", "number,title,state,url"], root)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "issue lookup failed").strip()
        raise ContinuityError(f"cannot verify authoritative issue {issue_url}: {detail}")
    try:
        issue = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ContinuityError("GitHub returned invalid issue data") from exc
    if issue.get("url") != issue_url or str(issue.get("number")) != number:
        raise ContinuityError(f"GitHub issue response does not match task link: {issue_url}")
    if meta.get("status") == "active" and str(issue.get("state", "")).upper() != "OPEN":
        raise ContinuityError(f"authoritative issue is {issue.get('state')}; resolve lifecycle before resuming task {task_id}")
    return {"number": number, "title": str(issue.get("title", "")), "state": str(issue.get("state", "")), "url": issue_url}


def run_external(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=False)
    except OSError as exc:
        raise ContinuityError(f"could not run {command[0]}: {exc}") from exc


def remote_default_branch(root: Path, github_repo: str | None) -> str:
    if github_repo:
        result = run_external(
            ["gh", "repo", "view", github_repo, "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"],
            root,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "GitHub default branch unavailable").strip()
            raise ContinuityError(f"cannot verify the GitHub default branch: {detail}")
        branch = result.stdout.strip()
    else:
        result = run_external(["git", "-C", str(root), "ls-remote", "--symref", "origin", "HEAD"], root)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "remote HEAD unavailable").strip()
            raise ContinuityError(f"cannot determine the origin default branch: {detail}")
        match = re.search(r"^ref: refs/heads/([^\t]+)\tHEAD$", result.stdout, re.MULTILINE)
        branch = match.group(1) if match else ""
    if not branch or re.fullmatch(r"[A-Za-z0-9._/-]+", branch) is None:
        raise ContinuityError("origin did not provide a valid default branch name")
    return branch


def task_exists_on_remote(root: Path, task_path: Path, base_ref: str, task_id: str) -> None:
    relative = task_path.relative_to(root).as_posix()
    remote_text = git_run(root, ["show", f"{base_ref}:{relative}"]).stdout
    meta = extract_marker(remote_text, "task")
    if meta is None or meta.get("id") != task_id or meta.get("status") != "active":
        raise ContinuityError(
            f"task {task_id} must be active in the pushed canonical default branch before creating its worktree"
        )
    if task_path.read_text(encoding="utf-8") != remote_text:
        raise ContinuityError(
            f"task {task_id} has local-only checkpoint changes; push them before creating its worktree"
        )


@contextmanager
def local_task_lock(root: Path, task_id: str) -> Iterator[None]:
    registry_dir = local_workspace_registry_path().parent
    registry_dir.mkdir(parents=True, exist_ok=True)
    remote = git_value(root, ["remote", "get-url", "origin"])
    repo_identity = (github_repository(remote) or remote.rstrip("/").removesuffix(".git")).casefold()
    lock_name = hashlib.sha256(f"{repo_identity}\0{task_id}".encode()).hexdigest() + ".lock"
    lock_file = (registry_dir / lock_name).open("a+b")
    try:
        if os.name == "nt":
            msvcrt: Any = __import__("msvcrt")

            try:
                lock_file.seek(0, 2)
                if lock_file.tell() == 0:
                    lock_file.write(b"0")
                    lock_file.flush()
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise ContinuityError("another local session is resolving this task checkout; retry after it finishes") from exc
        else:
            fcntl = __import__("fcntl")

            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise ContinuityError("another local session is resolving this task checkout; retry after it finishes") from exc
        try:
            yield
        finally:
            if os.name == "nt":
                msvcrt_unlock: Any = __import__("msvcrt")

                lock_file.seek(0)
                msvcrt_unlock.locking(lock_file.fileno(), msvcrt_unlock.LK_UNLCK, 1)
            else:
                fcntl = __import__("fcntl")

                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    finally:
        lock_file.close()


def create_managed_worktree(root: Path, task_id: str) -> tuple[Path, bool]:
    root = canonical_worktree_root(root)
    with local_task_lock(root, task_id):
        return _create_managed_worktree(root, task_id)


def _create_managed_worktree(root: Path, task_id: str) -> tuple[Path, bool]:
    root = canonical_worktree_root(root)
    config = load_config(root)
    if workspace_mode(config) != "managed-worktrees":
        raise ContinuityError(
            "this project uses strict single-checkout mode; change workspace.mode before creating worktrees"
        )
    task_path, meta = task_for_worktree(root, task_id, config)
    if meta.get("status") != "active":
        raise ContinuityError(f"task {task_id} is not active")
    if errors := validate_managed_worktrees(root, config):
        raise ContinuityError("existing worktree policy violation: " + "; ".join(errors))

    path = managed_worktree_path(root, task_id)
    branch = branch_for_task(task_path)
    remote_value = git_value(root, ["remote", "get-url", "origin"])
    remote_identity = (github_repository(remote_value) or remote_value.rstrip("/").removesuffix(".git")).casefold()
    candidate_entries: list[GitWorktree] = []
    seen_worktrees: set[str] = set()
    for registered_root in [root, *local_workspace_roots()]:
        if not registered_root.is_dir():
            continue
        candidate_remote = run_external(["git", "-C", str(registered_root), "remote", "get-url", "origin"], root)
        candidate_value = candidate_remote.stdout.strip()
        candidate_identity = (github_repository(candidate_value) or candidate_value.rstrip("/").removesuffix(".git")).casefold()
        if candidate_remote.returncode != 0 or candidate_identity != remote_identity:
            continue
        for entry in worktree_inventory(registered_root):
            key = str(Path(entry.path).resolve()).casefold()
            if entry.branch == f"refs/heads/{branch}" and key not in seen_worktrees:
                candidate_entries.append(entry)
                seen_worktrees.add(key)
    if len(candidate_entries) > 1:
        raise ContinuityError(f"task branch {branch} is present in multiple registered checkouts; resolve ownership before continuing")
    if candidate_entries:
        existing = candidate_entries[0]
        existing_path = Path(existing.path).resolve()
        if existing.locked:
            raise ContinuityError(f"task worktree is locked; refusing to create a duplicate: {existing.path}")
        status = run_external(["git", "-C", str(existing_path), "status", "--porcelain", "--untracked-files=all"], root)
        if status.returncode != 0:
            raise ContinuityError(f"cannot inspect existing task checkout: {existing.path}")
        if status.stdout.strip():
            raise ContinuityError(f"existing task checkout is dirty; preserve it and resolve ownership before continuing: {existing.path}")
        candidate_config = load_config(existing_path)
        _, candidate_meta = task_for_worktree(existing_path, task_id, candidate_config)
        if candidate_meta.get("issue_url") != meta.get("issue_url"):
            raise ContinuityError(f"existing task checkout has conflicting issue ownership: {existing.path}")
        if existing_path == path.resolve(strict=False):
            return path, True
        return existing_path, True
    if path.exists() or path.is_symlink():
        raise ContinuityError(f"refusing to overwrite an existing unmanaged path: {path}")

    remote = git_value(root, ["remote", "get-url", "origin"])
    github_repo = github_repository(remote)
    base_branch = remote_default_branch(root, github_repo)
    git_run(root, ["fetch", "origin", base_branch])
    base_ref = f"origin/{base_branch}"
    git_value(root, ["rev-parse", "--verify", base_ref])
    task_exists_on_remote(root, task_path, base_ref, task_id)

    path.parent.mkdir(parents=True, exist_ok=True)
    ensure_managed_worktree_ignored(root)
    local_branch = run_external(
        ["git", "-C", str(root), "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], root
    )
    if local_branch.returncode == 0:
        git_run(root, ["worktree", "add", str(path), branch])
    else:
        remote_branch = run_external(
            ["git", "-C", str(root), "ls-remote", "--heads", "origin", f"refs/heads/{branch}"], root
        )
        if remote_branch.returncode != 0:
            raise ContinuityError(f"could not inspect remote task branch {branch}")
        if remote_branch.stdout.strip():
            git_run(root, ["fetch", "origin", branch])
            git_run(root, ["worktree", "add", "--track", "-b", branch, str(path), f"origin/{branch}"])
        else:
            git_run(root, ["worktree", "add", "-b", branch, str(path), base_ref])
    return path, False


def verify_merged_task(root: Path, path: Path, branch: str, remote: str) -> bool:
    github_repo = github_repository(remote)
    if not github_repo:
        raise ContinuityError(
            "cannot verify required CI and merged pull-request evidence for this remote; leaving the worktree in place"
        )
    base_branch = remote_default_branch(root, github_repo)
    git_run(root, ["fetch", "origin", base_branch])
    base_ref = f"origin/{base_branch}"
    git_value(root, ["rev-parse", "--verify", base_ref])
    head_oid = git_value(path, ["rev-parse", "HEAD"])

    prs_result = run_external(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            github_repo,
            "--state",
            "merged",
            "--head",
            branch,
            "--limit",
            "100",
            "--json",
            "number,headRefName,headRefOid,baseRefName,mergedAt,mergeCommit",
        ],
        root,
    )
    if prs_result.returncode != 0:
        detail = (prs_result.stderr or prs_result.stdout or "merged pull request lookup failed").strip()
        raise ContinuityError(f"cannot verify the merged GitHub pull request: {detail}")
    try:
        prs = json.loads(prs_result.stdout)
    except json.JSONDecodeError as exc:
        raise ContinuityError("GitHub returned invalid pull request data") from exc
    matches = [
        item
        for item in prs
        if item.get("headRefName") == branch
        and item.get("headRefOid") == head_oid
        and item.get("baseRefName") == base_branch
        and item.get("mergedAt")
    ]
    if len(matches) != 1:
        raise ContinuityError(
            f"no uniquely matching merged PR proves that {branch}@{head_oid[:12]} reached {base_branch}"
        )
    pr = matches[0]
    check_result = run_external(
        ["gh", "pr", "checks", str(pr["number"]), "--repo", github_repo, "--required", "--json", "name,bucket"],
        root,
    )
    if check_result.returncode != 0:
        detail = (check_result.stderr or check_result.stdout or "required checks are not green").strip()
        raise ContinuityError(f"cannot verify required GitHub checks: {detail}")
    try:
        checks = json.loads(check_result.stdout)
    except json.JSONDecodeError as exc:
        raise ContinuityError("GitHub returned invalid required-check data") from exc
    if not checks or any(item.get("bucket") != "pass" for item in checks):
        raise ContinuityError("refusing cleanup: the PR has no required checks or not all required checks passed")
    merge_commit = pr.get("mergeCommit")
    merge_oid = merge_commit.get("oid") if isinstance(merge_commit, dict) else None
    if not isinstance(merge_oid, str):
        raise ContinuityError("GitHub did not provide the pull request's merge commit")
    ancestor = run_external(["git", "-C", str(root), "merge-base", "--is-ancestor", merge_oid, base_ref], root)
    if ancestor.returncode != 0:
        raise ContinuityError("the merged PR commit is not present on the fetched remote default branch")
    return True


def remove_managed_worktree(root: Path, task_id: str) -> Path:
    root = canonical_worktree_root(root)
    config = load_config(root)
    if workspace_mode(config) != "managed-worktrees":
        raise ContinuityError("this project uses strict single-checkout mode; no managed worktrees may be removed")
    task_path, _ = task_for_worktree(root, task_id, config)
    path = managed_worktree_path(root, task_id)
    branch = branch_for_task(task_path)
    matches = [entry for entry in worktree_inventory(root) if Path(entry.path).resolve() == path.resolve(strict=False)]
    if len(matches) != 1 or matches[0].branch != f"refs/heads/{branch}":
        raise ContinuityError(f"no uniquely registered managed worktree for {task_id} at {path}")
    if matches[0].locked:
        raise ContinuityError(f"refusing cleanup: managed worktree for {task_id} is pinned/locked: {path}")
    status = git_run(path, ["status", "--porcelain", "--untracked-files=all"]).stdout.strip()
    if status:
        raise ContinuityError(f"refusing cleanup: managed worktree has uncommitted or untracked work: {path}")
    registered_root = Path(git_value(path, ["rev-parse", "--show-toplevel"])).resolve()
    if registered_root != path.resolve():
        raise ContinuityError(f"refusing cleanup: registered worktree identity changed: {path}")
    remote = git_value(root, ["remote", "get-url", "origin"])
    github_merge = verify_merged_task(root, path, branch, remote)
    base_branch = remote_default_branch(root, github_repository(remote))
    relative_task = task_path.relative_to(root).as_posix()
    remote_task = git_run(root, ["show", f"origin/{base_branch}:{relative_task}"]).stdout
    remote_meta = extract_marker(remote_task, "task")
    if remote_meta is None or remote_meta.get("id") != task_id or remote_meta.get("status") != "completed":
        raise ContinuityError(f"refusing cleanup: task {task_id} is not marked completed on origin/{base_branch}")
    try:
        remote_config = json.loads(git_run(root, ["show", f"origin/{base_branch}:.continuity/config.json"]).stdout)
    except json.JSONDecodeError as exc:
        raise ContinuityError(f"refusing cleanup: invalid canonical config on origin/{base_branch}") from exc
    canonical_paths = config.get("canonical")
    if (
        not isinstance(canonical_paths, dict)
        or not canonical_paths
        or not isinstance(remote_config, dict)
        or remote_config.get("canonical") != canonical_paths
    ):
        raise ContinuityError(f"refusing cleanup: canonical continuity paths differ on origin/{base_branch}")
    git_run(root, ["worktree", "remove", str(path)])
    branch_delete = run_external(["git", "-C", str(root), "branch", "-d", branch], root)
    if branch_delete.returncode != 0:
        if not github_merge:
            raise ContinuityError(f"worktree removed, but Git refused to delete the task branch: {branch}")
        # A squash-merged GitHub PR is proven above even though Git cannot see
        # its original commits as ancestors of the new squash commit.
        git_run(root, ["branch", "-D", branch])
    return path


@dataclass(frozen=True)
class ReceiptComment:
    marker: str
    payload_sha256: str


def decide_receipt_retry(
    comments: list[ReceiptComment],
    marker: str,
    payload_sha256: str,
    *,
    lookup_complete: bool,
) -> str:
    """Choose whether a lost comment response may be posted again.

    A lost response is not evidence that the receipt is absent. An incomplete
    or ambiguous lookup stops instead of posting.
    """
    if not lookup_complete:
        raise ContinuityError("receipt lookup is incomplete; refusing to post")
    matches = [comment for comment in comments if comment.marker == marker]
    if len(matches) > 1:
        raise ContinuityError("receipt marker is ambiguous; refusing to post")
    if not matches:
        return "post"
    if matches[0].payload_sha256 != payload_sha256:
        raise ContinuityError("receipt identity was reused with a different payload")
    return "recovered"


_RECEIPT_V2_PREFIX = "<!-- pcm:receipt-v2 "


def render_receipt_marker(
    *,
    repository: str,
    task_id: str,
    request_id: str,
    pushed_sha: str,
    destination: str,
    kind: str,
    payload_sha256: str,
) -> str:
    """Render the application marker. This is not a GitHub uniqueness constraint."""
    return (
        f"{_RECEIPT_V2_PREFIX}"
        f"repository={repository} task={task_id} request={request_id} "
        f"sha={pushed_sha} destination={destination} kind={kind} "
        f"payload={payload_sha256} -->"
    )


def parse_receipt_marker(body: str) -> ReceiptComment | None:
    """Read a v2 marker. Historical pcm:receipt comments are left unchanged."""
    start = body.find(_RECEIPT_V2_PREFIX)
    if start < 0:
        return None
    end = body.find("-->", start)
    if end < 0:
        return None
    fields = body[start + len(_RECEIPT_V2_PREFIX) : end].split()
    values = {}
    for field in fields:
        if "=" not in field:
            return None
        key, value = field.split("=", 1)
        values[key] = value
    required = ("repository", "task", "request", "sha", "destination", "kind", "payload")
    if any(key not in values or not values[key] for key in required):
        return None
    marker = body[start : end + 3]
    return ReceiptComment(marker=marker, payload_sha256=values["payload"])


def recover_receipt(
    bodies: list[str],
    marker: str,
    payload_sha256: str,
    *,
    lookup_complete: bool,
) -> str:
    """Decide from fetched comment bodies. This does not post a comment."""
    comments = []
    for body in bodies:
        parsed = parse_receipt_marker(body)
        if parsed is not None and parsed.marker == marker:
            comments.append(parsed)
    return decide_receipt_retry(comments, marker, payload_sha256, lookup_complete=lookup_complete)


def post_receipt_if_absent(
    bodies: list[str],
    marker: str,
    payload_sha256: str,
    *,
    lookup_complete: bool,
    post: Callable[[], object],
) -> str:
    """Post only when lookup proves the marker is absent. Never posts on uncertainty."""
    decision = recover_receipt(
        bodies,
        marker,
        payload_sha256,
        lookup_complete=lookup_complete,
    )
    if decision == "post":
        post()
    return decision


def github_issue_comment_path(repository: str, issue_number: str) -> str:
    owner, separator, name = repository.partition("/")
    if not separator or not owner or not name or "/" in name or ".." in repository:
        raise ContinuityError(f"receipt repository must be owner/name: {repository}")
    if not issue_number.isdecimal():
        raise ContinuityError(f"receipt issue number must be numeric: {issue_number}")
    return f"repos/{repository}/issues/{issue_number}/comments"


def publish_issue_receipt(
    bodies: list[str],
    marker: str,
    payload_sha256: str,
    *,
    lookup_complete: bool,
    repository: str,
    issue_number: str,
    body: str,
    run: Callable[[list[str], str], subprocess.CompletedProcess[str]],
) -> str:
    """Post through an injected runner only after lookup proves the marker is absent."""

    def post() -> None:
        if marker not in body:
            raise ContinuityError("receipt body is missing its marker")
        path = github_issue_comment_path(repository, issue_number)
        result = run(["gh", "api", "--method", "POST", path, "--input", "-"], body)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "GitHub comment post failed").strip()
            raise ContinuityError(f"receipt post failed; do not retry without a new lookup: {detail}")

    return post_receipt_if_absent(
        bodies,
        marker,
        payload_sha256,
        lookup_complete=lookup_complete,
        post=post,
    )


def publish_then_receipt(
    publish: Callable[[], str],
    bodies: list[str],
    *,
    repository: str,
    task_id: str,
    request_id: str,
    destination: str,
    kind: str,
    payload_sha256: str,
    lookup_complete: bool,
    issue_number: str,
    run: Callable[[list[str], str], subprocess.CompletedProcess[str]],
) -> str:
    """Run the receipt path only after publish returns a confirmed commit."""
    commit = publish()
    marker = render_receipt_marker(
        repository=repository,
        task_id=task_id,
        request_id=request_id,
        pushed_sha=commit,
        destination=destination,
        kind=kind,
        payload_sha256=payload_sha256,
    )
    publish_issue_receipt(
        bodies,
        marker,
        payload_sha256,
        lookup_complete=lookup_complete,
        repository=repository,
        issue_number=issue_number,
        body=marker,
        run=run,
    )
    return commit


def require_receipt_pair(repository: str | None, issue_number: str | None) -> tuple[str, str] | None:
    if repository is None and issue_number is None:
        return None
    if not repository or not issue_number:
        raise ContinuityError("receipt automation requires both --receipt-repo and --receipt-issue")
    return repository, issue_number


def page_is_complete(count: int, page_size: int) -> bool:
    if page_size < 1:
        raise ContinuityError("receipt page size must be positive")
    return count < page_size


def classify_receipt_failure(detail: str) -> str:
    text = detail.lower()
    if any(token in text for token in ("401", "403", "authentication", "permission", "forbidden")):
        return "permission"
    if any(token in text for token in ("404", "not found")):
        return "wrong-target"
    return "unavailable"


def receipt_failure_message(commit: str, detail: str) -> str:
    kind = classify_receipt_failure(detail)
    return (
        f"RECEIPT_{kind.upper().replace('-', '_')}: push {commit} stands; "
        f"do not roll back and do not post again until a new lookup succeeds; {detail}"
    )


def deliver_leaf_then_parent(leaf: Callable[[], str], parent: Callable[[], str]) -> str:
    """Post the parent only after the leaf succeeds. A parent failure does not undo the leaf."""
    leaf_result = leaf()
    try:
        parent()
    except ContinuityError as exc:
        raise ContinuityError(
            f"RECEIPT_PARENT_PARTIAL: leaf receipt stands; parent was not posted; do not roll back; {exc}"
        ) from exc
    return leaf_result


def comment_bodies(payload: str) -> list[str]:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ContinuityError("receipt lookup returned invalid JSON") from exc
    if not isinstance(data, list):
        raise ContinuityError("receipt lookup did not return a list")
    bodies: list[str] = []
    for item in data:
        if not isinstance(item, dict) or not isinstance(item.get("body"), str):
            raise ContinuityError("receipt lookup is missing a comment body")
        bodies.append(item["body"])
    return bodies


def maybe_post_from_page(
    payload: str,
    page_size: int,
    *,
    marker: str,
    payload_sha256: str,
    repository: str,
    issue_number: str,
    run: Callable[[list[str], str], subprocess.CompletedProcess[str]],
) -> str:
    bodies = comment_bodies(payload)
    if not page_is_complete(len(bodies), page_size):
        raise ContinuityError("receipt lookup is not proven complete; refusing to post")
    return publish_issue_receipt(
        bodies,
        marker,
        payload_sha256,
        lookup_complete=True,
        repository=repository,
        issue_number=issue_number,
        body=marker,
        run=run,
    )


def publish_checkpoint(
    root: Path,
    checkpoint_path: Path,
    task_id: str,
    next_action: str,
    recovery: bool = False,
    request_id: str | None = None,
) -> str:
    """Commit and push one checkpoint so the shared branch is the durable handoff."""
    root = root.resolve()
    checkpoint_path = checkpoint_path.resolve()
    try:
        relative = checkpoint_path.relative_to(root).as_posix()
    except ValueError as exc:
        raise ContinuityError(f"checkpoint is outside the publishing repository: {checkpoint_path}") from exc

    git_run(root, ["rev-parse", "--show-toplevel"])
    branch = git_value(root, ["rev-parse", "--abbrev-ref", "HEAD"])
    if branch == "HEAD":
        raise ContinuityError("checkpoint publishing requires an attached task branch")
    remote = git_value(root, ["remote", "get-url", "origin"], None)

    status = git_run(root, ["status", "--porcelain", "--untracked-files=all"]).stdout.splitlines()
    unexpected = [line for line in status if line[3:] != relative]
    if unexpected and not recovery:
        raise ContinuityError(
            "checkpoint publishing requires product changes to be committed first; "
            f"uncommitted paths: {', '.join(line[3:] for line in unexpected)}"
        )

    git_run(root, ["add", "--", relative])
    staged = git_run(root, ["diff", "--cached", "--name-only"]).stdout.splitlines()
    if relative in staged:
        kind = "recovery receipt" if recovery else "checkpoint"
        message = f"PCM {kind} {task_id}: {next_action}"
        git_run(root, ["commit", "-m", message])
    else:
        # A previous invocation may already have committed the checkpoint, or
        # pushed it successfully while losing the server response. In either
        # case, verify the current commit contains this checkpoint before
        # retrying the same push rather than inventing another commit.
        head_text = git_run(root, ["show", f"HEAD:{relative}"]).stdout
        if recovery:
            try:
                head_receipt = json.loads(head_text)
            except json.JSONDecodeError as exc:
                raise ContinuityError(f"committed recovery receipt is invalid: {relative}") from exc
            committed = (
                head_receipt.get("schema") == "project-continuity.recovery.v1"
                and head_receipt.get("task_id") == task_id
                and (request_id is None or head_receipt.get("checkpoint", {}).get("request_id") == request_id)
            )
        else:
            committed = any(
                meta
                and meta.get("task_id") == task_id
                and (request_id is None or (operation and operation.get("request_id") == request_id))
                for meta, operation in checkpoint_records(head_text)
            )
        if not committed:
            raise ContinuityError(f"checkpoint produced no staged change and is absent from HEAD: {checkpoint_path}")

    commit = git_value(root, ["rev-parse", "HEAD"])
    git_run(root, ["push", "--set-upstream", remote, f"HEAD:{branch}"])
    return commit


def committed_file(root: Path, commit: str, rel: str) -> bytes:
    dirty = git_run(root, ["status", "--porcelain", "--untracked-files=all", "--", rel]).stdout.strip()
    if dirty:
        raise ContinuityError(f"context source is not a clean committed snapshot: {rel}; commit or checkpoint it first")
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "show", f"{commit}:{rel}"],
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContinuityError(f"context source is absent from commit {commit}: {rel}") from exc
    return result.stdout


def committed_files(root: Path, commit: str, relatives: list[str]) -> dict[str, bytes]:
    """Read a clean committed source set with one status and one archive operation."""
    relatives = list(dict.fromkeys(relatives))
    dirty = git_run(root, ["status", "--porcelain", "--untracked-files=all", "--", *relatives]).stdout.strip()
    if dirty:
        raise ContinuityError("context sources are not a clean committed snapshot; commit or checkpoint them first")
    try:
        archive = subprocess.run(
            ["git", "-C", str(root), "archive", "--format=tar", commit, "--", *relatives],
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.decode("utf-8", errors="replace").strip() if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        raise ContinuityError(f"could not read committed context sources: {detail}") from exc
    result: dict[str, bytes] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as bundle:
            for member in bundle.getmembers():
                if not member.isfile():
                    continue
                source = bundle.extractfile(member)
                if source is not None:
                    result[member.name] = source.read()
    except tarfile.TarError as exc:
        raise ContinuityError("Git returned an invalid committed context archive") from exc
    missing = sorted(set(relatives) - result.keys())
    if missing:
        raise ContinuityError(f"context source is absent from commit {commit}: {', '.join(missing)}")
    return result


def pack_task(root: Path, task_id: str, output: Path | None) -> Path:
    config = load_config(root)
    task_path = find_task(root, config, task_id)
    task_meta = task_metadata(task_path)
    if task_meta is None:
        raise ContinuityError(f"task metadata is missing: {task_path}")
    project_path = root / config["canonical"]["project"]
    current_path = root / config["canonical"]["current"]
    sources = [
        project_path.relative_to(root).as_posix(),
        current_path.relative_to(root).as_posix(),
        task_path.relative_to(root).as_posix(),
    ]
    selected_documents: list[dict[str, Any]] = []
    selection_sources: list[str] = []
    catalog_path = root / DOCUMENT_CATALOG_PATH
    if catalog_path.exists():
        catalog = load_document_catalog(root)
        selected_documents = context_documents_for_task(catalog, task_id)
        errors = validate_document_catalog_data(
            root,
            catalog,
            document_task_ids(root, config),
            {record["path"] for record in selected_documents},
        )
        if errors:
            raise ContinuityError("document inventory is invalid: " + "; ".join(errors))
        sources.extend(record["path"] for record in selected_documents)
        selection_sources = [DOCUMENT_CATALOG_PATH]
    else:
        # Keep the established behavior for repositories that have not opted
        # into the optional, task-scoped document inventory.
        for optional in ("SPEC.md", "AGENTS.md"):
            if (root / optional).exists():
                sources.append(optional)
    sources = list(dict.fromkeys(sources))
    repo = git_value(root, ["config", "--get", "remote.origin.url"], root.name)
    ref = git_value(root, ["rev-parse", "--abbrev-ref", "HEAD"])
    commit = git_value(root, ["rev-parse", "HEAD"])
    remote = remote_tracking_head(root) if selected_documents else None
    remote_hashes = (
        remote_document_hashes(root, remote[0], [record["path"] for record in selected_documents])
        if remote
        else None
    )
    generated = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    meta = {
        "schema": "project-continuity.context-pack.v1",
        "protocol_version": config["protocol_version"],
        "repository": repo,
        "ref": ref,
        "commit": commit,
        "task_id": task_id,
        "generated_at": generated,
        "sources": sources,
    }
    chunks = [
        "# Continuity Context Pack",
        "",
        marker("context-pack", meta),
        "",
        "> Derived convenience view. Canonical source files remain authoritative.",
        "",
        "## Exact next action",
        "",
        str(task_meta["next_action"]),
        "",
    ]
    source_contents = committed_files(root, commit, sources + selection_sources)
    if selection_sources:
        chunks.extend(["## Document selection provenance", ""])
        for rel in selection_sources:
            content = source_contents[rel]
            chunks.append(f"- `{rel}` at `{commit}`; SHA-256 `{sha256_bytes(content)}`")
        chunks.append("")
    for rel in sources:
        content = source_contents[rel]
        try:
            text_content = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ContinuityError(f"context source is not UTF-8 text: {rel}") from exc
        details = f"; SHA-256 `{sha256_bytes(content)}`"
        record = next((item for item in selected_documents if item["path"] == rel), None)
        if record is not None:
            freshness, current_hash = document_freshness(
                root, record, include_remote=True, remote_hashes=remote_hashes
            )
            details += f"; review status `{freshness}`"
            if freshness == "NEEDS_REVIEW":
                chunks.extend(
                    [
                        f"> **Needs review:** `{rel}` differs from the content previously reviewed ({record['reviewed_sha256']}); current SHA-256 is `{current_hash}`. Preserve the old checkpoint as history and reconcile this source before relying on it.",
                        "",
                    ]
                )
            elif freshness == "REMOTE_UNKNOWN":
                chunks.extend(
                    [
                        f"> **Remote freshness unknown:** `{rel}` could not be compared with a descendant of its recorded review commit. Fetch `origin` and verify the current file before relying on it.",
                        "",
                    ]
                )
        blob = git_value(root, ["rev-parse", f"{commit}:{rel}"])
        chunks += [f"## Source: `{rel}`", "", f"> Git blob `{blob}`{details}", "", text_content.rstrip(), ""]
    if output is None:
        output = root / ".continuity" / "packs" / f"{task_id}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="continuity")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("--root", default=".")
    p_init.add_argument("--profile", choices=["minimal", "software"], default="minimal")
    p_init.add_argument("--name", default=None)
    p_init.add_argument("--task-prefix", default="TASK")
    p_init.add_argument("--workspace-mode", choices=sorted(WORKSPACE_MODES), default="managed-worktrees")
    p_init.add_argument("--github-authority", action="store_true", help="require GitHub issue links even before origin is configured")
    p_init.add_argument(
        "--github-templates",
        action="store_true",
        help="install optional GitHub issue and PR writing templates; does not enable synchronization",
    )

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("--root", default=".")

    p_preflight = sub.add_parser("preflight")
    p_preflight.add_argument("--root", required=True)

    p_task = sub.add_parser("task")
    task_sub = p_task.add_subparsers(dest="task_command", required=True)
    p_task_new = task_sub.add_parser("new")
    p_task_new.add_argument("--root", default=".")
    p_task_new.add_argument("--slug", required=True)
    p_task_new.add_argument("--goal", required=True)
    p_task_new.add_argument("--why", required=True)
    p_task_new.add_argument("--owner", default="unassigned")
    p_task_new.add_argument("--priority", default="P1")
    p_task_new.add_argument("--issue", default=None, help="authoritative GitHub issue URL")

    p_issue = sub.add_parser("issue")
    issue_sub = p_issue.add_subparsers(dest="issue_command", required=True)
    p_issue_verify = issue_sub.add_parser("verify")
    p_issue_verify.add_argument("task_id")
    p_issue_verify.add_argument("--root", default=".")

    p_checkpoint = sub.add_parser("checkpoint")
    p_checkpoint.add_argument("task_id")
    p_checkpoint.add_argument("--root", default=".")
    p_checkpoint.add_argument("--agent", required=True)
    p_checkpoint.add_argument("--time", default=None)
    p_checkpoint.add_argument(
        "--request-id",
        default=None,
        help="stable retry key; reuse the printed ID if a checkpoint command is interrupted",
    )
    p_checkpoint.add_argument("--completed", action="append", default=[])
    p_checkpoint.add_argument("--evidence", action="append", default=[])
    p_checkpoint.add_argument("--decision", action="append", default=[])
    p_checkpoint.add_argument("--changed", action="append", default=[])
    p_checkpoint.add_argument("--blocked", action="append", default=[])
    p_checkpoint.add_argument("--next", dest="next_action", required=True)
    p_checkpoint.add_argument(
        "--recovery-root",
        default=None,
        help="authorized alternate checkout/host for a recovery receipt if canonical state is unavailable",
    )
    p_checkpoint.add_argument("--receipt-repo", default=None, help="opt-in owner/name for a GitHub receipt")
    p_checkpoint.add_argument("--receipt-issue", default=None, help="opt-in issue number for a GitHub receipt")

    p_recovery = sub.add_parser("recovery")
    recovery_sub = p_recovery.add_subparsers(dest="recovery_command", required=True)
    p_reconcile = recovery_sub.add_parser("reconcile")
    p_reconcile.add_argument("--root", required=True)
    p_reconcile.add_argument("--file", required=True)

    p_docs = sub.add_parser("docs")
    docs_sub = p_docs.add_subparsers(dest="docs_command", required=True)
    p_docs_init = docs_sub.add_parser("init")
    p_docs_init.add_argument("--root", default=".")
    p_docs_add = docs_sub.add_parser("add")
    p_docs_add.add_argument("document_id")
    p_docs_add.add_argument("--root", default=".")
    p_docs_add.add_argument("--path", required=True)
    p_docs_add.add_argument("--title", required=True)
    p_docs_add.add_argument("--summary", required=True)
    p_docs_add.add_argument("--keyword", action="append", default=[])
    p_docs_add.add_argument("--related", action="append", default=[])
    p_docs_add.add_argument("--task", action="append", default=[])
    p_docs_find = docs_sub.add_parser("find")
    p_docs_find.add_argument("query")
    p_docs_find.add_argument("--root", default=".")
    p_docs_find.add_argument("--task", default=None)
    p_docs_refresh = docs_sub.add_parser("refresh")
    p_docs_refresh.add_argument("document_id")
    p_docs_refresh.add_argument("--root", default=".")
    p_docs_render = docs_sub.add_parser("render")
    p_docs_render.add_argument("--root", default=".")
    p_docs_render.add_argument("--check", action="store_true")

    p_pack = sub.add_parser("pack")
    p_pack.add_argument("task_id")
    p_pack.add_argument("--root", default=".")
    p_pack.add_argument("--output", default=None)

    p_worktree = sub.add_parser("worktree")
    worktree_sub = p_worktree.add_subparsers(dest="worktree_command", required=True)
    p_worktree_create = worktree_sub.add_parser("create")
    p_worktree_create.add_argument("task_id")
    p_worktree_create.add_argument("--root", default=".")
    p_worktree_remove = worktree_sub.add_parser("remove")
    p_worktree_remove.add_argument("task_id")
    p_worktree_remove.add_argument("--root", default=".")

    p_workspace = sub.add_parser("workspace")
    workspace_sub = p_workspace.add_subparsers(dest="workspace_command", required=True)
    p_workspace_register = workspace_sub.add_parser("register")
    p_workspace_register.add_argument("--root", required=True)
    workspace_sub.add_parser("list")
    p_workspace_unregister = workspace_sub.add_parser("unregister")
    p_workspace_unregister.add_argument("--root", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            root = Path(args.root).resolve()
            name = args.name or root.name
            results = init_repo(
                root,
                args.profile,
                name,
                args.task_prefix,
                github_templates=args.github_templates,
                workspace_mode=args.workspace_mode,
                github_authority=True if args.github_authority else None,
            )
            for line in results:
                print(line)
            return 0

        if args.command == "validate":
            root = Path(args.root).resolve()
            errors = validate_repo(root)
            if errors:
                for error in errors:
                    print(f"ERROR: {error}")
                print(f"INVALID: {len(errors)} error(s)")
                return 1
            print("VALID")
            return 0

        if args.command == "preflight":
            root = Path(args.root).resolve()
            mode, errors = preflight_repo(root)
            print(f"ROOT: {root}")
            print(f"MODE: {mode}")
            if mode == "TARGET_VALID":
                print("VALID")
                return 0
            for error in errors:
                print(f"ERROR: {error}")
            return 1 if mode == "INVALID_TARGET" else 2

        if args.command == "task" and args.task_command == "new":
            path = task_new(
                Path(args.root).resolve(),
                args.slug,
                args.goal,
                args.why,
                args.owner,
                args.priority,
                args.issue,
            )
            print(path)
            return 0

        if args.command == "issue" and args.issue_command == "verify":
            issue = verify_task_issue(Path(args.root).resolve(), args.task_id)
            print(f"ISSUE: {issue['url']}")
            print(f"STATE: {issue['state']}")
            print(f"TITLE: {issue['title']}")
            return 0

        if args.command == "workspace":
            registry_path = local_workspace_registry_path()
            roots = local_workspace_roots()
            if args.workspace_command == "register":
                register_local_workspace(Path(args.root))
                print("REGISTERED: local checkout (path stored only in this device's private registry)")
                return 0
            if args.workspace_command == "list":
                for item in roots:
                    print(item)
                if not roots:
                    print("EMPTY: no local checkouts registered")
                return 0
            if args.workspace_command == "unregister":
                target = Path(args.root).expanduser().resolve()
                roots = [item for item in roots if item != target]
                registry_path.parent.mkdir(parents=True, exist_ok=True)
                registry_path.write_text(
                    json.dumps({"version": 1, "roots": sorted(str(item) for item in roots)}, indent=2) + "\n",
                    encoding="utf-8",
                )
                if os.name != "nt":
                    os.chmod(registry_path.parent, 0o700)
                    os.chmod(registry_path, 0o600)
                print("UNREGISTERED: local checkout")
                return 0

        if args.command == "checkpoint":
            timestamp = args.time or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            request_id = args.request_id or uuid.uuid4().hex
            print(f"REQUEST_ID: {request_id}", flush=True)
            receipt_pair = require_receipt_pair(args.receipt_repo, args.receipt_issue)
            recovery_root = Path(args.recovery_root).resolve() if args.recovery_root else None
            path = checkpoint_task(
                Path(args.root).resolve(),
                args.task_id,
                args.agent,
                timestamp,
                args.completed or ["work completed"],
                args.evidence or ["no external evidence recorded"],
                args.decision or ["no new decisions"],
                args.changed or ["none"],
                args.blocked,
                args.next_action,
                recovery_root,
                request_id,
            )
            if recovery_root is not None and path.is_relative_to(recovery_root / ".continuity" / "recovery"):
                commit = publish_checkpoint(
                    recovery_root, path, args.task_id, args.next_action, recovery=True, request_id=request_id
                )
                print(f"DEGRADED_CONTINUITY: canonical checkpoint unavailable; recovery receipt written: {path}")
                print(f"PUSHED: {commit}")
            else:
                commit = publish_checkpoint(
                    Path(args.root).resolve(), path, args.task_id, args.next_action, request_id=request_id
                )
                print(path)
                print(f"PUSHED: {commit}")
                if receipt_pair is not None:
                    repository, issue_number = receipt_pair
                    comment_path = github_issue_comment_path(repository, issue_number)
                    fetched = run_external(
                        ["gh", "api", "--method", "GET", f"{comment_path}?per_page=100"],
                        Path(args.root).resolve(),
                    )
                    if fetched.returncode != 0:
                        detail = (fetched.stderr or fetched.stdout or "GitHub comment lookup failed").strip()
                        raise ContinuityError(receipt_failure_message(commit, detail))
                    payload_sha = hashlib.sha256(f"{args.task_id}\n{request_id}\n{commit}".encode()).hexdigest()
                    marker = render_receipt_marker(
                        repository=repository,
                        task_id=args.task_id,
                        request_id=request_id,
                        pushed_sha=commit,
                        destination=issue_number,
                        kind="leaf",
                        payload_sha256=payload_sha,
                    )

                    def run_post(command: list[str], body: str) -> subprocess.CompletedProcess[str]:
                        try:
                            return subprocess.run(
                                command,
                                input=body,
                                cwd=Path(args.root).resolve(),
                                capture_output=True,
                                text=True,
                                encoding="utf-8",
                                check=False,
                            )
                        except OSError as exc:
                            raise ContinuityError(f"could not run {command[0]}: {exc}") from exc

                    try:
                        decision = maybe_post_from_page(
                            fetched.stdout,
                            100,
                            marker=marker,
                            payload_sha256=payload_sha,
                            repository=repository,
                            issue_number=issue_number,
                            run=run_post,
                        )
                    except ContinuityError as exc:
                        raise ContinuityError(f"{exc}; push {commit} stands") from exc
                    print(f"RECEIPT: {decision}")
            return 0

        if args.command == "recovery" and args.recovery_command == "reconcile":
            path = reconcile_recovery(Path(args.root).resolve(), Path(args.file).resolve())
            print(path)
            return 0

        if args.command == "docs":
            root = Path(args.root).resolve()
            if args.docs_command == "init":
                catalog_path, view_path = initialize_document_catalog(root)
                print(f"INVENTORY: {catalog_path}")
                print(f"HUMAN_VIEW: {view_path}")
                return 0

            if args.docs_command == "add":
                record = upsert_document(
                    root,
                    args.document_id,
                    args.path,
                    args.title,
                    args.summary,
                    args.keyword,
                    args.related,
                    args.task,
                )
                print(f"REGISTERED: {record['id']} -> {record['path']}")
                return 0

            if args.docs_command == "find":
                catalog = load_document_catalog(root)
                errors = validate_document_catalog_data(root, catalog, document_task_ids(root, load_config(root)))
                if errors:
                    raise ContinuityError("document inventory is invalid: " + "; ".join(errors))
                if args.task and args.task not in document_task_ids(root, load_config(root)):
                    raise ContinuityError(f"task not found: {args.task}")
                matches = search_document_catalog(root, catalog, args.query, args.task)
                if not matches:
                    print(f"NO_MATCHES: {args.query}")
                    return 1
                print(f"QUERY: {args.query}")
                remote = remote_tracking_head(root)
                if remote:
                    print(
                        f"REMOTE_TRACKING: {remote[0]} @ {remote[1]} (cached ref; run `git fetch origin` before relying on freshness)"
                    )
                else:
                    print("REMOTE_TRACKING: unavailable; freshness is limited to the local checkout")
                matched_ids = {record["id"] for _, record in matches}
                neighbor_ids: set[str] = set()
                by_id = {record["id"]: record for record in catalog["documents"]}
                for _, record in matches:
                    neighbor_ids.update(item["id"] for item in document_neighbors(catalog, record["id"]))
                selected_ids = matched_ids | neighbor_ids
                remote_hashes = (
                    remote_document_hashes(
                        root,
                        remote[0],
                        [by_id[doc_id]["path"] for doc_id in sorted(selected_ids)],
                    )
                    if remote
                    else None
                )
                for score, record in matches:
                    freshness, _ = document_freshness(
                        root, record, include_remote=True, remote_hashes=remote_hashes
                    )
                    print(f"MATCH {record['id']} [{freshness}] score={score}")
                    print(f"  FILE: {record['path']}")
                    print(f"  TITLE: {record['title']}")
                    print(f"  SUMMARY: {record['summary']}")
                    print(f"  REVIEWED_AT: {record['reviewed_commit']} sha256={record['reviewed_sha256']}")
                for neighbor_id in sorted(neighbor_ids - matched_ids):
                    record = by_id[neighbor_id]
                    freshness, _ = document_freshness(
                        root, record, include_remote=True, remote_hashes=remote_hashes
                    )
                    print(f"RELATED {neighbor_id} [{freshness}]")
                    print(f"  FILE: {record['path']}")
                    print(f"  TITLE: {record['title']}")
                return 0

            if args.docs_command == "refresh":
                record = refresh_document(root, args.document_id)
                print(f"REVIEWED: {record['id']} at {record['reviewed_commit']} sha256={record['reviewed_sha256']}")
                return 0

            if args.docs_command == "render":
                catalog = load_document_catalog(root)
                errors = validate_document_catalog_data(root, catalog, document_task_ids(root, load_config(root)))
                if errors:
                    raise ContinuityError("document inventory is invalid: " + "; ".join(errors))
                view_path = managed_output_path(root, DOCUMENT_INDEX_PATH)
                expected = render_document_index(root, catalog)
                if args.check:
                    try:
                        actual = view_path.read_text(encoding="utf-8")
                    except OSError:
                        actual = ""
                    if actual != expected:
                        print(f"OUT_OF_DATE: {view_path}")
                        return 1
                    print(f"SYNCHRONIZED: {view_path}")
                    return 0
                view_path.parent.mkdir(parents=True, exist_ok=True)
                view_path.write_text(expected, encoding="utf-8")
                print(f"RENDERED: {view_path}")
                return 0

        if args.command == "pack":
            output = Path(args.output).resolve() if args.output else None
            path = pack_task(Path(args.root).resolve(), args.task_id, output)
            print(path)
            return 0

        if args.command == "worktree" and args.worktree_command == "create":
            workspace_root = Path(args.root).resolve()
            register_local_workspace(workspace_root)
            path, resumed = create_managed_worktree(workspace_root, args.task_id)
            print(f"{'RESUMED' if resumed else 'CREATED'}: {path}")
            return 0

        if args.command == "worktree" and args.worktree_command == "remove":
            path = remove_managed_worktree(Path(args.root).resolve(), args.task_id)
            print(f"REMOVED: {path}")
            return 0

        parser.error("unhandled command")
    except ContinuityError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2
