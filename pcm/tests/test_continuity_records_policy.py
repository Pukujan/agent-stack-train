from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from continuity.cli import (
    CONTINUITY_RECORDS_POLICY_MARKER,
    GITHUB_ISSUE_LIFECYCLE_GUIDANCE,
    github_issue_template,
    github_pr_template,
    init_repo,
    task_new,
)

ROOT = Path(__file__).parents[1]


class ContinuityRecordsPolicyTests(unittest.TestCase):
    def test_canonical_policy_covers_human_machine_evidence_and_boundaries(self) -> None:
        policy = (ROOT / "docs" / "CONTINUITY_RECORDS_POLICY.md").read_text(encoding="utf-8")
        lowered = policy.lower()
        for required in (
            "human explanation",
            "problem and consequence",
            "observable outcome",
            "evidence and provenance",
            "directly to a relevant, authoritative source",
            "starting code/data/source revision",
            "machine-readable layer",
            "proportionality and enforcement",
            "automatic chat capture",
        ):
            with self.subTest(required=required):
                self.assertIn(required, lowered)
        self.assertNotIn("readme", lowered)
        self.assertIn(CONTINUITY_RECORDS_POLICY_MARKER, policy)

    def test_policy_marker_is_synchronized_across_pcm_and_generated_guidance(self) -> None:
        for relative_path in (
            "AGENTS.md",
            "HANDOFF.md",
            "templates/v1/minimal/HANDOFF.md",
            "templates/v1/software/AGENTS.md",
        ):
            with self.subTest(path=relative_path):
                content = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn(CONTINUITY_RECORDS_POLICY_MARKER, content)

    def test_pcm_issue_and_pr_templates_match_the_installed_templates(self) -> None:
        issue_path = ROOT / ".github" / "ISSUE_TEMPLATE" / "task.md"
        pr_path = ROOT / ".github" / "pull_request_template.md"
        self.assertEqual(issue_path.read_text(encoding="utf-8"), github_issue_template())
        self.assertEqual(pr_path.read_text(encoding="utf-8"), github_pr_template())
        self.assertIn("Problem and consequence", github_issue_template())
        self.assertIn("Evidence and sources", github_issue_template())
        self.assertIn("Reproduction (only when needed)", github_issue_template())
        self.assertIn("Human outcome", github_pr_template())
        self.assertIn("do not paste full logs", github_pr_template())
        self.assertIn("only when useful", github_pr_template())

    def test_issue_transition_safeguard_reaches_policy_and_generated_guidance(self) -> None:
        policy = (ROOT / "docs" / "CONTINUITY_RECORDS_POLICY.md").read_text(encoding="utf-8").lower()
        self.assertIn("negated sentence can still be interpreted", policy)
        self.assertIn("commit message", policy)
        self.assertIn("linking-a-pull-request-to-an-issue", policy)

        generated = github_pr_template().lower()
        self.assertIn("negation does not cancel it", generated)
        self.assertIn("refs #<number>", generated)
        self.assertIn(GITHUB_ISSUE_LIFECYCLE_GUIDANCE.lower(), generated)

        minimal_root = Path(tempfile.mkdtemp(prefix="continuity-records-minimal-issues-"))
        software_root = Path(tempfile.mkdtemp(prefix="continuity-records-software-issues-"))
        self.addCleanup(shutil.rmtree, minimal_root, True)
        self.addCleanup(shutil.rmtree, software_root, True)
        init_repo(minimal_root, "minimal", "Minimal Example", "MIN", github_templates=True)
        init_repo(software_root, "software", "Software Example", "APP", github_templates=True)
        for relative_path in ("HANDOFF.md", ".github/pull_request_template.md"):
            text = (minimal_root / relative_path).read_text(encoding="utf-8").lower()
            self.assertIn("negation does not cancel it", text)
        for relative_path in ("AGENTS.md", ".github/pull_request_template.md"):
            text = (software_root / relative_path).read_text(encoding="utf-8").lower()
            self.assertIn("negation does not cancel it", text)
        for relative_path in (
            "HANDOFF.md",
            "AGENTS.md",
            "templates/v1/minimal/HANDOFF.md",
            "templates/v1/software/AGENTS.md",
        ):
            text = (ROOT / relative_path).read_text(encoding="utf-8").lower()
            self.assertTrue("negation does not cancel it" in text or "under negation" in text)

    def test_new_profiles_and_tasks_carry_the_short_contract(self) -> None:
        minimal_root = Path(tempfile.mkdtemp(prefix="continuity-records-minimal-"))
        software_root = Path(tempfile.mkdtemp(prefix="continuity-records-software-"))
        self.addCleanup(shutil.rmtree, minimal_root, True)
        self.addCleanup(shutil.rmtree, software_root, True)

        init_repo(minimal_root, "minimal", "Minimal Example", "MIN")
        init_repo(software_root, "software", "Software Example", "APP")
        minimal_handoff = (minimal_root / "HANDOFF.md").read_text(encoding="utf-8").lower()
        software_agents = (software_root / "AGENTS.md").read_text(encoding="utf-8").lower()
        for text in (minimal_handoff, software_agents):
            self.assertIn("continuity records", text)
            self.assertIn("human", text)
            self.assertIn("evidence", text)
            self.assertIn("skimmable", text)
            self.assertIn(CONTINUITY_RECORDS_POLICY_MARKER, text)

        task_path = task_new(
            minimal_root,
            "example task",
            "Deliver a useful human-visible result.",
            "A fresh session needs the context and evidence to continue.",
            "test-agent",
            "P1",
        )
        task_text = task_path.read_text(encoding="utf-8").lower()
        self.assertIn("human outcome", task_text)
        self.assertIn("scope and boundaries", task_text)
        self.assertIn("evidence and sources", task_text)
        self.assertIn("reproduction details (only when needed)", task_text)


if __name__ == "__main__":
    unittest.main()
