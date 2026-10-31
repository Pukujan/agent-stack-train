"""Tests for the hotload pin drift check (single-source manifest, fail closed)."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODULE_ROOT.parents[3]
SCRIPT = MODULE_ROOT / "scripts" / "check_pins.py"

# The pack's prose, registry and error strings. None may name a CGM version: the
# CGM in the stack checkout's cgm/ is the only source of it.
VERSION_FREE_FILES = [
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "registry.json",
    *(
        MODULE_ROOT / name
        for name in (
            "README.md",
            "HOTLOAD.md",
            "BEHAVIOR.md",
            "NOTES.md",
            "ROLES.md",
            "module.json",
            "scripts/hotload_check.py",
        )
    ),
]
CGM_VERSION_RE = re.compile(r"CGM\s+\(?\d+\.\d+\.\d+")


def _run(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def _seed_repo(tmp_path: Path) -> Path:
    """Copy the manifest and every projection into an isolated tree."""
    manifest = json.loads((MODULE_ROOT / "pins.json").read_text(encoding="utf-8"))
    root = tmp_path / "repo"
    for entry in manifest["projections"]:
        rel = entry["file"]
        src = REPO_ROOT / rel
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    (root / "pins.json").parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(MODULE_ROOT / "pins.json", root / "pins.json")
    return root


def test_pins_manifest_is_self_consistent():
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("check_pins", SCRIPT)
    assert spec and spec.loader
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    manifest = json.loads((MODULE_ROOT / "pins.json").read_text(encoding="utf-8"))
    assert mod.check_manifest(manifest) == []


def test_check_pins_passes_on_aligned_tree(tmp_path: Path):
    root = _seed_repo(tmp_path)
    proc = _run(root)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "check_pins: OK" in proc.stdout


def test_check_pins_fails_on_drifted_module_count(tmp_path: Path):
    root = _seed_repo(tmp_path)
    # HOTLOAD.md projects cgm.module_count. Version commits are not projected.
    target = root / "modules/coordination/multi-agent-hotload/v0.1.0/HOTLOAD.md"
    text = target.read_text(encoding="utf-8")
    assert "eight module" in text
    target.write_text(text.replace("eight module", "six module"), encoding="utf-8")
    proc = _run(root)
    assert proc.returncode == 1
    assert "check_pins: FAIL" in proc.stdout
    assert "HOTLOAD.md" in proc.stdout and "six" in proc.stdout


def test_check_pins_fails_on_drifted_version(tmp_path: Path):
    root = _seed_repo(tmp_path)
    target = root / "registry.json"
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace('"version": "0.1.0"', '"version": "0.1.9"', 1), encoding="utf-8")
    proc = _run(root)
    assert proc.returncode == 1
    assert "check_pins: FAIL" in proc.stdout
    assert "registry.json" in proc.stdout


def test_check_pins_fails_on_superseded_value_even_when_canonical_present(tmp_path: Path):
    root = _seed_repo(tmp_path)
    target = root / "modules/coordination/multi-agent-hotload/v0.1.0/HOTLOAD.md"
    text = target.read_text(encoding="utf-8")
    # Canonical value stays; a superseded one is appended (the "carries both" case).
    target.write_text(text + "\n(legacy) seven modules\n", encoding="utf-8")
    proc = _run(root)
    assert proc.returncode == 1
    assert "check_pins: FAIL" in proc.stdout
    assert "superseded" in proc.stdout


def test_check_pins_fails_on_missing_projection_file(tmp_path: Path):
    root = _seed_repo(tmp_path)
    (root / "registry.json").unlink()
    proc = _run(root)
    assert proc.returncode == 1
    assert "check_pins: FAIL" in proc.stdout
    assert "registry.json" in proc.stdout


def test_pins_manifest_carries_no_component_versions():
    """Component versions come from the stack checkout; a copy here only drifts."""
    manifest = json.loads((MODULE_ROOT / "pins.json").read_text(encoding="utf-8"))
    assert "pcm" not in manifest["pins"]
    assert "version" not in manifest["pins"]["cgm"]
    assert "cgm.version" not in manifest["superseded"]


def _shipped_text(path: Path) -> str:
    """The file's text; for a script, without comments (they cite older CGM behaviour)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if path.suffix == ".py":
        lines = [line for line in lines if not line.lstrip().startswith("#")]
    return "\n".join(lines)


def test_pack_prose_names_no_cgm_version():
    offenders = [
        f"{path.relative_to(REPO_ROOT).as_posix()}: {match.group(0)}"
        for path in VERSION_FREE_FILES
        for match in CGM_VERSION_RE.finditer(_shipped_text(path))
    ]
    assert offenders == []
