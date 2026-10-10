from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".github/scripts"))

import oio_installer  # noqa: E402
from oio_installer import InstallError, _TargetFS, _recover_transaction, install, priority_key, validate_project_ontology  # noqa: E402
from oio_triage import _resolve_attestation, classify_issue, priority_label  # noqa: E402


class OntologyTests(unittest.TestCase):
    def setUp(self):
        self.core = json.loads((ROOT / "ontology/default.json").read_text())
        self.project = json.loads((ROOT / "ontology/oio-project.json").read_text())

    def test_default_ontology_matches_schema(self):
        from jsonschema import Draft202012Validator

        schema = json.loads((ROOT / "schemas/v1/default-ontology.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.core)

    def test_project_ontology_validates_with_project_namespaces(self):
        validate_project_ontology(self.project, core=self.core)

    def test_hierarchical_priority_is_not_a_float(self):
        values = ["1.2", "1.10", "1", "2", "100"]
        self.assertEqual(sorted(values, key=priority_key), ["1", "1.2", "1.10", "2", "100"])
        for invalid in ["0", "01", "1.0", "1.01", "1..2", "1e2", "101"]:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                priority_key(invalid)
        deep = "1" + ".1" * 40
        self.assertLessEqual(len(priority_label(deep)), 50)
        self.assertTrue(priority_label(deep).startswith("priority:ref-"))

    def test_project_priority_requires_declared_parent_and_unique_path(self):
        project = json.loads(json.dumps(self.project))
        project["priorities"].append({"path": "6.1", "concept_id": "oio-project:priority-6-1", "label": "Child", "definition": "Child"})
        with self.assertRaisesRegex(InstallError, "undefined parent"):
            validate_project_ontology(project, core=self.core)

    def test_extension_version_compatibility_is_explicit(self):
        compatible_core = json.loads(json.dumps(self.core))
        compatible_core["version"] = "1.1.0"
        compatible_core["compatible_project_ontology_versions"] = ["1.0.0"]
        validate_project_ontology(self.project, core=compatible_core)
        compatible_core["compatible_project_ontology_versions"] = []
        with self.assertRaisesRegex(InstallError, "must extend"):
            validate_project_ontology(self.project, core=compatible_core)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name) / "adopter"
        self.target.mkdir()
        subprocess.run(["git", "init", "-q", str(self.target)], check=True)
        subprocess.run(["git", "-C", str(self.target), "remote", "add", "origin", "https://github.com/example/adopter.git"], check=True)
        (self.target / "AGENTS.md").write_text("# Existing adopter rules\n\nKeep this paragraph.\n")

    def tree(self):
        return {str(path.relative_to(self.target)).replace("\\", "/"): path.read_bytes() for path in self.target.rglob("*") if path.is_file() and ".git" not in path.parts}

    def make_dir_link(self, link, target):
        """Create a directory link: a symlink, or a Windows junction where symlinks need privilege."""
        try:
            os.symlink(target, link, target_is_directory=True)
        except (OSError, NotImplementedError):
            if sys.platform != "win32":
                raise
            import _winapi

            _winapi.CreateJunction(str(target), str(link))
        self.addCleanup(self._remove_dir_link, link)

    @staticmethod
    def _remove_dir_link(link):
        if link.is_symlink():
            link.unlink()
        elif link.exists():
            os.rmdir(link)

    def test_fresh_and_repeat_install_are_confined_and_preserve_extension(self):
        before = set(self.tree())
        install(str(self.target))
        after_first = self.tree()
        added = set(after_first) - before
        allowed = set(__import__("oio_installer").PACKAGE_FILES) | {
            "AGENTS.md", ".oio/ontology/project.json", ".oio/install-manifest.json"
        }
        self.assertEqual(added, allowed - before)
        self.assertIn("Keep this paragraph.", after_first["AGENTS.md"].decode())
        project_file = self.target / ".oio/ontology/project.json"
        project = json.loads(project_file.read_text())
        self.assertEqual(len(project["priorities"]), 100)
        self.assertEqual(project["priorities"][0]["concept_id"], "example-adopter:priority-1")
        project["priorities"] = [{"path": "1", "concept_id": "adopter:top", "label": "Top", "definition": "Top priority"}]
        project["namespace"] = "adopter"
        project["concepts"] = []
        project_file.write_text(json.dumps(project, indent=2) + "\n")
        project_before = project_file.read_bytes()
        self.assertIn("VALID", " ".join(install(str(self.target), check_only=True)))
        install(str(self.target))
        self.assertEqual(project_file.read_bytes(), project_before)
        project_file.unlink()
        with self.assertRaisesRegex(InstallError, "project ontology is missing"):
            install(str(self.target), check_only=True)

    def test_installed_copy_can_check_its_target(self):
        install(str(self.target))
        script = self.target / ".github/scripts/oio_installer.py"
        result = subprocess.run([sys.executable, str(script), "--target", str(self.target), "--check"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("VALID: OIO package", result.stdout)

    def test_digit_starting_owner_gets_valid_project_namespace(self):
        target = Path(self.temp.name) / "numeric-owner"
        target.mkdir()
        subprocess.run(["git", "init", "-q", str(target)], check=True)
        install(str(target), "123owner/repository")
        project = json.loads((target / ".oio/ontology/project.json").read_text())
        self.assertEqual(project["namespace"], "project-123owner-repository")
        validate_project_ontology(project)

    def test_unmanaged_collision_refuses_without_other_writes(self):
        collision = self.target / ".github/ISSUE_TEMPLATE/observational-issue.yml"
        collision.parent.mkdir(parents=True)
        collision.write_text("adopter-owned\n")
        before = self.tree()
        with self.assertRaisesRegex(InstallError, "unmanaged file already exists"):
            install(str(self.target))
        self.assertEqual(self.tree(), before)

    def test_modified_managed_file_refuses_without_overwriting(self):
        install(str(self.target))
        managed = self.target / ".oio/ontology/default.json"
        managed.write_text("adopter edit\n")
        before = self.tree()
        with self.assertRaisesRegex(InstallError, "managed file changed"):
            install(str(self.target))
        self.assertEqual(self.tree(), before)

    def test_install_writes_lf_canonical_bytes_and_hashes_them(self):
        install(str(self.target))
        source = (ROOT / "ontology/default.json").read_bytes()
        expected = source.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        installed = (self.target / ".oio/ontology/default.json").read_bytes()
        self.assertNotIn(b"\r\n", installed)
        self.assertEqual(installed, expected)
        manifest = json.loads((self.target / ".oio/install-manifest.json").read_text())
        self.assertEqual(manifest["managed_files"][".oio/ontology/default.json"], hashlib.sha256(installed).hexdigest())

    def test_check_passes_after_an_lf_checkout_normalizes_the_worktree(self):
        install(str(self.target))
        for relative in list(oio_installer.PACKAGE_FILES) + ["AGENTS.md"]:
            path = self.target / relative
            if path.exists():
                path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
        result = " ".join(install(str(self.target), check_only=True))
        self.assertIn("VALID", result)

    def test_eol_only_difference_is_reported_not_refused(self):
        install(str(self.target))
        managed = self.target / ".oio/ontology/default.json"
        managed.write_bytes(managed.read_bytes().replace(b"\n", b"\r\n"))
        result = " ".join(install(str(self.target), check_only=True))
        self.assertIn("VALID", result)
        self.assertIn("line endings differ", result)

    def test_legacy_crlf_digest_manifest_migrates_without_deleting_the_install(self):
        install(str(self.target))
        manifest_path = self.target / ".oio/install-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        for relative in list(manifest["managed_files"]):
            managed = self.target / relative
            crlf = managed.read_bytes().replace(b"\n", b"\r\n")
            managed.write_bytes(crlf)
            manifest["managed_files"][relative] = hashlib.sha256(crlf).hexdigest()
        manifest_path.write_text(json.dumps(manifest, indent=2))
        install(str(self.target))
        self.assertNotIn(b"\r\n", (self.target / ".oio/ontology/default.json").read_bytes())
        self.assertIn("VALID", " ".join(install(str(self.target), check_only=True)))

    def test_content_edit_under_crlf_is_still_refused(self):
        install(str(self.target))
        managed = self.target / ".oio/ontology/default.json"
        managed.write_bytes(managed.read_bytes().replace(b"\n", b"\r\n") + b"\r\n")
        with self.assertRaisesRegex(InstallError, "managed file changed"):
            install(str(self.target))

    def test_agents_block_in_a_crlf_worktree_is_not_treated_as_an_edit(self):
        install(str(self.target))
        agents = self.target / "AGENTS.md"
        agents.write_bytes(agents.read_bytes().replace(b"\n", b"\r\n"))
        install(str(self.target))

    def test_symlink_target_path_is_refused(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        self.make_dir_link(self.target / ".oio", outside)
        with self.assertRaisesRegex(InstallError, "symlink"):
            install(str(self.target))
        self.assertEqual(list(outside.iterdir()), [])

    def test_symlinks_in_managed_directories_are_refused_without_outside_writes(self):
        for relative in [".github/ISSUE_TEMPLATE", ".github/workflows", ".github/scripts", ".oio/ontology"]:
            with self.subTest(relative=relative):
                shutil.rmtree(self.target / ".github", ignore_errors=True)
                shutil.rmtree(self.target / ".oio", ignore_errors=True)
                outside = Path(self.temp.name) / ("outside-" + relative.replace("/", "-"))
                outside.mkdir()
                path = self.target / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                self.make_dir_link(path, outside)
                outside_before = {str(p): p.read_bytes() for p in outside.rglob("*") if p.is_file()}
                with self.assertRaisesRegex(InstallError, "symlink"):
                    install(str(self.target))
                self.assertEqual({str(p): p.read_bytes() for p in outside.rglob("*") if p.is_file()}, outside_before)
                self._remove_dir_link(path)

    def test_directory_swap_to_symlink_during_install_cannot_redirect_write(self):
        target = self.target
        managed_parent = target / ".oio/ontology"
        managed_parent.mkdir(parents=True)
        outside = Path(self.temp.name) / "race-outside"
        outside.mkdir()
        sentinel = outside / "default.json"
        sentinel.write_text("outside sentinel")
        moved = outside / "ontology-opened"

        def swap_after_open(root, relative):
            if relative == ".oio/ontology/default.json":
                managed_parent.rename(moved)
                self.make_dir_link(managed_parent, outside)

        with mock.patch("oio_installer._after_parent_open", side_effect=swap_after_open):
            with _TargetFS(target) as target_fs, self.assertRaises((InstallError, OSError)):
                target_fs.atomic_write(".oio/ontology/default.json", b"attacker-controlled target")
        self.assertEqual(sentinel.read_text(), "outside sentinel")
        self.assertEqual(list(moved.iterdir()), [])

    def test_directory_swap_to_symlink_during_recovery_cannot_redirect_write(self):
        target = self.target
        managed_parent = target / ".oio/ontology"
        managed_parent.mkdir(parents=True)
        outside = Path(self.temp.name) / "recovery-outside"
        outside.mkdir()
        sentinel = outside / "default.json"
        sentinel.write_text("outside sentinel")
        managed_file = managed_parent / "default.json"
        planned = b"installed bytes"
        managed_file.write_bytes(planned)
        journal = target / ".oio/.installer-transaction.json"
        journal.write_text(json.dumps({
            "schema_version": "oio.installer-transaction.v1",
            "entries": {
                ".oio/ontology/default.json": {
                    "before": __import__("base64").b64encode(b"previous bytes").decode(),
                    "planned_sha256": __import__("hashlib").sha256(planned).hexdigest(),
                }
            },
        }))
        moved = outside / "ontology-opened"

        def swap_after_open(root, relative):
            if relative == ".oio/ontology/default.json":
                managed_parent.rename(moved)
                self.make_dir_link(managed_parent, outside)

        with mock.patch("oio_installer._after_parent_open", side_effect=swap_after_open):
            with _TargetFS(target) as target_fs, self.assertRaises((InstallError, OSError)):
                _recover_transaction(target, target_fs)
        self.assertEqual(sentinel.read_text(), "outside sentinel")
        self.assertEqual((moved / "default.json").read_bytes(), planned)
        self.assertTrue(journal.exists(), "recovery journal stays for a safe retry after path tampering")

    def test_interrupted_install_recovers_before_retry(self):
        before = self.tree()
        with mock.patch.dict(os.environ, {"OIO_INSTALL_TEST_INTERRUPT_AFTER": "2"}):
            with self.assertRaises(SystemExit):
                install(str(self.target))
        journal = self.target / ".oio/.installer-transaction.json"
        self.assertTrue(journal.exists())
        os.environ.pop("OIO_INSTALL_TEST_INTERRUPT_AFTER", None)
        install(str(self.target))
        self.assertFalse(journal.exists())
        self.assertTrue((self.target / ".oio/install-manifest.json").exists())
        for rel, data in before.items():
            if rel != "AGENTS.md":
                self.assertEqual((self.target / rel).read_bytes(), data)
        self.assertIn("Keep this paragraph.", (self.target / "AGENTS.md").read_text())
        self.assertIn("oio:issue-log-guidance:start", (self.target / "AGENTS.md").read_text())

    def test_recovery_refuses_human_edit_after_interruption(self):
        with mock.patch.dict(os.environ, {"OIO_INSTALL_TEST_INTERRUPT_AFTER": "2"}):
            with self.assertRaises(SystemExit):
                install(str(self.target))
        managed = self.target / "AGENTS.md"
        managed.write_text("human edit after interruption\n")
        installer_file = self.target / ".oio/ontology/default.json"
        self.assertTrue(installer_file.exists())
        with self.assertRaisesRegex(InstallError, "recovery conflict"):
            install(str(self.target))
        self.assertEqual(managed.read_text(), "human edit after interruption\n")
        self.assertTrue(installer_file.exists(), "recovery conflict must be detected before any rollback writes")

    def test_recovery_rejects_journal_path_outside_allow_list(self):
        (self.target / ".oio").mkdir(exist_ok=True)
        journal = self.target / ".oio/.installer-transaction.json"
        victim = self.target / "README.md"
        victim.write_text("adopter-owned\n")
        before = victim.read_bytes()
        journal.write_text(json.dumps({"schema_version": "oio.installer-transaction.v1", "entries": {
            "README.md": {"before": None, "planned_sha256": "0" * 64}
        }}))
        with self.assertRaisesRegex(InstallError, "outside the OIO-managed allow-list"):
            install(str(self.target))
        self.assertEqual(victim.read_bytes(), before)


class TriageTests(unittest.TestCase):
    def setUp(self):
        self.project = json.loads((ROOT / "ontology/oio-project.json").read_text())

    def make_issue(self, origin="agent-proposed", path="5", concept="oio-project:priority-5", auth_state="claimed", director_id="not-applicable"):
        body = f"""### Issue Type
observational

### Filer Origin (who initiated this filing)
{origin}

### Filing Authorization Evidence
{auth_state}

### Session, Authorization Evidence, and Instruction Reference
Session reference: session-123; instruction reference: test prompt; authorization evidence: claimed

### Content Author Account or Runtime Identity
agent:codex/session-123

### Directing Human GitHub Account ID
{director_id}

### Destination Repository
Pukujan/observational-issue-ops

### Ontology Versions Used
oio=1.0.0; project=1.0.0

### Project Priority Path
{path}

### Project Priority Concept ID
{concept}

### Affected App, Adopter, Users, or Systems
OIO repository contributors

### Observed Consequence and Workaround
Priority display is ambiguous; use owner review.

### Impact if Unresolved
moderate

### Likelihood
observed

### Exposure
limited-test-or-preview

### Exposure Duration
unknown

### Recoverability
manual-recovery

### Recovery Evidence
No automated recovery; owner can correct the issue metadata.

### Risk if the Observation Remains Unresolved
Project queue may be misleading.

### Risk Introduced by a Proposed Change
not assessed

### Evidence Confidence
confirmed

### Product or Release Relevance
affects

### Named Product Outcome and Cost of Delay
Reliable issue intake; see issue #17.

### Cost of Delay
May delay triage.

### Smallest Useful Product Slice
Correct the filing and check classification.
"""
        return {"body": body, "labels": [{"name": "observational-issue"}], "user": {"id": 137629468, "login": "Pukujan"}, "created_at": "2026-10-03T12:00:00Z"}

    def test_queue_class_account_and_project_priority_are_separate_labels(self):
        issue = self.make_issue()
        decision = classify_issue(issue, ROOT)
        self.assertIn("queue:class-3", decision["labels"])
        self.assertIn("account:owner", decision["labels"])
        self.assertIn("priority:5", decision["labels"])
        self.assertIn("release:affects", decision["labels"])
        self.assertIn("queue:class-3:account-01", decision["labels"])
        self.assertIn("authorization:claimed", decision["labels"])
        self.assertIn("review:product-outcome-review", decision["labels"])
        self.assertEqual(decision["record"]["ontology"], {"default_version": "1.0.0", "project_version": "1.0.0"})
        self.assertNotIn("needs-record-schema", decision["labels"])

    def test_authenticated_human_account_controls_human_queue_rank(self):
        issue = self.make_issue(origin="human-direct", auth_state="verified")
        event = {"oio_attestation": {"label": "oio-auth:human-direct", "actor": {"id": 137629468, "login": "Pukujan"}, "event_id": "17", "body_sha256": "abc"}}
        decision = classify_issue(issue, ROOT, event=event)
        self.assertIn("queue:class-1:account-01", decision["labels"])
        self.assertIn("authorization:verified-account-attestation", decision["labels"])
        self.assertIn("oio-auth:human-direct", decision["labels"])
        issue["user"] = {"id": 987654321, "login": "unknown-agent"}
        decision = classify_issue(issue, ROOT)
        self.assertIn("queue:class-3:account-99", decision["labels"])
        self.assertIn("needs-account-review", decision["labels"])

    def test_unknown_priority_is_not_silently_clamped(self):
        decision = classify_issue(self.make_issue(path="6", concept="oio-project:priority-6"), ROOT)
        self.assertIn("needs-priority-definition", decision["labels"])
        self.assertNotIn("priority:6", decision["labels"])
        self.assertEqual(decision["record"]["priority"], {"status": "unresolved", "path": None, "concept_id": None})

    def test_record_schema_forbids_resolved_priority_without_rank(self):
        from jsonschema import Draft202012Validator

        schema = json.loads((ROOT / "schemas/v1/issue-log-record.schema.json").read_text())
        decision = classify_issue(self.make_issue(path="6", concept="oio-project:priority-6"), ROOT)
        Draft202012Validator(schema).validate(decision["record"])
        invalid = json.loads(json.dumps(decision["record"]))
        invalid["priority"]["status"] = "resolved"
        with self.assertRaises(Exception):
            Draft202012Validator(schema).validate(invalid)

    def test_human_via_agent_needs_authenticated_directing_account(self):
        verified = classify_issue(self.make_issue(origin="human-via-agent", auth_state="verified", director_id="137629468"), ROOT)
        self.assertIn("queue:class-3", verified["labels"])
        claimed = classify_issue(self.make_issue(origin="human-via-agent", auth_state="claimed", director_id="137629468"), ROOT)
        self.assertIn("queue:class-3", claimed["labels"])
        self.assertIn("needs-human-verification", claimed["labels"])

    def test_human_via_agent_requires_separate_authorized_github_attestation(self):
        issue = self.make_issue(origin="human-via-agent", director_id="137629468")
        issue["user"] = {"id": 987654321, "login": "agent-service"}
        event = {"oio_attestation": {"label": "oio-auth:human-via-agent", "actor": {"id": 137629468, "login": "Pukujan"}, "event_id": "18", "body_sha256": "def"}}
        decision = classify_issue(issue, ROOT, event=event)
        self.assertIn("authorization:verified-account-attestation", decision["labels"])
        self.assertIn("queue:class-2:account-01", decision["labels"])

    def test_human_attestation_is_durable_and_bound_to_exact_body(self):
        issue = self.make_issue(origin="human-direct", auth_state="verified")
        issue["number"] = 42
        issue["labels"].append({"name": "oio-auth:human-direct"})
        actor = {"id": 137629468, "login": "Pukujan"}
        history = [{"id": 9981, "event": "labeled", "label": {"name": "oio-auth:human-direct"}, "actor": actor, "created_at": "2026-10-03T12:01:00Z"}]
        api = mock.Mock(return_value=(201, {"id": 10}))
        with mock.patch("oio_triage._get_pages", side_effect=[history, []]), mock.patch("oio_triage._api", api):
            attestation = _resolve_attestation(issue, {"action": "labeled", "label": {"name": "oio-auth:human-direct"}, "issue": issue}, self.project, "token", "example/repo")
        self.assertEqual(attestation["event_id"], "9981")
        self.assertEqual(attestation["actor"], actor)
        self.assertEqual(api.call_args.args[1], "POST")
        self.assertIn("body_sha256=", api.call_args.args[3]["body"])

    def test_durable_attestation_is_reused_on_later_unrelated_event(self):
        issue = self.make_issue(origin="human-direct", auth_state="verified")
        issue["number"] = 42
        issue["labels"].append({"name": "oio-auth:human-direct"})
        actor = {"id": 137629468, "login": "Pukujan"}
        history = [{"id": 9981, "event": "labeled", "label": {"name": "oio-auth:human-direct"}, "actor": actor, "created_at": "2026-10-03T12:01:00Z"}]
        digest = __import__("hashlib").sha256(issue["body"].encode()).hexdigest()
        comments = [{"body": f"<!-- oio-account-attestation:v1 issue=42 event=9981 label=oio-auth:human-direct body_sha256={digest} -->", "user": {"login": "github-actions[bot]"}}]
        with mock.patch("oio_triage._get_pages", side_effect=[history, comments]), mock.patch("oio_triage._api") as api:
            attestation = _resolve_attestation(issue, {"action": "edited", "issue": issue}, self.project, "token", "example/repo")
        self.assertEqual(attestation["event_id"], "9981")
        api.assert_not_called()

    def test_human_via_agent_attestation_resolves_directing_human_field(self):
        issue = self.make_issue(origin="human-via-agent", director_id="137629468")
        issue["number"] = 43
        issue["user"] = {"id": 987654321, "login": "agent-service"}
        issue["labels"].append({"name": "oio-auth:human-via-agent"})
        actor = {"id": 137629468, "login": "Pukujan"}
        history = [{"id": 9982, "event": "labeled", "label": {"name": "oio-auth:human-via-agent"}, "actor": actor, "created_at": "2026-10-03T12:01:00Z"}]
        with mock.patch("oio_triage._get_pages", side_effect=[history, []]), mock.patch("oio_triage._api", return_value=(201, {})):
            attestation = _resolve_attestation(issue, {"action": "labeled", "label": {"name": "oio-auth:human-via-agent"}, "issue": issue}, self.project, "token", "example/repo")
        self.assertEqual(attestation["actor"], actor)

    def test_same_second_label_reapplication_uses_later_event_id(self):
        issue = self.make_issue(origin="human-direct", auth_state="verified")
        issue["number"] = 44
        issue["labels"].append({"name": "oio-auth:human-direct"})
        old_actor = {"id": 123456, "login": "outsider"}
        owner = {"id": 137629468, "login": "Pukujan"}
        history = [
            {"id": 101, "event": "labeled", "label": {"name": "oio-auth:human-direct"}, "actor": old_actor, "created_at": "2026-10-03T12:01:00Z"},
            {"id": 102, "event": "unlabeled", "label": {"name": "oio-auth:human-direct"}, "actor": old_actor, "created_at": "2026-10-03T12:01:00Z"},
            {"id": 103, "event": "labeled", "label": {"name": "oio-auth:human-direct"}, "actor": owner, "created_at": "2026-10-03T12:01:00Z"},
        ]
        with mock.patch("oio_triage._get_pages", side_effect=[history, []]), mock.patch("oio_triage._api", return_value=(201, {})):
            attestation = _resolve_attestation(issue, {"action": "labeled", "label": {"name": "oio-auth:human-direct"}, "issue": issue}, self.project, "token", "example/repo")
        self.assertEqual(attestation["event_id"], "103")

    def test_removing_attestation_label_revokes_origin_class(self):
        issue = self.make_issue(origin="human-direct", auth_state="verified")
        issue["number"] = 45
        self.assertIsNone(_resolve_attestation(issue, {"action": "unlabeled", "issue": issue}, self.project, "token", "example/repo"))

    def test_old_attestation_does_not_survive_issue_body_edit(self):
        issue = self.make_issue(origin="human-direct", auth_state="verified")
        issue["number"] = 42
        issue["labels"].append({"name": "oio-auth:human-direct"})
        actor = {"id": 137629468, "login": "Pukujan"}
        history = [{"id": 9981, "event": "labeled", "label": {"name": "oio-auth:human-direct"}, "actor": actor, "created_at": "2026-10-03T12:01:00Z"}]
        old_digest = __import__("hashlib").sha256(issue["body"].encode()).hexdigest()
        comments = [{"body": f"<!-- oio-account-attestation:v1 issue=42 event=9981 label=oio-auth:human-direct body_sha256={old_digest} -->", "user": {"login": "github-actions[bot]"}}]
        issue["body"] += "\nEdited after attestation"
        with mock.patch("oio_triage._get_pages", side_effect=[history, comments]):
            attestation = _resolve_attestation(issue, {"action": "edited", "issue": issue}, self.project, "token", "example/repo")
        self.assertIsNone(attestation)

    def test_agent_author_using_owner_account_cannot_self_claim_human_direct(self):
        issue = self.make_issue(origin="human-direct", auth_state="verified")
        decision = classify_issue(issue, ROOT)
        self.assertIn("authorization:claimed", decision["labels"])
        self.assertIn("queue:class-3", decision["labels"])
        self.assertIn("needs-human-verification", decision["labels"])

    def test_garbage_content_author_does_not_pass_filer_stamp(self):
        issue = self.make_issue()
        issue["body"] = issue["body"].replace("agent:codex/session-123", "abcdefgh")
        decision = classify_issue(issue, ROOT)
        self.assertIn("needs-filer-stamp", decision["labels"])

    def test_uncertain_product_claim_uses_bounded_review_lane(self):
        issue = self.make_issue()
        issue["body"] = issue["body"].replace("confirmed", "unknown").replace("affects", "blocks")
        decision = classify_issue(issue, ROOT)
        self.assertIn("review:bounded-or-uncertain-review", decision["labels"])
        self.assertNotIn("review:product-outcome-review", decision["labels"])

    def test_risk_lane_does_not_promote_agent_authority(self):
        issue = self.make_issue(origin="agent-initiated")
        issue["body"] = issue["body"].replace("moderate", "critical").replace("limited-test-or-preview", "active-production")
        decision = classify_issue(issue, ROOT)
        self.assertIn("queue:class-4", decision["labels"])
        self.assertIn("review:production-risk-review", decision["labels"])

    def test_wrong_target_project_overlay_is_rejected(self):
        with self.assertRaisesRegex(InstallError, "does not match"):
            classify_issue(self.make_issue(), ROOT, "example/other")

    def test_non_oio_issue_is_skipped(self):
        decision = classify_issue({"body": "ordinary issue", "labels": [], "user": {}}, ROOT)
        self.assertTrue(decision["skip"])

    def test_general_proposal_and_incident_are_outside_ontology_scope(self):
        for issue_type in ["proposal", "incident"]:
            issue = self.make_issue()
            issue["body"] = issue["body"].replace("observational", issue_type, 1)
            with self.subTest(issue_type=issue_type):
                self.assertTrue(classify_issue(issue, ROOT)["skip"])


class PlatformProbeTests(unittest.TestCase):
    """The probe a caller uses must agree with the dispatch the installer uses.

    ACS calls ``--check-platform`` instead of keeping its own copy of OIO's
    precondition. A copy is what went stale: it kept reporting Windows
    unsupported after the Windows backend landed, so an install that would have
    succeeded reported PARTIAL.
    """

    def test_probe_reports_the_backend_the_installer_dispatches_to(self):
        supported, backend = oio_installer.platform_support()
        self.assertTrue(supported, backend)
        expected = "Windows" if sys.platform == "win32" else "descriptor-relative"
        self.assertIn(expected, backend)

    def test_check_platform_flag_runs_without_a_target(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(oio_installer.main(["--check-platform"]), 0)

    def test_posix_precondition_is_the_probe_and_the_refusal(self):
        """One source of truth for the POSIX precondition.

        The reason the probe reports is the reason the backend refuses with, so
        a caller cannot be told something the install would then reject.
        """
        if sys.platform == "win32":
            self.skipTest("the POSIX precondition is not consulted on Windows")
        with mock.patch.object(oio_installer.os, "supports_dir_fd", set()):
            self.assertTrue(oio_installer._posix_precondition())
            self.assertFalse(oio_installer.platform_support()[0])
            with self.assertRaises(InstallError):
                oio_installer._PosixTargetFS(Path("."))


if __name__ == "__main__":
    unittest.main()
