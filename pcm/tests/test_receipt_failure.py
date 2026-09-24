from __future__ import annotations

import unittest

from continuity.cli import classify_receipt_failure, receipt_failure_message


class ReceiptFailureTests(unittest.TestCase):
    def test_permission_and_wrong_target_are_distinct(self) -> None:
        self.assertEqual(classify_receipt_failure("HTTP 403 Forbidden"), "permission")
        self.assertEqual(classify_receipt_failure("HTTP 404 Not Found"), "wrong-target")
        self.assertEqual(classify_receipt_failure("connection reset"), "unavailable")

    def test_message_keeps_the_push_and_forbids_rollback(self) -> None:
        message = receipt_failure_message("a" * 40, "HTTP 401 authentication required")
        self.assertIn("RECEIPT_PERMISSION", message)
        self.assertIn("stands", message)
        self.assertIn("do not roll back", message)
        self.assertNotIn("delivery complete", message)


if __name__ == "__main__":
    unittest.main()
