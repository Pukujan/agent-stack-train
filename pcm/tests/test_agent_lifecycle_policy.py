from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class AgentLifecyclePolicyTests(unittest.TestCase):
    def test_canonical_policy_requires_capture_then_close(self) -> None:
        policy = (ROOT / "docs" / "AGENT_LIFECYCLE.md").read_text(encoding="utf-8")
        self.assertIn("capture the worker's result", policy)
        self.assertIn("close the worker immediately", policy)
        self.assertIn("A completed", policy)
        self.assertIn("Failure, interruption, cancellation, and timeout", policy)

    def test_operating_guidance_references_worker_cleanup(self) -> None:
        guidance = [
            ROOT / "AGENTS.md",
            ROOT / "SPEC.md",
            ROOT / "docs" / "HANDOFF_PROTOCOL.md",
            ROOT / "templates" / "v1" / "minimal" / "HANDOFF.md",
            ROOT / "templates" / "v1" / "software" / "AGENTS.md",
        ]
        for path in guidance:
            text = path.read_text(encoding="utf-8")
            self.assertIn("close", text.lower(), path.as_posix())
            self.assertIn("worker", text.lower(), path.as_posix())


if __name__ == "__main__":
    unittest.main()
