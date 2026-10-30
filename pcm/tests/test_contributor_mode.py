"""Contributor mode, first slice (#247 / PCM issue 247): the leak guard and
the task descriptor.

Problem and consequence: the stack's install surfaces (PCM init, OIO's
installer, ACS's hotload pack) all write into the repository being worked on.
For a repository the worker does not administer, that is impossible — and the
workaround (hand-installing artifacts into the foreign checkout) risks stack
paths landing in an upstream pull request, which is externally visible and
unfixable after merge without upstream cooperation.

Two promises are checked here, both offline:

1. **The leak guard fails closed.** Given a foreign checkout's Git status,
   every stack-owned path (PCM, OIO, ACS, CGM install surfaces) is reported as
   a leak in every state — staged, unstaged, untracked — while an ordinary
   clean tree passes. A guard that cannot run is a failure, never a clean
   result: a non-repository root raises instead of returning empty.
2. **The descriptor round-trips on the owner's side of the boundary.** The
   minimal task identity — upstream ``owner/repo``, the anchoring upstream
   SHA, the private sidecar location — writes to the store root, reads back
   field-for-field, refuses to be written inside the guarded foreign checkout,
   and fails closed on malformed or partial JSON rather than resolving to a
   plausible-looking stale record.

The private sidecar repository, journal/checkpoint storage inside it, the
coordination database, and the cross-repo index are deliberately out of scope:
the upstream issue is an explicit proposal and this is its first slice.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from shutil import rmtree

from continuity.cli import (
    ContinuityError,
    foreign_leak_findings,
    load_contributor_descriptor,
    main,
    write_contributor_descriptor,
)
from continuity.contributor import (
    ANCHOR_KINDS,
    STACK_PATHS,
    leak_findings,
    parse_contributor_descriptor,
    render_contributor_descriptor,
    stack_path_for,
)

FULL_SHA = "1" * 40
OTHER_SHA = "2" * 40


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)


def foreign_repo() -> Path:
    """A minimal clean upstream-style repository: one committed file."""
    root = Path(tempfile.mkdtemp(prefix="continuity-contributor-"))
    git(root, "init", "-q")
    git(root, "config", "user.name", "Upstream")
    git(root, "config", "user.email", "upstream@example.invalid")
    (root / "README.md").write_text("# upstream project\n", encoding="utf-8")
    git(root, "add", "--", "README.md")
    git(root, "commit", "-qm", "initial upstream state")
    return root


class StackPathSetTests(unittest.TestCase):
    def test_every_component_surface_is_listed(self) -> None:
        # PCM, OIO, ACS, CGM — one representative path per install surface.
        expected = {
            ".continuity", "schemas/v1", ".github/ISSUE_TEMPLATE/task.md", ".github/pull_request_template.md",
            ".oio", ".github/ISSUE_TEMPLATE/observational-issue.yml", ".github/workflows/issue-triage.yml",
            "AGENTS.md", ".coord", "stack-manifest.json", ".content-system",
        }
        self.assertEqual(set(STACK_PATHS), expected)

    def test_a_path_under_a_directory_prefix_matches_its_prefix(self) -> None:
        self.assertEqual(stack_path_for(".coord/assignment.json"), ".coord")
        self.assertEqual(stack_path_for(".continuity/packs/x.json"), ".continuity")
        self.assertIsNone(stack_path_for("src/main.py"))
        self.assertIsNone(stack_path_for(".github/workflows/their-own-ci.yml"))

    def test_an_exact_file_entry_matches_itself_and_children(self) -> None:
        self.assertEqual(stack_path_for("stack-manifest.json"), "stack-manifest.json")
        self.assertEqual(stack_path_for("AGENTS.md"), "AGENTS.md")
        self.assertIsNone(stack_path_for("docs/AGENTS.md"))

    def test_rename_entries_are_judged_by_destination(self) -> None:
        self.assertEqual(stack_path_for("old.txt -> .oio/ontology/default.json"), ".oio")
        self.assertIsNone(stack_path_for(".oio/old -> docs/notes.md"))


class LeakFindingsContractTests(unittest.TestCase):
    def test_staged_unstaged_and_untracked_are_all_leaks(self) -> None:
        status = "\n".join(
            [
                "A  .coord/assignment.json",
                " M .oio/ontology/default.json",
                "?? .continuity/config.json",
                "?? .content-system/asset-manifest.json",
                "A  stack-manifest.json",
            ]
        )
        findings = leak_findings(status)
        self.assertEqual(len(findings), 5)
        for finding in findings:
            self.assertIn("stack-owned path", finding)

    def test_untracked_directory_is_expanded_by_the_guard_not_guessed(self) -> None:
        # The CLI runs --untracked-files=all so a directory leak names files.
        findings = leak_findings("?? .coord/watchdog.json")
        self.assertEqual(len(findings), 1)
        self.assertIn(".coord/watchdog.json", findings[0])

    def test_ordinary_changes_and_ignored_entries_are_not_leaks(self) -> None:
        status = "\n".join(
            [
                " M src/main.py",
                "?? docs/notes.md",
                "!! .oio/local-scratch.json",
                "A  .github/workflows/upstream-own.yml",
            ]
        )
        self.assertEqual(leak_findings(status), [])

    def test_an_unparseable_status_line_is_a_leak_not_silence(self) -> None:
        findings = leak_findings("garbage line")
        self.assertEqual(len(findings), 1)
        self.assertIn("treated as a leak", findings[0])


class ForeignLeakGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = foreign_repo()

    def tearDown(self) -> None:
        rmtree(self.root, ignore_errors=True)

    def test_clean_foreign_tree_is_clean(self) -> None:
        self.assertEqual(foreign_leak_findings(self.root), [])

    def test_each_stack_path_class_fails_the_guard(self) -> None:
        (self.root / ".coord").mkdir()
        (self.root / ".coord" / "assignment.json").write_text("{}", encoding="utf-8")
        git(self.root, "add", "--", ".coord")
        (self.root / ".oio").mkdir()
        (self.root / ".oio" / "ontology").mkdir()
        (self.root / ".oio" / "ontology" / "default.json").write_text("{}", encoding="utf-8")  # unstaged
        (self.root / ".continuity").mkdir()
        (self.root / ".continuity" / "config.json").write_text("{}", encoding="utf-8")  # untracked
        (self.root / ".content-system").mkdir()
        (self.root / ".content-system" / "asset-manifest.json").write_text("{}", encoding="utf-8")
        findings = foreign_leak_findings(self.root)
        assert findings is not None
        self.assertEqual(len(findings), 4)
        joined = "\n".join(findings)
        self.assertIn(".coord/assignment.json", joined)
        self.assertIn(".oio/ontology/default.json", joined)
        self.assertIn(".continuity/config.json", joined)
        self.assertIn(".content-system/asset-manifest.json", joined)

    def test_a_gitignored_stack_path_is_still_a_leak(self) -> None:
        (self.root / ".gitignore").write_text(".coord/\n", encoding="utf-8")
        git(self.root, "add", "--", ".gitignore")
        git(self.root, "commit", "-qm", "upstream adds an ignore rule")
        (self.root / ".coord").mkdir()
        (self.root / ".coord" / "assignment.json").write_text("{}", encoding="utf-8")
        findings = foreign_leak_findings(self.root)
        assert findings is not None
        self.assertEqual(len(findings), 1)
        self.assertIn("is ignored in the foreign checkout", findings[0])

    def test_a_renamed_file_into_a_stack_path_is_a_leak(self) -> None:
        git(self.root, "mv", "README.md", "stack-manifest.json")
        findings = foreign_leak_findings(self.root)
        assert findings is not None
        self.assertEqual(len(findings), 1)
        self.assertIn("stack-manifest.json", findings[0])

    def test_a_non_repository_root_fails_closed(self) -> None:
        not_a_repo = Path(tempfile.mkdtemp(prefix="continuity-not-a-repo-"))
        with self.assertRaises(ContinuityError):
            foreign_leak_findings(not_a_repo)

    def test_upstreams_own_committed_stack_paths_are_not_our_leak(self) -> None:
        # The upstream repository may itself be a stack adopter. Committed
        # content is upstream's business; the guard polices the working tree.
        (self.root / ".oio").mkdir()
        (self.root / ".oio" / "ontology").mkdir()
        (self.root / ".oio" / "ontology" / "default.json").write_text("{}", encoding="utf-8")
        git(self.root, "add", "--", ".oio")
        git(self.root, "commit", "-qm", "upstream adopts OIO")
        self.assertEqual(foreign_leak_findings(self.root), [])

    def test_guard_cli_exits_one_on_leak_and_zero_on_clean(self) -> None:
        self.assertEqual(main(["contributor", "guard", "--root", str(self.root)]), 0)
        (self.root / ".oio").mkdir()
        (self.root / ".oio" / "f").write_text("x", encoding="utf-8")
        self.assertEqual(main(["contributor", "guard", "--root", str(self.root)]), 1)


class ContributorDescriptorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = Path(tempfile.mkdtemp(prefix="continuity-sidecar-"))
        self.foreign = foreign_repo()

    def tearDown(self) -> None:
        for path in (self.store, self.foreign):
            rmtree(path, ignore_errors=True)

    def test_descriptor_round_trips(self) -> None:
        for anchor_kind in ANCHOR_KINDS:
            with self.subTest(anchor=anchor_kind):
                store = Path(tempfile.mkdtemp(prefix="continuity-sidecar-"))
                write_contributor_descriptor(
                    store, self.foreign, "upstream/project", FULL_SHA, anchor_kind, "D:/sidecar/home"
                )
                fields = load_contributor_descriptor(store)
                self.assertEqual(fields["repository"], "upstream/project")
                self.assertEqual(fields["anchor_sha"], FULL_SHA)
                self.assertEqual(fields["anchor_kind"], anchor_kind)
                self.assertEqual(fields["sidecar"], "D:/sidecar/home")
                self.assertEqual(fields["schema"], "project-continuity.contributor.v1")

    def test_render_parse_round_trip(self) -> None:
        text = render_contributor_descriptor("u/p", FULL_SHA, "pr", "D:/s")
        self.assertEqual(parse_contributor_descriptor(text), {
            "schema": "project-continuity.contributor.v1",
            "repository": "u/p",
            "anchor_kind": "pr",
            "anchor_sha": FULL_SHA,
            "sidecar": "D:/s",
        })

    def test_write_refuses_a_store_root_inside_the_foreign_checkout(self) -> None:
        with self.assertRaises(ContinuityError):
            write_contributor_descriptor(self.foreign, self.foreign, "u/p", FULL_SHA, "pr", "D:/s")
        nested = self.foreign / "sub"
        nested.mkdir()
        with self.assertRaises(ContinuityError):
            write_contributor_descriptor(nested, self.foreign, "u/p", FULL_SHA, "pr", "D:/s")

    def test_conflicting_rewrite_is_refused_and_identical_rewrite_is_idempotent(self) -> None:
        write_contributor_descriptor(self.store, self.foreign, "u/p", FULL_SHA, "pr", "D:/s")
        write_contributor_descriptor(self.store, self.foreign, "u/p", FULL_SHA, "pr", "D:/s")  # idempotent
        with self.assertRaises(ContinuityError):
            write_contributor_descriptor(self.store, self.foreign, "u/q", OTHER_SHA, "commit", "D:/t")

    def test_malformed_partial_and_unknown_schema_descriptors_fail_closed(self) -> None:
        path = self.store / "contributor.json"

        def document(**overrides: object) -> str:
            payload: dict[str, object] = {
                "schema": "project-continuity.contributor.v1",
                "repository": "u/p",
                "anchor_kind": "pr",
                "anchor_sha": FULL_SHA,
                "sidecar": "D:/s",
            }
            payload.update(overrides)
            return json.dumps(payload)

        bad_documents = {
            "not json": "not json",
            "partial": '{"schema": "project-continuity.contributor.v1"}',
            "unknown schema": document(schema="other.v9"),
            "short sha": document(anchor_sha="short"),
            "bad repository slug": document(repository="not a slug"),
            "empty sidecar": document(sidecar=""),
            "extra field": document(extra=1),
            "non-string field": document(**{"repository": 5}),
            "json array": "[]",
        }
        for label, bad in bad_documents.items():
            with self.subTest(bad=label):
                path.write_text(bad, encoding="utf-8")
                with self.assertRaises(ContinuityError):
                    load_contributor_descriptor(self.store)

    def test_describe_cli_writes_on_the_owner_side(self) -> None:
        code = main([
            "contributor", "describe",
            "--root", str(self.store),
            "--foreign-root", str(self.foreign),
            "--repo", "upstream/project",
            "--anchor-sha", FULL_SHA,
            "--anchor", "commit",
            "--sidecar", "D:/sidecar/home",
        ])
        self.assertEqual(code, 0)
        self.assertEqual(load_contributor_descriptor(self.store)["anchor_kind"], "commit")


if __name__ == "__main__":
    unittest.main()
