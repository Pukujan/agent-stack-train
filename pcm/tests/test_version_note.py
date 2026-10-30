"""PCM-0057 (#162 owner decision B): checkpoint publishes a loud version-drift
NOTE comparing the running CLI build against the checkout's declared version.
Observability only — it never refuses to publish.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp

from continuity import __version__ as installed_version
from continuity.cli import version_drift_note


class VersionDriftNoteTests(unittest.TestCase):
    def checkout_with(self, version: str | None) -> Path:
        root = Path(mkdtemp(prefix="continuity-vdn-"))
        self.addCleanup(rmtree, root, True)
        if version is not None:
            package = root / "src" / "continuity"
            package.mkdir(parents=True)
            (package / "__init__.py").write_text(
                f'"""Fixture."""\n\n__version__ = "{version}"\n', encoding="utf-8"
            )
        return root

    def test_mismatch_is_reported_naming_both_versions(self) -> None:
        note = version_drift_note(self.checkout_with("9.9.9"))
        self.assertIsNotNone(note)
        assert note is not None
        self.assertIn("9.9.9", note)
        self.assertIn(installed_version, note)
        self.assertIn("NOTE", note)

    def test_match_is_silent(self) -> None:
        self.assertIsNone(version_drift_note(self.checkout_with(installed_version)))

    def test_non_python_checkout_has_no_version_to_compare(self) -> None:
        self.assertIsNone(version_drift_note(self.checkout_with(None)))

    def test_malformed_version_file_degrades_silently(self) -> None:
        root = self.checkout_with("1.0.0")
        (root / "src" / "continuity" / "__init__.py").write_text("x = ", encoding="utf-8")
        self.assertIsNone(version_drift_note(root))


if __name__ == "__main__":
    unittest.main()
