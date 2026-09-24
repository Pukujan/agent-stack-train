from __future__ import annotations

import json
import unittest

from continuity.cli import ContinuityError, require_issue_owner


class ReceiptOwnerTests(unittest.TestCase):
    def test_unassigned_issue_does_not_block_the_actor(self) -> None:
        require_issue_owner(json.dumps({"assignees": []}), "Pukujan")

    def test_matching_assignee_is_accepted(self) -> None:
        payload = json.dumps({"assignees": [{"login": "Pukujan"}]})
        require_issue_owner(payload, "Pukujan")

    def test_other_assignee_is_rejected(self) -> None:
        payload = json.dumps({"assignees": [{"login": "other"}]})
        with self.assertRaises(ContinuityError):
            require_issue_owner(payload, "Pukujan")


if __name__ == "__main__":
    unittest.main()
