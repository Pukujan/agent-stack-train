from __future__ import annotations

import unittest

from continuity.cli import ContinuityError, build_parser, deliver_leaf_then_parent, require_parent_issue


class ParentReceiptTests(unittest.TestCase):
    def test_parent_is_not_called_when_leaf_fails(self) -> None:
        calls: list[str] = []

        def leaf() -> str:
            raise ContinuityError("leaf lookup failed")

        def parent() -> str:
            calls.append("parent")
            return "parent"

        with self.assertRaises(ContinuityError):
            deliver_leaf_then_parent(leaf, parent)
        self.assertEqual(calls, [])

    def test_parent_failure_keeps_the_leaf_and_does_not_claim_completion(self) -> None:
        def leaf() -> str:
            return "leaf-sha"

        def parent() -> str:
            raise ContinuityError("parent permission denied")

        with self.assertRaises(ContinuityError) as caught:
            deliver_leaf_then_parent(leaf, parent)
        message = str(caught.exception)
        self.assertIn("RECEIPT_PARENT_PARTIAL", message)
        self.assertIn("leaf receipt stands", message)
        self.assertIn("do not roll back", message)
        self.assertNotIn("delivery complete", message)

    def test_both_success_returns_the_leaf_result(self) -> None:
        calls: list[str] = []

        def leaf() -> str:
            calls.append("leaf")
            return "leaf-sha"

        def parent() -> str:
            calls.append("parent")
            return "parent-sha"

        self.assertEqual(deliver_leaf_then_parent(leaf, parent), "leaf-sha")
        self.assertEqual(calls, ["leaf", "parent"])

    def test_parent_flag_requires_the_leaf_receipt_flags(self) -> None:
        with self.assertRaises(ContinuityError):
            require_parent_issue(False, "53")
        self.assertEqual(require_parent_issue(True, "53"), "53")
        args = build_parser().parse_args(
            ["checkpoint", "PCM-0026", "--agent", "staff", "--next", "continue", "--receipt-parent", "53"]
        )
        self.assertEqual(args.receipt_parent, "53")


if __name__ == "__main__":
    unittest.main()
