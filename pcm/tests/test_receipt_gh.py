from __future__ import annotations

import subprocess
import unittest

from continuity.cli import ContinuityError, publish_issue_receipt, render_receipt_marker

IDENTITY = {
    "repository": "Pukujan/project-continuity-modules",
    "task_id": "PCM-0026",
    "request_id": "receipt-001",
    "pushed_sha": "be3e3f1" + "a" * 33,
    "destination": "67",
    "kind": "leaf",
    "payload_sha256": "c" * 64,
}


class ReceiptGhTests(unittest.TestCase):
    def marker(self) -> str:
        return render_receipt_marker(**IDENTITY)

    def runner(self, calls: list[tuple[list[str], str]], code: int = 0):
        def run(command: list[str], body: str) -> subprocess.CompletedProcess[str]:
            calls.append((command, body))
            return subprocess.CompletedProcess(command, code, stdout="", stderr="denied")

        return run

    def test_posts_once_through_the_runner_when_absent(self) -> None:
        calls: list[tuple[list[str], str]] = []
        marker = self.marker()
        decision = publish_issue_receipt(
            ["unrelated"],
            marker,
            IDENTITY["payload_sha256"],
            lookup_complete=True,
            repository=IDENTITY["repository"],
            issue_number="67",
            body=marker,
            run=self.runner(calls),
        )
        self.assertEqual(decision, "post")
        self.assertEqual(len(calls), 1)
        self.assertEqual(
            calls[0][0],
            [
                "gh",
                "api",
                "--method",
                "POST",
                "repos/Pukujan/project-continuity-modules/issues/67/comments",
                "--input",
                "-",
            ],
        )
        self.assertIn(marker, calls[0][1])

    def test_does_not_call_the_runner_when_recovered(self) -> None:
        calls: list[tuple[list[str], str]] = []
        marker = self.marker()
        decision = publish_issue_receipt(
            [marker],
            marker,
            IDENTITY["payload_sha256"],
            lookup_complete=True,
            repository=IDENTITY["repository"],
            issue_number="67",
            body=marker,
            run=self.runner(calls),
        )
        self.assertEqual(decision, "recovered")
        self.assertEqual(calls, [])

    def test_runner_failure_is_not_retried_inside_the_call(self) -> None:
        calls: list[tuple[list[str], str]] = []
        with self.assertRaises(ContinuityError):
            publish_issue_receipt(
                [],
                self.marker(),
                IDENTITY["payload_sha256"],
                lookup_complete=True,
                repository=IDENTITY["repository"],
                issue_number="67",
                body=self.marker(),
                run=self.runner(calls, code=1),
            )
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
