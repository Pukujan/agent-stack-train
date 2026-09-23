from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROTOCOL_VERSION = "0.1.0-draft"
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
    "context-pack": "context-pack.schema.json",
    "recovery": "recovery.schema.json",
}

BUILTIN_SCHEMAS = {'config': {'$id': 'https://project-continuity.dev/schema/v1/config.schema.json', '$schema': 'https://json-schema.org/draft/2020-12/schema', 'additionalProperties': False, 'properties': {'canonical': {'additionalProperties': False, 'properties': {'current': {'minLength': 1, 'type': 'string'}, 'project': {'minLength': 1, 'type': 'string'}, 'tasks': {'minLength': 1, 'type': 'string'}}, 'required': ['project', 'current', 'tasks'], 'type': 'object'}, 'profile': {'enum': ['minimal', 'software'], 'type': 'string'}, 'protocol': {'const': 'project-continuity'}, 'protocol_version': {'minLength': 1, 'type': 'string'}, 'schema': {'const': 'project-continuity.config.v1'}, 'schema_dir': {'const': 'schemas/v1'}, 'task_prefix': {'pattern': '^[A-Z][A-Z0-9]*$', 'type': 'string'}, 'trackers': {'additionalProperties': False, 'properties': {'beads': {'type': 'boolean'}, 'github': {'type': 'boolean'}}, 'required': ['github', 'beads'], 'type': 'object'}}, 'required': ['schema', 'protocol', 'protocol_version', 'profile', 'task_prefix', 'canonical', 'schema_dir', 'trackers'], 'title': 'Project Continuity Config v1', 'type': 'object'}, 'project': {'$id': 'https://project-continuity.dev/schema/v1/project.schema.json', '$schema': 'https://json-schema.org/draft/2020-12/schema', 'additionalProperties': False, 'properties': {'id': {'pattern': '^[a-z0-9][a-z0-9-]*$', 'type': 'string'}, 'protocol_version': {'minLength': 1, 'type': 'string'}, 'schema': {'const': 'project-continuity.project.v1'}, 'title': {'minLength': 1, 'type': 'string'}}, 'required': ['schema', 'protocol_version', 'id', 'title'], 'title': 'Project metadata v1', 'type': 'object'}, 'current': {'$id': 'https://project-continuity.dev/schema/v1/current.schema.json', '$schema': 'https://json-schema.org/draft/2020-12/schema', 'additionalProperties': False, 'properties': {'active_task': {'pattern': '^[A-Z][A-Z0-9]*-[0-9]{4}$', 'type': ['string', 'null']}, 'active_task_file': {'minLength': 1, 'type': ['string', 'null']}, 'protocol_version': {'minLength': 1, 'type': 'string'}, 'schema': {'const': 'project-continuity.current.v1'}}, 'required': ['schema', 'protocol_version', 'active_task', 'active_task_file'], 'title': 'Current checkpoint metadata v1', 'type': 'object'}, 'task': {'$id': 'https://project-continuity.dev/schema/v1/task.schema.json', '$schema': 'https://json-schema.org/draft/2020-12/schema', 'additionalProperties': False, 'properties': {'acceptance': {'items': {'minLength': 1, 'type': 'string'}, 'minItems': 1, 'type': 'array'}, 'depends_on': {'items': {'minLength': 1, 'type': 'string'}, 'type': 'array'}, 'goal': {'minLength': 1, 'type': 'string'}, 'id': {'pattern': '^[A-Z][A-Z0-9]*-[0-9]{4}$', 'type': 'string'}, 'next_action': {'minLength': 1, 'type': 'string'}, 'owner': {'minLength': 1, 'type': 'string'}, 'priority': {'minLength': 1, 'type': 'string'}, 'protocol_version': {'minLength': 1, 'type': 'string'}, 'schema': {'const': 'project-continuity.task.v1'}, 'status': {'enum': ['queued', 'active', 'blocked', 'completed', 'cancelled'], 'type': 'string'}, 'why': {'minLength': 1, 'type': 'string'}}, 'required': ['schema', 'protocol_version', 'id', 'status', 'owner', 'priority', 'depends_on', 'goal', 'why', 'acceptance', 'next_action'], 'title': 'Task metadata v1', 'type': 'object'}, 'checkpoint': {'$id': 'https://project-continuity.dev/schema/v1/checkpoint.schema.json', '$schema': 'https://json-schema.org/draft/2020-12/schema', 'additionalProperties': False, 'properties': {'agent': {'minLength': 1, 'type': 'string'}, 'blocked': {'items': {'minLength': 1, 'type': 'string'}, 'type': 'array'}, 'changed': {'items': {'minLength': 1, 'type': 'string'}, 'minItems': 1, 'type': 'array'}, 'completed': {'items': {'minLength': 1, 'type': 'string'}, 'minItems': 1, 'type': 'array'}, 'decisions': {'items': {'minLength': 1, 'type': 'string'}, 'minItems': 1, 'type': 'array'}, 'evidence': {'items': {'minLength': 1, 'type': 'string'}, 'minItems': 1, 'type': 'array'}, 'next_action': {'minLength': 1, 'type': 'string'}, 'protocol_version': {'minLength': 1, 'type': 'string'}, 'schema': {'const': 'project-continuity.checkpoint.v1'}, 'task_id': {'pattern': '^[A-Z][A-Z0-9]*-[0-9]{4}$', 'type': 'string'}, 'timestamp': {'minLength': 1, 'type': 'string'}}, 'required': ['schema', 'protocol_version', 'task_id', 'timestamp', 'agent', 'completed', 'evidence', 'decisions', 'changed', 'blocked', 'next_action'], 'title': 'Checkpoint metadata v1', 'type': 'object'}, 'context-pack': {'$id': 'https://project-continuity.dev/schema/v1/context-pack.schema.json', '$schema': 'https://json-schema.org/draft/2020-12/schema', 'additionalProperties': False, 'properties': {'commit': {'minLength': 1, 'type': 'string'}, 'generated_at': {'minLength': 1, 'type': 'string'}, 'protocol_version': {'minLength': 1, 'type': 'string'}, 'ref': {'minLength': 1, 'type': 'string'}, 'repository': {'minLength': 1, 'type': 'string'}, 'schema': {'const': 'project-continuity.context-pack.v1'}, 'sources': {'items': {'minLength': 1, 'type': 'string'}, 'minItems': 3, 'type': 'array'}, 'task_id': {'pattern': '^[A-Z][A-Z0-9]*-[0-9]{4}$', 'type': 'string'}}, 'required': ['schema', 'protocol_version', 'repository', 'ref', 'commit', 'task_id', 'generated_at', 'sources'], 'title': 'Context pack metadata v1', 'type': 'object'}}


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
        return load_json(path)
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
        if not any(isinstance(instance, type_map[t]) and not (t == "integer" and isinstance(instance, bool)) for t in types):
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
        "## Program state\n\nPhase: bootstrap.\n\n"
        "## Completed\n\n- continuity protocol initialized.\n\n"
        "## Active\n\n- none.\n\n"
        "## Queued\n\n- create the first bounded task.\n\n"
        "## Blockers\n\nNone known.\n\n"
        "## Next atomic action\n\n"
        f"Create the first {prefix} task with `continuity task new`.\n"
    )


def handoff_template() -> str:
    return (
        "# Current Handoff\n\n"
        "Start from repository state, not prior chat history.\n\n"
        "## Read order\n\n"
        "1. `PROJECT.md`\n"
        "2. `AGENTS.md` when present\n"
        "3. `checkpoints/CURRENT.md`\n"
        "4. the active task named by CURRENT\n"
        "5. the minimum relevant specification/design document\n\n"
        "## Authority\n\nCanonical repository files are authoritative. Tracker items and context packs are mirrors/derived views.\n\n"
        "## Degraded continuity\n\n"
        "Execution safety and existing authorization outrank continuity bookkeeping. If a canonical continuity file is temporarily unavailable, do not stop safe work, repair storage just to force a checkpoint, or ask again for an already-authorized host/worktree. Use an authorized alternate checkout and run `continuity checkpoint <TASK-ID> --root <canonical-root> --recovery-root <alternate-root> ...` to write a JSON recovery receipt under `.continuity/recovery/`; do not create an ad-hoc Markdown checkpoint or replace the alternate task file. Reconcile it into the canonical task with `continuity recovery reconcile --root <canonical-root> --file <receipt>` when writable. The repository/task lineage is authoritative; a physical path is not.\n\n"
        "Normal checkpointing is a delivery operation, not a local note: commit the product change first, then run `continuity checkpoint`. The command commits the canonical checkpoint and pushes the task branch to `origin`; it fails rather than silently leaving a normal checkpoint local. CI runs on the pushed branch and the repository's pull-request automation merges it after required checks pass.\n"
    )


def agents_template() -> str:
    workspace_rules = (
        "## Canonical checkout\n\n"
        "- Identify and reuse the one canonical checkout by host/path and normalized Git remote.\n"
        "- Do not create clones, task folders, or linked Git worktrees anywhere.\n"
        "- Run tasks sequentially on branches in the canonical checkout. Before switching tasks, commit and push the checkpoint, open or update its PR, pass required CI, merge, then fast-forward this same checkout.\n"
        "- Reuse the repository's one root dependency environment; do not install per-task `.venv` or `node_modules` copies.\n\n"
    )
    return (
        "# Agent Operating Contract\n\n"
        "## Start\n\n"
        "Read PROJECT → CURRENT → active TASK → minimum relevant spec before editing.\n\n"
        "## Scope\n\n"
        "Work only inside the active bounded task. Split or revise the task before materially expanding scope.\n\n"
        + workspace_rules
        + "## Checkpoint\n\n"
        "Before stopping after meaningful work, append completed work, exact evidence, decisions, changed paths, blockers, and one next atomic action.\n\n"
        "If canonical continuity state is temporarily unavailable, treat that as degraded continuity rather than an execution blocker: keep safe authorized work moving, use an already-authorized alternate checkout/host, and run `continuity checkpoint <TASK-ID> --root <canonical-root> --recovery-root <alternate-root> --agent <name> --completed <work> --evidence <result> --next <next-action>` to write the JSON recovery receipt under `.continuity/recovery/`. Do not write an ad-hoc checkpoint under `checkpoints/`, replace the alternate task file, treat a physical worktree as project identity, repair storage merely to write a checkpoint, or request redundant permission. Reconcile later with `continuity recovery reconcile --root <canonical-root> --file <receipt>`.\n\n"
        "For a normal checkpoint, commit the product change first and then run `continuity checkpoint`; it commits and pushes the checkpoint to the task branch. A normal checkpoint is not complete while it exists only in a local worktree. CI and pull-request automation take the pushed branch through validation and merge.\n"
    )


def readme_template(name: str) -> str:
    return (
        f"# {name}\n\n"
        "This repository uses Project Continuity Protocol.\n\n"
        "Point a fresh agent/session to `HANDOFF.md`; it contains the cold-start read order.\n"
    )


def init_repo(
    root: Path,
    profile: str,
    name: str,
    prefix: str,
) -> list[str]:
    if profile not in {"minimal", "software"}:
        raise ContinuityError(f"unsupported profile: {profile}")
    prefix = prefix.upper()
    if re.fullmatch(r"[A-Z][A-Z0-9]*", prefix) is None:
        raise ContinuityError("task prefix must match [A-Z][A-Z0-9]*")
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
        "trackers": {"github": False, "beads": False},
    }

    planned = {
        ".continuity/config.json": json.dumps(config, indent=2, sort_keys=True) + "\n",
        "PROJECT.md": project_template(name),
        "checkpoints/CURRENT.md": current_template(prefix),
        "HANDOFF.md": handoff_template(),
    }
    for kind, filename in SCHEMA_FILES.items():
        planned[f"schemas/v1/{filename}"] = json.dumps(
            BUILTIN_SCHEMAS[kind], indent=2, sort_keys=True
        ) + "\n"
    if profile == "software":
        planned["AGENTS.md"] = agents_template()
        planned["README.md"] = readme_template(name)

    conflicts = [
        rel for rel, content in planned.items()
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


def task_new(root: Path, slug: str, goal: str, why: str, owner: str, priority: str) -> Path:
    config = load_config(root)
    task_id = next_task_id(root, config)
    slug = slugify(slug)
    tasks_dir: str = config["canonical"]["tasks"]
    path = root / tasks_dir / f"TASK-{task_id}-{slug}.md"
    meta = {
        "schema": "project-continuity.task.v1",
        "protocol_version": config["protocol_version"],
        "id": task_id,
        "status": "active",
        "owner": owner,
        "priority": priority,
        "depends_on": [],
        "goal": goal,
        "why": why,
        "acceptance": ["define task-specific acceptance criteria"],
        "next_action": "replace placeholder acceptance criteria, then begin bounded work",
    }
    content = (
        f"# TASK-{task_id} — {slug.replace('-', ' ').title()}\n\n"
        f"{marker('task', meta)}\n\n"
        f"- Status: active\n- Owner: {owner}\n- Priority: {priority}\n- Depends on: none\n\n"
        f"## Goal\n\n{goal}\n\n## Why\n\n{why}\n\n"
        "## Allowed files\n\n- define bounded paths before implementation.\n\n"
        "## Acceptance criteria\n\n- [ ] define task-specific acceptance criteria.\n\n"
        "## Checkpoint log\n\n"
        "No checkpoints yet.\n\n"
        "## Handoff\n\n"
        "Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.\n"
    )
    write_file_no_overwrite(path, content)
    return path


def validate_checkpoint_structure(root: Path, task_path: Path, text: str) -> list[str]:
    errors: list[str] = []
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
        required_sections = SECTION_NAMES if meta is not None else (
            "Completed:", "Evidence:", "Decisions:", "Blocked/uncertain:", "Next:"
        )
        missing = [name for name in required_sections if name not in body]
        if missing:
            errors.append(f"{task_path}: checkpoint {index} missing sections: {', '.join(missing)}")
        if meta is not None:
            for err in validate_schema(meta, load_schema(root, "checkpoint")):
                errors.append(f"{task_path}: checkpoint {index}: {err}")
    return errors


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
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        return [f"could not inspect registered Git worktrees: {exc}"]

    worktrees = [
        line.removeprefix("worktree ")
        for line in result.stdout.splitlines()
        if line.startswith("worktree ")
    ]

    def normalize(path: str | Path) -> str:
        return str(Path(path).resolve()).replace("\\", "/").casefold()

    if len(worktrees) != 1 or normalize(worktrees[0]) != normalize(root):
        found = ", ".join(worktrees) if worktrees else "none"
        return [(
            "single-checkout mode requires exactly one registered Git worktree "
            f"at {root}; found: {found}"
        )]
    return []


def validate_repo(root: Path) -> list[str]:
    errors: list[str] = []
    config_path = root / ".continuity" / "config.json"
    try:
        config = load_json(config_path)
    except ContinuityError as exc:
        return [str(exc)]

    if "workspace_mode" in config:
        return [(
            f"{config_path}: unsupported legacy key 'workspace_mode'; "
            "migration required: remove this key from .continuity/config.json, then run continuity validate again. "
            "Validation does not modify configuration."
        )]

    try:
        config_errors = [
            f"{config_path}: {e}"
            for e in validate_schema(config, load_schema(root, "config"))
        ]
        errors.extend(config_errors)
    except ContinuityError as exc:
        errors.append(str(exc))
        return sorted(set(errors))

    # Invalid config is a terminal structural error. Do not index required
    # keys after schema validation has already established that they are absent.
    if config_errors:
        return sorted(set(errors))

    errors.extend(validate_single_checkout(root))

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
        errors.extend(validate_checkpoint_structure(root, path, text))

    for _task_id, (path, meta) in tasks_by_id.items():
        for dep in meta.get("depends_on", []):
            if dep.startswith("external:"):
                continue
            if dep not in tasks_by_id:
                errors.append(f"{path}: dependency does not resolve: {dep}")

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
                    f"{receipt_path}: {error}"
                    for error in validate_schema(receipt, load_schema(root, "recovery"))
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


def checkpoint_addition(meta: dict[str, Any]) -> str:
    human_time = meta["timestamp"].replace("T", " ").replace("Z", " UTC")
    return "\n".join(
        [
            "",
            f"### {human_time} — {meta['agent']}",
            "",
            marker("checkpoint", meta),
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


def recovery_path(recovery_root: Path, task_id: str, timestamp: str) -> Path:
    safe_time = re.sub(r"[^0-9A-Za-z-]", "", timestamp)
    return recovery_root / ".continuity" / "recovery" / f"{task_id}-{safe_time}.json"


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
    path = recovery_path(recovery_root, task_id, timestamp)
    content = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
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
) -> Path:
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
        addition = checkpoint_addition(meta)
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
        )


def reconcile_recovery(root: Path, receipt_path: Path) -> Path:
    receipt = load_json(receipt_path)
    if receipt.get("schema") != "project-continuity.recovery.v1":
        raise ContinuityError(f"invalid recovery receipt schema: {receipt_path}")
    if receipt.get("status") == "reconciled":
        raise ContinuityError(f"recovery receipt is already reconciled: {receipt_path}")
    checkpoint = receipt.get("checkpoint")
    if not isinstance(checkpoint, dict):
        raise ContinuityError(f"recovery receipt has no checkpoint: {receipt_path}")
    task_id = checkpoint.get("task_id")
    required = (
        "task_id", "agent", "timestamp", "completed", "evidence", "decisions", "changed", "blocked", "next_action"
    )
    if not all(key in checkpoint for key in required) or not isinstance(task_id, str):
        raise ContinuityError(f"recovery receipt checkpoint is incomplete: {receipt_path}")
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
    )
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
        )
    except FileNotFoundError as exc:
        raise ContinuityError("git is required for checkpoint publishing") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "git command failed").strip()
        raise ContinuityError(f"git {' '.join(args)} failed: {detail}") from exc


def publish_checkpoint(
    root: Path, checkpoint_path: Path, task_id: str, next_action: str, recovery: bool = False
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
    if relative not in staged:
        raise ContinuityError(f"checkpoint produced no staged change: {checkpoint_path}")

    kind = "recovery receipt" if recovery else "checkpoint"
    message = f"PCM {kind} {task_id}: {next_action}"
    git_run(root, ["commit", "-m", message])
    commit = git_value(root, ["rev-parse", "HEAD"])
    git_run(root, ["push", "--set-upstream", remote, f"HEAD:{branch}"])
    return commit


def pack_task(root: Path, task_id: str, output: Path | None) -> Path:
    config = load_config(root)
    task_path = find_task(root, config, task_id)
    project_path = root / config["canonical"]["project"]
    current_path = root / config["canonical"]["current"]
    sources = [
        project_path.relative_to(root).as_posix(),
        current_path.relative_to(root).as_posix(),
        task_path.relative_to(root).as_posix(),
    ]
    for optional in ("SPEC.md", "AGENTS.md"):
        if (root / optional).exists():
            sources.append(optional)
    repo = git_value(root, ["config", "--get", "remote.origin.url"], root.name)
    ref = git_value(root, ["rev-parse", "--abbrev-ref", "HEAD"])
    commit = git_value(root, ["rev-parse", "HEAD"])
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
    ]
    for rel in sources:
        chunks += [f"## Source: `{rel}`", "", (root / rel).read_text(encoding="utf-8").rstrip(), ""]
    if output is None:
        output = root / ".continuity" / "packs" / f"{task_id}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="continuity")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("--root", default=".")
    p_init.add_argument("--profile", choices=["minimal", "software"], default="minimal")
    p_init.add_argument("--name", default=None)
    p_init.add_argument("--task-prefix", default="TASK")

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

    p_checkpoint = sub.add_parser("checkpoint")
    p_checkpoint.add_argument("task_id")
    p_checkpoint.add_argument("--root", default=".")
    p_checkpoint.add_argument("--agent", required=True)
    p_checkpoint.add_argument("--time", default=None)
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

    p_recovery = sub.add_parser("recovery")
    recovery_sub = p_recovery.add_subparsers(dest="recovery_command", required=True)
    p_reconcile = recovery_sub.add_parser("reconcile")
    p_reconcile.add_argument("--root", required=True)
    p_reconcile.add_argument("--file", required=True)

    p_pack = sub.add_parser("pack")
    p_pack.add_argument("task_id")
    p_pack.add_argument("--root", default=".")
    p_pack.add_argument("--output", default=None)

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
            )
            print(path)
            return 0

        if args.command == "checkpoint":
            timestamp = args.time or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
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
            )
            if recovery_root is not None and path.is_relative_to(recovery_root / ".continuity" / "recovery"):
                commit = publish_checkpoint(recovery_root, path, args.task_id, args.next_action, recovery=True)
                print(f"DEGRADED_CONTINUITY: canonical checkpoint unavailable; recovery receipt written: {path}")
                print(f"PUSHED: {commit}")
            else:
                commit = publish_checkpoint(Path(args.root).resolve(), path, args.task_id, args.next_action)
                print(path)
                print(f"PUSHED: {commit}")
            return 0

        if args.command == "recovery" and args.recovery_command == "reconcile":
            path = reconcile_recovery(Path(args.root).resolve(), Path(args.file).resolve())
            print(path)
            return 0

        if args.command == "pack":
            output = Path(args.output).resolve() if args.output else None
            path = pack_task(Path(args.root).resolve(), args.task_id, output)
            print(path)
            return 0

        parser.error("unhandled command")
    except ContinuityError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2
