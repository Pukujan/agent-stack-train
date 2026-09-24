from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from continuity.cli import ContinuityError, init_repo

ROOT = Path(__file__).parents[1]

# Independent contract expectations: deleting the generator's own source text must
# fail these checks too. Historical checkpoint prose is intentionally not scanned.
REQUIRED = (
    "github issues are required",
    "durable project progression",
    "mandatory versioned projections",
    "ephemeral execution aids",
    "leaf child issue",
    "parent ancestry and dependencies",
    "one child per independently deliverable scope",
    "correction/supersession link before dependent work",
    "one primary writer",
    "shared-document edits",
    "disputed or unknown",
    "never rewrite checkpoint history",
    "affected descendants",
    "re-plan and revalidate",
    "before every push",
    "reviewed catalog/generated index",
    "synchronously pushes",
    "after every successful push",
    "request id and exact pushed sha",
    "linked parent progression update",
    "without another checkpoint/push",
    "automatic issue-comment synchronization is not implemented",
    "required ci and github auto-merge are mandatory",
    "exact current-base or merge-queue candidate",
    "missing, failed, skipped, stale or unverified gates fail closed",
    "no completion or cleanup",
    "receipt-only transitions need no recursive doc commit",
    "as-of/pending state",
)
FORBIDDEN = (
    "coordination mirrors, not sole authority",
    "issues/beads/prs mirror coordination",
    "checkpoint commits are pushed asynchronously",
    "github tracking is optional",
    "auto-merge is optional",
)


def assert_guidance(test: unittest.TestCase, content: str) -> None:
    text = content.lower()
    for phrase in REQUIRED:
        test.assertIn(phrase, text)
    for phrase in FORBIDDEN:
        test.assertNotIn(phrase, text)


class GitHubProgressionPolicyTests(unittest.TestCase):
    def test_checked_in_guidance_carries_the_whole_contract(self) -> None:
        for path in (
            "AGENTS.md", "HANDOFF.md", "templates/v1/minimal/HANDOFF.md",
            "templates/v1/minimal/PROJECT.md", "templates/v1/software/AGENTS.md",
            "templates/v1/software/README.md", ".github/ISSUE_TEMPLATE/task.md",
            ".github/pull_request_template.md",
        ):
            with self.subTest(path=path):
                assert_guidance(self, (ROOT / path).read_text(encoding="utf-8"))

    def test_adopted_profiles_and_workspace_modes_receive_contract(self) -> None:
        for profile in ("minimal", "software"):
            for mode in ("managed-worktrees", "single-checkout"):
                with self.subTest(profile=profile, mode=mode), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    init_repo(root, profile, "Adopter", "APP", github_templates=True,
                              workspace_mode=mode, github_authority=True)
                    paths = ["PROJECT.md", "HANDOFF.md", ".github/ISSUE_TEMPLATE/task.md",
                             ".github/pull_request_template.md"]
                    if profile == "software":
                        paths.extend(["AGENTS.md", "README.md"])
                    for path in paths:
                        with self.subTest(path=path):
                            assert_guidance(self, (root / path).read_text(encoding="utf-8"))
                    current = (root / "checkpoints/CURRENT.md").read_text(encoding="utf-8")
                    self.assertIn("as-of projection", current)
                    self.assertIn("issue, record its APP task/branch identity", current)

    def test_optional_template_installation_does_not_make_policy_optional(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            init_repo(root, "minimal", "Adopter", "APP", github_authority=True)
            self.assertFalse((root / ".github").exists())
            assert_guidance(self, (root / "HANDOFF.md").read_text(encoding="utf-8"))

    def test_adoption_conflict_preserves_every_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in ("PROJECT.md", "AGENTS.md", "HANDOFF.md", ".github/ISSUE_TEMPLATE/task.md"):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("Target-owned contract: preserve me.\n", encoding="utf-8")
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            with self.assertRaises(ContinuityError):
                init_repo(root, "software", "Adopter", "APP", github_templates=True, github_authority=True)
            after = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_normative_and_human_docs_do_not_reintroduce_old_authority(self) -> None:
        for relative in ("PROJECT.md", "README.md", "SPEC.md", "docs/HANDOFF_PROTOCOL.md",
                         "docs/TARGET_ADOPTION.md", "docs/CONTINUITY_RECORDS_POLICY.md"):
            with self.subTest(path=relative):
                text = (ROOT / relative).read_text(encoding="utf-8").lower()
                for phrase in FORBIDDEN:
                    self.assertNotIn(phrase, text)
                for phrase in ("github", "required ci", "auto-merge", "leaf", "dependenc"):
                    self.assertIn(phrase, text)
        spec = (ROOT / "SPEC.md").read_text(encoding="utf-8").lower()
        for phrase in ("before every push", "after each successful push", "after ci/merge",
                       "stop the receipt loop", "owner direction", "contradictory evidence",
                       "visited set", "issue prose and local locks are not distributed mutual exclusion"):
            self.assertIn(phrase, spec)


if __name__ == "__main__":
    unittest.main()
