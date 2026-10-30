from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from continuity.cli import agents_template, handoff_template, init_repo

ROOT = Path(__file__).parents[1]

CGM_26 = "content-generation-modules/issues/26"

BAD_STEM_EXAMPLES = (
    "m5_kg_",
    "song_food-p0-00e86d.mp3",
)

# Documented rejection patterns (regexes agents must treat as forbidden for new stems)
FORBIDDEN_BASENAME_PATTERNS = (
    re.compile(r"m5_kg_", re.IGNORECASE),
    re.compile(r"-[0-9a-f]{6}\.(mp3|wav|png|jpg)$", re.IGNORECASE),
)

GOOD_EXAMPLES = (
    "claim_activity_edges.md",
    "task-handoff-notes.md",
)


class ContinuityPathNamingPolicyTests(unittest.TestCase):
    def test_naming_doc_rejects_bad_and_shows_good_examples(self) -> None:
        doc = (ROOT / "docs" / "CONTINUITY_PATH_NAMING.md").read_text(encoding="utf-8")
        lower = doc.lower()
        self.assertIn("pronounceable", lower)
        self.assertIn("forward-only", lower)
        for bad in BAD_STEM_EXAMPLES:
            self.assertIn(bad, doc)
        for good in GOOD_EXAMPLES:
            self.assertIn(good, doc)
        self.assertIn(CGM_26, doc)
        self.assertIn("pcm owns", lower)
        self.assertIn("belong to content generation modules (cgm)", lower)
        self.assertRegex(doc, r"(?i)\|\s*\*\*cgm\*\*\s*\|")
        # Forbidden patterns must match the documented bad examples
        for pattern in FORBIDDEN_BASENAME_PATTERNS:
            matched = [ex for ex in BAD_STEM_EXAMPLES if pattern.search(ex)]
            self.assertTrue(matched, f"{pattern.pattern} should match a documented bad example")

    def test_forbidden_patterns_do_not_match_good_examples(self) -> None:
        for good in GOOD_EXAMPLES:
            for pattern in FORBIDDEN_BASENAME_PATTERNS:
                with self.subTest(good=good, pattern=pattern.pattern):
                    self.assertIsNone(pattern.search(good))

    def test_target_adoption_links_doc_and_checklist(self) -> None:
        text = (ROOT / "docs" / "TARGET_ADOPTION.md").read_text(encoding="utf-8")
        lower = text.lower()
        self.assertIn("CONTINUITY_PATH_NAMING.md", text)
        self.assertIn(CGM_26, text)
        self.assertIn("acs-hotload-path-checklist.md", text)
        self.assertIn("pronounceable", lower)
        self.assertIn("adoption checklist", lower)
        # Checklist items
        self.assertIn("new continuity-managed source paths follow the pronounceable rule", lower)
        self.assertIn("pin and apply", lower)
        self.assertIn("cgm filename helper", lower)
        self.assertIn("filenames row", lower)

    def test_acs_hotload_checklist_covers_titles_filenames_and_source_paths(self) -> None:
        text = (ROOT / "docs" / "acs-hotload-path-checklist.md").read_text(encoding="utf-8").lower()
        self.assertIn("titles", text)
        self.assertIn("artifact filenames", text)
        self.assertIn("source paths", text)
        self.assertIn(CGM_26, text)
        self.assertIn("continuity_path_naming.md", text)

    def test_docs_cross_link_cgm_26(self) -> None:
        for relative in (
            "docs/CONTINUITY_PATH_NAMING.md",
            "docs/TARGET_ADOPTION.md",
            "docs/acs-hotload-path-checklist.md",
            "README.md",
            "AGENTS.md",
            "templates/v1/software/AGENTS.md",
            "templates/v1/minimal/HANDOFF.md",
        ):
            with self.subTest(path=relative):
                self.assertIn(CGM_26, (ROOT / relative).read_text(encoding="utf-8"))

    def test_templates_carry_short_pointer(self) -> None:
        for relative in (
            "templates/v1/software/AGENTS.md",
            "templates/v1/minimal/HANDOFF.md",
            "templates/v1/software/README.md",
            "AGENTS.md",
        ):
            with self.subTest(path=relative):
                text = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("CONTINUITY_PATH_NAMING.md", text)
                self.assertIn("pronounceable", text.lower())

    def test_init_generators_and_installed_profiles_carry_pointer(self) -> None:
        self.assertIn("CONTINUITY_PATH_NAMING.md", agents_template("managed-worktrees"))
        self.assertIn("CONTINUITY_PATH_NAMING.md", handoff_template("single-checkout"))
        self.assertIn(CGM_26, agents_template("managed-worktrees"))
        for profile in ("minimal", "software"):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                init_repo(
                    root,
                    profile,
                    "Adopter",
                    "APP",
                    github_templates=True,
                    github_authority=True,
                )
                handoff = (root / "HANDOFF.md").read_text(encoding="utf-8")
                self.assertIn("CONTINUITY_PATH_NAMING.md", handoff)
                self.assertIn(CGM_26, handoff)
                if profile == "software":
                    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
                    self.assertIn("CONTINUITY_PATH_NAMING.md", agents)
                    readme = (root / "README.md").read_text(encoding="utf-8")
                    self.assertIn("CONTINUITY_PATH_NAMING.md", readme)


if __name__ == "__main__":
    unittest.main()
