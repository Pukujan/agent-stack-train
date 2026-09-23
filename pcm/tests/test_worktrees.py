from __future__ import annotations

import ctypes
import json
import os
import random
import subprocess
import tempfile
import unittest
from ctypes import wintypes
from pathlib import Path
from unittest.mock import patch

from continuity.cli import (
    ContinuityError,
    create_managed_worktree,
    extract_marker,
    github_repository,
    init_repo,
    marker,
    remove_managed_worktree,
    task_new,
    verify_merged_task,
)


class ManagedWorktreeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="continuity-managed-worktrees-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.remote = self.base / "origin.git"
        self.root = self.base / "project"
        subprocess.run(
            ["git", "init", "--bare", "--initial-branch=main", str(self.remote)],
            cwd=self.base,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "clone", str(self.remote), str(self.root)],
            cwd=self.base,
            check=True,
            capture_output=True,
            text=True,
        )
        self.git(["git", "config", "user.name", "PCM Test"])
        self.git(["git", "config", "user.email", "pcm-test@example.invalid"])
        init_repo(self.root, "software", "Worktree Test", "DPT")
        self.task_path = task_new(
            self.root, "safe-cleanup", "Test managed cleanup", "Test safe lifecycle", "test", "P1"
        )
        self.task_id = "DPT-0001"
        current_path = self.root / "checkpoints" / "CURRENT.md"
        current_text = current_path.read_text(encoding="utf-8")
        current_meta = extract_marker(current_text, "current")
        assert current_meta is not None
        current_meta["active_task"] = self.task_id
        current_meta["active_task_file"] = self.task_path.relative_to(self.root).as_posix()
        current_path.write_text(
            current_text.replace(
                marker("current", extract_marker(current_text, "current") or {}),
                marker("current", current_meta),
                1,
            ),
            encoding="utf-8",
        )
        self.commit_all("activate task")
        self.git(["git", "push", "--set-upstream", "origin", "main"])
        self.git(["git", "remote", "set-head", "origin", "main"])

    def git(self, args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            args,
            cwd=cwd or self.root,
            capture_output=True,
            check=True,
            text=True,
        )

    def commit_all(self, message: str, cwd: Path | None = None) -> None:
        self.git(["git", "add", "-A"], cwd)
        self.git(["git", "commit", "-m", message], cwd)

    def complete_task_on_main(self) -> None:
        text = self.task_path.read_text(encoding="utf-8")
        meta = extract_marker(text, "task")
        assert meta is not None
        meta["status"] = "completed"
        self.task_path.write_text(
            text.replace(marker("task", extract_marker(text, "task") or {}), marker("task", meta), 1),
            encoding="utf-8",
        )
        self.commit_all("complete test task")
        self.git(["git", "push", "origin", "main"])

    def test_create_is_confined_to_task_and_resume_is_idempotent(self) -> None:
        path, resumed = create_managed_worktree(self.root, self.task_id)
        self.assertFalse(resumed)
        self.assertEqual(path, self.root / "pcm" / "worktree" / self.task_id)
        self.assertTrue(path.is_dir())
        self.assertEqual((path, True), create_managed_worktree(self.root, self.task_id))
        worktree_count = sum(
            line.startswith("worktree ")
            for line in self.git(["git", "worktree", "list", "--porcelain"]).stdout.splitlines()
        )
        self.assertEqual(2, worktree_count)

    def test_create_refuses_task_not_pushed_to_default_branch(self) -> None:
        self.task_path.write_text(
            self.task_path.read_text(encoding="utf-8") + "\nLocal-only change.\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(ContinuityError, "local-only checkpoint changes"):
            create_managed_worktree(self.root, self.task_id)

    def test_create_refuses_strict_single_checkout_mode(self) -> None:
        config_path = self.root / ".continuity" / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["workspace"]["mode"] = "single-checkout"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        self.commit_all("select strict checkout mode")
        self.git(["git", "push", "origin", "main"])
        with self.assertRaisesRegex(ContinuityError, "strict single-checkout mode"):
            create_managed_worktree(self.root, self.task_id)

    def test_create_refuses_a_task_branch_already_checked_out_in_home_base(self) -> None:
        branch = "task/DPT-0001-safe-cleanup"
        self.git(["git", "checkout", "-b", branch])
        with self.assertRaisesRegex(ContinuityError, "already attached"):
            create_managed_worktree(self.root, self.task_id)

    def test_create_rejects_invalid_task_id_without_touching_filesystem(self) -> None:
        with self.assertRaisesRegex(ContinuityError, "invalid task ID"):
            create_managed_worktree(self.root, "../outside")
        self.assertFalse((self.base / "outside").exists())

    def test_cleanup_refuses_dirty_or_untracked_work(self) -> None:
        path, _ = create_managed_worktree(self.root, self.task_id)
        self.complete_task_on_main()
        (path / "operator-notes.txt").write_text("keep this", encoding="utf-8")
        with self.assertRaisesRegex(ContinuityError, "uncommitted or untracked work"):
            remove_managed_worktree(self.root, self.task_id)
        self.assertTrue(path.exists())

    def test_cleanup_refuses_pinned_worktree(self) -> None:
        path, _ = create_managed_worktree(self.root, self.task_id)
        self.git(["git", "worktree", "lock", "--reason", "user requested hold", str(path)])
        with self.assertRaisesRegex(ContinuityError, "pinned/locked"):
            remove_managed_worktree(self.root, self.task_id)
        self.assertTrue(path.exists())

    def test_cleanup_refuses_pushed_but_unmerged_branch(self) -> None:
        path, _ = create_managed_worktree(self.root, self.task_id)
        (path / "README.md").write_text("Task work\n", encoding="utf-8")
        self.commit_all("task change", path)
        branch = "task/DPT-0001-safe-cleanup"
        self.git(["git", "push", "--set-upstream", "origin", branch], path)
        self.complete_task_on_main()

        def no_merged_pr(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
            if command[:3] == ["gh", "pr", "list"]:
                return subprocess.CompletedProcess(command, 0, "[]", "")
            return subprocess.run(command, cwd=cwd, capture_output=True, check=False, text=True)

        with (
            patch("continuity.cli.github_repository", return_value="org/repo"),
            patch("continuity.cli.remote_default_branch", return_value="main"),
            patch("continuity.cli.run_external", side_effect=no_merged_pr),
            self.assertRaisesRegex(ContinuityError, "no uniquely matching merged PR"),
        ):
            remove_managed_worktree(self.root, self.task_id)
        self.assertTrue(path.exists())

    def test_cleanup_refuses_non_github_remote_without_ci_evidence(self) -> None:
        path, _ = create_managed_worktree(self.root, self.task_id)
        self.complete_task_on_main()
        with self.assertRaisesRegex(ContinuityError, "cannot verify required CI"):
            remove_managed_worktree(self.root, self.task_id)
        self.assertTrue(path.exists())

    def test_cleanup_refuses_remote_canonical_path_mismatch(self) -> None:
        path, _ = create_managed_worktree(self.root, self.task_id)
        self.complete_task_on_main()
        config_path = self.root / ".continuity" / "config.json"
        original_config = config_path.read_text(encoding="utf-8")
        changed_config = json.loads(original_config)
        changed_config["canonical"]["current"] = "alternate/CURRENT.md"
        config_path.write_text(json.dumps(changed_config), encoding="utf-8")
        self.commit_all("change canonical continuity path")
        self.git(["git", "push", "origin", "main"])
        self.git(["git", "fetch", "origin", "main"])
        config_path.write_text(original_config, encoding="utf-8")

        with (
            patch("continuity.cli.verify_merged_task", return_value=True),
            patch("continuity.cli.remote_default_branch", return_value="main"),
            self.assertRaisesRegex(ContinuityError, "canonical continuity paths differ"),
        ):
            remove_managed_worktree(self.root, self.task_id)
        self.assertTrue(path.exists())

    def test_cleanup_removes_only_a_clean_pushed_and_merged_task(self) -> None:
        path, _ = create_managed_worktree(self.root, self.task_id)
        (path / "README.md").write_text("Merged task work\n", encoding="utf-8")
        task_text = self.task_path.read_text(encoding="utf-8")
        task_meta = extract_marker(task_text, "task")
        assert task_meta is not None
        task_meta["status"] = "completed"
        self.task_path = path / self.task_path.relative_to(self.root)
        self.task_path.write_text(
            task_text.replace(marker("task", extract_marker(task_text, "task") or {}), marker("task", task_meta), 1),
            encoding="utf-8",
        )
        self.commit_all("task change", path)
        branch = "task/DPT-0001-safe-cleanup"
        self.git(["git", "push", "--set-upstream", "origin", branch], path)
        merge_checkout = self.base / "merge-checkout"
        subprocess.run(
            ["git", "clone", str(self.remote), str(merge_checkout)],
            cwd=self.base,
            capture_output=True,
            check=True,
            text=True,
        )
        self.git(["git", "fetch", "origin", branch], merge_checkout)
        self.git(["git", "merge", "--ff-only", f"origin/{branch}"], merge_checkout)
        self.git(["git", "push", "origin", "HEAD:main"], merge_checkout)
        local_task_text = (self.root / self.task_path.relative_to(path)).read_text(encoding="utf-8")
        local_task_meta = extract_marker(local_task_text, "task")
        assert local_task_meta is not None
        self.assertEqual("active", local_task_meta["status"])

        head_oid = self.git(["git", "rev-parse", "HEAD"], cwd=path).stdout.strip()
        pr_list = json.dumps(
            [
                {
                    "number": 12,
                    "headRefName": branch,
                    "headRefOid": head_oid,
                    "baseRefName": "main",
                    "mergedAt": "2026-09-23T00:00:00Z",
                    "mergeCommit": {"oid": head_oid},
                }
            ]
        )

        def external(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
            if command[:3] == ["gh", "pr", "list"]:
                return subprocess.CompletedProcess(command, 0, pr_list, "")
            if command[:3] == ["gh", "pr", "checks"]:
                checks = json.dumps([{"name": "quality", "bucket": "pass"}])
                return subprocess.CompletedProcess(command, 0, checks, "")
            return subprocess.run(command, cwd=cwd, capture_output=True, check=False, text=True)

        with (
            patch("continuity.cli.github_repository", return_value="org/repo"),
            patch("continuity.cli.remote_default_branch", return_value="main"),
            patch("continuity.cli.run_external", side_effect=external),
        ):
            self.assertEqual(path, remove_managed_worktree(self.root, self.task_id))
        self.assertFalse(path.exists())
        self.assertNotIn(f"refs/heads/{branch}", self.git(["git", "worktree", "list", "--porcelain"]).stdout)
        self.assertNotEqual(
            0,
            subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=self.root
            ).returncode,
        )

    def test_github_cleanup_requires_merged_pr_head_and_green_required_checks(self) -> None:
        head = "a" * 40
        merge = "b" * 40
        pr_list = json.dumps(
            [
                {
                    "number": 9,
                    "headRefName": "task/DPT-0001-safe-cleanup",
                    "headRefOid": head,
                    "baseRefName": "main",
                    "mergedAt": "2026-09-23T00:00:00Z",
                    "mergeCommit": {"oid": merge},
                }
            ]
        )

        def external(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
            if command[0] == "gh" and command[1:3] == ["pr", "list"]:
                return subprocess.CompletedProcess(command, 0, pr_list, "")
            if command[0] == "gh" and command[1:3] == ["pr", "checks"]:
                checks = json.dumps([{"name": "quality", "bucket": "pass"}])
                return subprocess.CompletedProcess(command, 0, checks, "")
            return subprocess.CompletedProcess(command, 0, "", "")

        def git_run(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args, 0, "", "")

        def git_value(root: Path, args: list[str], fallback: str | None = None) -> str:
            return head if root.name == "task" else "origin/main"

        with (
            patch("continuity.cli.remote_default_branch", return_value="main"),
            patch("continuity.cli.git_run", side_effect=git_run),
            patch("continuity.cli.git_value", side_effect=git_value),
            patch("continuity.cli.run_external", side_effect=external),
        ):
            self.assertTrue(
                verify_merged_task(
                    self.root, self.base / "task", "task/DPT-0001-safe-cleanup", "git@github.com:org/repo.git"
                )
            )

        def failing_checks(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
            if command[0] == "gh" and command[1:3] == ["pr", "list"]:
                return subprocess.CompletedProcess(command, 0, pr_list, "")
            if command[0] == "gh" and command[1:3] == ["pr", "checks"]:
                return subprocess.CompletedProcess(command, 1, "", "required check failed")
            return subprocess.CompletedProcess(command, 0, "", "")

        with (
            patch("continuity.cli.remote_default_branch", return_value="main"),
            patch("continuity.cli.git_run", side_effect=git_run),
            patch("continuity.cli.git_value", side_effect=git_value),
            patch("continuity.cli.run_external", side_effect=failing_checks),
            self.assertRaisesRegex(ContinuityError, "required GitHub checks"),
        ):
            verify_merged_task(
                self.root, self.base / "task", "task/DPT-0001-safe-cleanup", "git@github.com:org/repo.git"
            )

    def test_github_remote_identity_supports_https_and_ssh(self) -> None:
        self.assertEqual("org/repo", github_repository("https://github.com/org/repo.git"))
        self.assertEqual("org/repo", github_repository("git@github.com:org/repo.git"))
        self.assertIsNone(github_repository(str(self.remote)))


class WorktreeStorageExperimentTests(unittest.TestCase):
    def test_repeated_worktrees_share_git_objects_but_keep_checkout_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="continuity-worktree-storage-") as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            source.mkdir()

            def git(cwd: Path, *args: str) -> str:
                result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=True, text=True)
                return result.stdout.strip()

            git(source, "init", "--initial-branch=main")
            git(source, "config", "user.name", "PCM Storage Test")
            git(source, "config", "user.email", "pcm-storage@example.invalid")
            git(source, "config", "core.compression", "0")
            payload = random.Random(19).randbytes(1024 * 1024)
            (source / "representative-payload.bin").write_bytes(payload)
            git(source, "add", "representative-payload.bin")
            git(source, "commit", "-m", "storage experiment baseline")

            worktrees = [root / f"worktree-{index}" for index in range(3)]
            clones = [root / f"clone-{index}" for index in range(3)]
            for index, path in enumerate(worktrees):
                git(source, "worktree", "add", "--detach", str(path), "HEAD")
                subprocess.run(
                    ["git", "clone", "--no-hardlinks", str(source), str(clones[index])],
                    cwd=root,
                    capture_output=True,
                    check=True,
                    text=True,
                )

            def files_size(path: Path) -> int:
                return sum(
                    file.stat().st_size
                    for file in path.rglob("*")
                    if file.is_file() and ".git" not in file.relative_to(path).parts
                )

            def object_size(path: Path) -> int:
                return sum(file.stat().st_size for file in (path / ".git" / "objects").rglob("*") if file.is_file())

            def allocated_size(file: Path) -> int:
                if os.name != "nt":
                    raise unittest.SkipTest("Windows file-allocation measurement is Windows-only")
                kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
                get_compressed_file_size = kernel32.GetCompressedFileSizeW
                get_compressed_file_size.argtypes = (wintypes.LPCWSTR, ctypes.POINTER(wintypes.DWORD))
                get_compressed_file_size.restype = wintypes.DWORD
                high = wintypes.DWORD()
                ctypes.set_last_error(0)
                low = get_compressed_file_size(str(file), ctypes.byref(high))
                error = ctypes.get_last_error()
                if low == 0xFFFFFFFF and error:
                    raise ctypes.WinError(error)
                return (high.value << 32) | low

            def allocated_files(path: Path, exclude_git: bool = False) -> int:
                return sum(
                    allocated_size(file)
                    for file in path.rglob("*")
                    if file.is_file() and (not exclude_git or ".git" not in file.relative_to(path).parts)
                )

            linked_common_dirs = set()
            for path in [source, *worktrees]:
                common_dir = Path(git(path, "rev-parse", "--git-common-dir"))
                linked_common_dirs.add((path / common_dir).resolve() if not common_dir.is_absolute() else common_dir)
            self.assertEqual(1, len(linked_common_dirs))
            worktree_checkout_bytes = sum(files_size(path) for path in worktrees)
            clone_checkout_bytes = sum(files_size(path) for path in clones)
            shared_git_object_bytes = object_size(source)
            cloned_git_object_bytes = sum(object_size(path) for path in clones)
            self.assertGreater(shared_git_object_bytes, 0)
            self.assertEqual(worktree_checkout_bytes, clone_checkout_bytes)
            self.assertGreater(cloned_git_object_bytes, shared_git_object_bytes)
            summary = (
                "LOGICAL_STORAGE_EXPERIMENT bytes: "
                f"three_worktree_checkouts={worktree_checkout_bytes}; "
                f"one_shared_git_object_store={shared_git_object_bytes}; "
                f"three_clone_checkouts={clone_checkout_bytes}; "
                f"three_cloned_git_object_stores={cloned_git_object_bytes}; "
            )
            if os.name == "nt":
                home_checkout_and_objects = allocated_files(source, exclude_git=True) + allocated_files(
                    source / ".git" / "objects"
                )
                worktree_allocated = home_checkout_and_objects + sum(
                    allocated_files(path, exclude_git=True) for path in worktrees
                )
                clones_allocated = home_checkout_and_objects + sum(
                    allocated_files(path / ".git" / "objects") + allocated_files(path, exclude_git=True)
                    for path in clones
                )
                self.assertGreater(clones_allocated, worktree_allocated)
                summary += (
                    "\nWINDOWS_FILE_STORAGE_EXPERIMENT bytes: "
                    f"home_plus_three_linked_worktrees={worktree_allocated}; "
                    f"home_plus_three_no_hardlink_clones={clones_allocated}; "
                    "Win32 GetCompressedFileSizeW; excludes filesystem metadata and package environments"
                )
            else:
                summary += " physical Windows allocation and package environments not measured"
            print(summary)


if __name__ == "__main__":
    unittest.main()
