from __future__ import annotations

import json
import unittest

from continuity.cli import ContinuityError, require_issue_identity


class ReceiptIssueIdentityTests(unittest.TestCase):
    def test_matching_issue_is_accepted(self) -> None:
        payload = json.dumps({"number": 67, "title": "PCM-0026 receipts", "body": ""})
        require_issue_identity(payload, issue_number="67", task_id="PCM-0026")

    def test_wrong_number_is_rejected(self) -> None:
        payload = json.dumps({"number": 15, "title": "PCM-0026 receipts", "body": ""})
        with self.assertRaises(ContinuityError):
            require_issue_identity(payload, issue_number="67", task_id="PCM-0026")

    def test_missing_task_name_is_rejected(self) -> None:
        payload = json.dumps({"number": 67, "title": "unrelated", "body": "no task here"})
        with self.assertRaises(ContinuityError):
            require_issue_identity(payload, issue_number="67", task_id="PCM-0026")


if __name__ == "__main__":
    unittest.main()
