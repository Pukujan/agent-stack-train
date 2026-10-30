from __future__ import annotations

import json
import subprocess
import unittest

from continuity.cli import ContinuityError, comment_bodies, maybe_post_from_page, render_receipt_marker

MARKER = render_receipt_marker(
    repository="Pukujan/project-continuity-modules",
    task_id="PCM-0026",
    request_id="receipt-001",
    pushed_sha="a" * 40,
    destination="67",
    kind="leaf",
    payload_sha256="c" * 64,
)


class ReceiptLookupTests(unittest.TestCase):
    def test_parses_comment_bodies(self) -> None:
        payload = json.dumps([{"body": "one"}, {"body": "two"}])
        self.assertEqual(comment_bodies(payload), ["one", "two"])

    def test_full_page_does_not_post(self) -> None:
        calls: list[str] = []
        payload = json.dumps([{"body": "x"} for _ in range(2)])

        def run(command: list[str], body: str) -> subprocess.CompletedProcess[str]:
            calls.append(body)
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with self.assertRaises(ContinuityError):
            maybe_post_from_page(
                payload,
                2,
                marker=MARKER,
                payload_sha256="c" * 64,
                repository="Pukujan/project-continuity-modules",
                issue_number="67",
                run=run,
            )
        self.assertEqual(calls, [])

    def test_short_page_without_marker_posts_once(self) -> None:
        calls: list[str] = []
        payload = json.dumps([{"body": "unrelated"}])

        def run(command: list[str], body: str) -> subprocess.CompletedProcess[str]:
            calls.append(body)
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        decision = maybe_post_from_page(
            payload,
            100,
            marker=MARKER,
            payload_sha256="c" * 64,
            repository="Pukujan/project-continuity-modules",
            issue_number="67",
            run=run,
        )
        self.assertEqual(decision, "post")
        # PCM-0055: the post payload must be gh JSON request parameters, not raw text.
        self.assertEqual([json.loads(call)["body"] for call in calls], [MARKER])


if __name__ == "__main__":
    unittest.main()
