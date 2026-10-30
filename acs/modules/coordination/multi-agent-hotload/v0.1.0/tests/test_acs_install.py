"""Tests for the multi-agent hotload installer (acs_install.py).

Pure-function tests plus end-to-end runs of ``run()`` against a fixture
agent-stack-train checkout (``tests/conftest.py``) with the pack's external
checkers stubbed, so the suite needs no network and no real stack.
"""

from __future__ import annotations

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

from conftest import (
    CGM_MODULES,
    MODULE_REL,
    MODULE_ROOT,
    SCRIPT,
    STACK_SHA,
    VERSIONS,
    git_repo,
    pins_at_stack,
    stack_requires,
)

REPOSITORY = "Pukujan/agent-stack-train"


def _example() -> dict:
    return json.loads(
        (MODULE_ROOT / "examples" / "assignment.example.json").read_text(encoding="utf-8")
    )


def _load_hotload_check():
    spec = spec_from_file_location("hotload_check", MODULE_ROOT / "scripts" / "hotload_check.py")
    assert spec and spec.loader
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _lock(adopter: Path) -> dict:
    return json.loads((adopter / ".coord" / "hotload.lock.json").read_text(encoding="utf-8"))


# --- pure functions -------------------------------------------------------


def test_commits_agree(installer):
    other = "f" * 40
    assert installer.commits_agree(STACK_SHA, STACK_SHA)
    assert installer.commits_agree(STACK_SHA, STACK_SHA[:12])
    assert installer.commits_agree(STACK_SHA[:12], STACK_SHA)
    assert not installer.commits_agree(STACK_SHA, other)


def test_resolve_stack_root_defaults_to_the_stack_the_pack_sits_in(installer, tmp_path: Path):
    assert installer.stack_checkout.DEFAULT_ROOT == MODULE_ROOT.parents[4]
    assert installer.resolve_stack_root(None) == installer.stack_checkout.DEFAULT_ROOT.resolve()
    assert installer.resolve_stack_root(tmp_path) == tmp_path.resolve()


def test_stack_requires_gives_each_component_its_version_at_the_one_commit(installer, make_stack):
    found = installer.stack_checkout.requires(make_stack(), head=STACK_SHA)
    assert found == stack_requires()
    assert {entry["commit"] for entry in found.values()} == {STACK_SHA}


def test_stack_requires_reads_the_commit_from_git(installer, make_stack):
    stack = make_stack()
    head = git_repo(stack)
    found = installer.stack_checkout.requires(stack)
    assert {entry["commit"] for entry in found.values()} == {head}
    assert {name: entry["version"] for name, entry in found.items()} == VERSIONS


def test_stack_requires_rejects_a_non_git_directory(installer, make_stack):
    with pytest.raises(installer.stack_checkout.StackError, match="not a git checkout"):
        installer.stack_checkout.requires(make_stack())


@pytest.mark.parametrize("folder", ["pcm", "cgm", "oio"])
def test_stack_requires_rejects_a_missing_component_folder(installer, make_stack, folder):
    stack = make_stack(omit=folder)
    with pytest.raises(installer.stack_checkout.StackError, match=f"no {folder}/ folder"):
        installer.stack_checkout.requires(stack, head=STACK_SHA)


def test_stack_requires_rejects_an_unreadable_version(installer, make_stack):
    stack = make_stack()
    (stack / "cgm" / "system-version.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(
        installer.stack_checkout.StackError,
        match="cannot read the content-generation-modules version",
    ):
        installer.stack_checkout.requires(stack, head=STACK_SHA)


def test_build_assignment_repins_from_pins(installer):
    data = installer.build_assignment(_example(), pins_at_stack(), "adopter-x")
    assert data["project"] == "adopter-x"
    assert data["pins"]["pcm"]["revision"] == STACK_SHA
    assert data["pins"]["pcm"]["cli_version"] == "0.6.0"
    assert data["pins"]["cgm"]["revision"] == STACK_SHA
    assert data["pins"]["cgm"]["version"] == "0.5.12"
    assert data["pins"]["cgm"]["modules"] == CGM_MODULES
    # No foreign repo's issue URL leaks into the adopter assignment.
    check_in = data["boss_failover"]["check_in"]
    assert "issue_url" not in check_in
    assert check_in["mechanism"] == "claim_file"
    assert data["boss_failover"]["claim_queue"] == []


def test_build_assignment_is_schema_valid(installer):
    jsonschema = __import__("jsonschema", fromlist=["Draft202012Validator"])
    schema = json.loads(
        (MODULE_ROOT / "schema" / "assignment.schema.json").read_text(encoding="utf-8")
    )
    data = installer.build_assignment(_example(), pins_at_stack(), "adopter-x")
    jsonschema.Draft202012Validator(schema).validate(data)


def test_generated_assignment_passes_pack_validator(installer, tmp_path: Path):
    """The installer's output must satisfy hotload_check's own pin/failover rules."""
    check = _load_hotload_check()
    stack = installer.stack_checkout
    # The installer overlays the stack checkout onto pins.json before it writes.
    requires = stack.requires(stack.DEFAULT_ROOT)
    pcm = requires["project-continuity-modules"]
    cgm = requires["content-generation-modules"]
    real_pins = installer.load_json(MODULE_ROOT / "pins.json")["pins"]
    real_pins["pcm"]["commit"] = pcm["commit"]
    real_pins["pcm"]["cli_version"] = pcm["version"]
    real_pins["cgm"]["commit"] = cgm["commit"]
    real_pins["cgm"]["version"] = cgm["version"]
    generated = installer.build_assignment(_example(), real_pins, "adopter-x")
    out = tmp_path / "assignment.json"
    out.write_text(json.dumps(generated), encoding="utf-8")
    errors = check.validate_assignment(MODULE_ROOT / "schema" / "assignment.schema.json", out)
    assert errors == [], errors


def test_build_lock_has_no_absolute_paths(installer, tmp_path: Path):
    checkouts = {label: {"commit": STACK_SHA, "verified": True} for label in ("pcm", "cgm", "oio")}
    lock = installer.build_lock(pins_at_stack(), STACK_SHA, checkouts, validated=True)
    assert lock["schema"] == "acs.hotload.lock.v1"
    assert lock["hotload_check"] == "OK"
    assert lock["stack"] == {"repository": REPOSITORY, "commit": STACK_SHA}
    assert lock["acs"]["commit"] == STACK_SHA
    blob = json.dumps(lock)
    assert str(tmp_path) not in blob
    assert ":\\" not in blob and '"/' not in blob


def test_write_json_atomic_leaves_no_temp_files(installer, tmp_path: Path):
    target = tmp_path / "sub" / "out.json"
    installer.write_json_atomic(target, {"a": 1}, root=tmp_path)
    assert json.loads(target.read_text(encoding="utf-8")) == {"a": 1}
    installer.write_json_atomic(target, {"a": 2}, root=tmp_path)
    assert json.loads(target.read_text(encoding="utf-8")) == {"a": 2}
    assert [p.name for p in target.parent.iterdir()] == ["out.json"]


def test_write_json_atomic_refuses_to_escape_root(installer, tmp_path: Path):
    adopter = tmp_path / "adopter"
    adopter.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        (adopter / ".coord").symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not permitted on this platform")
    with pytest.raises(ValueError):
        installer.write_json_atomic(
            adopter / ".coord" / "assignment.json", {"x": 1}, root=adopter
        )
    assert list(outside.iterdir()) == []


# --- end-to-end run() -----------------------------------------------------


def test_run_success_writes_surface(installer, make_stack, make_adopter, stub_externals, run_args):
    stub_externals()
    adopter = make_adopter()

    rc = installer.run(run_args(make_stack(), adopter))
    assert rc == 0
    assignment = json.loads((adopter / ".coord" / "assignment.json").read_text(encoding="utf-8"))
    lock = _lock(adopter)
    # Every revision the adopter records is the one stack commit.
    assert assignment["pins"]["pcm"]["revision"] == STACK_SHA
    assert assignment["pins"]["pcm"]["cli_version"] == VERSIONS["project-continuity-modules"]
    assert assignment["pins"]["cgm"]["revision"] == STACK_SHA
    assert assignment["pins"]["cgm"]["version"] == VERSIONS["content-generation-modules"]
    assert lock["hotload_check"] == "OK"
    assert lock["state"] == "READY"
    assert lock["oio_install"] == "OK"
    assert lock["stack"] == {"repository": REPOSITORY, "commit": STACK_SHA}
    for label in ("pcm", "cgm", "oio"):
        assert lock["checkouts"][label] == {"commit": STACK_SHA, "verified": True}


def test_run_writes_empty_pin_manifest(installer, make_stack, make_adopter, stub_externals, run_args):
    """Train routing: one pin on the whole stack, left empty (follow the train)."""
    stub_externals()
    adopter = make_adopter()

    assert installer.run(run_args(make_stack(), adopter)) == 0
    manifest = json.loads((adopter / "stack-manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "agent-stack-train.stack-manifest.v1"
    assert manifest["release_train"] == "current"
    assert manifest["source"] == installer.TRAIN_SOURCE
    assert manifest["pins"] == {"agent-stack-train": {}}
    # No install-day version leaked into the manifest.
    assert STACK_SHA not in json.dumps(manifest)


def test_run_refuses_foreign_manifest(installer, make_stack, make_adopter, stub_externals, run_args):
    stub_externals()
    adopter = make_adopter()
    foreign = {"schema_version": "someone-else.v1", "pins": {"pcm": "0.6.0"}}
    (adopter / "stack-manifest.json").write_text(json.dumps(foreign), encoding="utf-8")

    rc = installer.run(run_args(make_stack(), adopter))
    assert rc == 1
    assert json.loads((adopter / "stack-manifest.json").read_text(encoding="utf-8")) == foreign
    assert not (adopter / ".coord").exists()


def test_run_fails_closed_without_the_oio_installer(
    installer, make_stack, make_adopter, stub_externals, run_args, capsys
):
    """The stack's oio/ folder has no installer: nothing is written, not even PARTIAL."""
    stub_externals()
    adopter = make_adopter()

    rc = installer.run(run_args(make_stack(with_oio_installer=False), adopter))
    out = capsys.readouterr().out
    assert rc == 1
    assert "oio_installer.py" in out
    assert not (adopter / ".coord").exists()
    assert not (adopter / "stack-manifest.json").exists()


def test_run_partial_when_oio_install_fails(
    installer, make_stack, make_adopter, stub_externals, run_args, capsys
):
    """OIO's own installer failing leaves the validated coordination surface in place."""
    stub_externals(oio_exit=1)
    adopter = make_adopter()

    rc = installer.run(run_args(make_stack(), adopter))
    out = capsys.readouterr().out
    assert rc == 1
    assert "OIO install did not complete (exit 1)" in out
    lock = _lock(adopter)
    assert lock["state"] == "PARTIAL"
    assert lock["oio_install"] == "FAILED"
    assert lock["hotload_check"] == "OK"
    assert (adopter / ".coord" / "assignment.json").is_file()
    assert (adopter / "stack-manifest.json").is_file()


def test_run_partial_when_oio_unsupported(
    installer, make_stack, make_adopter, stub_externals, run_args
):
    """A platform OIO cannot run on reports PARTIAL, never a fake OK."""
    stub_externals(oio_supported=False)
    adopter = make_adopter()

    rc = installer.run(run_args(make_stack(), adopter))
    assert rc == 1
    lock = _lock(adopter)
    assert lock["state"] == "PARTIAL"
    assert lock["oio_install"] == "not_run"


def test_run_dry_run_writes_nothing(installer, make_stack, make_adopter, stub_externals, run_args):
    stub_externals()
    adopter = make_adopter()

    rc = installer.run(run_args(make_stack(), adopter, dry_run=True))
    assert rc == 0
    assert not (adopter / ".coord").exists()
    assert not (adopter / "stack-manifest.json").exists()


def test_run_missing_adapter_fails_closed(
    installer, make_stack, make_adopter, stub_externals, run_args
):
    stub_externals()
    adopter = make_adopter(with_adapter=False)

    rc = installer.run(run_args(make_stack(), adopter))
    assert rc == 1
    assert not (adopter / ".coord").exists()


@pytest.mark.parametrize("folder", ["pcm", "cgm", "oio"])
def test_run_missing_component_folder_fails_closed(
    installer, make_stack, make_adopter, stub_externals, run_args, capsys, folder
):
    stub_externals()
    adopter = make_adopter()

    rc = installer.run(run_args(make_stack(omit=folder), adopter))
    out = capsys.readouterr().out
    assert rc == 2
    assert f"no {folder}/ folder" in out
    assert not (adopter / ".coord").exists()


def test_run_non_git_stack_fails_closed(
    installer, make_stack, make_adopter, run_args, monkeypatch, capsys
):
    """A stack root with no commit is refused before any checker runs or file is written."""
    ran: list[list[str]] = []
    monkeypatch.setattr(installer, "run_script", lambda argv: ran.append(argv) or 0)
    adopter = make_adopter()

    rc = installer.run(run_args(make_stack(), adopter))
    out = capsys.readouterr().out
    assert rc == 2
    assert "not a git checkout" in out
    assert ran == []
    assert not (adopter / ".coord").exists()


def test_run_keeps_existing_files_without_force(
    installer, make_stack, make_adopter, stub_externals, run_args
):
    stub_externals()
    adopter = make_adopter()
    coord = adopter / ".coord"
    coord.mkdir()
    sentinel = {"project": "hand-edited"}
    (coord / "assignment.json").write_text(json.dumps(sentinel), encoding="utf-8")

    rc = installer.run(run_args(make_stack(), adopter))
    assert rc == 0
    kept = json.loads((coord / "assignment.json").read_text(encoding="utf-8"))
    assert kept == sentinel  # untouched without --force
    assert (coord / "hotload.lock.json").is_file()


def test_run_force_overwrites(installer, make_stack, make_adopter, stub_externals, run_args):
    stub_externals()
    adopter = make_adopter()
    coord = adopter / ".coord"
    coord.mkdir()
    (coord / "assignment.json").write_text('{"project": "hand-edited"}', encoding="utf-8")

    rc = installer.run(run_args(make_stack(), adopter, force=True))
    assert rc == 0
    data = json.loads((coord / "assignment.json").read_text(encoding="utf-8"))
    assert data["project"] == "adopter"


def test_run_fails_closed_when_hotload_check_fails(
    installer, make_stack, make_adopter, stub_externals, run_args, monkeypatch
):
    stub_externals()
    adopter = make_adopter()
    calls = {"n": 0}

    def run_script(argv):
        calls["n"] += 1
        return 0 if calls["n"] == 1 else 1  # check_pins OK, hotload_check FAIL

    monkeypatch.setattr(installer, "run_script", run_script)
    rc = installer.run(run_args(make_stack(), adopter))
    assert rc == 1
    # A failed final check must not leave a partial install behind.
    assert not (adopter / ".coord" / "assignment.json").exists()
    assert not (adopter / ".coord" / "hotload.lock.json").exists()
    assert not (adopter / "stack-manifest.json").exists()


def test_run_hands_the_stack_root_to_every_checker(
    installer, make_stack, make_adopter, stub_externals, run_args, monkeypatch
):
    """check_pins, hotload_check and OIO's installer all come from the one stack checkout."""
    stub_externals()
    calls: list[list[str]] = []
    monkeypatch.setattr(installer, "run_script", lambda argv: calls.append(list(argv)) or 0)
    stack = make_stack()
    adopter = make_adopter()

    assert installer.run(run_args(stack, adopter, project_id="owner/repo")) == 0

    def value(argv: list[str], flag: str) -> str:
        return argv[argv.index(flag) + 1]

    def calls_of(script: str) -> list[list[str]]:
        return [argv for argv in calls if Path(argv[1]).name == script]

    stack_r = stack.resolve()
    (pins_call,) = calls_of("check_pins.py")
    assert value(pins_call, "--root") == str(stack_r / "acs")
    (check_call,) = calls_of("hotload_check.py")
    assert value(check_call, "--stack-root") == str(stack_r)
    assert value(check_call, "--root") == str(stack_r / "acs" / MODULE_REL)
    assert value(check_call, "--adopter-root") == str(adopter.resolve())
    # hotload_check finds the stack's own cgm/ folder; no CGM path is handed over.
    assert "--cgm-root" not in check_call
    oio_install, oio_check = calls_of("oio_installer.py")
    oio_script = stack_r / "oio" / ".github" / "scripts" / "oio_installer.py"
    assert Path(oio_install[1]) == oio_script
    assert value(oio_install, "--target") == str(adopter.resolve())
    assert value(oio_install, "--project-id") == "owner/repo"
    assert oio_check[-1] == "--check"


def test_build_stack_manifest_empty_pins(installer):
    manifest = installer.build_stack_manifest("adopter-x")
    assert manifest["adopter"] == "adopter-x"
    assert manifest["source"] == installer.TRAIN_SOURCE
    assert manifest["pins"] == {"agent-stack-train": {}}


def test_oio_platform_probe_comes_from_the_pinned_installer(installer, tmp_path: Path):
    """The verdict is OIO's, not a copy of its precondition kept here.

    A local copy is what went stale: it kept reporting Windows unsupported
    after OIO gained a Windows backend, so an install that would have succeeded
    reported PARTIAL. This asserts ACS reads the installer's answer instead.
    """
    supported = tmp_path / "supports.py"
    supported.write_text('import sys; print("supported: fake backend"); sys.exit(0)', encoding="utf-8")
    assert installer.oio_platform_supported(supported) == (True, "")

    refuses = tmp_path / "refuses.py"
    refuses.write_text('import sys; print("unsupported: no dir_fd"); sys.exit(1)', encoding="utf-8")
    ok, why = installer.oio_platform_supported(refuses)
    assert ok is False
    assert "no dir_fd" in why


def test_oio_platform_probe_defers_when_the_installer_cannot_answer(installer, tmp_path: Path):
    """An installer too old to carry the probe is not guessed about.

    Such a checkout predates the backend the probe describes, so ACS attempts
    the install and lets OIO fail closed on its own terms.
    """
    old = tmp_path / "old.py"
    old.write_text("import sys; sys.exit(2)", encoding="utf-8")
    assert installer.oio_platform_supported(old) == (True, "")

    missing = tmp_path / "absent.py"
    assert installer.oio_platform_supported(missing) == (True, "")


def test_module_has_no_hardcoded_pins():
    """The installer must read pins.json, never bake pin literals (drift surface)."""
    text = SCRIPT.read_text(encoding="utf-8")
    assert "0.5.12" not in text
    assert "6831f91e" not in text
    assert "4e23854" not in text
