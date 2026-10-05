"""PCM-0225 / #225: the boundary with observational-issue-ops (OIO).

Two promises are checked here, both offline:

1. PCM's checked-in release-train pin (docs/OBSERVATIONAL_ISSUE_DELEGATION.md)
   keeps two halves apart: the `certified` train entry and this checkout's
   `source` version. The source half agrees with this repository's own version
   sources, so it cannot drift from the build; the certified half agrees with
   the commit it names, so it cannot claim a certification that commit does not
   carry. A source version may lead the certified train (a build lands before
   the train is re-certified), so the halves are never forced equal.
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


def repository_versions() -> tuple[str, str]:
    """The versions this checkout declares: CLI package, then protocol."""
    config = json.loads((ROOT / ".continuity" / "config.json").read_text(encoding="utf-8"))
    return cli_version, str(config["protocol_version"])


def pin_findings(
    pin: dict[str, object],
    *,
    source_version: str,
    source_protocol_version: str,
    commit_version: str | None = None,
) -> list[str]:
    """Return the problems with a release-train pin, given the checkout's versions.

    The pin records two halves that are checked against different authorities:

    - ``source`` is what this checkout declares; it must equal the versions the
      checkout actually carries, so the record cannot drift from the build.
    - ``certified`` is what the train published. It must be internally
      consistent and, when ``commit_version`` is given, its commit must declare
      the version it certifies — a pin naming a revision that carries a
      different version is a false claim, not a lagging one.

    A source version may legitimately *lead* the certified train (a new build
    lands before the train is re-certified), so the two halves are never forced
    equal. ``commit_version`` is ``None`` in a shallow clone that lacks the
    certified commit; that assertion is then skipped.
    """
    problems: list[str] = []
    certified = cast("dict[str, object]", pin["certified"])
    source = cast("dict[str, object]", pin["source"])
    if certified["version"] != certified["cli"]:
        problems.append("certified version and cli disagree")
    if source["version"] != source_version:
        problems.append("source version disagrees with the checkout")
    if source["protocol_version"] != source_protocol_version:
        problems.append("source protocol version disagrees with the checkout")
    if commit_version is not None and commit_version != certified["version"]:
        problems.append("certified version disagrees with the commit it names")
    return problems


def git_available() -> bool:
    try:
        result = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--git-dir"], capture_output=True)
    except OSError:
        return False
    return result.returncode == 0


class ReleaseTrainPinTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pin = load_pin()
        self.certified = cast("dict[str, object]", self.pin["certified"])
        self.source = cast("dict[str, object]", self.pin["source"])

    def certified_commit(self) -> str:
        return str(self.certified["commit"])

    def commit_is_present(self) -> bool:
        if not git_available():
            return False
        probe = subprocess.run(
            ["git", "-C", str(ROOT), "cat-file", "-e", self.certified_commit()], capture_output=True
        )
        return probe.returncode == 0

    def test_pin_names_pcm_and_the_train_publisher(self) -> None:
        self.assertEqual(self.pin["component"], "project-continuity-modules")
        self.assertEqual(self.pin["train_publisher"], TRAIN_URL)
        self.assertEqual(self.pin["train_source"], "stack-releases.json")
        self.assertRegex(str(self.pin["release_train"]), r"^\d{4}-\d{2}-\d{2}$")

    def test_source_half_agrees_with_this_repository(self) -> None:
        # A source version may lead the last certified train (PCM #234 raised the
        # CLI to 0.7.0 after train 2026-10-01 published 0.6.0). The source half is
        # checked against this checkout, so it cannot drift from the build.
        source_version, source_protocol_version = repository_versions()
        self.assertEqual(self.source["version"], source_version)
        self.assertEqual(self.source["protocol_version"], source_protocol_version)

    def test_certified_half_is_internally_consistent(self) -> None:
        # The train publishes one version per component; the certified half cannot
        # disagree with itself, and its commit must be a full revision id.
        self.assertEqual(self.certified["version"], self.certified["cli"])
        self.assertRegex(self.certified_commit(), FULL_SHA_RE)

    def test_certified_commit_declares_the_certified_version(self) -> None:
        if not self.commit_is_present():
            self.skipTest("certified commit absent from this clone (shallow checkout); string checks still apply")
        declared = subprocess.run(
            ["git", "-C", str(ROOT), "show", f"{self.certified_commit()}:src/continuity/__init__.py"],
            capture_output=True,
            check=True,
            text=True,
        ).stdout
        self.assertIn(f'__version__ = "{self.certified["version"]}"', declared)

    def test_certified_commit_subject_matches_the_record(self) -> None:
        if not self.commit_is_present():
            self.skipTest("certified commit absent from this clone (shallow checkout); string checks still apply")
        subject = subprocess.run(
            ["git", "-C", str(ROOT), "log", "-1", "--format=%s", self.certified_commit()],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(subject, self.certified["commit_subject"])

    def test_the_current_pin_is_consistent(self) -> None:
        source_version, source_protocol_version = repository_versions()
        commit_version = None
        if self.commit_is_present():
            commit_version = str(self.certified["version"])
        self.assertEqual(
            pin_findings(
                self.pin,
                source_version=source_version,
                source_protocol_version=source_protocol_version,
                commit_version=commit_version,
            ),
            [],
        )

    def test_source_may_lead_the_certified_train(self) -> None:
        # Regression for the model this record now encodes: a source that leads
        # the certified train is a legitimate state, not drift.
        pin = load_pin()
        pin["source"] = {"version": "0.7.0", "protocol_version": "0.1.0-draft"}
        pin["certified"] = {**self.certified, "version": "0.6.0", "cli": "0.6.0"}
        self.assertEqual(
            pin_findings(
                pin, source_version="0.7.0", source_protocol_version="0.1.0-draft", commit_version="0.6.0"
            ),
            [],
        )

    def test_a_false_certification_is_rejected(self) -> None:
        # The failure this record exists to prevent: claiming the train certified
        # a version its named commit does not carry.
        pin = load_pin()
        pin["certified"] = {**self.certified, "version": "0.7.0", "cli": "0.7.0"}
        problems = pin_findings(
            pin, source_version="0.7.0", source_protocol_version="0.1.0-draft", commit_version="0.6.0"
        )
        self.assertIn("certified version disagrees with the commit it names", problems)

    def test_a_source_that_drifts_from_the_checkout_is_rejected(self) -> None:
        pin = load_pin()
        pin["source"] = {**self.source, "version": "9.9.9"}
        problems = pin_findings(
            pin, source_version=cli_version, source_protocol_version=repository_versions()[1], commit_version=None
        )
        self.assertIn("source version disagrees with the checkout", problems)


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
