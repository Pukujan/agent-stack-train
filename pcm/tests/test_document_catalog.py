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

from continuity.cli import (
    BUILTIN_SCHEMAS,
    SCHEMA_FILES,
    agents_template,
    document_freshness,
    handoff_template,
    main,
    remote_document_hashes,
    sha256_document_bytes,
    validate_repo,
)

FIXTURE = Path(__file__).parent / "fixtures" / "valid-minimal"


class DocumentCatalogTests(unittest.TestCase):
    def make_repo(self) -> Path:
        root = Path(tempfile.mkdtemp(prefix="continuity-documents-"))
        self.addCleanup(shutil.rmtree, root, True)
        shutil.copytree(FIXTURE, root, dirs_exist_ok=True)
        (root / "docs").mkdir()
        (root / "docs" / "checkpoint-retries.md").write_text(
            "# Safe checkpoint retries\n\nA request key makes publishing retries idempotent.\n", encoding="utf-8"
        )
        (root / "docs" / "session-discovery.md").write_text(
            "# Fresh session discovery\n\nFind prior decisions and linked records.\n", encoding="utf-8"
        )
        (root / "docs" / "unrelated.md").write_text("Unrelated release note.\n", encoding="utf-8")
        return root

    def run_cli(self, args: list[str]) -> tuple[int, str]:
        output = StringIO()
        with redirect_stdout(output):
            result = main(args)
        return result, output.getvalue()

    def test_optional_schemas_match_the_installed_cli_contract(self) -> None:
        for kind in ("documents", "checkpoint-operation"):
            path = Path(__file__).parents[1] / "schemas" / "v1" / SCHEMA_FILES[kind]
            with self.subTest(kind=kind):
                self.assertEqual(json.loads(path.read_text(encoding="utf-8")), BUILTIN_SCHEMAS[kind])

    def test_generated_and_checked_in_guidance_explain_retry_and_discovery(self) -> None:
        generated_handoff = handoff_template("managed-worktrees")
        generated_agents = agents_template("managed-worktrees")
        static_handoff = (Path(__file__).parents[1] / "templates" / "v1" / "minimal" / "HANDOFF.md").read_text(
            encoding="utf-8"
        )
        static_agents = (Path(__file__).parents[1] / "templates" / "v1" / "software" / "AGENTS.md").read_text(
            encoding="utf-8"
        )
        for guidance in (generated_handoff, generated_agents, static_handoff, static_agents):
            with self.subTest(guidance=guidance[:30]):
                self.assertIn("REQUEST_ID", guidance)
                self.assertIn("continuity docs find", guidance)
                self.assertIn("documents.json", guidance)

    def initialize_catalog(self, root: Path) -> None:
        code, _ = self.run_cli(["docs", "init", "--root", str(root)])
        self.assertEqual(code, 0)

    def add_doc(self, root: Path, doc_id: str, path: str, title: str, summary: str, *extra: str) -> None:
        code, output = self.run_cli(
            [
                "docs",
                "add",
                doc_id,
                "--root",
                str(root),
                "--path",
                path,
                "--title",
                title,
                "--summary",
                summary,
                *extra,
            ]
        )
        self.assertEqual(code, 0, output)

    def test_init_and_add_are_idempotent_and_index_is_rendered_from_manifest(self) -> None:
        root = self.make_repo()
        self.initialize_catalog(root)
        self.add_doc(
            root,
            "checkpoint-retries",
            "docs/checkpoint-retries.md",
            "Safe checkpoint retries",
            "A request key makes retries idempotent.",
            "--keyword",
            "checkpoint retry",
            "--task",
            "PCM-0001",
        )
        catalog = root / ".continuity" / "documents.json"
        view = root / "docs" / "CONTINUITY_INDEX.md"
        first_catalog = catalog.read_bytes()
        first_view = view.read_bytes()

        self.initialize_catalog(root)
        self.add_doc(
            root,
            "checkpoint-retries",
            "docs/checkpoint-retries.md",
            "Safe checkpoint retries",
            "A request key makes retries idempotent.",
            "--keyword",
            "checkpoint retry",
            "--task",
            "PCM-0001",
        )

        self.assertEqual(catalog.read_bytes(), first_catalog)
        self.assertEqual(view.read_bytes(), first_view)
        self.assertIn("Safe checkpoint retries", view.read_text(encoding="utf-8"))
        self.assertIn("Local content status", view.read_text(encoding="utf-8"))
        self.assertIn("docs find` for cached remote freshness", view.read_text(encoding="utf-8"))
        self.assertEqual(validate_repo(root), [])

    def test_lookup_returns_deterministic_match_and_related_neighbor(self) -> None:
        root = self.make_repo()
        self.initialize_catalog(root)
        self.add_doc(
            root,
            "checkpoint-retries",
            "docs/checkpoint-retries.md",
            "Safe checkpoint retries",
            "A request key makes retries idempotent.",
            "--keyword",
            "request key",
            "--task",
            "PCM-0001",
        )
        self.add_doc(
            root,
            "session-discovery",
            "docs/session-discovery.md",
            "Fresh session discovery",
            "Find prior decisions and linked records.",
            "--keyword",
            "handoff documents",
            "--related",
            "checkpoint-retries",
        )

        first_code, first_output = self.run_cli(["docs", "find", "handoff documents", "--root", str(root)])
        second_code, second_output = self.run_cli(["docs", "find", "handoff documents", "--root", str(root)])

        self.assertEqual(first_code, 0)
        self.assertEqual(second_code, 0)
        self.assertEqual(first_output, second_output)
        self.assertIn("session-discovery", first_output)
        self.assertIn("checkpoint-retries", first_output)

    def test_lookup_is_invariant_to_catalog_record_order(self) -> None:
        root = self.make_repo()
        self.initialize_catalog(root)
        self.add_doc(
            root,
            "checkpoint-retries",
            "docs/checkpoint-retries.md",
            "Safe checkpoint retries",
            "A request key makes retries idempotent.",
            "--keyword",
            "request key",
        )
        self.add_doc(
            root,
            "session-discovery",
            "docs/session-discovery.md",
            "Fresh session discovery",
            "Find prior decisions and linked records.",
            "--keyword",
            "request key history",
            "--related",
            "checkpoint-retries",
        )
        code, before = self.run_cli(["docs", "find", "request key", "--root", str(root)])
        self.assertEqual(code, 0)

        catalog_path = root / ".continuity" / "documents.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["documents"].reverse()
        catalog_path.write_text(json.dumps(catalog, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        code, after = self.run_cli(["docs", "find", "request key", "--root", str(root)])

        self.assertEqual(code, 0)
        self.assertEqual(after, before)

    def test_document_hash_treats_windows_line_endings_as_same_content(self) -> None:
        root = self.make_repo()
        self.initialize_catalog(root)
        self.add_doc(
            root,
            "checkpoint-retries",
            "docs/checkpoint-retries.md",
            "Safe checkpoint retries",
            "A request key makes retries idempotent.",
            "--keyword",
            "request key",
        )
        path = root / "docs" / "checkpoint-retries.md"
        normalized_text = path.read_text(encoding="utf-8")
        path.write_bytes(normalized_text.replace("\n", "\r\n").encode("utf-8"))

        code, output = self.run_cli(["docs", "find", "request key", "--root", str(root)])

        self.assertEqual(code, 0)
        self.assertNotIn("NEEDS_REVIEW", output)

    def test_only_changed_relevant_document_is_marked_needs_review(self) -> None:
        root = self.make_repo()
        self.initialize_catalog(root)
        self.add_doc(
            root,
            "checkpoint-retries",
            "docs/checkpoint-retries.md",
            "Safe checkpoint retries",
            "A request key makes retries idempotent.",
            "--keyword",
            "request key",
            "--task",
            "PCM-0001",
        )
        self.add_doc(
            root,
            "session-discovery",
            "docs/session-discovery.md",
            "Fresh session discovery",
            "Find prior decisions and linked records.",
            "--related",
            "checkpoint-retries",
        )
        (root / "docs" / "unrelated.md").write_text("An unrelated change.\n", encoding="utf-8")
        (root / "docs" / "checkpoint-retries.md").write_text(
            "# Safe checkpoint retries\n\nThe shared source changed after the recorded review.\n", encoding="utf-8"
        )

        code, output = self.run_cli(["docs", "find", "request key", "--root", str(root)])

        self.assertEqual(code, 0)
        self.assertIn("checkpoint-retries", output)
        self.assertIn("NEEDS_REVIEW", output)
        self.assertIn("session-discovery", output)
        self.assertIn("REMOTE_UNKNOWN", output)
        self.assertNotIn(" [CURRENT]", output)

        code, _ = self.run_cli(["docs", "render", "--root", str(root)])
        self.assertEqual(code, 0)
        self.assertEqual(validate_repo(root), [])

        code, _ = self.run_cli(["docs", "refresh", "checkpoint-retries", "--root", str(root)])
        self.assertEqual(code, 0)
        code, refreshed = self.run_cli(["docs", "find", "request key", "--root", str(root)])
        self.assertEqual(code, 0)
        self.assertNotIn("NEEDS_REVIEW", refreshed)

    def test_lookup_does_not_claim_remote_freshness_without_tracking_head(self) -> None:
        root = self.make_repo()
        self.initialize_catalog(root)
        self.add_doc(
            root,
            "checkpoint-retries",
            "docs/checkpoint-retries.md",
            "Safe checkpoint retries",
            "A request key makes retries idempotent.",
            "--keyword",
            "request key",
        )

        code, output = self.run_cli(["docs", "find", "request key", "--root", str(root)])

        self.assertEqual(code, 0)
        self.assertIn("REMOTE_TRACKING: unavailable", output)
        self.assertIn("MATCH checkpoint-retries [REMOTE_UNKNOWN]", output)

    def test_remote_content_check_survives_squash_merge_without_commit_ancestry(self) -> None:
        root = self.make_repo()
        source = b"# Reviewed document\n\nThe reviewed bytes remain authoritative.\n"
        (root / "docs" / "checkpoint-retries.md").write_bytes(source)
        record = {
            "path": "docs/checkpoint-retries.md",
            "reviewed_commit": "0" * 40,
            "reviewed_sha256": sha256_document_bytes(source),
        }
        remote_snapshot = subprocess.CompletedProcess(
            args=["git", "cat-file", "--batch"],
            returncode=0,
            stdout=b"a" * 40 + b" blob " + str(len(source)).encode("ascii") + b"\n" + source + b"\n",
            stderr=b"",
        )

        with patch("continuity.cli.subprocess.run", return_value=remote_snapshot) as run:
            remote_hashes = remote_document_hashes(root, "origin/main", [record["path"]])
            freshness, current_hash = document_freshness(
                root, record, include_remote=True, remote_hashes=remote_hashes
            )

        self.assertEqual(freshness, "CURRENT")
        self.assertEqual(current_hash, record["reviewed_sha256"])
        run.assert_called_once()

    def test_validate_rejects_a_human_index_that_drifted_from_manifest(self) -> None:
        root = self.make_repo()
        self.initialize_catalog(root)
        (root / "docs" / "CONTINUITY_INDEX.md").write_text("Manually diverged view.\n", encoding="utf-8")

        errors = validate_repo(root)

        self.assertTrue(any("generated document index is out of date" in error for error in errors), errors)

    def test_issue_b_remote_change_flags_issue_a_but_unrelated_change_does_not(self) -> None:
        root = self.make_repo()
        remote = Path(tempfile.mkdtemp(prefix="continuity-documents-remote-"))
        self.addCleanup(shutil.rmtree, remote, True)
        subprocess.run(["git", "init", "-q", "--bare", remote], check=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
        subprocess.run(["git", "-C", root, "config", "user.email", "fixture@example.invalid"], check=True)
        subprocess.run(["git", "-C", root, "config", "user.name", "Fixture"], check=True)
        subprocess.run(["git", "-C", root, "add", "."], check=True)
        subprocess.run(["git", "-C", root, "commit", "-qm", "source checkpoint"], check=True)
        subprocess.run(["git", "-C", root, "remote", "add", "origin", str(remote)], check=True)
        subprocess.run(["git", "-C", root, "push", "-q", "--set-upstream", "origin", "main"], check=True)
        subprocess.run(["git", "-C", root, "remote", "set-head", "origin", "main"], check=True)
        self.initialize_catalog(root)
        self.add_doc(
            root,
            "checkpoint-retries",
            "docs/checkpoint-retries.md",
            "Safe checkpoint retries",
            "A request key makes retries idempotent.",
            "--keyword",
            "request key",
            "--task",
            "PCM-0001",
        )
        subprocess.run(["git", "-C", root, "add", "."], check=True)
        inventory = json.loads((root / ".continuity" / "documents.json").read_text(encoding="utf-8"))
        reviewed_commit = inventory["documents"][0]["reviewed_commit"]
        subprocess.run(["git", "-C", root, "commit", "-qm", "register reviewed source"], check=True)
        subprocess.run(["git", "-C", root, "push", "-q"], check=True)
        subprocess.run(["git", "-C", root, "switch", "-q", "-c", "task/issue-a"], check=True)

        subprocess.run(["git", "-C", root, "switch", "-q", "main"], check=True)
        (root / "docs" / "unrelated.md").write_text("An unrelated change on issue B.\n", encoding="utf-8")
        subprocess.run(["git", "-C", root, "add", "docs/unrelated.md"], check=True)
        subprocess.run(["git", "-C", root, "commit", "-qm", "issue B changes an unrelated file"], check=True)
        subprocess.run(["git", "-C", root, "push", "-q"], check=True)
        subprocess.run(["git", "-C", root, "fetch", "-q", "origin"], check=True)
        subprocess.run(["git", "-C", root, "switch", "-q", "task/issue-a"], check=True)
        code, unrelated_output = self.run_cli(["docs", "find", "request key", "--root", str(root)])
        self.assertEqual(code, 0)
        self.assertIn("MATCH checkpoint-retries [CURRENT]", unrelated_output)

        subprocess.run(["git", "-C", root, "switch", "-q", "main"], check=True)
        (root / "docs" / "checkpoint-retries.md").write_text(
            "# Safe checkpoint retries\n\nIssue B changed the shared checkpoint protocol.\n", encoding="utf-8"
        )
        subprocess.run(["git", "-C", root, "add", "docs/checkpoint-retries.md"], check=True)
        subprocess.run(["git", "-C", root, "commit", "-qm", "issue B changes the shared file"], check=True)
        subprocess.run(["git", "-C", root, "push", "-q"], check=True)
        subprocess.run(["git", "-C", root, "fetch", "-q", "origin"], check=True)
        subprocess.run(["git", "-C", root, "switch", "-q", "task/issue-a"], check=True)
        code, shared_output = self.run_cli(["docs", "find", "request key", "--root", str(root)])

        self.assertEqual(code, 0)
        self.assertIn(f"REVIEWED_AT: {reviewed_commit}", shared_output)
        self.assertIn("MATCH checkpoint-retries [NEEDS_REVIEW]", shared_output)
        self.assertIn("git fetch origin", shared_output)

        subprocess.run(["git", "-C", root, "switch", "-q", "main"], check=True)
        subprocess.run(["git", "-C", root, "rm", "-q", "docs/checkpoint-retries.md"], check=True)
        subprocess.run(["git", "-C", root, "commit", "-qm", "issue B removes the shared file"], check=True)
        subprocess.run(["git", "-C", root, "push", "-q"], check=True)
        subprocess.run(["git", "-C", root, "fetch", "-q", "origin"], check=True)
        subprocess.run(["git", "-C", root, "switch", "-q", "task/issue-a"], check=True)
        code, deleted_output = self.run_cli(["docs", "find", "request key", "--root", str(root)])

        self.assertEqual(code, 0)
        self.assertIn("MATCH checkpoint-retries [NEEDS_REVIEW]", deleted_output)

    def test_task_context_pack_contains_only_declared_docs_and_exact_next_action(self) -> None:
        root = self.make_repo()
        self.initialize_catalog(root)
        self.add_doc(
            root,
            "session-discovery",
            "docs/session-discovery.md",
            "Fresh session discovery",
            "Find prior decisions and linked records.",
            "--task",
            "PCM-0001",
        )
        self.add_doc(
            root,
            "checkpoint-retries",
            "docs/checkpoint-retries.md",
            "Safe checkpoint retries",
            "A request key makes retries idempotent.",
            "--related",
            "session-discovery",
            "--task",
            "PCM-0001",
        )
        self.add_doc(
            root,
            "unrelated-release-note",
            "docs/unrelated.md",
            "Unrelated release note",
            "A record for another task.",
        )
        subprocess.run(["git", "init", "-q", "-b", "task/PCM-0001-pack"], cwd=root, check=True)
        subprocess.run(["git", "-C", root, "config", "user.email", "fixture@example.invalid"], check=True)
        subprocess.run(["git", "-C", root, "config", "user.name", "Fixture"], check=True)
        subprocess.run(["git", "-C", root, "add", "."], check=True)
        subprocess.run(["git", "-C", root, "commit", "-qm", "fixture with document catalog"], check=True)

        code, output = self.run_cli(["pack", "PCM-0001", "--root", str(root)])
        self.assertEqual(code, 0, output)
        pack = (root / ".continuity" / "packs" / "PCM-0001.md").read_text(encoding="utf-8")
        metadata_line = next(line for line in pack.splitlines() if "continuity:context-pack" in line)
        metadata = json.loads(metadata_line.split("continuity:context-pack ", 1)[1].removesuffix(" -->"))

        self.assertIn("docs/checkpoint-retries.md", metadata["sources"])
        self.assertIn("docs/session-discovery.md", metadata["sources"])
        self.assertNotIn("docs/unrelated.md", metadata["sources"])
        self.assertIn("run validation", pack)
        self.assertIn("SHA-256", pack)
        self.assertIn("review status `REMOTE_UNKNOWN`", pack)


if __name__ == "__main__":
    unittest.main()
