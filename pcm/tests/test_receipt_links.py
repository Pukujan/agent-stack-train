from __future__ import annotations

import unittest

from continuity.cli import ContinuityError, receipt_commit_url, receipt_pr_line


class ReceiptLinkTests(unittest.TestCase):
    def test_commit_url_uses_the_pushed_sha(self) -> None:
        self.assertEqual(
            receipt_commit_url("Pukujan/project-continuity-modules", "abc123"),
            "https://github.com/Pukujan/project-continuity-modules/commit/abc123",
        )

    def test_missing_pull_request_is_not_invented(self) -> None:
        self.assertEqual(receipt_pr_line(None), "not supplied")

    def test_non_github_pull_request_is_rejected(self) -> None:
        with self.assertRaises(ContinuityError):
            receipt_pr_line("https://example.test/pull/1")


if __name__ == "__main__":
    unittest.main()
