import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_content_system import check, check_adapter, check_project_brief_v2, check_readme


ROOT = Path(__file__).resolve().parents[1]
MODULES = sorted({"brand-foundation", "content-context", "writing-direction", "visual-direction", "image-generation", "html-demo"})
COMMIT = "a" * 40
SOURCE_URI = f"https://github.com/Pukujan/demo/blob/{COMMIT}/src/app.py#L2-L6"


def sample_evidence(**overrides):
    item = {
        "claim": "The command writes a report.",
        "source": "The command implementation and its test.",
        "status": "shipped",
        "supports": "The test confirms that this command writes a report for the sample input.",
        "limits": "The test does not establish performance or behavior for every input.",
        "recorded_at": "2026-09-23T12:00:00Z",
        "source_revision": {
            "kind": "repository_artifact",
            "reference": "Implementation and unit test",
            "repository": "Pukujan/demo",
            "commit": COMMIT,
            "path": "src/app.py",
            "locator": "lines 2-6",
            "uri": SOURCE_URI,
        },
        "cite_in_readme": False,
    }
    item.update(overrides)
    return item


def write_adapter(adapter: Path, brief_version="v2"):
    project_schema = f"content-generation.project-brief.{brief_version}"
    evidence = sample_evidence()
    if brief_version == "v1":
        evidence = {"claim": evidence["claim"], "source": evidence["source"]}
    files = {
        "system-version.json": {
            "schema_version": "content-generation.adapter.v1",
            "helper_repository": "https://github.com/Pukujan/content-generation-modules",
            "helper_version": "0.4.0",
            "helper_commit": COMMIT,
            "modules": MODULES,
        },
        "project-brief.json": {
            "schema_version": project_schema,
            "project": "Demo",
            "audience": ["people"],
            "problem": "A concrete reader problem.",
            "solution": "A useful response.",
            "evidence": [evidence],
            "boundaries": ["One explicit limitation."],
        },
        "brand-language.json": {"schema_version": "content-generation.brand-language.v1", "name": "Demo", "personality": ["clear"], "promise": "A useful promise", "avoid": ["hype"]},
        "visual-style.json": {"schema_version": "content-generation.visual-style.v1", "reference_asset": "hero.png", "generation_workflow": "built-in image_gen", "narrative_roles": ["hero", "problem", "supporting"], "palette": {"background": "#000"}, "roles": {"hero": {}}, "reject_when": ["busy"]},
        "asset-manifest.json": {"schema_version": "content-generation.asset-manifest.v1", "system_version": "0.4.0", "assets": [{"path": "diagram.png", "role": "diagram"}]},
        "review-rubric.json": {"schema_version": "content-generation.review-rubric.v1", "dimensions": [{"id": "clarity", "question": "clear?"}], "decision_rule": "human review"},
    }
    for name, value in files.items():
        (adapter / name).write_text(json.dumps(value), encoding="utf-8")


class ContentSystemValidationTests(unittest.TestCase):
    def test_repository_contract_is_valid(self):
        self.assertEqual(check(ROOT), [])

    def test_readme_gate_rejects_a_technical_only_readme(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "templates").mkdir()
            (target / "templates" / "readme-contract.json").write_bytes(
                (ROOT / "templates" / "readme-contract.json").read_bytes()
            )
            (target / "README.md").write_text("# Internal API\n\n## Setup\n", encoding="utf-8")
            errors = check_readme(target)
            self.assertTrue(any("README missing required section" in error for error in errors))
            self.assertTrue(any("local narrative image" in error for error in errors))

    def test_readme_gate_rejects_technical_details_before_the_human_story(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "templates").mkdir()
            (target / "templates" / "readme-contract.json").write_bytes(
                (ROOT / "templates" / "readme-contract.json").read_bytes()
            )
            (target / "README.md").write_text(
                "# Project\n\n```powershell\npython run.py\n```\n\n## Why this exists\n",
                encoding="utf-8",
            )
            errors = check_readme(target)
            self.assertTrue(any("technical code after the human situation" in error for error in errors))

    def test_readme_gate_requires_scan_anchor(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "templates").mkdir()
            (target / "templates" / "readme-contract.json").write_bytes(
                (ROOT / "templates" / "readme-contract.json").read_bytes()
            )
            (target / "README.md").write_text(
                "# Project\n\n## Why this exists\n\nA human situation.\n",
                encoding="utf-8",
            )
            errors = check_readme(target)
            self.assertTrue(any("bold scan anchor" in error for error in errors))

    def test_missing_module_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for source in (ROOT / "system-version.json", ROOT / "CHATGPT_SETUP.md"):
                destination = target / source.name
                destination.write_bytes(source.read_bytes())
            errors = check(target)
            self.assertTrue(any("missing module" in error for error in errors))

    def test_adapter_requires_project_and_asset_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            adapter = Path(directory) / ".content-system"
            adapter.mkdir()
            files = {
                "system-version.json": {
                    "schema_version": "content-generation.adapter.v1",
                    "helper_repository": "https://example.invalid/helper",
                    "helper_version": "0.1.1",
                    "helper_commit": "abc123",
                    "modules": sorted({"brand-foundation", "content-context", "writing-direction", "visual-direction", "image-generation", "html-demo"}),
                },
                "project-brief.json": {"schema_version": "content-generation.project-brief.v1", "project": "Demo", "audience": ["people"], "problem": "problem", "solution": "solution", "evidence": [{"claim": "claim", "source": "README.md"}], "boundaries": ["boundary"]},
                "brand-language.json": {"schema_version": "content-generation.brand-language.v1", "name": "Demo", "personality": ["clear"], "promise": "promise", "avoid": ["hype"]},
                "visual-style.json": {"schema_version": "content-generation.visual-style.v1", "reference_asset": "hero.png", "palette": {"background": "#000"}, "roles": {"hero": {}}, "reject_when": ["busy"]},
                "asset-manifest.json": {"schema_version": "content-generation.asset-manifest.v1", "system_version": "0.1.1", "assets": [{"path": "hero.png"}]},
                "review-rubric.json": {"schema_version": "content-generation.review-rubric.v1", "dimensions": [{"id": "clarity", "question": "clear?"}], "decision_rule": "human review"},
            }
            for name, value in files.items():
                (adapter / name).write_text(__import__("json").dumps(value), encoding="utf-8")
            project_root = Path(directory) / "project"
            project_root.mkdir()
            (project_root / "hero.png").write_bytes(b"placeholder")
            self.assertEqual(check_adapter(adapter, project_root), [])

    def test_03_adapter_rejects_svg_narrative_substitution(self):
        with tempfile.TemporaryDirectory() as directory:
            adapter = Path(directory) / ".content-system"
            adapter.mkdir()
            files = {
                "system-version.json": {
                    "schema_version": "content-generation.adapter.v1",
                    "helper_repository": "https://example.invalid/helper",
                    "helper_version": "0.3.1",
                    "helper_commit": "abc123",
                    "modules": sorted({"brand-foundation", "content-context", "writing-direction", "visual-direction", "image-generation", "html-demo"}),
                },
                "project-brief.json": {"schema_version": "content-generation.project-brief.v1", "project": "Demo", "audience": ["people"], "problem": "problem", "solution": "solution", "evidence": [{"claim": "claim", "source": "README.md"}], "boundaries": ["boundary"]},
                "brand-language.json": {"schema_version": "content-generation.brand-language.v1", "name": "Demo", "personality": ["clear"], "promise": "promise", "avoid": ["hype"]},
                "visual-style.json": {"schema_version": "content-generation.visual-style.v1", "reference_asset": "hero.svg", "generation_workflow": "built-in image_gen", "narrative_roles": ["hero"], "palette": {"background": "#000"}, "roles": {"hero": {}}, "reject_when": ["busy"]},
                "asset-manifest.json": {"schema_version": "content-generation.asset-manifest.v1", "system_version": "0.3.1", "assets": [{"path": "hero.svg", "role": "hero", "orientation": "wide", "dimensions": "1600x900", "text_policy": "exact copy", "prompt_recipe": "Title / Subtitle", "exact_title": "Title", "exact_subtitle": "Subtitle", "alt_text": "A clear story", "usage": "README hero", "crop_behavior": "center", "rejection_conditions": ["garbled copy"], "review_decision": "accepted", "provider": "built-in image_gen", "prompt_record": "IMAGE_NOTES.md", "hash": hashlib.sha256(b"placeholder").hexdigest()}]},
                "review-rubric.json": {"schema_version": "content-generation.review-rubric.v1", "dimensions": [{"id": "clarity", "question": "clear?"}], "decision_rule": "human review"},
            }
            for name, value in files.items():
                (adapter / name).write_text(json.dumps(value), encoding="utf-8")
            project_root = Path(directory) / "project"
            project_root.mkdir()
            (project_root / "hero.svg").write_bytes(b"placeholder")
            (project_root / "IMAGE_NOTES.md").write_text("prompt record", encoding="utf-8")
            errors = check_adapter(adapter, project_root)
            self.assertTrue(any("must be a raster image" in error for error in errors))

    def test_v2_claim_record_requires_bounded_revision_pinned_evidence(self):
        evidence = sample_evidence()
        readme = f"The report is generated. [Implementation]({SOURCE_URI})"
        brief = {"schema_version": "content-generation.project-brief.v2", "evidence": [evidence]}
        self.assertEqual(check_project_brief_v2(brief, readme), [])
        bounded = sample_evidence(valid_time={"start": "2026-09-20T00:00:00Z", "end": "2026-09-23T12:00:00Z"})
        self.assertEqual(check_project_brief_v2({**brief, "evidence": [bounded]}, readme), [])

        cases = [
            ({**evidence, "supports": ""}, "missing non-empty supports"),
            ({**evidence, "limits": ""}, "missing non-empty limits"),
            ({**evidence, "recorded_at": "2026-09-23T12:00:00"}, "recorded_at must be an RFC 3339 timestamp"),
            ({**evidence, "valid_time": {"start": "2026-09-23T12:00:00Z", "end": "2026-09-22T12:00:00Z"}}, "must not follow"),
            ({**evidence, "status": []}, "has invalid status"),
            ({**evidence, "source_revision": {**evidence["source_revision"], "uri": "https://github.com/Pukujan/demo/blob/main/src/app.py"}}, "immutable web permalink"),
            ({**evidence, "source_revision": {**evidence["source_revision"], "uri": "https://[invalid"}}, "immutable web permalink"),
            ({**evidence, "cite_in_readme": True}, "not linked in the target README"),
            ({**evidence, "status": "shipped", "source_revision": {"kind": "unknown_search", "reference": "Searched the available repository", "observed_at": "2026-09-23"}}, "cannot label a claim shipped"),
        ]
        for invalid, expected in cases:
            with self.subTest(expected=expected):
                target_readme = "" if expected == "not linked in the target README" else readme
                errors = check_project_brief_v2({**brief, "evidence": [invalid]}, target_readme)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_v2_claim_order_is_metamorphically_invariant(self):
        first = sample_evidence()
        second = sample_evidence(claim="The same implementation has a defined entry point.")
        brief = {"schema_version": "content-generation.project-brief.v2", "evidence": [first, second]}
        readme = ""
        self.assertEqual(check_project_brief_v2(brief, readme), [])
        brief["evidence"].reverse()
        self.assertEqual(check_project_brief_v2(brief, readme), [])

    def test_04_adapter_requires_v2_brief_and_accepts_valid_v2(self):
        with tempfile.TemporaryDirectory() as directory:
            adapter = Path(directory) / ".content-system"
            adapter.mkdir()
            write_adapter(adapter, "v2")
            self.assertEqual(check_adapter(adapter), [])

            write_adapter(adapter, "v1")
            errors = check_adapter(adapter)
            self.assertTrue(any("require project-brief.v2" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
