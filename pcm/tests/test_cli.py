from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from continuity import __version__
from continuity.cli import (
    ContinuityError,
    build_parser,
    checkpoint_task,
    extract_marker,
    github_issue_template,
    github_pr_template,
    init_repo,
    load_json,
    main,
    pack_task,
    preflight_repo,
    publish_checkpoint,
    reconcile_recovery,
    task_new,
    validate_repo,
    verify_task_issue,
)

FIXTURES = Path(__file__).parent / "fixtures"


class ContinuityTests(unittest.TestCase):
    def copy_fixture(self, name: str) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="continuity-test-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        shutil.copytree(FIXTURES / name, tmp, dirs_exist_ok=True)
        return tmp

    def test_cli_version_matches_package_version(self) -> None:
        output = StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as raised:
            main(["--version"])

        self.assertEqual(raised.exception.code, 0)
        self.assertEqual(output.getvalue(), f"continuity {__version__}\n")

    def test_github_templates_are_opt_in_idempotent_and_valid(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-github-templates-"))
        self.addCleanup(shutil.rmtree, root, True)

        self.assertEqual(
            main(["init", "--root", str(root), "--profile", "minimal", "--name", "Example", "--github-templates"]),
            0,
        )
        issue_path = root / ".github" / "ISSUE_TEMPLATE" / "task.md"
        pr_path = root / ".github" / "pull_request_template.md"
        self.assertEqual(issue_path.read_text(encoding="utf-8"), github_issue_template())
        self.assertEqual(pr_path.read_text(encoding="utf-8"), github_pr_template())
        config = json.loads((root / ".continuity" / "config.json").read_text(encoding="utf-8"))
        self.assertFalse(config["trackers"]["github"])
        self.assertEqual(validate_repo(root), [])

        before = {path: path.read_bytes() for path in (issue_path, pr_path)}
        self.assertEqual(
            main(["init", "--root", str(root), "--profile", "minimal", "--name", "Example", "--github-templates"]),
            0,
        )
        self.assertEqual({path: path.read_bytes() for path in before}, before)

    def test_github_template_conflict_prevents_partial_initialization(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-github-conflict-"))
        self.addCleanup(shutil.rmtree, root, True)
        custom_template = root / ".github" / "pull_request_template.md"
        custom_template.parent.mkdir(parents=True)
        custom_template.write_text("Existing project-owned PR template.\n", encoding="utf-8")

        with self.assertRaisesRegex(ContinuityError, "initialization conflicts"):
            init_repo(root, "minimal", "Example", "APP", github_templates=True)

        self.assertEqual(custom_template.read_text(encoding="utf-8"), "Existing project-owned PR template.\n")
        self.assertFalse((root / "PROJECT.md").exists())
        self.assertFalse((root / ".continuity" / "config.json").exists())

    def test_github_templates_remain_opt_in_and_do_not_claim_sync(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-no-github-templates-"))
        self.addCleanup(shutil.rmtree, root, True)
        init_repo(root, "minimal", "Example", "APP")

        self.assertFalse((root / ".github" / "ISSUE_TEMPLATE" / "task.md").exists())
        config = json.loads((root / ".continuity" / "config.json").read_text(encoding="utf-8"))
        self.assertFalse(config["trackers"]["github"])
        self.assertIn("does not automatically synchronize", github_issue_template().lower())
        self.assertIn("does not automatically synchronize", github_pr_template().lower())

    def test_github_authority_requires_issue_links_for_new_active_tasks(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-github-authority-"))
        self.addCleanup(shutil.rmtree, root, True)
        init_repo(root, "minimal", "Example", "APP", github_authority=True)
        with self.assertRaisesRegex(ContinuityError, "require --issue"):
            task_new(root, "first", "Do work", "Why", "owner", "P1")
        task = task_new(
            root, "first", "Do work", "Why", "owner", "P1", "https://github.com/example/repo/issues/12"
        )
        meta = extract_marker(task.read_text(encoding="utf-8"), "task")
        self.assertEqual("https://github.com/example/repo/issues/12", meta["issue_url"])
        self.assertEqual([], validate_repo(root))

    def test_generated_handoff_names_github_and_private_workspace_authorities(self) -> None:
        from continuity.cli import handoff_template

        generated = handoff_template("managed-worktrees")
        self.assertIn("GitHub Issues are authoritative", generated)
        self.assertIn("continuity workspace register", generated)
        self.assertIn("must never be copied into issues, commits, PRs, or handoffs", generated)

    def test_issue_verification_reads_live_github_state(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-issue-verify-"))
        self.addCleanup(shutil.rmtree, root, True)
        init_repo(root, "minimal", "Example", "APP", github_authority=True)
        task_new(root, "first", "Do work", "Why", "owner", "P1", "https://github.com/example/repo/issues/12")
        response = json.dumps({"number": 12, "title": "First issue", "state": "OPEN", "url": "https://github.com/example/repo/issues/12"})
        with (
            patch("continuity.cli.git_value", return_value="https://github.com/example/repo.git"),
            patch(
                "continuity.cli.run_external",
                return_value=subprocess.CompletedProcess([], 0, response, ""),
            ) as external,
        ):
            result = verify_task_issue(root, "APP-0001")
        self.assertEqual("OPEN", result["state"])
        self.assertIn("gh", external.call_args.args[0][0])

    def test_valid_fixture(self) -> None:
        root = self.copy_fixture("valid-minimal")
        self.assertEqual(validate_repo(root), [])

    def test_broken_fixture_reports_missing_current(self) -> None:
        root = self.copy_fixture("broken-missing-current")
        errors = validate_repo(root)
        self.assertTrue(any("missing canonical current" in error for error in errors), errors)

    def test_init_nonempty_unrelated_repo_is_non_destructive(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-init-"))
        self.addCleanup(shutil.rmtree, root, True)
        (root / "notes.txt").write_text("keep me\n", encoding="utf-8")
        results = init_repo(root, "minimal", "Example", "PCM")
        self.assertEqual((root / "notes.txt").read_text(encoding="utf-8"), "keep me\n")
        self.assertTrue(any(line.endswith("PROJECT.md") for line in results))
        self.assertEqual(validate_repo(root), [])

    def test_software_profile_includes_managed_worktree_policy(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-software-init-"))
        self.addCleanup(shutil.rmtree, root, True)
        init_repo(root, "software", "Example", "SOFT")

        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("one per independent active task, not one per session or agent", agents)
        self.assertIn("pcm/worktree/<TASK-ID>", agents)
        self.assertIn("continuity worktree remove", agents)
        self.assertIn("git worktree lock", agents)
        self.assertIn("git worktree unlock", agents)
        self.assertIn("expected release date", agents)
        self.assertIn("completed task's checkpoint", agents)
        self.assertIn("unlock/remove next action", agents)
        self.assertIn("required CI passes", agents)
        self.assertIn("every fresh session or task takeover/resumption must consult it", agents)
        self.assertIn("issue title and task-objective terms", agents)
        self.assertIn("read the returned matches and declared neighbors", agents)
        self.assertIn("Reuse package-manager download/build caches", agents)
        self.assertNotIn("Do not create clones, task folders, or linked Git worktrees anywhere", agents)
        config = json.loads((root / ".continuity" / "config.json").read_text(encoding="utf-8"))
        schema = json.loads((root / "schemas" / "v1" / "config.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(config["workspace"]["mode"], "managed-worktrees")
        self.assertEqual(
            schema["properties"]["workspace"]["properties"]["mode"]["enum"],
            ["managed-worktrees", "single-checkout"],
        )
        self.assertEqual(validate_repo(root), [])

    def test_minimal_profile_documents_time_bounded_worktree_holds(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-minimal-worktree-policy-"))
        self.addCleanup(shutil.rmtree, root, True)
        init_repo(root, "minimal", "Example", "APP")

        handoff = (root / "HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("expected release date", handoff)
        self.assertIn("git worktree lock", handoff)
        self.assertIn("git worktree unlock", handoff)
        self.assertIn("Every fresh session or task takeover/resumption must consult the inventory", handoff)
        self.assertIn("issue title and task-objective terms", handoff)
        self.assertIn("read matching records and their declared neighbors", handoff)

    def test_init_cli_accepts_only_supported_workspace_modes(self) -> None:
        args = build_parser().parse_args(
            ["init", "--profile", "software", "--workspace-mode", "single-checkout"]
        )
        self.assertEqual(args.workspace_mode, "single-checkout")
        with self.assertRaises(SystemExit):
            build_parser().parse_args(
                ["init", "--profile", "software", "--workspace-mode", "linked-worktrees"]
            )

    def test_validation_accepts_only_canonical_worktree(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-canonical-worktree-"))
        self.addCleanup(shutil.rmtree, root, True)
        init_repo(root, "minimal", "Example", "SOFT")
        (root / ".git").mkdir()
        result = subprocess.CompletedProcess(
            args=["git", "worktree", "list", "--porcelain"],
            returncode=0,
            stdout=f"worktree {root}\nHEAD 0123456789abcdef\n",
            stderr="",
        )

        with patch("continuity.cli.subprocess.run", return_value=result):
            errors = validate_repo(root)

        self.assertEqual(errors, [])

    def test_validation_rejects_registered_additional_worktree(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-single-checkout-"))
        self.addCleanup(shutil.rmtree, root, True)
        init_repo(root, "minimal", "Example", "SOFT")
        config_path = root / ".continuity" / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["workspace"]["mode"] = "single-checkout"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        (root / ".git").mkdir()
        worktree_output = (
            f"worktree {root}\nHEAD 0123456789abcdef\n\n"
            f"worktree {root / '.worktrees' / 'task'}\nHEAD fedcba9876543210\n"
        )
        result = subprocess.CompletedProcess(
            args=["git", "worktree", "list", "--porcelain"],
            returncode=0,
            stdout=worktree_output,
            stderr="",
        )

        with patch("continuity.cli.subprocess.run", return_value=result):
            errors = validate_repo(root)

        self.assertTrue(
            any("single-checkout mode requires exactly one registered Git worktree" in e for e in errors),
            errors,
        )

    def test_legacy_workspace_mode_requires_manual_migration_without_rewriting(self) -> None:
        root = self.copy_fixture("valid-minimal")
        config_path = root / ".continuity" / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["workspace_mode"] = "linked-worktrees"
        original = json.dumps(config, indent=3).encode("utf-8")
        config_path.write_bytes(original)

        errors = validate_repo(root)
        self.assertTrue(any("unsupported legacy key 'workspace_mode'" in error for error in errors), errors)
        self.assertTrue(any("use `workspace:" in error for error in errors), errors)
        self.assertEqual(config_path.read_bytes(), original)

        config.pop("workspace_mode")
        config_path.write_text(json.dumps(config), encoding="utf-8")
        self.assertEqual(validate_repo(root), [])

    def test_init_refuses_conflicting_existing_content_before_writes(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-conflict-"))
        self.addCleanup(shutil.rmtree, root, True)
        (root / "PROJECT.md").write_text("user content\n", encoding="utf-8")
        with self.assertRaisesRegex(Exception, "initialization conflicts"):
            init_repo(root, "minimal", "Example", "PCM")
        self.assertFalse((root / ".continuity" / "config.json").exists())
        self.assertEqual((root / "PROJECT.md").read_text(encoding="utf-8"), "user content\n")

    def test_preflight_accepts_explicit_valid_target(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-preflight-target-"))
        self.addCleanup(shutil.rmtree, root, True)
        init_repo(root, "minimal", "Inference Recommendation Engine", "IRE")
        mode, errors = preflight_repo(root)
        self.assertEqual(mode, "TARGET_VALID")
        self.assertEqual(errors, [])

    def test_preflight_rejects_pcm_helper_as_target(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-preflight-helper-"))
        self.addCleanup(shutil.rmtree, root, True)
        init_repo(root, "minimal", "Project Continuity Modules", "PCM")
        mode, errors = preflight_repo(root)
        self.assertEqual(mode, "HELPER_REPOSITORY")
        self.assertTrue(any("helper repository" in error for error in errors), errors)

    def test_preflight_rejects_continuity_looking_but_invalid_target(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-preflight-invalid-"))
        self.addCleanup(shutil.rmtree, root, True)
        (root / ".continuity").mkdir(parents=True)
        (root / ".continuity" / "config.json").write_text(
            json.dumps({
                "protocolVersion": "0.1.0",
                "projectName": "inference-recommendation-engine",
                "taskPrefix": "IRE",
                "activeTask": "IRE-0001",
            }),
            encoding="utf-8",
        )
        validation_errors = validate_repo(root)
        self.assertTrue(validation_errors)
        self.assertTrue(any("missing required key" in error for error in validation_errors), validation_errors)
        mode, errors = preflight_repo(root)
        self.assertEqual(mode, "INVALID_TARGET")
        self.assertEqual(errors, validation_errors)

    def test_task_new_allocates_stable_next_id(self) -> None:
        root = self.copy_fixture("valid-minimal")
        path = task_new(root, "second task", "Do the second thing.", "Exercise ID allocation.", "agent", "P1")
        self.assertEqual(path.name, "TASK-PCM-0002-second-task.md")
        meta = extract_marker(path.read_text(encoding="utf-8"), "task")
        self.assertEqual(meta["id"], "PCM-0002")

    def test_checkpoint_preserves_existing_history_and_adds_marker(self) -> None:
        root = self.copy_fixture("valid-minimal")
        task = root / "tasks" / "TASK-PCM-0001-example.md"
        original = task.read_text(encoding="utf-8")
        path = checkpoint_task(
            root,
            "PCM-0001",
            "test-agent",
            "2026-09-20T18:00:00Z",
            ["implemented fixture"],
            ["python -m unittest -> pass"],
            ["use append-only checkpoints"],
            ["tests/test_cli.py"],
            [],
            "run validation",
        )
        updated = path.read_text(encoding="utf-8")
        self.assertIn(original.split("## Handoff", 1)[0].rstrip(), updated)
        self.assertIn("continuity:checkpoint", updated)
        self.assertIn("implemented fixture", updated)
        self.assertEqual(validate_repo(root), [])

    def test_unavailable_canonical_state_is_reported_without_traceback(self) -> None:
        root = self.copy_fixture("valid-minimal")
        task = root / "tasks" / "TASK-PCM-0001-example.md"
        original_read = Path.read_text

        def blocked_read(path: Path, *args, **kwargs):
            if path.resolve() == task.resolve():
                raise PermissionError("canonical task temporarily unavailable")
            return original_read(path, *args, **kwargs)

        with patch.object(Path, "read_text", blocked_read):
            errors = validate_repo(root)
            self.assertTrue(any("canonical task unavailable" in error for error in errors), errors)
            mode, preflight_errors = preflight_repo(root)
            self.assertEqual(mode, "DEGRADED_TARGET")
            self.assertEqual(preflight_errors, errors)
            with self.assertRaisesRegex(ContinuityError, "canonical task unavailable"):
                checkpoint_task(
                    root,
                    "PCM-0001",
                    "test-agent",
                    "2026-09-20T18:00:00Z",
                    ["implemented fixture"],
                    ["temporary write failure reproduced"],
                    ["continue safe work"],
                    ["tests/test_cli.py"],
                    [],
                    "run validation",
                )

    def test_checkpoint_writes_recovery_receipt_and_reconciles(self) -> None:
        root = self.copy_fixture("valid-minimal")
        recovery_root = self.copy_fixture("valid-minimal")
        task = root / "tasks" / "TASK-PCM-0001-example.md"
        original_write = Path.write_text

        def block_canonical_write(path: Path, data: str, *args, **kwargs):
            if path.resolve() == task.resolve():
                raise PermissionError("canonical task temporarily unavailable")
            return original_write(path, data, *args, **kwargs)

        with patch.object(Path, "write_text", block_canonical_write):
            receipt_path = checkpoint_task(
                root,
                "PCM-0001",
                "test-agent",
                "2026-09-20T18:05:00Z",
                ["implemented fixture"],
                ["recovery receipt written"],
                ["continue safe work"],
                ["tests/test_cli.py"],
                ["canonical task temporarily unavailable"],
                "reconcile the receipt when canonical state is writable",
                recovery_root,
            )

        receipt = load_json(receipt_path)
        self.assertEqual(receipt["schema"], "project-continuity.recovery.v1")
        self.assertEqual(receipt["status"], "pending-reconciliation")
        self.assertEqual(receipt["checkpoint"]["agent"], "test-agent")
        self.assertEqual(receipt["checkpoint"]["task_id"], "PCM-0001")
        self.assertEqual(validate_repo(recovery_root), [])

        output = reconcile_recovery(root, receipt_path)
        self.assertEqual(output, task)
        self.assertEqual(validate_repo(root), [])
        self.assertEqual(load_json(receipt_path)["status"], "reconciled")
        task_after_first_reconcile = task.read_bytes()
        receipt_after_first_reconcile = receipt_path.read_bytes()
        self.assertEqual(reconcile_recovery(root, receipt_path), task)
        self.assertEqual(task.read_bytes(), task_after_first_reconcile)
        self.assertEqual(receipt_path.read_bytes(), receipt_after_first_reconcile)

    def test_checkpoint_publish_commits_and_pushes_to_origin(self) -> None:
        root = self.copy_fixture("valid-minimal")
        remote = Path(tempfile.mkdtemp(prefix="continuity-remote-"))
        self.addCleanup(shutil.rmtree, remote, True)
        subprocess.run(["git", "init", "-q", "--bare", remote], check=True)
        subprocess.run(["git", "-C", root, "init", "-q", "-b", "task/PCM-0001-example"], check=True)
        subprocess.run(["git", "-C", root, "config", "user.email", "fixture@example.invalid"], check=True)
        subprocess.run(["git", "-C", root, "config", "user.name", "Fixture"], check=True)
        subprocess.run(["git", "-C", root, "add", "."], check=True)
        subprocess.run(["git", "-C", root, "commit", "-qm", "fixture"], check=True)
        subprocess.run(["git", "-C", root, "remote", "add", "origin", str(remote)], check=True)
        subprocess.run(["git", "-C", root, "push", "-q", "--set-upstream", "origin", "HEAD"], check=True)

        task = root / "tasks" / "TASK-PCM-0001-example.md"
        checkpoint_task(
            root,
            "PCM-0001",
            "test-agent",
            "2026-09-20T18:10:00Z",
            ["prepared durable delivery"],
            ["local validation passed"],
            ["checkpoint delivery is a Git operation"],
            ["tests/test_cli.py"],
            [],
            "open the automated review path",
        )
        commit = publish_checkpoint(root, task, "PCM-0001", "open the automated review path")

        self.assertEqual(subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip(), commit)
        remote_commit = subprocess.check_output(
            ["git", "--git-dir", remote, "rev-parse", "refs/heads/task/PCM-0001-example"], text=True
        ).strip()
        self.assertEqual(remote_commit, commit)
        self.assertEqual(subprocess.check_output(["git", "-C", root, "status", "--porcelain"], text=True), "")

    def test_pack_records_git_provenance_and_sources(self) -> None:
        root = self.copy_fixture("valid-minimal")
        subprocess.run(["git", "init", "-q", root], check=True)
        subprocess.run(["git", "-C", root, "config", "user.email", "fixture@example.invalid"], check=True)
        subprocess.run(["git", "-C", root, "config", "user.name", "Fixture"], check=True)
        subprocess.run(["git", "-C", root, "add", "."], check=True)
        subprocess.run(["git", "-C", root, "commit", "-qm", "fixture"], check=True)
        subprocess.run(
            ["git", "-C", root, "remote", "add", "origin", "https://example.invalid/fixture.git"], check=True
        )
        output = pack_task(root, "PCM-0001", None)
        meta = extract_marker(output.read_text(encoding="utf-8"), "context-pack")
        self.assertEqual(meta["repository"], "https://example.invalid/fixture.git")
        self.assertNotEqual(meta["commit"], "unknown")
        self.assertIn("PROJECT.md", meta["sources"])
        self.assertEqual(validate_repo(root), [])

    def test_minimal_end_to_end_dogfood_flow(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-e2e-"))
        self.addCleanup(shutil.rmtree, root, True)

        init_repo(root, "minimal", "Dogfood", "DOG")
        self.assertEqual(validate_repo(root), [])

        task = task_new(
            root,
            "first dogfood task",
            "Exercise the initialized minimal repository.",
            "Verify the v1 commands compose end to end.",
            "dogfood-agent",
            "P0",
        )
        self.assertEqual(task.name, "TASK-DOG-0001-first-dogfood-task.md")
        self.assertEqual(validate_repo(root), [])

        original = task.read_text(encoding="utf-8")
        checkpoint_task(
            root,
            "DOG-0001",
            "dogfood-agent",
            "2026-09-20T18:35:00Z",
            ["initialized and validated the minimal repository"],
            ["init and validate returned success"],
            ["keep the minimal profile dependency-free"],
            ["tasks/TASK-DOG-0001-first-dogfood-task.md"],
            [],
            "generate a provenance-bearing context pack",
        )
        updated = task.read_text(encoding="utf-8")
        self.assertIn(original.split("## Handoff", 1)[0].rstrip(), updated)
        self.assertIn("continuity:checkpoint", updated)
        self.assertEqual(validate_repo(root), [])

        subprocess.run(["git", "init", "-q", root], check=True)
        subprocess.run(["git", "-C", root, "config", "user.email", "dogfood@example.invalid"], check=True)
        subprocess.run(["git", "-C", root, "config", "user.name", "PCM Dogfood"], check=True)
        subprocess.run(["git", "-C", root, "add", "."], check=True)
        subprocess.run(["git", "-C", root, "commit", "-qm", "dogfood source state"], check=True)
        subprocess.run(
            ["git", "-C", root, "remote", "add", "origin", "https://example.invalid/pcm-minimal-dogfood.git"],
            check=True,
        )

        output = pack_task(root, "DOG-0001", None)
        meta = extract_marker(output.read_text(encoding="utf-8"), "context-pack")
        self.assertEqual(meta["repository"], "https://example.invalid/pcm-minimal-dogfood.git")
        self.assertEqual(meta["task_id"], "DOG-0001")
        self.assertNotEqual(meta["commit"], "unknown")
        self.assertIn("PROJECT.md", meta["sources"])
        self.assertIn("checkpoints/CURRENT.md", meta["sources"])
        self.assertIn("tasks/TASK-DOG-0001-first-dogfood-task.md", meta["sources"])
        self.assertEqual(validate_repo(root), [])


if __name__ == "__main__":
    unittest.main()
