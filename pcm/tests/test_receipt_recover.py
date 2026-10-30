from __future__ import annotations

import unittest

from continuity.cli import ContinuityError, recover_receipt, render_receipt_marker

IDENTITY = {
    "repository": "Pukujan/project-continuity-modules",
    "task_id": "PCM-0026",
    "request_id": "receipt-001",
    "pushed_sha": "736667f" + "a" * 33,
    "destination": "67",
    "kind": "leaf",
    "payload_sha256": "c" * 64,
}


class ReceiptRecoverTests(unittest.TestCase):
    def marker(self, **overrides: str) -> str:
        values = dict(IDENTITY)
        values.update(overrides)
        return render_receipt_marker(**values)

    def test_complete_lookup_without_marker_may_post(self) -> None:
        decision = recover_receipt(["unrelated"], self.marker(), IDENTITY["payload_sha256"], lookup_complete=True)
        self.assertEqual(decision, "post")

    def test_timeout_does_not_authorize_a_second_post(self) -> None:
        with self.assertRaises(ContinuityError):
            recover_receipt([], self.marker(), IDENTITY["payload_sha256"], lookup_complete=False)

    def test_exact_remote_marker_is_recovered(self) -> None:
        body = f"before\n{self.marker()}\nafter"
        decision = recover_receipt([body], self.marker(), IDENTITY["payload_sha256"], lookup_complete=True)
        self.assertEqual(decision, "recovered")

    def test_historical_marker_is_not_a_recovery(self) -> None:
        historical = "<!-- pcm:receipt PCM-0025 merge:9328f36 -->"
        decision = recover_receipt([historical], self.marker(), IDENTITY["payload_sha256"], lookup_complete=True)
        self.assertEqual(decision, "post")

    def test_duplicate_exact_markers_stop(self) -> None:
        marker = self.marker()
        with self.assertRaises(ContinuityError):
            recover_receipt([marker, marker], marker, IDENTITY["payload_sha256"], lookup_complete=True)


if __name__ == "__main__":
    unittest.main()
