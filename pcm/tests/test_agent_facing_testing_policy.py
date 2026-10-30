from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class AgentFacingTestingPolicyTests(unittest.TestCase):
    def test_canonical_policy_covers_risk_based_selection_and_oracle_fairness(self) -> None:
        policy = (ROOT / "docs" / "TESTING_POLICY.md").read_text(encoding="utf-8").lower()
        for required in (
            "deterministic regression test",
            "fresh-session holdout",
            "metamorphic",
            "differential",
            "visible contract",
            "inconclusive",
            "llm opinion alone",
            "human-visible outcome",
            "elapsed time",
        ):
            with self.subTest(required=required):
                self.assertIn(required, policy)

    def test_agent_instructions_carry_the_short_policy(self) -> None:
        guidance = (
            ROOT / "AGENTS.md",
            ROOT / "templates" / "v1" / "software" / "AGENTS.md",
            ROOT / "templates" / "v1" / "minimal" / "HANDOFF.md",
        )
        for path in guidance:
            text = path.read_text(encoding="utf-8").lower()
            self.assertIn("human-visible", text, path.as_posix())
            self.assertIn("deterministic", text, path.as_posix())
            self.assertIn("holdout", text, path.as_posix())

    def test_policy_requires_visible_requirements_and_not_only_test_success(self) -> None:
        policy = (ROOT / "docs" / "TESTING_POLICY.md").read_text(encoding="utf-8").lower()
        self.assertIn("hide the diagnosis, not the requirement", policy)
        self.assertIn("tests support that outcome; they do not replace it", policy)
        self.assertIn("a holdout pass cannot excuse", policy)


if __name__ == "__main__":
    unittest.main()
