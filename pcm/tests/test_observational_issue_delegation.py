"""PCM-0225 / #225: the boundary with observational-issue-ops (OIO).

Two promises are checked here, both offline:

1. PCM's checked-in release-train pin (docs/OBSERVATIONAL_ISSUE_DELEGATION.md)
   agrees with this repository's own version sources, so the pin cannot drift
   away from the build it certifies.
2. PCM keeps no second copy of the OIO protocol: no observational-issue form
   and no 3-plane triage workflow live in this repository.

The test reads checked-in files and, for the pin's commit, the local Git object
store. A shallow CI clone that lacks that commit skips the Git-backed assertion
instead of failing; no network access is used.
"""

from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path
from typing import cast

from continuity import __version__ as cli_version

ROOT = Path(__file__).resolve().parents[1]
DELEGATION = ROOT / "docs" / "OBSERVATIONAL_ISSUE_DELEGATION.md"

START_MARKER = "<!-- pcm:stack-release-train:start -->"
END_MARKER = "<!-- pcm:stack-release-train:end -->"
TRAIN_URL = "https://github.com/Pukujan/agent-stack-train"
OIO_URL = "https://github.com/Pukujan/observational-issue-ops"
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def load_pin() -> dict[str, object]:
    """Read the release-train pin block out of the delegation record."""
    text = DELEGATION.read_text(encoding="utf-8")
    assert START_MARKER in text, "release-train pin block start marker is missing"
    assert END_MARKER in text, "release-train pin block end marker is missing"
    block = text.split(START_MARKER, 1)[1].split(END_MARKER, 1)[0]
    match = re.search(r"```json\s*(.*?)```", block, flags=re.DOTALL)
    assert match is not None, "release-train pin block has no JSON fence"
    return cast("dict[str, object]", json.loads(match.group(1)))


def git_available() -> bool:
    try:
        result = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--git-dir"], capture_output=True)
    except OSError:
        return False
    return result.returncode == 0


class ReleaseTrainPinTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pin = load_pin()

    def test_pin_names_pcm_and_the_train_publisher(self) -> None:
        self.assertEqual(self.pin["component"], "project-continuity-modules")
        self.assertEqual(self.pin["train_publisher"], TRAIN_URL)
        self.assertEqual(self.pin["train_source"], "stack-releases.json")
        self.assertRegex(str(self.pin["release_train"]), r"^\d{4}-\d{2}-\d{2}$")

    def test_pin_cli_version_agrees_with_this_repository(self) -> None:
        # The pin certifies a CLI version; it must equal the version this
        # checkout declares, or the published train names a build that is not here.
        self.assertEqual(self.pin["version"], cli_version)
        self.assertEqual(self.pin["cli"], cli_version)

    def test_pin_protocol_version_agrees_with_the_repository_config(self) -> None:
        config = json.loads((ROOT / ".continuity" / "config.json").read_text(encoding="utf-8"))
        self.assertEqual(self.pin["protocol_version"], config["protocol_version"])

    def test_verified_commit_is_a_full_commit_id(self) -> None:
        # A pin must name a full 40-character commit id; a truncated or padded
        # string would not resolve to the revision the train claims to certify.
        self.assertRegex(str(self.pin["verified_commit"]), FULL_SHA_RE)

    def test_verified_commit_resolves_locally_when_history_is_available(self) -> None:
        if not git_available():
            self.skipTest("no local Git repository; the checked-in pin values are still asserted above")
        verified = str(self.pin["verified_commit"])
        probe = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", verified], capture_output=True)
        if probe.returncode != 0:
            self.skipTest("pin commit is absent from this clone (shallow checkout); string checks still apply")
        subject = subprocess.run(
            ["git", "-C", str(ROOT), "log", "-1", "--format=%s", verified],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(subject, self.pin["verified_commit_subject"])


class NoCompetingProtocolCopyTests(unittest.TestCase):
    """PCM points at OIO; it must not carry a second copy of OIO's protocol."""

    def test_no_observational_issue_form_is_vendored(self) -> None:
        names = sorted(path.name for path in (ROOT / ".github" / "ISSUE_TEMPLATE").glob("*") if path.is_file())
        self.assertIn("task.md", names)  # PCM's own task template stays
        for name in names:
            with self.subTest(name=name):
                self.assertNotIn("observational", name.lower())

    def test_no_triage_workflow_is_vendored(self) -> None:
        for path in (ROOT / ".github" / "workflows").glob("*"):
            if not path.is_file():
                continue
            with self.subTest(path=path.name):
                self.assertNotIn("triage", path.name.lower())
                self.assertNotIn("observational", path.name.lower())
                self.assertNotIn("three-plane", path.read_text(encoding="utf-8").lower())

    def test_the_record_names_oio_and_redirects_the_superseded_proposal(self) -> None:
        for relative in ("docs/OBSERVATIONAL_ISSUE_DELEGATION.md", "README.md", "AGENTS.md", "SPEC.md"):
            with self.subTest(path=relative):
                self.assertIn("observational-issue-ops", (ROOT / relative).read_text(encoding="utf-8"))
        record = DELEGATION.read_text(encoding="utf-8")
        self.assertIn("issues/224", record)  # superseded in-PCM proposal
        self.assertIn("issues/225", record)  # owning boundary issue
        self.assertIn("superseded", record.lower())
        # The record points at the publisher that actually holds the train today,
        # not at the earlier "OIO publishes stack-releases.json" claim.
        self.assertIn(TRAIN_URL, record)
        self.assertIn(OIO_URL, record)


if __name__ == "__main__":
    unittest.main()
