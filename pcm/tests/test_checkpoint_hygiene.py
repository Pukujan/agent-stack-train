from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from continuity.cli import ContinuityError, checkpoint_task, main

FIXTURE = Path(__file__).parent / "fixtures" / "valid-minimal"

EFFECTIVE_CLOSING = re.compile(
    r"(?i)\b(?:close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)\s*"
    r"(?::\s*)?(?:#\d+|https?://[^ ]*issues/\d+|(?:[\w.-]+/[\w.-]+)?#\d+)"
)


class HygieneCase(unittest.TestCase):
    def make_repo(self, branch: str = "task/PCM-0047-hygiene") -> tuple[Path, Path]:
        root = Path(tempfile.mkdtemp(prefix="continuity-checkpoint-hygiene-"))
        self.addCleanup(shutil.rmtree, root, True)
        shutil.copytree(FIXTURE, root, dirs_exist_ok=True)
        remote = Path(tempfile.mkdtemp(prefix="continuity-hygiene-remote-"))
        self.addCleanup(shutil.rmtree, remote, True)
        subprocess.run(["git", "init", "-q", "--bare", remote], check=True)
        subprocess.run(["git", "init", "-q", "-b", branch], cwd=root, check=True)
        subprocess.run(["git", "-C", root, "config", "user.email", "fixture@example.invalid"], check=True)
        subprocess.run(["git", "-C", root, "config", "user.name", "Fixture"], check=True)
        subprocess.run(["git", "-C", root, "add", "."], check=True)
        subprocess.run(["git", "-C", root, "commit", "-qm", "fixture"], check=True)
        subprocess.run(["git", "-C", root, "remote", "add", "origin", str(remote)], check=True)
        subprocess.run(["git", "-C", root, "push", "-q", "--set-upstream", "origin", "HEAD"], check=True)
        subprocess.run(["git", "--git-dir", str(remote), "symbolic-ref", "HEAD", f"refs/heads/{branch}"], check=True)
        return root, remote

    def run_cli(self, args: list[str]) -> tuple[int, str]:
        output = StringIO()
        with redirect_stdout(output):
            result = main(args)
        return result, output.getvalue()

    def checkpoint_via_cli(self, root: Path, next_text: str, *extra: str) -> str:
        code, output = self.run_cli(
            [
                "checkpoint",
                "PCM-0001",
                "--root",
                str(root),
                "--agent",
                "test-agent",
                "--time",
                "2026-09-25T09:00:00Z",
                "--request-id",
                "hygiene-001",
                "--completed",
                "verified work",
                "--evidence",
                "deterministic test passed",
                "--decision",
                "hygiene keeps publish safe",
                "--changed",
                "tests/test_checkpoint_hygiene.py",
                "--next",
                next_text,
                *extra,
            ]
        )
        self.assertEqual(code, 0, output)
        return output

    def head_subject(self, root: Path) -> str:
        return subprocess.check_output(["git", "-C", root, "log", "-1", "--format=%s", "HEAD"], text=True).strip()

    def committed_paths(self, root: Path, commit: str = "HEAD") -> list[str]:
        return subprocess.check_output(
            ["git", "-C", root, "show", "--format=", "--name-only", commit], text=True
        ).split()


class ClosingKeywordSanitizationTests(HygieneCase):
    def test_next_closing_keyword_is_sanitized_in_commit_message(self) -> None:
        root, _ = self.make_repo()
        output = self.checkpoint_via_cli(root, "close #99 and verify receipts later")

        subject = self.head_subject(root)
        self.assertNotRegex(subject, EFFECTIVE_CLOSING)
        self.assertIn("Refs #99", subject)
        self.assertIn("NOTE: closing keyword sanitized in commit message", output)

        task = root / "tasks" / "TASK-PCM-0001-example.md"
        self.assertIn("close #99", task.read_text(encoding="utf-8"))

    def test_url_closing_reference_is_sanitized_in_commit_message(self) -> None:
        root, _ = self.make_repo()
        output = self.checkpoint_via_cli(
            root, "resolve https://github.com/Pukujan/project-continuity-modules/issues/140 in follow-up"
        )

        subject = self.head_subject(root)
        self.assertNotRegex(subject, EFFECTIVE_CLOSING)
        self.assertIn(
            "Refs https://github.com/Pukujan/project-continuity-modules/issues/140",
            subject,
        )
        self.assertIn("NOTE: closing keyword sanitized in commit message", output)

    def test_opt_in_flag_preserves_the_closing_directive(self) -> None:
        root, _ = self.make_repo()
        output = self.checkpoint_via_cli(root, "close #99 and verify receipts later", "--allow-closing-keywords")

        subject = self.head_subject(root)
        self.assertEqual(subject, "PCM checkpoint PCM-0001: close #99 and verify receipts later")
        self.assertNotIn("NOTE: closing keyword sanitized in commit message", output)

    def test_next_without_closing_keyword_is_left_untouched(self) -> None:
        root, _ = self.make_repo()
        output = self.checkpoint_via_cli(root, "run the full suite")

        self.assertEqual(self.head_subject(root), "PCM checkpoint PCM-0001: run the full suite")
        self.assertNotIn("NOTE: closing keyword sanitized in commit message", output)

    def test_colon_closing_form_is_sanitized_in_commit_message(self) -> None:
        root, _ = self.make_repo()
        output = self.checkpoint_via_cli(root, "Closes: #99 after this increment lands")

        subject = self.head_subject(root)
        self.assertNotRegex(subject, EFFECTIVE_CLOSING)
        self.assertIn("Refs: #99", subject)
        self.assertIn("NOTE: closing keyword sanitized in commit message", output)

    def test_uppercase_colon_closing_form_is_sanitized(self) -> None:
        root, _ = self.make_repo()
        output = self.checkpoint_via_cli(root, "CLOSES:#99 immediately")

        subject = self.head_subject(root)
        self.assertNotRegex(subject, EFFECTIVE_CLOSING)
        self.assertIn("NOTE: closing keyword sanitized in commit message", output)

    def test_cross_repo_closing_form_is_sanitized(self) -> None:
        root, _ = self.make_repo()
        output = self.checkpoint_via_cli(root, "fixes octo-org/octo-repo#100 in the partner project")

        subject = self.head_subject(root)
        self.assertNotRegex(subject, EFFECTIVE_CLOSING)
        self.assertIn("Refs octo-org/octo-repo#100", subject)
        self.assertIn("NOTE: closing keyword sanitized in commit message", output)


class IndexFreshnessAtPublishTests(HygieneCase):
    def make_catalog_repo(self) -> tuple[Path, Path]:
        root, remote = self.make_repo(branch="task/PCM-0047-hygiene-catalog")
        code, output = self.run_cli(["docs", "init", "--root", str(root)])
        self.assertEqual(code, 0, output)
        code, output = self.run_cli(
            [
                "docs",
                "add",
                "example-task",
                "--root",
                str(root),
                "--path",
                "tasks/TASK-PCM-0001-example.md",
                "--title",
                "Example task record",
                "--summary",
                "Cataloged task file used by the hygiene regression.",
                "--keyword",
                "hygiene",
                "--task",
                "PCM-0001",
            ]
        )
        self.assertEqual(code, 0, output)
        subprocess.run(["git", "-C", root, "add", "."], check=True)
        subprocess.run(["git", "-C", root, "commit", "-qm", "catalog the task file"], check=True)
        subprocess.run(["git", "-C", root, "push", "-q", "origin", "HEAD"], check=True)
        return root, remote

    def test_checkpoint_of_cataloged_task_lands_the_same_commit_index(self) -> None:
        root, _ = self.make_catalog_repo()
        self.checkpoint_via_cli(root, "run the full suite")

        committed = self.committed_paths(root)
        self.assertIn("tasks/TASK-PCM-0001-example.md", committed)
        self.assertIn("docs/CONTINUITY_INDEX.md", committed)

    def test_pushed_head_is_synchronized_for_a_fresh_clone(self) -> None:
        root, remote = self.make_catalog_repo()
        self.checkpoint_via_cli(root, "run the full suite")

        clone = Path(tempfile.mkdtemp(prefix="continuity-hygiene-clone-"))
        self.addCleanup(shutil.rmtree, clone, True)
        subprocess.run(["git", "clone", "-q", str(remote), str(clone)], check=True)
        code, output = self.run_cli(["docs", "render", "--check", "--root", str(clone)])
        self.assertEqual(output.count("OUT_OF_DATE"), 0, output)
        self.assertEqual(code, 0, output)
        self.assertIn("SYNCHRONIZED", output)

    def test_working_index_is_synchronized_right_after_publish(self) -> None:
        root, _ = self.make_catalog_repo()
        self.checkpoint_via_cli(root, "run the full suite")

        code, output = self.run_cli(["docs", "render", "--check", "--root", str(root)])
        self.assertEqual(code, 0, output)
        self.assertIn("SYNCHRONIZED", output)


class PreservedCheckpointBehaviorTests(HygieneCase):
    def test_request_id_replay_publishes_one_remote_checkpoint(self) -> None:
        root, remote = self.make_repo()
        first, first_out = self.run_cli(
            [
                "checkpoint",
                "PCM-0001",
                "--root",
                str(root),
                "--agent",
                "test-agent",
                "--time",
                "2026-09-25T09:00:00Z",
                "--request-id",
                "hygiene-replay",
                "--completed",
                "verified work",
                "--evidence",
                "deterministic test passed",
                "--decision",
                "hygiene keeps publish safe",
                "--changed",
                "tests/test_checkpoint_hygiene.py",
                "--next",
                "run the full suite",
            ]
        )
        self.assertEqual(first, 0, first_out)
        second, second_out = self.run_cli(
            [
                "checkpoint",
                "PCM-0001",
                "--root",
                str(root),
                "--agent",
                "test-agent",
                "--time",
                "2026-09-25T09:00:00Z",
                "--request-id",
                "hygiene-replay",
                "--completed",
                "verified work",
                "--evidence",
                "deterministic test passed",
                "--decision",
                "hygiene keeps publish safe",
                "--changed",
                "tests/test_checkpoint_hygiene.py",
                "--next",
                "run the full suite",
            ]
        )
        self.assertEqual(second, 0, second_out)
        self.assertEqual(
            subprocess.check_output(["git", "-C", root, "rev-list", "--count", "HEAD"], text=True).strip(), "2"
        )
        self.assertEqual(
            subprocess.check_output(
                ["git", "--git-dir", str(remote), "rev-parse", "refs/heads/task/PCM-0047-hygiene"], text=True
            ).strip(),
            subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip(),
        )

    def test_reusing_request_id_with_different_payload_is_refused(self) -> None:
        root, _ = self.make_repo()
        task = checkpoint_task(
            root,
            "PCM-0001",
            "test-agent",
            "2026-09-25T09:00:00Z",
            ["first payload"],
            ["deterministic test passed"],
            ["hygiene keeps publish safe"],
            ["tests/test_checkpoint_hygiene.py"],
            [],
            "run the full suite",
            request_id="hygiene-refuse",
        )
        before = task.read_bytes()
        with self.assertRaisesRegex(ContinuityError, "request ID.*different checkpoint payload"):
            checkpoint_task(
                root,
                "PCM-0001",
                "test-agent",
                "2026-09-25T09:30:00Z",
                ["different payload"],
                ["deterministic test passed"],
                ["hygiene keeps publish safe"],
                ["tests/test_checkpoint_hygiene.py"],
                [],
                "run the full suite",
                request_id="hygiene-refuse",
            )
        self.assertEqual(task.read_bytes(), before)

    def test_repository_without_a_catalog_commits_only_the_checkpoint(self) -> None:
        root, _ = self.make_repo()
        output = self.checkpoint_via_cli(root, "run the full suite")

        self.assertNotIn("NOTE: closing keyword sanitized in commit message", output)
        self.assertEqual(self.committed_paths(root), ["tasks/TASK-PCM-0001-example.md"])
        self.assertEqual(self.head_subject(root), "PCM checkpoint PCM-0001: run the full suite")


if __name__ == "__main__":
    unittest.main()
