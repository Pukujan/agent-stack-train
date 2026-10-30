"""Shared fixtures for the hotload install taxonomy (SPEC.md section 8).

The five install test modules (acceptance/PDD, states/SDD, gates/TDD,
metamorphic, manifest/differential) all drive the same installer against the
same fake world: a fixture agent-stack-train checkout (``acs/``, ``pcm/``,
``cgm/``, ``oio/`` folders at one commit) and stubbed external checkers.
Keeping that world here means the tests assert behaviour, not scaffolding.

The seat-protocol fixtures at the bottom of this file (``seat_protocol``,
``claim_store``, ``clock``) are the same idea for the coordination runtime:
``claim_store`` is parametrised over the local-file store and the in-memory
store, so the protocol suite proves the state machine against the interface
rather than against one implementation.

No network and no pinned checkouts are needed; everything is offline and
cross-platform (Windows, macOS, Linux).
"""

from __future__ import annotations

import copy
import json
import subprocess
from datetime import datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

MODULE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = MODULE_ROOT / "scripts" / "acs_install.py"
SEAT_PROTOCOL = MODULE_ROOT / "scripts" / "seat_protocol.py"
MODULE_REL = "modules/coordination/multi-agent-hotload/v0.1.0"

# The fixture stack checkout's one commit: every component is at it.
STACK_SHA = "e" * 40
# The versions the fixture stack's component version files declare.
VERSIONS = {
    "project-continuity-modules": "0.6.0",
    "content-generation-modules": "0.5.12",
    "agent-custom-setup": "0.2.0",
    "observational-issue-ops": "0.1.0",
}

CGM_MODULES = [
    "brand-foundation",
    "content-context",
    "writing-direction",
    "human-sounding-writing",
    "human-output-naming",
    "visual-direction",
    "image-generation",
    "html-demo",
]

# Mirrors the real ``pins.json``: the CGM module shape and the ACS module id/version.
# It carries no ``pcm`` block and no ``cgm.version``; ``pins_at_stack`` adds those
# from the fixture stack, as ``acs_install.run`` does.
PINS = {
    "cgm": {"modules": list(CGM_MODULES)},
    "acs_hotload_module": {"id": "multi-agent-hotload", "version": "0.1.0"},
}


def load_installer():
    spec = spec_from_file_location("acs_install", SCRIPT)
    assert spec and spec.loader
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stack_requires() -> dict:
    """What the fixture stack provides: each component's version at STACK_SHA."""
    return {name: {"version": version, "commit": STACK_SHA} for name, version in VERSIONS.items()}


def pins_at_stack() -> dict:
    """``pins.json`` as ``acs_install.run`` overlays it: the stack's commit and versions."""
    pins = copy.deepcopy(PINS)
    pins.setdefault("pcm", {})["commit"] = STACK_SHA
    pins["pcm"]["cli_version"] = VERSIONS["project-continuity-modules"]
    pins.setdefault("cgm", {})["commit"] = STACK_SHA
    pins["cgm"]["version"] = VERSIONS["content-generation-modules"]
    return pins


def write_stack(root: Path, *, with_oio_installer: bool = True, omit: str | None = None) -> Path:
    """Lay out a fixture agent-stack-train checkout at ``root``.

    ``omit`` names a folder (``pcm``, ``cgm``, ``oio``) to leave out, for the
    incomplete-checkout cases. The git commit itself is stubbed (``stub_externals``).
    """
    pack = root / "acs" / MODULE_REL
    pack.mkdir(parents=True)
    (pack / "pins.json").write_text(json.dumps({"pins": PINS}), encoding="utf-8")
    (root / "acs" / "registry.json").write_text(
        json.dumps({"version": VERSIONS["agent-custom-setup"]}), encoding="utf-8"
    )
    if omit != "pcm":
        init = root / "pcm" / "src" / "continuity" / "__init__.py"
        init.parent.mkdir(parents=True)
        init.write_text(
            f'__version__ = "{VERSIONS["project-continuity-modules"]}"\n', encoding="utf-8"
        )
    if omit != "cgm":
        (root / "cgm").mkdir()
        (root / "cgm" / "system-version.json").write_text(
            json.dumps({"version": VERSIONS["content-generation-modules"]}), encoding="utf-8"
        )
    if omit != "oio":
        (root / "oio").mkdir()
        (root / "oio" / "VERSION").write_text(
            VERSIONS["observational-issue-ops"] + "\n", encoding="utf-8"
        )
        if with_oio_installer:
            scripts = root / "oio" / ".github" / "scripts"
            scripts.mkdir(parents=True)
            (scripts / "oio_installer.py").write_text("# stub\n", encoding="utf-8")
    return root


def git_repo(path: Path) -> str:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.invalid"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=path, check=True)
    (path / "f.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=path, check=True)
    out = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True, check=True
    )
    return out.stdout.strip()


@pytest.fixture
def installer():
    """A freshly loaded acs_install module (monkeypatch-safe, function-scoped)."""
    return load_installer()


@pytest.fixture
def make_stack(tmp_path: Path):
    """A fixture agent-stack-train checkout; see ``write_stack`` for the options."""

    def _make(**options) -> Path:
        return write_stack(tmp_path / "stack", **options)

    return _make


@pytest.fixture
def make_adopter(tmp_path: Path):
    def _make(name: str = "adopter", *, with_adapter: bool = True) -> Path:
        adopter = tmp_path / name
        adopter.mkdir()
        if with_adapter:
            (adopter / ".content-system").mkdir()
        return adopter

    return _make


@pytest.fixture
def stub_externals(monkeypatch, installer):
    """Make check_pins/hotload_check succeed and report the stack commit.

    ``oio_exit`` is the exit code of OIO's own installer (the one script
    ``run_script`` is asked to run for it); non-zero leaves the install PARTIAL.
    """

    def _stub(*, oio_supported: bool = True, oio_exit: int = 0) -> None:
        def fake_run_script(argv):
            return oio_exit if Path(str(argv[1])).name == "oio_installer.py" else 0

        monkeypatch.setattr(installer, "git_head", lambda root: STACK_SHA)
        monkeypatch.setattr(installer, "run_script", fake_run_script)
        monkeypatch.setattr(
            installer,
            "oio_platform_supported",
            lambda *_: (True, "") if oio_supported else (False, "os.O_NOFOLLOW is unavailable"),
        )

    return _stub


@pytest.fixture
def run_args(installer):
    def _make(stack_root, adopter, **over):
        base = dict(
            adopter_root=adopter,
            stack_root=stack_root,
            project_name=None,
            project_id=None,
            dry_run=False,
            force=False,
        )
        base.update(over)
        return installer.argparse.Namespace(**base)

    return _make


# ---------------------------------------------------------------------------
# Seat-protocol fixtures (tests/test_coordination*.py)


def load_seat_protocol():
    """Load ``scripts/seat_protocol.py`` the way the pack loads its scripts."""
    spec = spec_from_file_location("seat_protocol", SEAT_PROTOCOL)
    assert spec and spec.loader
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def seat_protocol():
    """A freshly loaded seat_protocol module (function-scoped)."""
    return load_seat_protocol()


@pytest.fixture(params=["local_file", "in_memory"])
def claim_store(seat_protocol, tmp_path, request):
    """The seat store under test, parametrised over both implementations.

    Running the same suite against the local-file store and the in-memory
    store is what proves the state machine is written against the
    ``ClaimStore`` interface rather than one implementation — the abstraction
    the authoritative-store question rests on.
    """
    if request.param == "local_file":
        return seat_protocol.LocalFileClaimStore(tmp_path / "boss_claim.json")
    return seat_protocol.InMemoryClaimStore()


@pytest.fixture
def machine(seat_protocol, claim_store):
    """A SeatMachine over the parametrised store at the default 30m lease."""
    return seat_protocol.SeatMachine(claim_store, lease_ttl_minutes=30)


@pytest.fixture
def clock():
    """A deterministic clock: starts 2026-10-13T12:00Z, ``advance`` moves it."""

    class _Clock:
        def __init__(self):
            self.now = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)

        def advance(self, minutes: float) -> datetime:
            self.now = self.now + timedelta(minutes=minutes)
            return self.now

        def at(self, minutes: float = 0.0) -> datetime:
            return self.now + timedelta(minutes=minutes)

    return _Clock()
