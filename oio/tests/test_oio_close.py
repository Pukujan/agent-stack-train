from __future__ import annotations

import contextlib
import glob
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".github/scripts"))

import oio_installer  # noqa: E402
import oio_close_refs  # noqa: E402
from oio_installer import InstallError  # noqa: E402
from oio_close_refs import closing_refs, drift_findings, resolve_lifecycle  # noqa: E402
from oio_triage import classify_issue  # noqa: E402

NEW_FIELDS = [
    "Summary",
    "Identity and Lineage",
    "Acceptance Criteria",
    "Boundaries and Next Action",
    "Symptoms",
    "Hypotheses (unverified)",
    "Counter-signal",
    "Honest Caveat",
    "Problems vs Gaps",
]


def issue_body(issue_type: str = "observational", extra: str = "") -> str:
    """A complete legacy body: every field triage already knew about."""
    return f"""### Issue Type
{issue_type}

### Lifecycle Status
open

### Filer Origin (who initiated this filing)
agent-proposed

### Filing Authorization Evidence
claimed

### Session, Authorization Evidence, and Instruction Reference
Session reference: session-123; instruction reference: test prompt; authorization evidence: claimed

### Content Author Account or Runtime Identity
agent:codex/session-123

### Directing Human GitHub Account ID
not-applicable

### Destination Repository
Pukujan/observational-issue-ops

### Ontology Versions Used
oio=1.1.0; project=1.0.0

### Project Priority Path
5

### Project Priority Concept ID
oio-project:priority-5

### Affected App, Adopter, Users, or Systems
OIO repository contributors

### Observed Consequence and Workaround
The log does not close; use owner review.

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
The queue may be misleading.

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

### Issue Relations
related: #21
{extra}"""


def make_issue(issue_type: str = "observational", extra: str = "") -> dict:
    return {
        "body": issue_body(issue_type, extra),
        "labels": [{"name": "observational-issue"}],
        "user": {"id": 137629468, "login": "Pukujan"},
        "created_at": "2026-10-03T12:00:00Z",
    }


class ClosingRefsTests(unittest.TestCase):
    def test_native_verbs_close_same_and_cross_repo_refs(self):
        self.assertEqual(closing_refs("Closes #12"), [(None, 12)])
        self.assertEqual(closing_refs("Fixes: #3"), [(None, 3)])
        self.assertEqual(closing_refs("resolves Pukujan/observational-issue-ops#4"), [("Pukujan/observational-issue-ops", 4)])
        self.assertEqual(closing_refs("CLOSES owner/repo#5"), [("owner/repo", 5)])

    def test_refs_keyword_is_not_a_close_directive(self):
        self.assertEqual(closing_refs("Refs #12\nrelated: #13"), [])
        self.assertEqual(closing_refs("This closes nothing."), [])

    def test_duplicates_collapse_case_insensitively(self):
        self.assertEqual(
            closing_refs("Closes #1\ncloses #1\nFixes OWNER/Repo#2\nfixes owner/repo#2"),
            [(None, 1), ("OWNER/Repo", 2)],
        )

    def test_metamorphic_reordering_and_progress_refs_do_not_change_the_set(self):
        base = closing_refs("Closes #1\nFixes #2\nResolves owner/repo#3")
        reordered = closing_refs("Resolves owner/repo#3\nCloses #1\nFixes #2")
        with_refs = closing_refs("Refs #99\nCloses #1\nRefs #2\nFixes #2\nResolves owner/repo#3\nRefs #3")
        self.assertEqual(set(base), set(reordered))
        self.assertEqual(set(base), set(with_refs))


class ApplyBehaviourTests(unittest.TestCase):
    def test_already_closed_issue_is_not_closed_again_but_is_synced(self):
        with (
            mock.patch("oio_close_refs._gh_json", side_effect=[
                {"body": "Closes #5", "url": "https://example/pr/1"},
                {"state": "CLOSED", "body": "### Lifecycle Status\nopen\n", "labels": []},
            ]),
            mock.patch("oio_close_refs._ensure_label"),
            mock.patch("oio_close_refs._close_issue") as close,
            mock.patch("oio_close_refs._sync_issue") as sync,
            contextlib.redirect_stderr(io.StringIO()),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(oio_close_refs.apply_refs("o/r", "https://example/pr/1"), 0)
        close.assert_not_called()
        sync.assert_called_once()

    def test_cross_repo_forbidden_close_warns_and_continues(self):
        forbidden = subprocess.CompletedProcess([], 1, "", "HTTP 403: Resource not accessible by integration")
        with (
            mock.patch("oio_close_refs._gh_json", side_effect=[
                {"body": "Closes other/repo#5", "url": "https://example/pr/1"},
                {"state": "OPEN", "body": "### Lifecycle Status\nopen\n", "labels": []},
            ]),
            mock.patch("oio_close_refs._ensure_label"),
            mock.patch("oio_close_refs._close_issue", return_value=forbidden),
            mock.patch("oio_close_refs._sync_issue") as sync,
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(oio_close_refs.apply_refs("o/r", "https://example/pr/1"), 0)
        sync.assert_not_called()

    def test_same_repo_close_failure_fails_the_run(self):
        failed = subprocess.CompletedProcess([], 1, "", "HTTP 500: server error")
        with (
            mock.patch("oio_close_refs._gh_json", side_effect=[
                {"body": "Closes #5", "url": "https://example/pr/1"},
                {"state": "OPEN", "body": "### Lifecycle Status\nopen\n", "labels": []},
            ]),
            mock.patch("oio_close_refs._ensure_label"),
            mock.patch("oio_close_refs._close_issue", return_value=failed),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(oio_close_refs.apply_refs("o/r", "https://example/pr/1"), 1)


class LifecycleBodyTests(unittest.TestCase):
    def test_replaces_an_existing_value(self):
        body = "### Issue Type\nobservational\n\n### Lifecycle Status\nopen\n\n### Citations\nnone\n"
        result = resolve_lifecycle(body)
        self.assertIn("### Lifecycle Status\n\nresolved\n", result)
        self.assertNotIn("\nopen\n", result)
        self.assertTrue(result.endswith("### Citations\nnone\n"))

    def test_appends_the_section_when_absent(self):
        result = resolve_lifecycle("### Issue Type\nobservational\n")
        self.assertTrue(result.endswith("### Lifecycle Status\n\nresolved\n"))

    def test_is_idempotent(self):
        for body in [
            "### Lifecycle Status\nopen\n\n### Next\nx\n",
            "### Issue Type\nobservational\n",
            "### Lifecycle Status\nresolved\n",
        ]:
            with self.subTest(body=body):
                once = resolve_lifecycle(body)
                self.assertEqual(resolve_lifecycle(once), once)

    def test_handles_crlf_bodies(self):
        body = "### Issue Type\r\nobservational\r\n\r\n### Lifecycle Status\r\nopen\r\n\r\n### Next\r\nx\r\n"
        once = resolve_lifecycle(body)
        self.assertIn("### Lifecycle Status\r\n\r\nresolved\r\n", once)
        self.assertEqual(resolve_lifecycle(once), once)


class DriftTests(unittest.TestCase):
    def issue(self, state, *labels):
        return {"number": 7, "state": state, "stateReason": "completed", "labels": [{"name": label} for label in labels]}

    def test_closed_open_is_a_finding(self):
        self.assertEqual(len(drift_findings([self.issue("CLOSED", "status:open")])), 1)

    def test_closed_resolved_is_not_a_finding(self):
        self.assertEqual(drift_findings([self.issue("CLOSED", "status:resolved")]), [])
        for settled in ("status:superseded", "status:obsolete", "status:wontfix"):
            with self.subTest(label=settled):
                self.assertEqual(drift_findings([self.issue("CLOSED", settled)]), [])

    def test_open_resolved_is_a_finding(self):
        self.assertEqual(len(drift_findings([self.issue("OPEN", "status:resolved")])), 1)

    def test_no_status_label_is_ignored(self):
        self.assertEqual(drift_findings([self.issue("CLOSED", "type:observational"), self.issue("OPEN")]), [])


class TemplateTests(unittest.TestCase):
    def template(self):
        return yaml.safe_load((ROOT / ".github/ISSUE_TEMPLATE/observational-issue.yml").read_text(encoding="utf-8"))

    def test_new_investigation_fields_exist_and_are_optional(self):
        fields = {item["attributes"]["label"]: item for item in self.template()["body"] if item["type"] != "markdown"}
        for label in NEW_FIELDS:
            with self.subTest(label=label):
                self.assertIn(label, fields)
                self.assertIs(fields[label]["validations"]["required"], False)

    def test_existing_fields_keep_their_relative_order(self):
        labels = [item["attributes"]["label"] for item in self.template()["body"] if item["type"] != "markdown"]
        existing = [
            "Issue Type", "Lifecycle Status", "Filer Origin (who initiated this filing)",
            "Filing Authorization Evidence", "Session, Authorization Evidence, and Instruction Reference",
            "Content Author Account or Runtime Identity", "Directing Human GitHub Account ID",
            "Destination Repository", "Ontology Versions Used", "Project Priority Path",
            "Project Priority Concept ID", "Affected App, Adopter, Users, or Systems",
            "Observed Consequence and Workaround", "Evidence Confidence", "Impact if Unresolved",
            "Likelihood", "Exposure", "Exposure Duration", "Recoverability", "Recovery Evidence",
            "Risk if the Observation Remains Unresolved", "Risk Introduced by a Proposed Change",
            "Product or Release Relevance", "Named Product Outcome and Cost of Delay", "Cost of Delay",
            "Smallest Useful Product Slice", "Provenance and Context",
            "Reproducibility Steps and Evidence", "Issue Relations", "Citations and References",
            "Non-Binding Proposed Next Actions",
        ]
        self.assertEqual(len(existing), 31)
        positions = [labels.index(label) for label in existing]
        self.assertEqual(positions, sorted(positions))

    def test_every_github_yaml_file_parses(self):
        files = sorted(glob.glob(str(ROOT / ".github/**/*.yml"), recursive=True))
        self.assertTrue(files)
        for path in files:
            with self.subTest(path=path):
                yaml.safe_load(Path(path).read_text(encoding="utf-8"))


class TriageOptionalFieldTests(unittest.TestCase):
    def test_operational_without_hypotheses_gets_the_investigation_label(self):
        decision = classify_issue(make_issue("operational"), ROOT)
        self.assertIn("needs-investigation-block", decision["labels"])

    def test_observational_without_hypotheses_gets_no_investigation_label(self):
        decision = classify_issue(make_issue("observational"), ROOT)
        self.assertNotIn("needs-investigation-block", decision["labels"])

    def test_operational_with_hypotheses_passes(self):
        extra = "\n### Hypotheses (unverified)\n- (hypothesis) the close step is missing\n"
        decision = classify_issue(make_issue("operational", extra), ROOT)
        self.assertNotIn("needs-investigation-block", decision["labels"])
        self.assertIn("the close step is missing", decision["optional_fields"]["hypotheses"])

    def test_optional_headings_are_matched_by_normalized_prefix(self):
        extra = (
            "\n### Summary\nShort problem statement.\n"
            "\n### Identity and Lineage\nleaf #55\n"
            "\n### Acceptance Criteria\n- [ ] closes\n"
            "\n### Boundaries and Next Action\nNext action: ship\n"
            "\n### Symptoms\n1. logs stay open\n"
            "\n### Hypotheses (unverified)\n- (hypothesis) no closer\n"
            "\n### Counter-signal\nnone observed\n"
            "\n### Honest Caveat\nnot reproduced in CI\n"
            "\n### Problems vs Gaps\n- Problem: logs stay open\n"
        )
        decision = classify_issue(make_issue(extra=extra), ROOT)
        self.assertEqual(decision["optional_fields"]["summary"], "Short problem statement.")
        self.assertEqual(decision["optional_fields"]["identity_and_lineage"], "leaf #55")
        self.assertEqual(decision["optional_fields"]["acceptance_criteria"], "- [ ] closes")
        self.assertEqual(decision["optional_fields"]["boundaries_and_next_action"], "Next action: ship")
        self.assertEqual(decision["optional_fields"]["symptoms"], "1. logs stay open")
        self.assertIn("no closer", decision["optional_fields"]["hypotheses"])
        self.assertEqual(decision["optional_fields"]["counter_signal"], "none observed")
        self.assertEqual(decision["optional_fields"]["honest_caveat"], "not reproduced in CI")
        self.assertIn("logs stay open", decision["optional_fields"]["problems_vs_gaps"])

    def test_legacy_body_labels_are_unchanged(self):
        decision = classify_issue(make_issue(), ROOT)
        self.assertEqual(
            decision["labels"],
            [
                "account:owner",
                "authorization:claimed",
                "evidence:confirmed",
                "exposure:limited-test-or-preview",
                "filer:agent-proposed",
                "impact:moderate",
                "likelihood:observed",
                "observational-issue",
                "ontology:oio-1.1.0",
                "ontology:project-1.0.0",
                "priority:5",
                "proposal",
                "queue:class-3",
                "queue:class-3:account-01",
                "recoverability:manual-recovery",
                "relation:related",
                "release:affects",
                "review:product-outcome-review",
                "status:open",
                "type:observational",
            ],
        )
        self.assertNotIn("needs-investigation-block", decision["labels"])
        self.assertEqual(decision["record"]["lifecycle"], {"status": "open"})


class WorkflowContractTests(unittest.TestCase):
    def workflow(self, name: str) -> dict:
        return yaml.safe_load((ROOT / ".github/workflows" / name).read_text(encoding="utf-8"))

    @staticmethod
    def triggers(workflow: dict) -> dict:
        return workflow.get("on", workflow.get(True))

    def test_close_workflow_is_reusable_and_merged_only(self):
        workflow = self.workflow("close-on-merge.yml")
        self.assertIn("workflow_call", self.triggers(workflow))
        self.assertEqual(workflow["jobs"]["close"]["if"], "github.event.pull_request.merged == true")
        self.assertEqual(
            workflow["permissions"],
            {"contents": "read", "issues": "write", "pull-requests": "read"},
        )

    def test_drift_workflow_is_reusable_and_read_only(self):
        workflow = self.workflow("oio-status-drift.yml")
        self.assertIn("workflow_call", self.triggers(workflow))
        self.assertEqual(workflow["permissions"], {"contents": "read", "issues": "read"})

    def test_same_repo_callers_pass_the_default_branch_as_oio_ref(self):
        for name in ("close-on-merge-caller.yml", "status-drift-caller.yml"):
            with self.subTest(name=name):
                job = self.workflow(name)["jobs"]["drift" if "drift" in name else "close"]
                self.assertTrue(job["uses"].startswith("./.github/workflows/"))
                self.assertEqual(job["with"]["oio_ref"], "${{ github.event.repository.default_branch }}")

    def test_close_caller_guards_on_merged(self):
        workflow = self.workflow("close-on-merge-caller.yml")
        self.assertEqual(workflow["jobs"]["close"]["if"], "github.event.pull_request.merged == true")


class InstallerVersionAndTemplateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name) / "adopter"
        self.target.mkdir()
        subprocess.run(["git", "init", "-q", str(self.target)], check=True)
        subprocess.run(
            ["git", "-C", str(self.target), "remote", "add", "origin", "https://github.com/example/adopter.git"],
            check=True,
        )

    def test_reported_version_matches_the_version_file(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(oio_installer.OIO_VERSION, version)
        oio_installer.install(str(self.target))
        manifest = json.loads((self.target / ".oio/install-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["oio_version"], version)

    def test_missing_version_sources_fail_closed(self):
        with tempfile.TemporaryDirectory() as empty:
            with self.assertRaisesRegex(InstallError, "cannot determine the OIO package version"):
                oio_installer._detect_version(Path(empty))

    def test_installed_template_bytes_match_the_source(self):
        oio_installer.install(str(self.target))
        source = (ROOT / ".github/ISSUE_TEMPLATE/observational-issue.yml").read_bytes()
        installed = (self.target / ".github/ISSUE_TEMPLATE/observational-issue.yml").read_bytes()
        self.assertEqual(oio_installer._lf_bytes(installed), oio_installer._lf_bytes(source))


if __name__ == "__main__":
    unittest.main()
