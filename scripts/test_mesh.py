#!/usr/bin/env python3
"""The four stack repos must require each other at the mesh versions."""
from __future__ import annotations

import json
import sys
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mesh  # noqa: E402

PCM = "project-continuity-modules"
CGM = "content-generation-modules"
ACS = "agent-custom-setup"
OIO = "observational-issue-ops"

OLD_PCM = "4e2385474b4af9249ca009cbdcb38c4498932475"
NEW_PCM = "197f7ba8dab34e9738f85a510a673bc2522b1899"
CGM_SHA = "b487b48c12c375ad8a82016f8bb50fb3c109b443"
ACS_SHA = "c15e53fc17e8158e9182709d5d3b6f255bcc11f2"
OIO_SHA = "469adf1e9cb12b004424118c77270e3ca0e71217"


def stack() -> dict:
    return {
        "certified": {
            PCM: {"version": "0.7.0", "commit": NEW_PCM},
            CGM: {"version": "0.5.12", "commit": CGM_SHA},
            ACS: {"version": "0.2.0", "commit": ACS_SHA},
            OIO: {"version": "0.1.0", "commit": OIO_SHA},
        }
    }


class MeshTests(unittest.TestCase):
    def test_a_pcm_release_moves_what_every_other_repo_must_require(self) -> None:
        current = stack()
        released = mesh.apply_release(current, PCM, "0.8.0", "a" * 40)
        required = mesh.declaration_from(released)["requires"]
        self.assertEqual(required[PCM]["version"], "0.8.0")
        self.assertEqual(required[CGM]["version"], "0.5.12")
        self.assertEqual(required[ACS]["commit"], ACS_SHA)
        self.assertEqual(required[OIO]["commit"], OIO_SHA)

    def test_cgm_cannot_keep_an_old_pcm_after_pcm_releases(self) -> None:
        released = mesh.apply_release(stack(), PCM, "0.8.0", "a" * 40)
        declaration = mesh.declaration_from(stack())
        errors = mesh.declaration_problems(released, declaration)
        self.assertTrue(any(PCM in error and "0.8.0" in error and "0.7.0" in error for error in errors))

    def test_acs_and_oio_cannot_keep_an_old_pcm_either(self) -> None:
        released = mesh.apply_release(stack(), PCM, "0.8.0", "a" * 40)
        errors = mesh.declaration_problems(released, mesh.declaration_from(stack()))
        self.assertTrue(errors)
        aligned = mesh.declaration_from(released)
        self.assertEqual(mesh.declaration_problems(released, aligned), [])

    def test_a_repo_cannot_stay_on_an_older_version_of_itself(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src" / "continuity").mkdir(parents=True)
            (repo / "src" / "continuity" / "__init__.py").write_text(
                '__version__ = "0.6.0"\n', encoding="utf-8"
            )
            (repo / mesh.MESH_NAME).write_text(
                json.dumps(mesh.declaration_from(stack())), encoding="utf-8"
            )
            errors = mesh.check_repo(stack(), repo, PCM)
            self.assertTrue(any("0.6.0" in error and "0.7.0" in error for error in errors))

    def test_write_then_check_is_clean_for_every_component(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "src" / "continuity").mkdir(parents=True)
            (repo / "src" / "continuity" / "__init__.py").write_text(
                '__version__ = "0.7.0"\n', encoding="utf-8"
            )
            workflow = repo / ".github" / "workflows"
            workflow.mkdir(parents=True)
            (workflow / "ci.yml").write_text(
                textwrap.dedent(
                    f"""\
                    env:
                      PCM_PIN: {OLD_PCM}
                    """
                ),
                encoding="utf-8",
            )
            mesh.write_repo(stack(), repo)
            self.assertEqual(mesh.check_repo(stack(), repo, PCM), [])
            pinned = (workflow / "ci.yml").read_text(encoding="utf-8")
            self.assertIn(NEW_PCM, pinned)
            self.assertNotIn(OLD_PCM, pinned)

    def test_missing_mesh_file_fails(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            errors = mesh.check_repo(stack(), Path(tmp), OIO)
            self.assertTrue(any(mesh.MESH_NAME in error for error in errors))


if __name__ == "__main__":
    unittest.main()
