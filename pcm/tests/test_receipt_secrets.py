from __future__ import annotations

import subprocess
import unittest

from continuity.cli import ContinuityError, publish_issue_receipt, reject_receipt_secrets


class ReceiptSecretTests(unittest.TestCase):
    def test_rejects_a_token_and_a_private_path(self) -> None:
        with self.assertRaises(ContinuityError):
            reject_receipt_secrets("token ghp_example")
        with self.assertRaises(ContinuityError):
            reject_receipt_secrets(r"see D:\claude\inferhub\.env")

    def test_secret_body_does_not_call_the_runner(self) -> None:
        calls: list[str] = []

        def run(command: list[str], body: str) -> subprocess.CompletedProcess[str]:
            calls.append(body)
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with self.assertRaises(ContinuityError):
            publish_issue_receipt(
                [],
                "marker",
                "c" * 64,
                lookup_complete=True,
                repository="Pukujan/project-continuity-modules",
                issue_number="67",
                body="marker ghp_example",
                run=run,
            )
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
