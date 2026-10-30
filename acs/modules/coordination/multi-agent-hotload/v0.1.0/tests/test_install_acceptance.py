"""PDD (acceptance): a fresh adopter reaches READY; a conflicted repo is refused.

These are the end-to-end promises of SPEC.md sections 2, 3 and 7: the happy path
completes and records state, and every unhappy path fails closed with a report
that names the cause — never a fake OK.
"""

from __future__ import annotations

import json

import pytest

from conftest import STACK_SHA


def test_fresh_adopter_reaches_ready(
    installer, make_stack, make_adopter, stub_externals, run_args, capsys,
):
    stub_externals()
    adopter = make_adopter()
    rc = installer.run(run_args(make_stack(), adopter))
    out = capsys.readouterr().out
    assert rc == 0
    assert "OK (state=READY)" in out
    assert (adopter / ".coord" / "assignment.json").is_file()
    assert (adopter / "stack-manifest.json").is_file()
    lock = json.loads((adopter / ".coord" / "hotload.lock.json").read_text(encoding="utf-8"))
    assert lock["state"] == "READY"
    assert lock["hotload_check"] == "OK"
    assert lock["oio_install"] == "OK"
    assert lock["stack"]["commit"] == STACK_SHA
    assert lock["checkouts"]["pcm"]["verified"] is True
    assert lock["checkouts"]["cgm"]["verified"] is True
    assert lock["checkouts"]["oio"]["verified"] is True


def test_conflicted_repo_is_refused_with_a_clear_report(
    installer, make_stack, make_adopter, stub_externals, run_args, capsys,
):
    stub_externals()
    adopter = make_adopter()
    foreign = {"schema_version": "someone-else.v1", "pins": {"pcm": "0.6.0"}}
    (adopter / "stack-manifest.json").write_text(json.dumps(foreign), encoding="utf-8")

    rc = installer.run(run_args(make_stack(), adopter))
    out = capsys.readouterr().out
    assert rc == 1
    assert "state=CONFLICTED" in out
    assert "stack-manifest.json" in out
    assert "foreign content" in out
    # Nothing was written anywhere.
    assert not (adopter / ".coord").exists()
    assert json.loads((adopter / "stack-manifest.json").read_text(encoding="utf-8")) == foreign


def test_partial_reports_the_one_remaining_command(
    installer, make_stack, make_adopter, stub_externals, run_args, capsys,
):
    """OIO's installer fails: coordination is installed and valid, OIO is the remaining step."""
    stub_externals(oio_exit=1)
    adopter = make_adopter()
    rc = installer.run(run_args(make_stack(), adopter))
    out = capsys.readouterr().out
    assert rc == 1
    assert "PARTIAL (state=PARTIAL)" in out
    assert "OIO install did not complete" in out
    # The one remaining command names OIO's installer in the stack checkout.
    assert "oio_installer.py --target" in out
    # The coordination surface is still written and honest about the state.
    lock = json.loads((adopter / ".coord" / "hotload.lock.json").read_text(encoding="utf-8"))
    assert lock["state"] == "PARTIAL"
    assert lock["oio_install"] == "FAILED"
    assert lock["hotload_check"] == "OK"


def test_unsupported_platform_reports_partial_never_ok(
    installer, make_stack, make_adopter, stub_externals, run_args, capsys,
):
    stub_externals(oio_supported=False)
    adopter = make_adopter()
    rc = installer.run(run_args(make_stack(), adopter))
    out = capsys.readouterr().out
    assert rc == 1
    assert "PARTIAL" in out
    assert "O_NOFOLLOW" in out
    lock = json.loads((adopter / ".coord" / "hotload.lock.json").read_text(encoding="utf-8"))
    assert lock["state"] == "PARTIAL"


def test_missing_cgm_adapter_fails_closed(
    installer, make_stack, make_adopter, stub_externals, run_args, capsys,
):
    stub_externals()
    adopter = make_adopter(with_adapter=False)
    rc = installer.run(run_args(make_stack(), adopter))
    out = capsys.readouterr().out
    assert rc == 1
    assert ".content-system" in out
    assert not (adopter / ".coord").exists()
    assert not (adopter / "stack-manifest.json").exists()


@pytest.mark.parametrize("folder", ["pcm", "cgm", "oio"])
def test_incomplete_stack_checkout_fails_closed(
    installer, make_stack, make_adopter, stub_externals, run_args, capsys, folder,
):
    """A stack with a component folder left out is refused, naming the folder."""
    stub_externals()
    adopter = make_adopter()
    rc = installer.run(run_args(make_stack(omit=folder), adopter))
    out = capsys.readouterr().out
    assert rc == 2
    assert f"no {folder}/ folder" in out
    assert not (adopter / ".coord").exists()
    assert not (adopter / "stack-manifest.json").exists()


def test_missing_oio_installer_fails_closed(
    installer, make_stack, make_adopter, stub_externals, run_args, capsys,
):
    stub_externals()
    adopter = make_adopter()
    rc = installer.run(run_args(make_stack(with_oio_installer=False), adopter))
    out = capsys.readouterr().out
    assert rc == 1
    assert "oio_installer.py" in out
    assert not (adopter / ".coord").exists()
    assert not (adopter / "stack-manifest.json").exists()


def test_dry_run_reaches_the_plan_and_writes_nothing(
    installer, make_stack, make_adopter, stub_externals, run_args, capsys,
):
    stub_externals()
    adopter = make_adopter()
    rc = installer.run(run_args(make_stack(), adopter, dry_run=True))
    out = capsys.readouterr().out
    assert rc == 0
    assert "dry-run OK" in out
    assert not (adopter / ".coord").exists()
    assert not (adopter / "stack-manifest.json").exists()
