"""Differential (offline shape): the adopter manifest agrees with the train.

The **live** comparison — the stack's component versions against the certified
release train, and the adopter manifest against ``check_manifest.py`` — runs in
``tests/test_train_parity.py`` (network) and the train's own ``check-adopter.yml``
CI. Here we prove the offline shape: the adopter pins the one stack entry,
the pin is empty (follow the train), and the schema is the train's.
"""

from __future__ import annotations

import json

from conftest import STACK_SHA, VERSIONS

TRAIN_SCHEMA = "agent-stack-train.stack-manifest.v1"


def test_written_manifest_pins_exactly_the_stack(
    installer, make_stack, make_adopter, stub_externals, run_args,
):
    stub_externals()
    adopter = make_adopter()
    assert installer.run(run_args(make_stack(), adopter)) == 0
    manifest = json.loads((adopter / "stack-manifest.json").read_text(encoding="utf-8"))
    assert set(manifest["pins"]) == {"agent-stack-train"}


def test_written_manifest_pins_are_empty(
    installer, make_stack, make_adopter, stub_externals, run_args,
):
    stub_externals()
    adopter = make_adopter()
    assert installer.run(run_args(make_stack(), adopter)) == 0
    manifest = json.loads((adopter / "stack-manifest.json").read_text(encoding="utf-8"))
    assert manifest["pins"] and all(pin == {} for pin in manifest["pins"].values())


def test_written_manifest_uses_the_train_schema_and_source(
    installer, make_stack, make_adopter, stub_externals, run_args,
):
    stub_externals()
    adopter = make_adopter()
    assert installer.run(run_args(make_stack(), adopter)) == 0
    manifest = json.loads((adopter / "stack-manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == TRAIN_SCHEMA
    assert manifest["source"] == installer.TRAIN_SOURCE
    assert manifest["release_train"] == installer.TRAIN_RELEASE
    assert manifest["adopter"] == adopter.name


def test_written_manifest_carries_no_install_day_version(
    installer, make_stack, make_adopter, stub_externals, run_args,
):
    """A pin is never frozen to install-day versions (SPEC.md section 1)."""
    stub_externals()
    adopter = make_adopter()
    assert installer.run(run_args(make_stack(), adopter)) == 0
    blob = (adopter / "stack-manifest.json").read_text(encoding="utf-8")
    assert STACK_SHA not in blob
    for version in VERSIONS.values():
        assert version not in blob
