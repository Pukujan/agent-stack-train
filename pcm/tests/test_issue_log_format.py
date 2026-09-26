"""Deterministic tests for the issue-log-format 1.2.0 module (PCM-0027, #99).

Severity decisions (owner direction on #99, comment 5828143593, 2026-09-25):
missing marker -> warning (adopters stay VALID); contradictory -> error;
stale -> warning that prints the exact update step.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from continuity.cli import (
    CONTINUITY_RECORDS_POLICY_MARKER,
    ISSUE_LOG_FORMAT_END_MARKER,
    ISSUE_LOG_FORMAT_GUIDANCE,
    ISSUE_LOG_FORMAT_POLICY_MARKER,
    ISSUE_LOG_FORMAT_POLICY_VERSION,
    ISSUE_LOG_FORMAT_START_MARKER,
    ContinuityError,
    agents_template,
    github_issue_template,
    github_pr_template,
    handoff_template,
    init_repo,
    issue_log_format_findings,
    readme_template,
    validate_repo,
)

ROOT = Path(__file__).resolve().parents[1]


class IssueLogFormatModuleTests(unittest.TestCase):
    def test_guidance_block_is_mechanically_replaceable(self) -> None:
        self.assertTrue(ISSUE_LOG_FORMAT_GUIDANCE.startswith(ISSUE_LOG_FORMAT_START_MARKER))
        self.assertTrue(ISSUE_LOG_FORMAT_GUIDANCE.endswith(ISSUE_LOG_FORMAT_END_MARKER))
        self.assertIn(ISSUE_LOG_FORMAT_POLICY_MARKER, ISSUE_LOG_FORMAT_GUIDANCE)
        self.assertEqual(ISSUE_LOG_FORMAT_GUIDANCE.count(ISSUE_LOG_FORMAT_START_MARKER), 1)
        self.assertEqual(ISSUE_LOG_FORMAT_GUIDANCE.count(ISSUE_LOG_FORMAT_END_MARKER), 1)
        self.assertIn("1.2.0", ISSUE_LOG_FORMAT_POLICY_MARKER)
        self.assertEqual(ISSUE_LOG_FORMAT_POLICY_VERSION, "1.2.0")

    def test_diagram_rules_ship_in_the_block(self) -> None:
        g = ISSUE_LOG_FORMAT_GUIDANCE
        for phrase in (
            "Diagrams (mermaid)",
            "graph TD",
            "text list or table",
            "4+ ordered steps",
            "<details>",
            "6-word labels",
            "8 nodes",
            "renderer URLs",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, g)
        doc = (ROOT / "docs" / "ISSUE_LOG_FORMAT.md").read_text(encoding="utf-8")
        self.assertIn("## Diagrams (mermaid)", doc)
        self.assertIn("v11.17.2", doc)

    def test_readability_rules_ship_in_the_block(self) -> None:
        g = ISSUE_LOG_FORMAT_GUIDANCE
        for phrase in (
            "Readability rules",
            "plain-word meaning in the same sentence",
            "claim first, numbers as support",
            "no unexplained acronym or bare identifier on first use",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, g)
        doc = (ROOT / "docs" / "ISSUE_LOG_FORMAT.md").read_text(encoding="utf-8")
        self.assertIn("## Readability rules", doc)

    def test_marker_json_is_wellformed(self) -> None:
        payload = ISSUE_LOG_FORMAT_POLICY_MARKER.split("<!-- pcm:policy ", 1)[1]
        payload = payload.rsplit(" -->", 1)[0]
        data = json.loads(payload)
        self.assertEqual(data["id"], "issue-log-format")
        self.assertEqual(data["policy_version"], ISSUE_LOG_FORMAT_POLICY_VERSION)

    def test_every_generated_artifact_carries_the_block(self) -> None:
        artifacts = {
            "handoff": handoff_template("single-checkout"),
            "agents": agents_template("single-checkout"),
            "issue": github_issue_template(),
            "pr": github_pr_template(),
            "readme": readme_template("Example"),
        }
        for name, text in artifacts.items():
            with self.subTest(artifact=name):
                self.assertIn(ISSUE_LOG_FORMAT_GUIDANCE, text)
                self.assertIn(ISSUE_LOG_FORMAT_POLICY_MARKER, text)
                self.assertEqual(text.count(ISSUE_LOG_FORMAT_START_MARKER), 1)
                self.assertEqual(text.count(ISSUE_LOG_FORMAT_END_MARKER), 1)

    def test_issue_template_carries_core_tier_and_collapsed_investigation(self) -> None:
        issue = github_issue_template()
        self.assertIn("Problem and consequence", issue)
        self.assertIn("Evidence and sources", issue)
        self.assertIn("Reproduction (only when needed)", issue)
        self.assertIn("Investigation issues add:", issue)

    def test_pr_template_carries_the_pr_shape(self) -> None:
        pr = github_pr_template()
        lowered = pr.lower()
        self.assertIn("stays unchanged", lowered)
        self.assertIn("refs #<number>", lowered)
        self.assertIn("pull requests open reader-first", ISSUE_LOG_FORMAT_GUIDANCE.lower())

    def test_static_copies_carry_the_block_verbatim(self) -> None:
        for relative_path in (
            "AGENTS.md",
            "HANDOFF.md",
            "templates/v1/software/AGENTS.md",
            "templates/v1/software/README.md",
            "templates/v1/minimal/HANDOFF.md",
            ".github/ISSUE_TEMPLATE/task.md",
            ".github/pull_request_template.md",
        ):
            with self.subTest(path=relative_path):
                text = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn(ISSUE_LOG_FORMAT_GUIDANCE, text)
                self.assertEqual(text.count(ISSUE_LOG_FORMAT_START_MARKER), 1)
                self.assertEqual(text.count(ISSUE_LOG_FORMAT_END_MARKER), 1)

    def test_module_doc_ships_the_spec(self) -> None:
        text = (ROOT / "docs" / "ISSUE_LOG_FORMAT.md").read_text(encoding="utf-8")
        self.assertIn(ISSUE_LOG_FORMAT_POLICY_MARKER, text)
        self.assertIn("https://github.com/Pukujan/inference-recommendation-engine/issues/40", text)
        lowered = text.lower()
        for phrase in (
            "core tier",
            "investigation tier",
            "pull requests",
            "writing rules",
            "unverified",
            "counter-signal",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, lowered)

    def test_records_policy_references_the_module(self) -> None:
        text = (ROOT / "docs" / "CONTINUITY_RECORDS_POLICY.md").read_text(encoding="utf-8")
        self.assertIn("issue-log-format", text)
        self.assertIn("ISSUE_LOG_FORMAT.md", text)
        self.assertIn('"policy_version":"1.3.0"', text)


class IssueLogFormatValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self._dir = tempfile.TemporaryDirectory(prefix="pcm0027-validator-")
        self.root = Path(self._dir.name)
        (self.root / "AGENTS.md").write_text(
            "# Agent Operating Contract\n\n" + ISSUE_LOG_FORMAT_GUIDANCE + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._dir.cleanup()

    def guidance_errors(self) -> list[str]:
        return [e for e in validate_repo(self.root) if "issue-log-format" in e]

    def test_missing_marker_warns_and_stays_valid(self) -> None:
        (self.root / "AGENTS.md").write_text(
            "# Agent Operating Contract\n\nno policy markers here\n", encoding="utf-8"
        )
        errors, warnings = issue_log_format_findings(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("missing issue-log-format policy marker", warnings[0])
        self.assertIn("AGENTS.md", warnings[0])
        self.assertEqual(self.guidance_errors(), [])

    def test_no_guidance_files_produces_no_findings(self) -> None:
        (self.root / "AGENTS.md").unlink()
        errors, warnings = issue_log_format_findings(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_stale_marker_warns_and_prints_update_step(self) -> None:
        stale = ISSUE_LOG_FORMAT_GUIDANCE.replace(
            '"policy_version":"1.2.0"', '"policy_version":"0.9.0"'
        )
        (self.root / "AGENTS.md").write_text(
            "# Agent Operating Contract\n\n" + stale + "\n", encoding="utf-8"
        )
        errors, warnings = issue_log_format_findings(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        warning = warnings[0]
        self.assertIn("stale", warning)
        self.assertIn("0.9.0", warning)
        self.assertIn(ISSUE_LOG_FORMAT_START_MARKER, warning)
        self.assertIn(ISSUE_LOG_FORMAT_END_MARKER, warning)
        self.assertIn("continuity validate", warning)
        self.assertEqual(self.guidance_errors(), [])

    def test_current_marker_produces_no_findings(self) -> None:
        errors, warnings = issue_log_format_findings(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_contradictory_versions_are_errors(self) -> None:
        other = ISSUE_LOG_FORMAT_GUIDANCE.replace(
            '"policy_version":"1.2.0"', '"policy_version":"2.0.0"'
        )
        (self.root / "HANDOFF.md").write_text(
            "# Current Handoff\n\n" + other + "\n", encoding="utf-8"
        )
        errors, warnings = issue_log_format_findings(self.root)
        self.assertEqual(warnings, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("contradictory", errors[0])
        self.assertIn("1.2.0", errors[0])
        self.assertIn("2.0.0", errors[0])
        self.assertEqual(len(self.guidance_errors()), 1)

    def test_unbalanced_markers_are_errors(self) -> None:
        text = (
            "# Agent Operating Contract\n\n"
            + ISSUE_LOG_FORMAT_GUIDANCE
            + "\n\n"
            + ISSUE_LOG_FORMAT_START_MARKER
            + "\n"
        )
        (self.root / "AGENTS.md").write_text(text, encoding="utf-8")
        errors, _ = issue_log_format_findings(self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("unbalanced", errors[0])
        self.assertEqual(len(self.guidance_errors()), 1)

    def test_malformed_marker_json_is_an_error(self) -> None:
        text = (
            "# Agent Operating Contract\n\n"
            "<!-- pcm:policy {id:issue-log-format broken -->\n"
        )
        (self.root / "AGENTS.md").write_text(text, encoding="utf-8")
        errors, warnings = issue_log_format_findings(self.root)
        self.assertEqual(warnings, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("malformed", errors[0])
        self.assertEqual(len(self.guidance_errors()), 1)

    def test_issue_template_directory_is_scanned(self) -> None:
        (self.root / "AGENTS.md").unlink()
        template_dir = self.root / ".github" / "ISSUE_TEMPLATE"
        template_dir.mkdir(parents=True)
        (template_dir / "task.md").write_text("# Continuity task\n\nno marker\n", encoding="utf-8")
        errors, warnings = issue_log_format_findings(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("ISSUE_TEMPLATE", warnings[0])


class IssueLogFormatInitTests(unittest.TestCase):
    def test_init_carries_block_in_all_profile_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pcm0027-init-") as tmp:
            root = Path(tmp) / "target"
            init_repo(root, "software", "Target", "TGT", github_templates=True)
            for relative_path in (
                "AGENTS.md",
                "HANDOFF.md",
                "README.md",
                ".github/ISSUE_TEMPLATE/task.md",
                ".github/pull_request_template.md",
            ):
                with self.subTest(path=relative_path):
                    text = (root / relative_path).read_text(encoding="utf-8")
                    self.assertIn(ISSUE_LOG_FORMAT_GUIDANCE, text)
            errors, warnings = issue_log_format_findings(root)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

    def test_init_preserves_existing_adopter_edits(self) -> None:
        """Documented init semantics: a conflicting file refuses the whole run.

        init never overwrites or injects the guidance block into content the
        adopter edited; it raises, writes nothing, and the adopter applies the
        block manually between the markers (see test_updating_the_block...).
        """
        with tempfile.TemporaryDirectory(prefix="pcm0027-preserve-") as tmp:
            root = Path(tmp) / "target"
            root.mkdir()
            marker = (
                '<!-- continuity:project {"schema":"project-continuity.project.v1",'
                '"protocol_version":"0.1.0-draft","id":"tgt","title":"Target",'
                '"project":"PROJECT.md","tasks":"tasks","current":"checkpoints/CURRENT.md",'
                '"profile":"software","trackers":{"github":false},"version":"0.1.0-draft"} -->'
            )
            (root / "PROJECT.md").write_text(
                f"# Target\n\n{marker}\n\nUser contract.\n", encoding="utf-8"
            )
            (root / "AGENTS.md").write_text(
                "# Custom Contract\n\nThe user's own guidance stays.\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ContinuityError, "initialization conflicts"):
                init_repo(root, "software", "Target", "TGT")
            preserved = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(preserved, "# Custom Contract\n\nThe user's own guidance stays.\n")
            self.assertNotIn(ISSUE_LOG_FORMAT_GUIDANCE, preserved)
            self.assertFalse((root / ".continuity" / "config.json").exists())
            self.assertIn("User contract.", (root / "PROJECT.md").read_text(encoding="utf-8"))

    def test_updating_the_block_between_markers_is_the_documented_step(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pcm0027-update-") as tmp:
            root = Path(tmp) / "target"
            init_repo(root, "minimal", "Target", "TGT")
            handoff = root / "HANDOFF.md"
            text = handoff.read_text(encoding="utf-8")
            stale = text.replace(ISSUE_LOG_FORMAT_GUIDANCE, ISSUE_LOG_FORMAT_GUIDANCE.replace(
                '"policy_version":"1.2.0"', '"policy_version":"0.9.0"'
            ))
            handoff.write_text(stale, encoding="utf-8")
            _, warnings = issue_log_format_findings(root)
            self.assertEqual(len(warnings), 1)
            updated = handoff.read_text(encoding="utf-8").replace(
                ISSUE_LOG_FORMAT_GUIDANCE.replace(
                    '"policy_version":"1.2.0"', '"policy_version":"0.9.0"'
                ),
                ISSUE_LOG_FORMAT_GUIDANCE,
            )
            handoff.write_text(updated, encoding="utf-8")
            errors, warnings = issue_log_format_findings(root)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])


class IssueLogFormatRolloutTests(unittest.TestCase):
    def test_pcm_repository_itself_is_clean(self) -> None:
        errors, warnings = issue_log_format_findings(ROOT)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_records_policy_version_is_propagated(self) -> None:
        for relative_path in (
            "docs/CONTINUITY_RECORDS_POLICY.md",
            "AGENTS.md",
            "HANDOFF.md",
            "templates/v1/software/AGENTS.md",
            "templates/v1/minimal/HANDOFF.md",
        ):
            with self.subTest(path=relative_path):
                text = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn('"policy_version":"1.3.0"', text)
        self.assertIn('"policy_version":"1.3.0"', CONTINUITY_RECORDS_POLICY_MARKER)


    def test_package_version_bumped(self) -> None:
        from continuity import __version__

        self.assertEqual(__version__, "0.6.0")


if __name__ == "__main__":
    unittest.main()
