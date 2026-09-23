from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from continuity.cli import ContinuityError, checkpoint_task, git_run, publish_checkpoint

FIXTURE = Path(__file__).parent / "fixtures" / "valid-minimal"


class CheckpointRetryTests(unittest.TestCase):
    def make_repo(self) -> tuple[Path, Path]:
        root = Path(tempfile.mkdtemp(prefix="continuity-checkpoint-retry-"))
        self.addCleanup(shutil.rmtree, root, True)
        shutil.copytree(FIXTURE, root, dirs_exist_ok=True)
        remote = Path(tempfile.mkdtemp(prefix="continuity-checkpoint-remote-"))
        self.addCleanup(shutil.rmtree, remote, True)
        subprocess.run(["git", "init", "-q", "--bare", remote], check=True)
        subprocess.run(["git", "init", "-q", "-b", "task/PCM-0001-retry"], cwd=root, check=True)
        subprocess.run(["git", "-C", root, "config", "user.email", "fixture@example.invalid"], check=True)
        subprocess.run(["git", "-C", root, "config", "user.name", "Fixture"], check=True)
        subprocess.run(["git", "-C", root, "add", "."], check=True)
        subprocess.run(["git", "-C", root, "commit", "-qm", "fixture"], check=True)
        subprocess.run(["git", "-C", root, "remote", "add", "origin", str(remote)], check=True)
        subprocess.run(["git", "-C", root, "push", "-q", "--set-upstream", "origin", "HEAD"], check=True)
        return root, remote

    def add_checkpoint(
        self,
        root: Path,
        request_id: str = "closeout-001",
        completed: str = "verified work",
        timestamp: str = "2026-09-23T12:00:00Z",
    ) -> Path:
        return checkpoint_task(
            root,
            "PCM-0001",
            "test-agent",
            timestamp,
            [completed],
            ["deterministic test passed"],
            ["retries preserve one event"],
            ["tests/test_checkpoint_retries.py"],
            [],
            "run the full suite",
            request_id=request_id,
        )

    def test_same_request_and_payload_are_a_byte_identical_noop(self) -> None:
        root, _ = self.make_repo()
        task = self.add_checkpoint(root)
        before = task.read_bytes()

        repeated = self.add_checkpoint(root, timestamp="2026-09-24T15:00:00Z")

        self.assertEqual(repeated, task)
        self.assertEqual(task.read_bytes(), before)

    def test_reusing_request_id_with_different_payload_fails_before_write(self) -> None:
        root, _ = self.make_repo()
        task = self.add_checkpoint(root)
        before = task.read_bytes()

        with self.assertRaisesRegex(ContinuityError, "request ID.*different checkpoint payload"):
            self.add_checkpoint(root, completed="different work")

        self.assertEqual(task.read_bytes(), before)

    def test_lost_push_response_retries_without_duplicate_commit_or_event(self) -> None:
        root, remote = self.make_repo()
        task = self.add_checkpoint(root, request_id="lost-response")
        original_git_run = git_run
        simulated_loss = False

        def accept_then_lose_ack(repo: Path, args: list[str]):
            nonlocal simulated_loss
            result = original_git_run(repo, args)
            if args and args[0] == "push" and not simulated_loss:
                simulated_loss = True
                raise ContinuityError("simulated lost push response")
            return result

        with (
            patch("continuity.cli.git_run", side_effect=accept_then_lose_ack),
            self.assertRaisesRegex(ContinuityError, "lost push response"),
        ):
                publish_checkpoint(root, task, "PCM-0001", "run the full suite", request_id="lost-response")

        committed = subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip()
        remote_before_retry = subprocess.check_output(
            ["git", "--git-dir", str(remote), "rev-parse", "refs/heads/task/PCM-0001-retry"], text=True
        ).strip()
        self.assertEqual(remote_before_retry, committed)

        self.add_checkpoint(root, request_id="lost-response")
        second_commit = publish_checkpoint(
            root, task, "PCM-0001", "run the full suite", request_id="lost-response"
        )

        self.assertEqual(second_commit, committed)
        self.assertEqual(
            subprocess.check_output(["git", "-C", root, "rev-list", "--count", "HEAD"], text=True).strip(), "2"
        )
        self.assertEqual(task.read_text(encoding="utf-8").count('"request_id":"lost-response"'), 1)

    def test_local_checkpoint_commit_can_be_pushed_after_first_push_fails(self) -> None:
        root, remote = self.make_repo()
        task = self.add_checkpoint(root, request_id="retry-commit")
        original_git_run = git_run
        push_attempts = 0

        def fail_first_push(repo: Path, args: list[str]):
            nonlocal push_attempts
            if args and args[0] == "push" and push_attempts == 0:
                push_attempts += 1
                raise ContinuityError("simulated offline remote")
            return original_git_run(repo, args)

        with (
            patch("continuity.cli.git_run", side_effect=fail_first_push),
            self.assertRaisesRegex(ContinuityError, "offline remote"),
        ):
                publish_checkpoint(root, task, "PCM-0001", "run the full suite", request_id="retry-commit")

        local_commit = subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip()
        pushed_commit = publish_checkpoint(root, task, "PCM-0001", "run the full suite", request_id="retry-commit")

        self.assertEqual(pushed_commit, local_commit)
        self.assertEqual(
            subprocess.check_output(
                ["git", "--git-dir", str(remote), "rev-parse", "refs/heads/task/PCM-0001-retry"], text=True
            ).strip(),
            local_commit,
        )

    def test_cli_replay_with_printed_request_id_creates_one_remote_checkpoint(self) -> None:
        from contextlib import redirect_stdout
        from io import StringIO

        from continuity.cli import main

        root, remote = self.make_repo()
        args = [
            "checkpoint",
            "PCM-0001",
            "--root",
            str(root),
            "--agent",
            "test-agent",
            "--request-id",
            "cli-replay",
            "--completed",
            "verified work",
            "--evidence",
            "deterministic test passed",
            "--decision",
            "retries preserve one event",
            "--changed",
            "tests/test_checkpoint_retries.py",
            "--next",
            "run the full suite",
        ]
        first_output = StringIO()
        with redirect_stdout(first_output):
            self.assertEqual(main(args), 0)
        second_output = StringIO()
        with redirect_stdout(second_output):
            self.assertEqual(main(args), 0)

        self.assertIn("REQUEST_ID: cli-replay", first_output.getvalue())
        self.assertIn("REQUEST_ID: cli-replay", second_output.getvalue())
        self.assertEqual(
            subprocess.check_output(["git", "-C", root, "rev-list", "--count", "HEAD"], text=True).strip(), "2"
        )
        self.assertEqual(
            subprocess.check_output(
                ["git", "--git-dir", str(remote), "rev-parse", "refs/heads/task/PCM-0001-retry"], text=True
            ).strip(),
            subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip(),
        )


if __name__ == "__main__":
    unittest.main()
