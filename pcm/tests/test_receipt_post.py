from __future__ import annotations

import unittest

from continuity.cli import (
    ContinuityError,
    github_issue_comment_path,
    post_receipt_if_absent,
    render_receipt_marker,
)

IDENTITY = {
    "repository": "Pukujan/project-continuity-modules",
    "task_id": "PCM-0026",
    "request_id": "receipt-001",
    "pushed_sha": "8caf98a" + "a" * 33,
    "destination": "67",
    "kind": "leaf",
    "payload_sha256": "c" * 64,
}


class ReceiptPostTests(unittest.TestCase):
    def marker(self) -> str:
        return render_receipt_marker(**IDENTITY)

    def test_posts_once_when_lookup_proves_absence(self) -> None:
        calls = []
        decision = post_receipt_if_absent(
            ["unrelated"],
            self.marker(),
            IDENTITY["payload_sha256"],
            lookup_complete=True,
            post=lambda: calls.append("posted"),
        )
        self.assertEqual(decision, "post")
        self.assertEqual(calls, ["posted"])

    def test_does_not_post_when_marker_is_already_present(self) -> None:
        calls = []
        decision = post_receipt_if_absent(
            [self.marker()],
            self.marker(),
            IDENTITY["payload_sha256"],
            lookup_complete=True,
            post=lambda: calls.append("posted"),
        )
        self.assertEqual(decision, "recovered")
        self.assertEqual(calls, [])

    def test_does_not_post_when_lookup_is_incomplete(self) -> None:
        calls = []
        with self.assertRaises(ContinuityError):
            post_receipt_if_absent(
                [],
                self.marker(),
                IDENTITY["payload_sha256"],
                lookup_complete=False,
                post=lambda: calls.append("posted"),
            )
        self.assertEqual(calls, [])

    def test_comment_path_rejects_a_bad_repository(self) -> None:
        self.assertEqual(
            github_issue_comment_path("Pukujan/project-continuity-modules", "67"),
            "repos/Pukujan/project-continuity-modules/issues/67/comments",
        )
        with self.assertRaises(ContinuityError):
            github_issue_comment_path("not-a-repo", "67")
        with self.assertRaises(ContinuityError):
            github_issue_comment_path("Pukujan/project-continuity-modules", "leaf")


if __name__ == "__main__":
    unittest.main()
