import tempfile
import unittest
from pathlib import Path

from scripts.validate_content_system import check, check_adapter


ROOT = Path(__file__).resolve().parents[1]


class ContentSystemValidationTests(unittest.TestCase):
    def test_repository_contract_is_valid(self):
        self.assertEqual(check(ROOT), [])

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


if __name__ == "__main__":
    unittest.main()
