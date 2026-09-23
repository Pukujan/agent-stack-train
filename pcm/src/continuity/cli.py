from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
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
}

BUILTIN_SCHEMAS = {'config': {'$id': 'https://project-continuity.dev/schema/v1/config.schema.json', '$schema': 'https://json-schema.org/draft/2020-12/schema', 'additionalProperties': False, 'properties': {'canonical': {'additionalProperties': False, 'properties': {'current': {'minLength': 1, 'type': 'string'}, 'project': {'minLength': 1, 'type': 'string'}, 'tasks': {'minLength': 1, 'type': 'string'}}, 'required': ['project', 'current', 'tasks'], 'type': 'object'}, 'profile': {'enum': ['minimal', 'software'], 'type': 'string'}, 'protocol': {'const': 'project-continuity'}, 'protocol_version': {'minLength': 1, 'type': 'string'}, 'schema': {'const': 'project-continuity.config.v1'}, 'schema_dir': {'const': 'schemas/v1'}, 'task_prefix': {'pattern': '^[A-Z][A-Z0-9]*$', 'type': 'string'}, 'trackers': {'additionalProperties': False, 'properties': {'beads': {'type': 'boolean'}, 'github': {'type': 'boolean'}}, 'required': ['github', 'beads'], 'type': 'object'}}, 'required': ['schema', 'protocol', 'protocol_version', 'profile', 'task_prefix', 'canonical', 'schema_dir', 'trackers'], 'title': 'Project Continuity Config v1', 'type': 'object'}, 'project': {'$id': 'https://project-continuity.dev/schema/v1/project.schema.json', '$schema': 'https://json-schema.org/draft/2020-12/schema', 'additionalProperties': False, 'properties': {'id': {'pattern': '^[a-z0-9][a-z0-9-]*$', 'type': 'string'}, 'protocol_version': {'minLength': 1, 'type': 'string'}, 'schema': {'const': 'project-continuity.project.v1'}, 'title': {'minLength': 1, 'type': 'string'}}, 'required': ['schema', 'protocol_version', 'id', 'title'], 'title': 'Project metadata v1', 'type': 'object'}, 'current': {'$id': 'https://project-continuity.dev/schema/v1/current.schema.json', '$schema': 'https://json-schema.org/draft/2020-12/schema', 'additionalProperties': False, 'properties': {'active_task': {'pattern': '^[A-Z][A-Z0-9]*-[0-9]{4}$', 'type': ['string', 'null']}, 'active_task_file': {'minLength': 1, 'type': ['string', 'null']}, 'protocol_version': {'minLength': 1, 'type': 'string'}, 'schema': {'const': 'project-continuity.current.v1'}}, 'required': ['schema', 'protocol_version', 'active_task', 'active_task_file'], 'title': 'Current checkpoint metadata v1', 'type': 'object'}, 'task': {'$id': 'https://project-continuity.dev/schema/v1/task.schema.json', '$schema': 'https://json-schema.org/draft/2020-12/schema', 'additionalProperties': False, 'properties': {'acceptance': {'items': {'minLength': 1, 'type': 'string'}, 'minItems': 1, 'type': 'array'}, 'depends_on': {'items': {'minLength': 1, 'type': 'string'}, 'type': 'array'}, 'goal': {'minLength': 1, 'type': 'string'}, 'id': {'pattern': '^[A-Z][A-Z0-9]*-[0-9]{4}$', 'type': 'string'}, 'next_action': {'minLength': 1, 'type': 'string'}, 'owner': {'minLength': 1, 'type': 'string'}, 'priority': {'minLength': 1, 'type': 'string'}, 'protocol_version': {'minLength': 1, 'type': 'string'}, 'schema': {'const': 'project-continuity.task.v1'}, 'status': {'enum': ['queued', 'active', 'blocked', 'completed', 'cancelled'], 'type': 'string'}, 'why': {'minLength': 1, 'type': 'string'}}, 'required': ['schema', 'protocol_version', 'id', 'status', 'owner', 'priority', 'depends_on', 'goal', 'why', 'acceptance', 'next_action'], 'title': 'Task metadata v1', 'type': 'object'}, 'checkpoint': {'$id': 'https://project-continuity.dev/schema/v1/checkpoint.schema.json', '$schema': 'https://json-schema.org/draft/2020-12/schema', 'additionalProperties': False, 'properties': {'agent': {'minLength': 1, 'type': 'string'}, 'blocked': {'items': {'minLength': 1, 'type': 'string'}, 'type': 'array'}, 'changed': {'items': {'minLength': 1, 'type': 'string'}, 'minItems': 1, 'type': 'array'}, 'completed': {'items': {'minLength': 1, 'type': 'string'}, 'minItems': 1, 'type': 'array'}, 'decisions': {'items': {'minLength': 1, 'type': 'string'}, 'minItems': 1, 'type': 'array'}, 'evidence': {'items': {'minLength': 1, 'type': 'string'}, 'minItems': 1, 'type': 'array'}, 'next_action': {'minLength': 1, 'type': 'string'}, 'protocol_version': {'minLength': 1, 'type': 'string'}, 'schema': {'const': 'project-continuity.checkpoint.v1'}, 'task_id': {'pattern': '^[A-Z][A-Z0-9]*-[0-9]{4}$', 'type': 'string'}, 'timestamp': {'minLength': 1, 'type': 'string'}}, 'required': ['schema', 'protocol_version', 'task_id', 'timestamp', 'agent', 'completed', 'evidence', 'decisions', 'changed', 'blocked', 'next_action'], 'title': 'Checkpoint metadata v1', 'type': 'object'}, 'context-pack': {'$id': 'https://project-continuity.dev/schema/v1/context-pack.schema.json', '$schema': 'https://json-schema.org/draft/2020-12/schema', 'additionalProperties': False, 'properties': {'commit': {'minLength': 1, 'type': 'string'}, 'generated_at': {'minLength': 1, 'type': 'string'}, 'protocol_version': {'minLength': 1, 'type': 'string'}, 'ref': {'minLength': 1, 'type': 'string'}, 'repository': {'minLength': 1, 'type': 'string'}, 'schema': {'const': 'project-continuity.context-pack.v1'}, 'sources': {'items': {'minLength': 1, 'type': 'string'}, 'minItems': 3, 'type': 'array'}, 'task_id': {'pattern': '^[A-Z][A-Z0-9]*-[0-9]{4}$', 'type': 'string'}}, 'required': ['schema', 'protocol_version', 'repository', 'ref', 'commit', 'task_id', 'generated_at', 'sources'], 'title': 'Context pack metadata v1', 'type': 'object'}}


class ContinuityError(Exception):
    pass


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
        "## Authority\n\nCanonical repository files are authoritative. Tracker items and context packs are mirrors/derived views.\n"
    )


def agents_template() -> str:
    return (
        "# Agent Operating Contract\n\n"
        "## Start\n\n"
        "Read PROJECT → CURRENT → active TASK → minimum relevant spec before editing.\n\n"
        "## Scope\n\n"
        "Work only inside the active bounded task. Split or revise the task before materially expanding scope.\n\n"
        "## Canonical checkout and worktree\n\n"
        "- Identify the single canonical checkout by host/path and normalized Git remote, then reuse it.\n"
        "- Do not create another clone or sibling project folder for a task.\n"
        "- When isolation is needed, reuse a registered linked worktree or create one under `<canonical-root>/.worktrees/<task-slug>`; ensure `.worktrees/` is ignored.\n"
        "- Record the canonical root separately from the task worktree. If the root is ambiguous or unavailable, resolve it before creating a directory.\n\n"
        "## Checkpoint\n\n"
        "Before stopping after meaningful work, append completed work, exact evidence, decisions, changed paths, blockers, and one next atomic action.\n"
    )


def readme_template(name: str) -> str:
    return (
        f"# {name}\n\n"
        "This repository uses Project Continuity Protocol.\n\n"
        "Point a fresh agent/session to `HANDOFF.md`; it contains the cold-start read order.\n"
    )


def init_repo(root: Path, profile: str, name: str, prefix: str) -> list[str]:
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
    return extract_marker(path.read_text(encoding="utf-8"), "task")


def find_task(root: Path, config: dict[str, Any], task_id: str) -> Path:
    for path in task_files(root, config):
        meta = task_metadata(path)
        if meta and meta.get("id") == task_id:
            return path
        if path.name.startswith(f"TASK-{task_id}-") or path.name == f"TASK-{task_id}.md":
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
    path = root / config["canonical"]["tasks"] / f"TASK-{task_id}-{slug}.md"
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


def validate_repo(root: Path) -> list[str]:
    errors: list[str] = []
    config_path = root / ".continuity" / "config.json"
    try:
        config = load_json(config_path)
    except ContinuityError as exc:
        return [str(exc)]

    try:
        errors.extend(f"{config_path}: {e}" for e in validate_schema(config, load_schema(root, "config")))
    except ContinuityError as exc:
        errors.append(str(exc))
        return sorted(errors)

    canonical = config.get("canonical", {})
    project_path = root / canonical.get("project", "PROJECT.md")
    current_path = root / canonical.get("current", "checkpoints/CURRENT.md")

    for kind, path in (("project", project_path), ("current", current_path)):
        if not path.exists():
            errors.append(f"missing canonical {kind}: {path}")
            continue
        text = path.read_text(encoding="utf-8")
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
        try:
            current_meta = extract_marker(current_path.read_text(encoding="utf-8"), "current")
        except ContinuityError:
            pass

    tasks_by_id: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in task_files(root, config):
        text = path.read_text(encoding="utf-8")
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
        if isinstance(task_id, str) and not task_id.startswith(config["task_prefix"] + "-"):
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

    for task_id, (path, meta) in tasks_by_id.items():
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
        if active_id is not None:
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
    return sorted(set(errors))


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
) -> Path:
    config = load_config(root)
    path = find_task(root, config, task_id)
    original = path.read_text(encoding="utf-8")
    meta = {
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
    human_time = timestamp.replace("T", " ").replace("Z", " UTC")
    entry = [
        "",
        f"### {human_time} — {agent}",
        "",
        marker("checkpoint", meta),
        "",
        "Completed:",
        *[f"- {item}" for item in completed],
        "",
        "Evidence:",
        *[f"- {item}" for item in evidence],
        "",
        "Decisions:",
        *[f"- {item}" for item in decisions],
        "",
        "Changed:",
        *[f"- {item}" for item in changed],
        "",
        "Blocked/uncertain:",
        *[f"- {item}" for item in (blocked or ["none"])],
        "",
        "Next:",
        f"- {next_action}",
        "",
    ]
    addition = "\n".join(entry)
    if "## Handoff" in original:
        before, after = original.split("## Handoff", 1)
        new_text = before.rstrip() + "\n" + addition + "\n## Handoff" + after
    else:
        new_text = original.rstrip() + "\n" + addition
    if not new_text.startswith(original.split("## Handoff", 1)[0].rstrip()):
        raise ContinuityError("checkpoint append invariant failed")
    path.write_text(new_text, encoding="utf-8")
    return path


def git_value(root: Path, args: list[str], fallback: str | None = None) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
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
    generated = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
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
            results = init_repo(root, args.profile, name, args.task_prefix)
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
            timestamp = args.time or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
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
            )
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
