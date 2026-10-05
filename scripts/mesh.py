#!/usr/bin/env python3
"""Keep the four stack repos on each other's current version.

stack-releases.json is the mesh. Each of project-continuity-modules,
content-generation-modules, agent-custom-setup, and observational-issue-ops
must require every component in that file, including itself. An older
version or commit fails the check. ``--write`` rewrites the local
stack-mesh.json (and a checkout pin left in CI) to those versions.

Usage:
    python scripts/mesh.py --check --root . --component content-generation-modules
    python scripts/mesh.py --write --root .
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

COMPONENTS = (
    "project-continuity-modules",
    "content-generation-modules",
    "agent-custom-setup",
    "observational-issue-ops",
)
SOURCE = "https://raw.githubusercontent.com/Pukujan/agent-stack-train/main/stack-releases.json"
MESH_NAME = "stack-mesh.json"
PCM_PIN = re.compile(r"^(\s*PCM_PIN:\s*)(\S+)\s*$", re.MULTILINE)
VERSION_RE = re.compile(r"__version__\s*=\s*[\"']([^\"']+)[\"']")

# Where a component records its own version. Missing file means the repo is
# not that component, or (for observational-issue-ops) the version lives only
# on the release the mesh already recorded.
OWN_VERSION = {
    "project-continuity-modules": ("src/continuity/__init__.py", "python"),
    "content-generation-modules": ("system-version.json", "json"),
    "agent-custom-setup": ("registry.json", "json"),
}


class MeshError(Exception):
    """The mesh file or a local declaration could not be read."""


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise MeshError(f"{path} is missing") from None
    except json.JSONDecodeError as exc:
        raise MeshError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise MeshError(f"{path} must contain a JSON object")
    return data


def fetch_mesh(url: str = SOURCE) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "agent-stack-train-mesh"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        raise MeshError(f"could not read the mesh at {url}: {exc}") from exc
    if not isinstance(data, dict):
        raise MeshError(f"{url} must return a JSON object")
    return data


def apply_release(mesh: dict, component: str, version: str, commit: str) -> dict:
    """Move one component. The other three stay, and every repo must follow."""
    if component not in COMPONENTS:
        raise MeshError(f"unknown component {component}")
    updated = json.loads(json.dumps(mesh))
    certified = updated.setdefault("certified", {})
    entry = dict(certified.get(component) or {})
    entry["version"] = version
    entry["commit"] = commit
    certified[component] = entry
    return updated


def declaration_from(mesh: dict) -> dict:
    certified = mesh.get("certified")
    if not isinstance(certified, dict):
        raise MeshError("mesh has no certified object")
    requires = {}
    for name in COMPONENTS:
        entry = certified.get(name)
        if not isinstance(entry, dict) or "version" not in entry or "commit" not in entry:
            raise MeshError(f"mesh is missing version and commit for {name}")
        requires[name] = {"version": entry["version"], "commit": entry["commit"]}
    return {"source": SOURCE, "requires": requires}


def declaration_problems(mesh: dict, declaration: dict) -> list[str]:
    """Fail when a repo requires anything other than the mesh versions."""
    required = declaration_from(mesh)["requires"]
    got = declaration.get("requires") if isinstance(declaration, dict) else None
    if not isinstance(got, dict):
        return [f"{MESH_NAME} must require every component at the mesh version"]
    errors = []
    for name, spec in required.items():
        actual = got.get(name)
        if not isinstance(actual, dict):
            errors.append(f"{name}: missing; the mesh requires {spec['version']} {spec['commit']}")
            continue
        if actual.get("version") != spec["version"] or actual.get("commit") != spec["commit"]:
            errors.append(
                f"{name}: requires {actual.get('version')} {actual.get('commit')}; "
                f"the mesh requires {spec['version']} {spec['commit']}"
            )
    return errors


def _read_version(path: Path, kind: str) -> str | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    if kind == "python":
        found = VERSION_RE.search(text)
        return found.group(1) if found else None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    version = data.get("version") if isinstance(data, dict) else None
    return version if isinstance(version, str) else None


def own_version_problems(mesh: dict, root: Path, component: str) -> list[str]:
    spec = OWN_VERSION.get(component)
    if spec is None:
        return []
    rel, kind = spec
    expected = declaration_from(mesh)["requires"][component]["version"]
    found = _read_version(root / rel, kind)
    if found is None:
        return [f"{component}: {rel} must declare version {expected}"]
    if found != expected:
        return [f"{component}: {rel} is {found}; the mesh requires {expected}"]
    return []


def _replace_pcm_pin(text: str, commit: str) -> str:
    return PCM_PIN.sub(lambda match: f"{match.group(1)}{commit}", text)


def pin_problems(mesh: dict, root: Path) -> list[str]:
    """A leftover checkout pin in CI is an older version this repo would install."""
    errors = []
    required = declaration_from(mesh)["requires"]["project-continuity-modules"]["commit"]
    workflow = root / ".github" / "workflows" / "ci.yml"
    if workflow.is_file():
        text = workflow.read_text(encoding="utf-8")
        found = PCM_PIN.search(text)
        if found and found.group(2) != required:
            errors.append(
                f".github/workflows/ci.yml PCM_PIN is {found.group(2)}; "
                f"the mesh requires {required}"
            )
    return errors


def check_repo(mesh: dict, root: Path, component: str) -> list[str]:
    if component not in COMPONENTS:
        raise MeshError(f"unknown component {component}")
    path = root / MESH_NAME
    if not path.is_file():
        errors = [f"missing {MESH_NAME}; this repo must require every component at the mesh version"]
    else:
        try:
            declaration = load_json(path)
        except MeshError as exc:
            errors = [str(exc)]
        else:
            errors = declaration_problems(mesh, declaration)
    errors.extend(own_version_problems(mesh, root, component))
    errors.extend(pin_problems(mesh, root))
    return errors


def write_repo(mesh: dict, root: Path) -> list[Path]:
    """Rewrite the local requirement file and a CI checkout pin to the mesh."""
    written = []
    path = root / MESH_NAME
    path.write_text(json.dumps(declaration_from(mesh), indent=2) + "\n", encoding="utf-8", newline="\n")
    written.append(path)
    workflow = root / ".github" / "workflows" / "ci.yml"
    if workflow.is_file():
        commit = declaration_from(mesh)["requires"]["project-continuity-modules"]["commit"]
        text = workflow.read_text(encoding="utf-8")
        updated = _replace_pcm_pin(text, commit)
        if updated != text:
            workflow.write_text(updated, encoding="utf-8", newline="\n")
            written.append(workflow)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--component", default="")
    parser.add_argument("--mesh", type=Path, default=None, help="Local stack-releases.json. Defaults to GitHub.")
    args = parser.parse_args(argv)

    try:
        document = load_json(args.mesh) if args.mesh else fetch_mesh()
        root = args.root.resolve()
        if args.write:
            written = write_repo(document, root)
            for path in written:
                print(f"wrote {path}")
            return 0
        component = args.component or ""
        if not component:
            raise MeshError("--component is required with --check")
        errors = check_repo(document, root, component)
    except MeshError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if errors:
        print("FAIL: this repo is behind the mesh", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("OK: this repo requires the mesh versions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
