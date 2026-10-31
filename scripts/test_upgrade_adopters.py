#!/usr/bin/env python3
"""Stdlib tests for the upgrade decisions and the behind-the-train warning."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_manifest  # noqa: E402
import upgrade_adopters as up  # noqa: E402

OLD, NEW = "a" * 40, "b" * 40
FOLLOWS = {"pins": {"agent-stack-train": {}}}


def adopter(manifest=FOLLOWS, installed=OLD, prs=None) -> up.Adopter:
    return up.Adopter("o/r", manifest, installed, prs or {})


def behind(old: str, new: str) -> bool:
    return (old, new) == (OLD, NEW)


class DecideTests(unittest.TestCase):
    def test_an_adopter_behind_the_train_is_upgraded(self) -> None:
        self.assertEqual(up.decide(adopter(), NEW, behind).action, "upgrade")

    def test_an_up_to_date_adopter_is_left_alone(self) -> None:
        self.assertEqual(up.decide(adopter(installed=NEW), NEW, behind).reason, "up to date")

    def test_an_open_pull_request_that_installs_it_wins(self) -> None:
        decision = up.decide(adopter(prs={12: OLD, 51: NEW}), NEW, behind)
        self.assertEqual((decision.action, decision.reason), ("skip", "open pull request #51 already installs it"))

    def test_a_four_repository_manifest_is_not_touched(self) -> None:
        manifest = {"pins": {"observational-issue-ops": {}, "agent-custom-setup": {}}}
        self.assertEqual(up.decide(adopter(manifest=manifest), NEW, behind).action, "skip")

    def test_a_fixed_stack_pin_is_not_touched(self) -> None:
        manifest = {"pins": {"agent-stack-train": {"commit": OLD}}}
        self.assertEqual(up.decide(adopter(manifest=manifest), NEW, behind).action, "skip")

    def test_a_missing_manifest_is_not_touched(self) -> None:
        self.assertEqual(up.decide(adopter(manifest=None), NEW, behind).action, "skip")

    def test_an_install_that_is_not_behind_is_not_downgraded(self) -> None:
        self.assertEqual(up.decide(adopter(installed="c" * 40), NEW, behind).action, "skip")

    def test_no_installed_commit_is_not_guessed(self) -> None:
        self.assertEqual(up.decide(adopter(installed=None), NEW, behind).action, "skip")

    def test_the_body_lists_files_that_still_name_the_old_commit(self) -> None:
        body = up.pr_body("1.0.2", NEW, OLD, ["AGENTS.md"], "acs_install: OK (state=READY)")
        self.assertIn("- `AGENTS.md`", body)
        self.assertIn("never merges", body)
        self.assertIn(f"Refs {up.UPGRADE_ISSUE}", body)


class InstalledWarningTests(unittest.TestCase):
    TRAIN = {"certified": {"agent-stack-train": {"version": "1.0.1", "commit": NEW}}}

    def test_an_old_install_warns(self) -> None:
        warning = check_manifest.installed_warning(FOLLOWS, {"oio_ref": OLD}, self.TRAIN)
        self.assertIn("certifies agent-stack-train 1.0.1", warning)

    def test_the_certified_install_does_not_warn(self) -> None:
        self.assertIsNone(check_manifest.installed_warning(FOLLOWS, {"oio_ref": NEW}, self.TRAIN))

    def test_a_four_repository_manifest_does_not_warn(self) -> None:
        manifest = {"pins": {"observational-issue-ops": {}}}
        self.assertIsNone(check_manifest.installed_warning(manifest, {"oio_ref": OLD}, self.TRAIN))


if __name__ == "__main__":
    unittest.main()
