from __future__ import annotations

import unittest

from continuity.cli import ContinuityError, ReceiptComment, decide_receipt_retry

MARKER = "merge:9328f363a56d46290904b786eb43cff87e23c2b4"
PAYLOAD = "a" * 64
OTHER = "b" * 64


class ReceiptRetryDecisionTests(unittest.TestCase):
    def test_complete_lookup_with_no_match_may_post(self) -> None:
        decision = decide_receipt_retry([], MARKER, PAYLOAD, lookup_complete=True)
        self.assertEqual(decision, "post")

    def test_lost_response_does_not_authorize_a_post_when_lookup_is_incomplete(self) -> None:
        with self.assertRaises(ContinuityError):
            decide_receipt_retry([], MARKER, PAYLOAD, lookup_complete=False)

    def test_same_marker_and_payload_is_recovered_without_another_post(self) -> None:
        comments = [ReceiptComment(MARKER, PAYLOAD)]
        decision = decide_receipt_retry(comments, MARKER, PAYLOAD, lookup_complete=True)
        self.assertEqual(decision, "recovered")

    def test_same_marker_with_a_different_payload_fails(self) -> None:
        comments = [ReceiptComment(MARKER, OTHER)]
        with self.assertRaises(ContinuityError):
            decide_receipt_retry(comments, MARKER, PAYLOAD, lookup_complete=True)

    def test_duplicate_markers_are_ambiguous_and_do_not_post(self) -> None:
        comments = [ReceiptComment(MARKER, PAYLOAD), ReceiptComment(MARKER, PAYLOAD)]
        with self.assertRaises(ContinuityError):
            decide_receipt_retry(comments, MARKER, PAYLOAD, lookup_complete=True)

    def test_unrelated_comment_does_not_change_a_recovered_decision(self) -> None:
        base = [ReceiptComment(MARKER, PAYLOAD)]
        with_extra = [ReceiptComment("other-marker", OTHER), *base]
        self.assertEqual(
            decide_receipt_retry(base, MARKER, PAYLOAD, lookup_complete=True),
            decide_receipt_retry(with_extra, MARKER, PAYLOAD, lookup_complete=True),
        )


if __name__ == "__main__":
    unittest.main()
