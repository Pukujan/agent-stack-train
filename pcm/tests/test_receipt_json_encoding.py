"""PCM-0055: the checkpoint receipt POST must send a JSON request body.

`gh api --input -` parses its stdin as JSON request parameters, not a plain
text body. The shipped opt-in receipt path piped the raw markdown receipt
straight in, so every real post returned HTTP 400 "Problems parsing JSON"
(first production use, push 2f8dc7a on #166; the identical text succeeded only
once wrapped as {"body": ...}). These tests pin the wire format so the fake
runner that passes on any substring cannot hide the defect again.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

from continuity.cli import publish_issue_receipt, render_receipt_marker

IDENTITY = {
    "repository": "Pukujan/project-continuity-modules",
    "task_id": "PCM-0055",
    "request_id": "receipt-json-001",
    "pushed_sha": "2f8dc7a" + "b" * 33,
    "destination": "166",
    "kind": "leaf",
    "payload_sha256": "d" * 64,
}


class ReceiptJsonWireFormatTests(unittest.TestCase):
    def marker(self) -> str:
        return render_receipt_marker(**IDENTITY)

    def body_with_marker(self) -> str:
        # render_receipt_body is not exercised here; the marker plus a
        # multi-line markdown tail is the shape that must survive the trip.
        return self.marker() + "\nActor: tester\nCommit: https://example.invalid/x\n"

    def test_post_payload_is_json_with_body_containing_marker(self) -> None:
        calls: list[tuple[list[str], str]] = []

        def run(command: list[str], payload: str) -> subprocess.CompletedProcess[str]:
            calls.append((command, payload))
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        publish_issue_receipt(
            [],
            self.marker(),
            IDENTITY["payload_sha256"],
            lookup_complete=True,
            repository=IDENTITY["repository"],
            issue_number=IDENTITY["destination"],
            body=self.body_with_marker(),
            run=run,
        )
        self.assertEqual(len(calls), 1)
        payload = calls[0][1]
        decoded = json.loads(payload)  # raises before the fix: raw markdown is not JSON
        self.assertIsInstance(decoded, dict)
        self.assertIn(self.marker(), decoded["body"])

    def test_real_gh_receives_json_on_stdin(self) -> None:
        # Prove the contract against a real subprocess reading `--input -`,
        # with no network: a stub `gh` records its raw stdin to a file.
        bin_dir = Path(tempfile.mkdtemp(prefix="continuity-ghstub-bin-"))
        self.addCleanup(shutil.rmtree, bin_dir, True)
        capture = Path(tempfile.mkdtemp(prefix="continuity-ghstub-cap-")) / "stdin.json"
        self.addCleanup(shutil.rmtree, capture.parent, True)
        env_path = str(capture)
        shim = bin_dir / "gh"
        shim.write_text(
            "#!/bin/sh\ntee \"$PCM_GH_CAPTURE\" >/dev/null\nexit 0\n",
            encoding="utf-8",
        )
        shim.chmod(shim.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

        def run(command: list[str], payload: str) -> subprocess.CompletedProcess[str]:
            env = dict(os.environ)
            env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
            env["PCM_GH_CAPTURE"] = env_path
            return subprocess.run(
                command,
                input=payload,
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )

        publish_issue_receipt(
            [],
            self.marker(),
            IDENTITY["payload_sha256"],
            lookup_complete=True,
            repository=IDENTITY["repository"],
            issue_number=IDENTITY["destination"],
            body=self.body_with_marker(),
            run=run,
        )
        recorded = capture.read_text(encoding="utf-8")
        decoded = json.loads(recorded)  # raises before the fix: stub saw raw markdown
        self.assertIn(self.marker(), decoded["body"])


if __name__ == "__main__":
    unittest.main()
