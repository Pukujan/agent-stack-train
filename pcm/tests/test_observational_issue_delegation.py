"""PCM-0225 / #225: the boundary with observational-issue-ops (OIO).

Two promises are checked here, both offline:

1. PCM keeps no copy of the release train. The certified set lives once, in
   the root `stack-releases.json` of agent-stack-train, whose `pcm/` folder
   this is. The train's PCM entry may lag this folder's version (a build lands
   before the train is re-certified) but must never be ahead of it.
2. PCM keeps no second copy of the OIO protocol: no observational-issue form
   and no 3-plane triage workflow live in this repository.

The test reads checked-in files only; no network access is used.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from typing import cast

from continuity import __version__ as cli_version

ROOT = Path(__file__).resolve().parents[1]
DELEGATION = ROOT / "docs" / "OBSERVATIONAL_ISSUE_DELEGATION.md"

STACK_ROOT = ROOT.parent
TRAIN = STACK_ROOT / "stack-releases.json"
TRAIN_URL = "https://github.com/Pukujan/agent-stack-train"
OIO_URL = "https://github.com/Pukujan/observational-issue-ops"
COMPONENT = "project-continuity-modules"
FULL_SHA_RE = re.compile(r"\b[0-9a-f]{40}\b")


def version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split("."))


def train_section() -> str:
    """The record's section on the release train, up to the next heading of its level."""
    record = DELEGATION.read_text(encoding="utf-8")
    section = record.split("## PCM's role in the stack release train", 1)[1]
    return section.split("\n### ", 1)[0]


class ReleaseTrainTests(unittest.TestCase):
    def test_the_record_points_at_the_train_and_copies_none_of_it(self) -> None:
        section = train_section()
        self.assertIn("stack-releases.json", section)
        self.assertIn(TRAIN_URL, section)
        self.assertNotIn("pcm:stack-release-train", section)
        self.assertNotIn("```json", section)
        self.assertIsNone(FULL_SHA_RE.search(section), "the record copies a commit from the train")

    def test_the_train_does_not_certify_a_version_ahead_of_this_folder(self) -> None:
        train = json.loads(TRAIN.read_text(encoding="utf-8"))
        entry = cast("dict[str, object]", train["certified"][COMPONENT])
        certified = str(entry["version"])
        self.assertLessEqual(
            version_tuple(certified),
            version_tuple(cli_version),
            f"the train certifies PCM {certified}, ahead of this folder's {cli_version}",
        )


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
