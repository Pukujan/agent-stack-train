"""Tests for the CLAUDE.md bridge (claude_bridge.py).

Claude Code reads CLAUDE.md, not AGENTS.md. These tests pin down that the
installer gives every adopter a CLAUDE.md that imports AGENTS.md, keeps the
adopter's own text, and that hotload_check fails an adopter Claude would read
without the stack's rules.
"""

from __future__ import annotations

import os
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

from conftest import MODULE_ROOT, STACK_SHA

STACK_ROOT = MODULE_ROOT.parents[4]


def _load():
    spec = spec_from_file_location("claude_bridge", MODULE_ROOT / "scripts" / "claude_bridge.py")
    assert spec and spec.loader
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def bridge():
    return _load()


def _region(bridge, cgm_root=None) -> str:
    return bridge.render_region(commit=STACK_SHA, cgm_root=cgm_root)


def _apply(bridge, adopter: Path, region: str) -> None:
    new = bridge.plan(adopter, region)
    if new is not None:
        (adopter / "CLAUDE.md").write_bytes(new)


def test_region_imports_agents_md_and_names_github_as_authority(bridge):
    region = _region(bridge)
    assert region.startswith(bridge.START_MARKER)
    assert region.rstrip().endswith(bridge.END_MARKER)
    assert bridge.IMPORT_RE.search(region)
    assert "GitHub is the authority" in region
    assert "https://github.com/Pukujan/agent-stack-train" in region
    assert STACK_SHA[:12] in region
    assert bridge.DEV_ROOT_RULE in region
    # Adopters' absolute-path lints accept a line that carries this marker.
    dev_line = next(line for line in region.splitlines() if bridge.DEV_ROOT_RULE in line)
    assert "paths:allow" in dev_line


def test_region_links_the_writing_rule_skills_to_github_at_the_commit(bridge):
    region = _region(bridge, STACK_ROOT / "cgm")
    url = f"https://github.com/Pukujan/agent-stack-train/blob/{STACK_SHA}/cgm/modules/human-sounding-writing/SKILL.md"
    assert url in region
    # Every skill path in the rule became a link; none is left bare.
    for line in region.splitlines():
        for hit in bridge.CGM_PATH_RE.finditer(line):
            assert line[hit.start() - 1] == "[", line


def test_fresh_adopter_gets_a_claude_md(bridge, tmp_path: Path):
    _apply(bridge, tmp_path, _region(bridge))
    text = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert text.startswith("# Claude Code\n")
    (tmp_path / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    assert bridge.check(tmp_path) == []


def test_existing_text_is_kept_and_the_region_appended_once(bridge, tmp_path: Path):
    own = "# Mine\n\nRead docs/DRIVING.md first.\n"
    (tmp_path / "CLAUDE.md").write_text(own, encoding="utf-8")
    region = _region(bridge)
    _apply(bridge, tmp_path, region)
    _apply(bridge, tmp_path, region)
    text = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert text.startswith(own)
    assert text.count(bridge.START_MARKER) == 1
    assert bridge.plan(tmp_path, region) is None


def test_reinstall_refreshes_only_the_region(bridge, tmp_path: Path):
    (tmp_path / "CLAUDE.md").write_text("before\n", encoding="utf-8")
    _apply(bridge, tmp_path, bridge.render_region(commit="a" * 40, cgm_root=None))
    with (tmp_path / "CLAUDE.md").open("a", encoding="utf-8") as fh:
        fh.write("\nafter\n")
    _apply(bridge, tmp_path, _region(bridge))
    text = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert text.startswith("before\n")
    assert text.endswith("\nafter\n")
    assert STACK_SHA[:12] in text and "a" * 12 not in text


def test_unbalanced_markers_are_refused(bridge, tmp_path: Path):
    (tmp_path / "CLAUDE.md").write_text(f"x\n{bridge.START_MARKER}\n", encoding="utf-8")
    with pytest.raises(bridge.BridgeError):
        bridge.plan(tmp_path, _region(bridge))
    assert bridge.check(tmp_path)


@pytest.mark.skipif(os.name == "nt", reason="symlinks need privileges on Windows")
def test_a_symlink_to_agents_md_already_bridges(bridge, tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").symlink_to("AGENTS.md")
    assert bridge.plan(tmp_path, _region(bridge)) is None
    assert bridge.check(tmp_path) == []


@pytest.mark.skipif(os.name == "nt", reason="symlinks need privileges on Windows")
def test_any_other_symlink_is_refused(bridge, tmp_path: Path):
    (tmp_path / "elsewhere.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").symlink_to("elsewhere.md")
    with pytest.raises(bridge.BridgeError):
        bridge.plan(tmp_path, _region(bridge))


def test_check_flags_a_claude_md_that_does_not_import_agents_md(bridge, tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    assert bridge.check(tmp_path)  # missing
    (tmp_path / "CLAUDE.md").write_text("Read AGENTS.md first.\n", encoding="utf-8")
    problems = bridge.check(tmp_path)
    assert problems and "does not import" in problems[0]
    (tmp_path / "CLAUDE.md").write_text("Intro\n\n@AGENTS.md\n", encoding="utf-8")
    assert bridge.check(tmp_path) == []


def test_check_cli_warn_only_exits_zero(bridge, tmp_path: Path, capsys):
    assert bridge.main(["--adopter-root", str(tmp_path)]) == 1
    assert bridge.main(["--adopter-root", str(tmp_path), "--warn-only"]) == 0
    assert "::warning::" in capsys.readouterr().out


def test_install_writes_the_bridge_and_keeps_adopter_text(
    installer, make_stack, make_adopter, stub_externals, run_args
):
    stub_externals()
    adopter = make_adopter()
    (adopter / "CLAUDE.md").write_text("# Mine\n", encoding="utf-8")
    assert installer.run(run_args(make_stack(), adopter)) == 0
    text = (adopter / "CLAUDE.md").read_text(encoding="utf-8")
    assert text.startswith("# Mine\n")
    assert "@AGENTS.md" in text
    assert STACK_SHA[:12] in text


def test_install_dry_run_leaves_claude_md_alone(
    installer, make_stack, make_adopter, stub_externals, run_args
):
    stub_externals()
    adopter = make_adopter()
    assert installer.run(run_args(make_stack(), adopter, dry_run=True)) == 0
    assert not (adopter / "CLAUDE.md").exists()


def test_install_refuses_unbalanced_markers_and_writes_nothing(
    installer, make_stack, make_adopter, stub_externals, run_args
):
    stub_externals()
    adopter = make_adopter()
    bridge = installer.claude_bridge
    (adopter / "CLAUDE.md").write_text(f"{bridge.END_MARKER}\n", encoding="utf-8")
    assert installer.run(run_args(make_stack(), adopter)) == 1
    assert not (adopter / ".coord").exists()
