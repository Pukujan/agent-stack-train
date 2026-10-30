from __future__ import annotations

import subprocess
import unittest

from continuity.cli import ContinuityError, publish_then_receipt

PAYLOAD = "c" * 64


class CheckpointReceiptHookTests(unittest.TestCase):
    def runner(self, calls: list[tuple[list[str], str]], code: int = 0):
        def run(command: list[str], body: str) -> subprocess.CompletedProcess[str]:
            calls.append((command, body))
            return subprocess.CompletedProcess(command, code, stdout="", stderr="")

        return run

    def publish(self, calls: list[str], commit: str = "a" * 40):
        def _publish() -> str:
            calls.append("published")
            return commit

        return _publish

    def test_receipt_is_not_attempted_when_publish_fails(self) -> None:
        calls: list[tuple[list[str], str]] = []

        def fail() -> str:
            raise ContinuityError("push failed")

        with self.assertRaises(ContinuityError):
            publish_then_receipt(
                fail,
                [],
                repository="Pukujan/project-continuity-modules",
                task_id="PCM-0026",
                request_id="receipt-001",
                destination="67",
                kind="leaf",
                payload_sha256=PAYLOAD,
                lookup_complete=True,
                issue_number="67",
                run=self.runner(calls),
            )
        self.assertEqual(calls, [])

    def test_confirmed_publish_posts_once_when_marker_is_absent(self) -> None:
        calls: list[tuple[list[str], str]] = []
        published: list[str] = []
        commit = "b" * 40
        result = publish_then_receipt(
            self.publish(published, commit),
            ["unrelated"],
            repository="Pukujan/project-continuity-modules",
            task_id="PCM-0026",
            request_id="receipt-001",
            destination="67",
            kind="leaf",
            payload_sha256=PAYLOAD,
            lookup_complete=True,
            issue_number="67",
            run=self.runner(calls),
        )
        self.assertEqual(result, commit)
        self.assertEqual(published, ["published"])
        self.assertEqual(len(calls), 1)
        self.assertIn(commit, calls[0][1])
        self.assertLess(published.index("published"), 1)


if __name__ == "__main__":
    unittest.main()
