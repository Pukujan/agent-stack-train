#!/usr/bin/env python3
"""The agent stack checkout this pack ships in, and what it provides.

ACS lives in Pukujan/agent-stack-train, next to PCM, CGM and OIO:

    <stack>/pcm  <stack>/cgm  <stack>/acs  <stack>/oio

One checkout of that repository is the whole stack. Every component sits at the
same commit by construction, so there is no per-component commit to pin, copy or
verify. Each component's version still comes from its own version file.

Stdlib only: ``acs_install.py`` and ``hotload_check.py`` both import it.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
# v0.1.0 -> multi-agent-hotload -> coordination -> modules -> acs -> stack root
DEFAULT_ROOT = MODULE_ROOT.parents[4]

REPOSITORY = "Pukujan/agent-stack-train"

# Component name (as the release train and stack manifests spell it) -> folder.
FOLDERS = {
    "project-continuity-modules": "pcm",
    "content-generation-modules": "cgm",
    "agent-custom-setup": "acs",
    "observational-issue-ops": "oio",
}


class StackError(RuntimeError):
    """The checkout is not a complete agent stack."""


def git_head(root: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return (proc.stdout or "").strip() or None


def folder(stack_root: Path, name: str) -> Path:
    return stack_root / FOLDERS[name]


def _json_value(path: Path, key: str) -> str | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    value = data.get(key) if isinstance(data, dict) else None
    return str(value) if value else None


def component_version(stack_root: Path, name: str) -> str | None:
    """The version a component's own version file declares, or None if unreadable."""
    root = folder(stack_root, name)
    if name == "project-continuity-modules":
        try:
            text = (root / "src" / "continuity" / "__init__.py").read_text(encoding="utf-8")
        except OSError:
            return None
        match = re.search(r"__version__\s*=\s*[\"']([^\"']+)[\"']", text)
        return match.group(1) if match else None
    if name == "content-generation-modules":
        return _json_value(root / "system-version.json", "version")
    if name == "agent-custom-setup":
        return _json_value(root / "registry.json", "version")
    try:
        return (root / "VERSION").read_text(encoding="utf-8").strip() or None
    except OSError:
        return None


def requires(stack_root: Path | None = None, *, head: str | None = None) -> dict[str, dict[str, str]]:
    """Each component's version, all at the checkout's one commit.

    ``head`` is the checkout's commit when the caller already has it. Raises
    StackError when the checkout is not a git checkout, a component folder is
    missing, or a version file is unreadable: a partial stack fails closed
    instead of installing whatever happens to be there.
    """
    root = (stack_root or DEFAULT_ROOT).expanduser().resolve()
    head = head or git_head(root)
    if not head:
        raise StackError(f"{root} is not a git checkout of {REPOSITORY} (rev-parse HEAD failed)")
    found: dict[str, dict[str, str]] = {}
    for name, rel in FOLDERS.items():
        if not (root / rel).is_dir():
            raise StackError(f"{root} has no {rel}/ folder: not a complete {REPOSITORY} checkout")
        version = component_version(root, name)
        if not version:
            raise StackError(f"{root / rel}: cannot read the {name} version")
        found[name] = {"version": version, "commit": head}
    return found
