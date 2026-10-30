"""PCM-0054 acceptance 3 (owner decision #169 5842002712): `continuity receipt
audit` proves whether every pushed checkpoint commit has a keyed leaf-issue
receipt. Gaps exit non-zero; unprovable lookups degrade to a NOTE (exit 0) and
never fabricate gaps; receipts stay opt-in — this only observes.
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
from unittest.mock import patch

from continuity.cli import (
    audit_receipt_gaps,
    checkpoint_task,
    main,
    receipt_coverage,
)

FIXTURE = Path(__file__).parent / "fixtures" / "valid-minimal"
SHA_A = "a" * 40
SHA_B = "b" * 40


def v2_body(sha: str, request: str) -> str:
    return (
        f"<!-- pcm:receipt-v2 repository=x/y task=PCM-0001 request={request} "
        f"sha={sha} destination=9 kind=leaf payload={'c' * 64} -->\nActor: t"
    )


class ReceiptCoverageTests(unittest.TestCase):
    def test_v2_marker_contributes_sha_and_request(self) -> None:
        shas, requests = receipt_coverage([v2_body(SHA_A, "req-1")])
        self.assertIn(SHA_A, shas)
        self.assertIn("req-1", requests)

    def test_manual_receipt_comment_sha_tokens_recognized(self) -> None:
        body = (
            "<!-- pcm:receipt pcm-0053-current-final-20260925-690b7f8 -->\n"
            "**Merge receipt.** squash SHA `d5021a35e0171fc02e70030acf99eb75efdf32e5` here.\n"
        )
        shas, requests = receipt_coverage([body])
        self.assertIn("d5021a35e0171fc02e70030acf99eb75efdf32e5", shas)
        self.assertEqual(requests, set())

    def test_non_receipt_comments_are_ignored(self) -> None:
        shas, requests = receipt_coverage([f"just prose {SHA_A}"])
        self.assertEqual(shas, set())
        self.assertEqual(requests, set())


class AuditGapTests(unittest.TestCase):
    def test_unreceipted_checkpoint_push_is_a_gap(self) -> None:
        status, gaps = audit_receipt_gaps(
            [(SHA_A, "req-1")], receipt_coverage([]), lookup_complete=True
        )
        self.assertEqual(status, "gaps")
        self.assertEqual(gaps, [(SHA_A, "req-1")])

    def test_v2_or_manual_coverage_clears_gaps(self) -> None:
        commits = [(SHA_A, "req-1"), (SHA_B, "req-2")]
        bodies = [v2_body(SHA_A, "req-1"), f"<!-- pcm:receipt k -->\nsquash `{SHA_B}`"]
        status, gaps = audit_receipt_gaps(commits, receipt_coverage(bodies), lookup_complete=True)
        self.assertEqual(status, "ok")
        self.assertEqual(gaps, [])

    def test_short_sha_prefix_in_manual_comment_covers(self) -> None:
        bodies = [f"<!-- pcm:receipt k -->\nsquash `{SHA_B[:7]}`"]
        status, _ = audit_receipt_gaps([(SHA_B, "r")], receipt_coverage(bodies), lookup_complete=True)
        self.assertEqual(status, "ok")

    def test_incomplete_lookup_degrades_without_fabricating_gaps(self) -> None:
        status, gaps = audit_receipt_gaps(
            [(SHA_A, "req-1")], receipt_coverage([]), lookup_complete=False
        )
        self.assertEqual(status, "degraded")
        self.assertEqual(gaps, [])


class ReceiptAuditCliTests(unittest.TestCase):
    def make_repo(self) -> Path:
        root = Path(tempfile.mkdtemp(prefix="continuity-ra-"))
        self.addCleanup(shutil.rmtree, root, True)
        shutil.copytree(FIXTURE, root, dirs_exist_ok=True)
        remote = Path(tempfile.mkdtemp(prefix="continuity-ra-remote-"))
        self.addCleanup(shutil.rmtree, remote, True)
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", remote], check=True)
        subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
        subprocess.run(["git", "-C", root, "config", "user.email", "fixture@example.invalid"], check=True)
        subprocess.run(["git", "-C", root, "config", "user.name", "Fixture"], check=True)
        subprocess.run(["git", "-C", root, "add", "."], check=True)
        subprocess.run(["git", "-C", root, "commit", "-qm", "fixture"], check=True)
        subprocess.run(["git", "-C", root, "remote", "add", "origin", str(remote)], check=True)
        subprocess.run(["git", "-C", root, "push", "-q", "-u", "origin", "main"], check=True)
        subprocess.run(["git", "-C", root, "checkout", "-q", "-b", "task/PCM-0001-audit"], check=True)
        path = checkpoint_task(
            root, "PCM-0001", "agent", "2026-09-26T02:00:00Z",
            ["audit work"], ["tests"], ["audit"], ["SPEC.md"], [], "next",
            request_id="req-cli-1",
        )
        subprocess.run(["git", "-C", root, "add", "--", str(path.relative_to(root))], check=True)
        subprocess.run(["git", "-C", root, "commit", "-qm", "PCM checkpoint PCM-0001: next"], check=True)
        subprocess.run(["git", "-C", root, "push", "-q", "-u", "origin", "task/PCM-0001-audit"], check=True)
        return root

    def stub_gh(self, bodies: list[str], calls: list[str]) -> Path:
        bin_dir = Path(tempfile.mkdtemp(prefix="continuity-ra-bin-"))
        self.addCleanup(shutil.rmtree, bin_dir, True)
        payload = bin_dir / "comments.json"
        payload.write_text(
            json.dumps([{"body": body} for body in bodies]), encoding="utf-8"
        )
        shim = bin_dir / "gh"
        shim.write_text(
            "#!/bin/sh\n"
            'echo "$@" >> "$PCM_GH_CALLS"\n'
            'cat "$PCM_GH_PAYLOAD"\n'
            "exit 0\n",
            encoding="utf-8",
        )
        shim.chmod(shim.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        log = bin_dir / "calls.log"
        log.touch()
        env = dict(os.environ)
        env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
        env["PCM_GH_PAYLOAD"] = str(payload)
        env["PCM_GH_CALLS"] = str(log)
        self._calls_file = log
        self._patch = patch.dict(os.environ, env)
        self._patch.start()
        self.addCleanup(self._patch.stop)
        return bin_dir

    def run_audit(self, root: Path) -> int:
        return main(
            [
                "receipt", "audit", "PCM-0001",
                "--root", str(root),
                "--repository", "fixture/repo",
                "--issue", "9",
            ]
        )

    def test_cli_exits_one_with_gap_list_when_receipt_absent(self) -> None:
        root = self.make_repo()
        self.stub_gh(["unrelated comment"], [])
        code = self.run_audit(root)
        self.assertEqual(code, 1)

    def test_cli_exits_zero_when_v2_receipt_covers(self) -> None:
        root = self.make_repo()
        head = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip()
        self.stub_gh([v2_body(head, "req-cli-1")], [])
        code = self.run_audit(root)
        self.assertEqual(code, 0)

    def test_cli_degrades_to_note_when_gh_unavailable(self) -> None:
        root = self.make_repo()
        empty_bin = Path(tempfile.mkdtemp(prefix="continuity-ra-nobin-"))
        self.addCleanup(shutil.rmtree, empty_bin, True)
        git_path = shutil.which("git")
        assert git_path is not None
        env = dict(os.environ)
        env["PATH"] = f"{empty_bin}{os.pathsep}{Path(git_path).parent}"
        with patch.dict(os.environ, env):
            code = self.run_audit(root)
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
