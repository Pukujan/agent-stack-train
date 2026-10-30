from __future__ import annotations

import unittest

from continuity.cli import receipt_retry_command, render_receipt_body


class ReceiptRetryCommandTests(unittest.TestCase):
    def test_retry_command_reuses_the_request_id(self) -> None:
        command = receipt_retry_command("PCM-0026", "receipt-001", "Pukujan/project-continuity-modules", "67")
        self.assertIn("--request-id receipt-001", command)
        self.assertIn("--receipt-issue 67", command)
        self.assertNotIn("delivery complete", command)

    def test_body_includes_actor_parent_tests_and_next_action(self) -> None:
        body = render_receipt_body(
            "<!-- pcm:receipt-v2 -->",
            actor="Pukujan",
            parent="https://github.com/Pukujan/project-continuity-modules/issues/53",
            tests="python -m unittest tests.test_receipt_retry_command",
            next_action="Reconcile issue 67.",
        )
        self.assertIn("Actor: Pukujan", body)
        self.assertIn("issues/53", body)
        self.assertIn("Reconcile issue 67.", body)
        self.assertIn("hosted checks", body)


if __name__ == "__main__":
    unittest.main()
