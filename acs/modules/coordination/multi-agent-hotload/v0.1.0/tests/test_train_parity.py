"""Differential check: the stack checkout and the adopter manifest against the train.

Two layers:

* **Offline** (always runs): the stack checkout this pack sits in provides all
  four components, each with a version and the one stack commit, and the
  manifest the installer builds pins exactly the stack (``agent-stack-train``)
  with an empty pin, in the train's schema.
* **Live** (skipped when the train is unreachable): each of the four components
  the live release train certifies is at the version the stack's own version
  file declares. This is the check that would have caught the 2026-10-01
  snapshot staying on PCM 0.6.0 after 0.7.0 shipped.

The live layer compares versions only. The train still certifies the old
repositories' commits until a later step, so a commit comparison would fail
against a correct stack; and any other certified key (a future
``agent-stack-train`` entry, say) is not one of the four components and is
ignored.

The live layer needs the network, so it is skipped in an offline CI; the train's
own ``check-adopter.yml`` runs the live manifest comparison in the repos that
call it.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

MODULE_ROOT = Path(__file__).resolve().parents[1]
# v0.1.0 -> multi-agent-hotload -> coordination -> modules -> acs folder -> stack root
STACK_ROOT = MODULE_ROOT.parents[4]
TRAIN_URL = "https://raw.githubusercontent.com/Pukujan/agent-stack-train/main/stack-releases.json"
TRAIN_SCHEMA = "agent-stack-train.stack-manifest.v1"
COMPONENTS = {
    "project-continuity-modules",
    "content-generation-modules",
    "agent-custom-setup",
    "observational-issue-ops",
}


def _live_train() -> dict | None:
    try:
        with urllib.request.urlopen(TRAIN_URL, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, json.JSONDecodeError):
        return None


def _load_script(name: str):
    spec = spec_from_file_location(name, MODULE_ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _installer():
    return _load_script("acs_install")


def _stack_checkout():
    return _load_script("stack_checkout")


# --- offline ---------------------------------------------------------------


def test_stack_provides_every_component_at_one_commit():
    stack = _stack_checkout()
    requires = stack.requires(STACK_ROOT)
    assert set(requires) == COMPONENTS
    for name, entry in requires.items():
        assert entry.get("version"), f"{name} has no version"
        assert entry.get("commit"), f"{name} has no commit"
    commits = {entry["commit"] for entry in requires.values()}
    assert len(commits) == 1, f"components are not at one commit: {commits}"
    assert re.fullmatch(r"[0-9a-f]{40}", commits.pop())


def test_manifest_pins_exactly_the_stack():
    """The manifest the installer writes pins the stack as one empty entry."""
    manifest = _installer().build_stack_manifest("adopter-x")
    assert manifest["adopter"] == "adopter-x"
    assert manifest["pins"] == {"agent-stack-train": {}}


def test_manifest_shape_is_train_schema():
    mod = _installer()
    manifest = mod.build_stack_manifest("adopter-x")
    assert manifest["schema_version"] == TRAIN_SCHEMA
    assert manifest["release_train"] == mod.TRAIN_RELEASE
    assert manifest["source"] == mod.TRAIN_SOURCE


# --- live (skipped offline) ------------------------------------------------


def test_stack_is_not_behind_the_live_train():
    train = _live_train()
    if train is None:
        pytest.skip("release train unreachable; live differential needs the network")
    stack = _stack_checkout()
    certified = train.get("certified", {})
    present = sorted(COMPONENTS & set(certified))
    assert present, "the live train certifies none of the stack's components"
    for name in present:
        assert stack.component_version(STACK_ROOT, name) == certified[name].get("version"), (
            f"{name}: the stack's version differs from the train's"
        )


def test_release_train_constant_is_current():
    train = _live_train()
    if train is None:
        pytest.skip("release train unreachable; live differential needs the network")
    assert _installer().TRAIN_RELEASE == train.get("release_train")
