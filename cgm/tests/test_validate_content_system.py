import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_content_system import (
    check,
    check_adapter,
    check_adopter_readme_product_only,
    check_issue_log_contract,
    check_project_brief_v2,
    check_readme,
    check_writing_contract,
    main,
)


ROOT = Path(__file__).resolve().parents[1]
MODULES = sorted({"brand-foundation", "content-context", "writing-direction", "human-sounding-writing", "human-output-naming", "visual-direction", "image-generation", "html-demo"})
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
            "helper_version": "0.5.0",
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
        "asset-manifest.json": {"schema_version": "content-generation.asset-manifest.v1", "system_version": "0.5.0", "assets": [{"path": "diagram.png", "role": "diagram"}]},
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
                    "modules": MODULES,
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
                    "modules": MODULES,
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



    def test_writing_contract_accepts_helper_checkout(self):
        self.assertEqual(check_writing_contract(ROOT), [])

    def test_writing_mode_entrypoint_prints_cgm_verify(self):
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["--root", str(ROOT), "--mode", "writing"])
        out = buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("CGM_VERIFY mode=writing status=OK", out)
        self.assertIn("writing_direction=present", out)
        self.assertIn("human_sounding_writing=present", out)
        self.assertIn("human_output_naming=present", out)
        self.assertIn("writing_router=present", out)
        self.assertIn("VALID: content-generation-modules writing contract", out)

    def test_writing_contract_rejects_missing_github_surfaces(self):
        import json
        import tempfile
        import shutil

        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory) / "cgm"
            # Minimal tree: copy only what writing check needs
            (staging / "modules" / "writing-direction").mkdir(parents=True)
            (staging / "modules" / "human-sounding-writing").mkdir(parents=True)
            (staging / "modules" / "writing-direction" / "SKILL.md").write_text("# wd\n", encoding="utf-8")
            (staging / "modules" / "human-sounding-writing" / "SKILL.md").write_text("# hsw\n", encoding="utf-8")
            (staging / "docs").mkdir()
            (staging / "docs" / "WRITING_ROUTING.md").write_text("# router\n", encoding="utf-8")
            version = {
                "system": "content-generation-modules",
                "version": "0.5.3",
                "modules": [
                    "brand-foundation",
                    "content-context",
                    "writing-direction",
                    "human-sounding-writing",
                    "visual-direction",
                    "image-generation",
                    "html-demo",
                ],
            }
            (staging / "system-version.json").write_text(json.dumps(version), encoding="utf-8")
            bad = {
                "schema_version": "content-generation.writing-routing.v1",
                "enforcement": "soft",
                "required_writing_modules": ["writing-direction", "human-sounding-writing"],
                "routes": [
                    {
                        "id": "readme_product_entry",
                        "surfaces": ["README.md"],
                        "load": "writing-direction",
                    },
                    {
                        "id": "github_and_docs_prose",
                        "surfaces": ["posts", "blogs"],
                        "load": "human-sounding-writing",
                    },
                ],
                "acs_verify_entrypoint": {
                    "writing": "python scripts/validate_content_system.py --root . --mode writing",
                    "full_helper": "python scripts/validate_content_system.py --root .",
                },
            }
            (staging / "docs" / "writing-routing.json").write_text(json.dumps(bad), encoding="utf-8")
            errors = check_writing_contract(staging)
            self.assertTrue(any("pull request" in e for e in errors))


    def test_writing_contract_rejects_missing_commit_surfaces(self):
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory) / "cgm"
            (staging / "modules" / "writing-direction").mkdir(parents=True)
            (staging / "modules" / "human-sounding-writing").mkdir(parents=True)
            (staging / "modules" / "writing-direction" / "SKILL.md").write_text("# wd\n", encoding="utf-8")
            (staging / "modules" / "human-sounding-writing" / "SKILL.md").write_text("# hsw\n", encoding="utf-8")
            (staging / "docs").mkdir()
            (staging / "docs" / "WRITING_ROUTING.md").write_text("# router\n", encoding="utf-8")
            version = {
                "system": "content-generation-modules",
                "version": "0.5.3",
                "modules": [
                    "brand-foundation",
                    "content-context",
                    "writing-direction",
                    "human-sounding-writing",
                    "visual-direction",
                    "image-generation",
                    "html-demo",
                ],
            }
            (staging / "system-version.json").write_text(json.dumps(version), encoding="utf-8")
            bad = {
                "schema_version": "content-generation.writing-routing.v1",
                "enforcement": "soft",
                "application": "must_load",
                "required_writing_modules": ["writing-direction", "human-sounding-writing"],
                "apply_checklist": ["a", "b", "c"],
                "not_routed": [],
                "routes": [
                    {
                        "id": "readme_product_entry",
                        "surfaces": ["README.md"],
                        "load": "writing-direction",
                        "required_load": True,
                    },
                    {
                        "id": "github_and_docs_prose",
                        "surfaces": [
                            "pull request titles",
                            "issue titles",
                            "issue log titles",
                            "non-README docs",
                            "changelog prose",
                        ],
                        "load": "human-sounding-writing",
                        "required_load": True,
                    },
                ],
                "acs_verify_entrypoint": {
                    "writing": "python scripts/validate_content_system.py --root . --mode writing",
                    "full_helper": "python scripts/validate_content_system.py --root .",
                },
                "acs_prompt_inject": {
                    "fields": ["routes", "apply_checklist"],
                    "instruction": "MUST load modules before writing commit messages.",
                },
            }
            (staging / "docs" / "writing-routing.json").write_text(json.dumps(bad), encoding="utf-8")
            errors = check_writing_contract(staging)
            self.assertTrue(any("commit message" in e for e in errors), errors)





    def test_writing_router_lists_html_report_and_compare_surfaces(self):
        import json
        contract = json.loads((ROOT / "docs" / "writing-routing.json").read_text(encoding="utf-8"))
        by_id = {route["id"]: route for route in contract["routes"]}
        route = by_id["github_and_docs_prose"]
        surfaces = {str(s).lower() for s in route["surfaces"]}
        self.assertEqual(route["load"], "human-sounding-writing")
        self.assertTrue(route["required_load"])
        self.assertTrue(route.get("default_on"))
        self.assertTrue(any("html report" in s for s in surfaces))
        self.assertTrue(any("compare html" in s for s in surfaces))
        self.assertTrue(any("compare ui" in s for s in surfaces))
        self.assertTrue(any("human-readable html" in s for s in surfaces))
        human_default = contract["human_facing_default"]
        self.assertEqual(human_default["load"], "human-sounding-writing")
        self.assertTrue(human_default["required_load"])
        self.assertTrue(human_default["default_on"])
        covers = {str(c).lower() for c in human_default["covers"]}
        self.assertTrue(any("every human-facing" in c for c in covers))
        instruction = str(contract["acs_prompt_inject"]["instruction"]).lower()
        self.assertTrue("html report" in instruction or "compare html" in instruction)
        self.assertTrue("every human-facing" in instruction or "default" in instruction)
        self.assertTrue("per-report" in instruction or "optional" in instruction)
        self.assertIn("human_facing_default", contract["acs_prompt_inject"]["fields"])
        when = str(contract["acs_prompt_inject"]["when"]).lower()
        self.assertTrue("html" in when or "compare" in when)

    def test_writing_contract_rejects_missing_html_report_surfaces(self):
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory) / "cgm"
            (staging / "modules" / "writing-direction").mkdir(parents=True)
            (staging / "modules" / "human-sounding-writing").mkdir(parents=True)
            (staging / "modules" / "writing-direction" / "SKILL.md").write_text("# wd\n", encoding="utf-8")
            (staging / "modules" / "human-sounding-writing" / "SKILL.md").write_text("# hsw\n", encoding="utf-8")
            (staging / "docs").mkdir()
            (staging / "docs" / "WRITING_ROUTING.md").write_text("# router\n", encoding="utf-8")
            version = {
                "system": "content-generation-modules",
                "version": "0.5.6",
                "modules": [
                    "brand-foundation",
                    "content-context",
                    "writing-direction",
                    "human-sounding-writing",
                    "visual-direction",
                    "image-generation",
                    "html-demo",
                ],
            }
            (staging / "system-version.json").write_text(json.dumps(version), encoding="utf-8")
            bad = {
                "schema_version": "content-generation.writing-routing.v1",
                "enforcement": "soft",
                "application": "must_load",
                "required_writing_modules": ["writing-direction", "human-sounding-writing"],
                "apply_checklist": ["a", "b", "c"],
                "not_routed": [],
                "human_facing_default": {
                    "load": "human-sounding-writing",
                    "required_load": True,
                    "default_on": True,
                    "covers": [
                        "every human-facing task/output",
                        "HTML reports",
                        "compare HTML",
                    ],
                },
                "routes": [
                    {
                        "id": "readme_product_entry",
                        "surfaces": ["README.md"],
                        "load": "writing-direction",
                        "required_load": True,
                    },
                    {
                        "id": "github_and_docs_prose",
                        "surfaces": [
                            "pull request titles",
                            "issue titles",
                            "issue log titles",
                            "commit messages",
                            "commit subjects",
                            "non-README docs",
                            "changelog prose",
                        ],
                        "load": "human-sounding-writing",
                        "required_load": True,
                        "default_on": True,
                    },
                    {
                        "id": "generated_artifact_filenames",
                        "surfaces": [
                            "generated artifact filenames",
                            "asset-manifest paths",
                            "committed media basenames",
                            "filename legends",
                        ],
                        "load": "human-output-naming",
                        "required_load": True,
                    },
                ],
                "acs_verify_entrypoint": {
                    "writing": "python scripts/validate_content_system.py --root . --mode writing",
                    "full_helper": "python scripts/validate_content_system.py --root .",
                },
                "acs_prompt_inject": {
                    "fields": ["routes", "apply_checklist", "human_facing_default"],
                    "when": "before HTML reports and compare deliverables",
                    "instruction": (
                        "MUST load hsw for every human-facing task including HTML reports "
                        "and compare HTML; do not treat as optional or per-report."
                    ),
                },
            }
            (staging / "docs" / "writing-routing.json").write_text(json.dumps(bad), encoding="utf-8")
            errors = check_writing_contract(staging)
            self.assertTrue(any("html report" in e for e in errors), errors)


    def test_writing_router_lists_artifact_filename_surfaces(self):
        import json
        contract = json.loads((ROOT / "docs" / "writing-routing.json").read_text(encoding="utf-8"))
        by_id = {route["id"]: route for route in contract["routes"]}
        route = by_id["generated_artifact_filenames"]
        surfaces = {str(s).lower() for s in route["surfaces"]}
        self.assertEqual(route["load"], "human-output-naming")
        self.assertTrue(route["required_load"])
        self.assertTrue(any("generated artifact" in s for s in surfaces))
        self.assertTrue(any("asset-manifest" in s for s in surfaces))
        self.assertTrue(any("committed media" in s for s in surfaces))
        instruction = str(contract["acs_prompt_inject"]["instruction"]).lower()
        self.assertTrue("filename" in instruction or "human-output-naming" in instruction)


    def test_writing_router_requires_always_on_inject(self):
        import json
        contract = json.loads((ROOT / "docs" / "writing-routing.json").read_text(encoding="utf-8"))
        inject = contract["acs_prompt_inject"]
        self.assertIs(inject["always_on"], True)
        self.assertIs(inject["opt_in_forbidden"], True)
        self.assertTrue(str(inject.get("audience", "")).lower().find("every") >= 0 or "adopter" in str(inject.get("audience", "")).lower())
        self.assertIn("system_block", inject["fields"])
        self.assertIn("always_on", inject["fields"])
        block = inject["system_block"].lower()
        self.assertIn("always-on", block)
        self.assertIn("human-sounding-writing", block)
        self.assertIn("opt-in is forbidden", block)
        self.assertIn("html", block)
        self.assertIs(contract["always_on_system_block"]["always_on"], True)
        self.assertTrue(contract["acs_verify_entrypoint"].get("hsw_automation"))
        instruction = inject["instruction"].lower()
        self.assertTrue("always_on" in instruction or "always-on" in instruction)
        self.assertIn("adopter", instruction)

    def test_writing_contract_rejects_missing_always_on_inject(self):
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory) / "cgm"
            (staging / "modules" / "writing-direction").mkdir(parents=True)
            (staging / "modules" / "human-sounding-writing").mkdir(parents=True)
            (staging / "modules" / "human-output-naming").mkdir(parents=True)
            (staging / "modules" / "writing-direction" / "SKILL.md").write_text("# wd\n", encoding="utf-8")
            (staging / "modules" / "human-sounding-writing" / "SKILL.md").write_text("# hsw\n", encoding="utf-8")
            (staging / "modules" / "human-output-naming" / "SKILL.md").write_text("# hon\n", encoding="utf-8")
            (staging / "scripts").mkdir()
            (staging / "scripts" / "verify_hsw_applied.py").write_text("# stub\n", encoding="utf-8")
            (staging / "docs").mkdir()
            (staging / "docs" / "WRITING_ROUTING.md").write_text("# router\n", encoding="utf-8")
            # Minimal filename contract so this failure focuses on always_on inject
            (staging / "docs" / "HUMAN_OUTPUT_NAMING.md").write_text("# hon\n", encoding="utf-8")
            (staging / "docs" / "human-output-naming.json").write_text(
                json.dumps({
                    "schema_version": "content-generation.human-output-naming.v1",
                    "default_style": "speakable",
                    "required_load": True,
                    "apply_checklist": ["a", "b", "c"],
                    "helper": {"module": "scripts/human_filename.py", "api": ["build_basename"]},
                    "legend": {"required": True, "helper_dir": "docs/filename-legends"},
                }),
                encoding="utf-8",
            )
            (staging / "docs" / "filename-legends").mkdir()
            (staging / "docs" / "filename-legends" / "sample.json").write_text(
                json.dumps({"schema_version": "content-generation.filename-legend.v1", "feature": "sample", "glossary": {"a": "b"}, "files": ["x.mp3"]}),
                encoding="utf-8",
            )
            (staging / "scripts" / "human_filename.py").write_text(
                "def build_basename(*a, **k):\n    return 'x'\n"
                "def build_basename_from_dimensions(*a, **k):\n    return 'x'\n"
                "def build_relative_path(*a, **k):\n    return 'x'\n"
                "def is_accepted_basename(*a, **k):\n    return True\n"
                "def is_hashy_junk_basename(*a, **k):\n    return False\n"
                "def is_robot_key_value_basename(*a, **k):\n    return False\n"
                "def pitch_phrase(*a, **k):\n    return 'x'\n"
                "def sanitize_label(*a, **k):\n    return 'x'\n"
                "def speed_phrase(*a, **k):\n    return 'x'\n",
                encoding="utf-8",
            )
            version = {
                "system": "content-generation-modules",
                "version": "0.5.7",
                "modules": [
                    "brand-foundation",
                    "content-context",
                    "writing-direction",
                    "human-sounding-writing",
                    "human-output-naming",
                    "visual-direction",
                    "image-generation",
                    "html-demo",
                ],
            }
            (staging / "system-version.json").write_text(json.dumps(version), encoding="utf-8")
            bad = {
                "schema_version": "content-generation.writing-routing.v1",
                "enforcement": "soft",
                "application": "must_load",
                "required_writing_modules": ["writing-direction", "human-sounding-writing"],
                "apply_checklist": ["a", "b", "c"],
                "not_routed": [],
                "human_facing_default": {
                    "load": "human-sounding-writing",
                    "required_load": True,
                    "default_on": True,
                    "covers": [
                        "every human-facing task/output",
                        "HTML reports",
                        "compare HTML",
                    ],
                },
                "routes": [
                    {
                        "id": "readme_product_entry",
                        "surfaces": ["README.md"],
                        "load": "writing-direction",
                        "required_load": True,
                    },
                    {
                        "id": "github_and_docs_prose",
                        "surfaces": [
                            "pull request titles",
                            "issue titles",
                            "issue log titles",
                            "commit messages",
                            "commit subjects",
                            "non-README docs",
                            "changelog prose",
                            "HTML reports",
                            "compare HTML",
                            "compare UIs",
                            "human-readable HTML",
                        ],
                        "load": "human-sounding-writing",
                        "required_load": True,
                        "default_on": True,
                    },
                    {
                        "id": "generated_artifact_filenames",
                        "surfaces": [
                            "generated artifact filenames",
                            "asset-manifest paths",
                            "committed media basenames",
                            "filename legends",
                        ],
                        "load": "human-output-naming",
                        "required_load": True,
                    },
                ],
                "acs_verify_entrypoint": {
                    "writing": "python scripts/validate_content_system.py --root . --mode writing",
                    "full_helper": "python scripts/validate_content_system.py --root .",
                },
                "acs_prompt_inject": {
                    "fields": ["routes", "apply_checklist", "human_facing_default"],
                    "when": "before HTML reports and compare deliverables",
                    "instruction": (
                        "MUST load hsw for every human-facing task including HTML reports "
                        "and compare HTML; filenames and speakable legends; do not treat as "
                        "optional or per-report."
                    ),
                },
            }
            (staging / "docs" / "writing-routing.json").write_text(json.dumps(bad), encoding="utf-8")
            errors = check_writing_contract(staging)
            self.assertTrue(any("always_on" in e for e in errors), errors)
            self.assertTrue(any("system_block" in e for e in errors), errors)


    def test_issue_log_contract_present(self):
        self.assertEqual(check_issue_log_contract(ROOT), [])
        import json
        contract = json.loads((ROOT / "docs" / "issue-log-contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["schema_version"], "content-generation.issue-log.v1")
        self.assertIn("every", str(contract["audience"]).lower())
        ids = {s["id"] for s in contract["intake_steps"]}
        for needed in (
            "reproduce_first",
            "classify_product_defect_all_adopters",
            "fix_pin_contract_validate",
            "never_single_adopter_ticket",
        ):
            self.assertIn(needed, ids)
        self.assertIn("validate_needles", contract["done_when_must_include"])
        self.assertIn("adopter_facing_docs", contract["done_when_must_include"])
        forbidden = " ".join(str(x).lower() for x in contract["forbidden_ticket_shapes"])
        self.assertIn("acs-only", forbidden)
        self.assertTrue((ROOT / ".github" / "ISSUE_TEMPLATE" / "operational.yml").is_file())

    def test_issue_log_contract_rejects_acs_only_gap(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory)
            (staging / "docs").mkdir()
            (staging / "docs" / "ISSUE_LOG.md").write_text("# issue log\n", encoding="utf-8")
            (staging / ".github" / "ISSUE_TEMPLATE").mkdir(parents=True)
            (staging / ".github" / "ISSUE_TEMPLATE" / "operational.yml").write_text(
                "name: Operational\nbody:\n  - reproduce every cgm adopter acs-only validate\n",
                encoding="utf-8",
            )
            bad = {
                "schema_version": "content-generation.issue-log.v1",
                "audience": "acs_only",
                "intake_steps": [
                    {"id": "reproduce_first", "required": True},
                    {"id": "classify_product_defect_all_adopters", "required": True},
                    {"id": "fix_pin_contract_validate", "required": True},
                    {"id": "never_single_adopter_ticket", "required": True},
                ],
                "forbidden_ticket_shapes": ["docs-only acknowledgment"],
                "done_when": ["a", "b", "c"],
                "done_when_must_include": ["validate_needles"],
                "validate_needles": ["intake_steps"],
            }
            (staging / "docs" / "issue-log-contract.json").write_text(json.dumps(bad), encoding="utf-8")
            errors = check_issue_log_contract(staging)
            self.assertTrue(any("audience" in e for e in errors), errors)
            self.assertTrue(any("ACS-only" in e or "acs-only" in e for e in errors), errors)
            self.assertTrue(any("adopter_facing_docs" in e for e in errors), errors)

    def test_adopter_readme_rejects_cgm_promotion(self):
        errors = check_adopter_readme_product_only(
            "# Demo\n\nBuilt with CGM and content-generation-modules.\n"
        )
        self.assertTrue(any("CGM" in e for e in errors))
        self.assertTrue(any("content-generation-modules" in e for e in errors))

    def test_adopter_readme_rejects_image_generation_heading(self):
        errors = check_adopter_readme_product_only(
            "# Demo\n\n## Image generation and use\n\nWe used ChatGPT.\n"
        )
        self.assertTrue(any("Image generation and use" in e for e in errors))

    def test_adopter_readme_allows_product_only_copy(self):
        self.assertEqual(
            check_adopter_readme_product_only(
                "# Demo\n\n## Why this exists\n\nReaders need a clear product story.\n"
            ),
            [],
        )

    def test_adapter_0_5_4_enforces_adopter_readme_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            adapter = project / ".content-system"
            adapter.mkdir()
            write_adapter(adapter)
            system = json.loads((adapter / "system-version.json").read_text(encoding="utf-8"))
            system["helper_version"] = "0.5.4"
            (adapter / "system-version.json").write_text(json.dumps(system), encoding="utf-8")
            (project / "diagram.png").write_bytes(b"png")
            (project / "README.md").write_text(
                "# Demo\n\nPowered by CGM.\n\n## Image generation and use\n\nPrompts live here.\n",
                encoding="utf-8",
            )
            errors = check_adapter(adapter, project)
            self.assertTrue(any("CGM" in e for e in errors))
            self.assertTrue(any("Image generation and use" in e for e in errors))

    def test_adapter_check_adopter_docs_rejects_stale_bootstrap_and_unreferenced_asset(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            adapter = project / ".content-system"
            adapter.mkdir()
            write_adapter(adapter)
            (project / "diagram.png").write_bytes(b"png")
            (project / "README.md").write_text(
                "# Octo\n\n"
                "Repository governance and planning are being initialized under issue #2. "
                "Product implementation starts with the login/workspace slice after that bootstrap is accepted.\n",
                encoding="utf-8",
            )
            # Default check_adapter passes on disk asset existence
            errors_default = check_adapter(adapter, project, check_adopter_docs=False)
            self.assertEqual(errors_default, [])

            # check_adopter_docs=True catches stale bootstrap and unreferenced asset
            errors_enforced = check_adapter(adapter, project, check_adopter_docs=True)
            self.assertTrue(any("bootstrap" in e for e in errors_enforced))
            self.assertTrue(any("never referenced" in e and "diagram.png" in e for e in errors_enforced))

    def test_main_check_adopter_docs_requires_adapter(self):
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["--root", str(ROOT), "--check-adopter-docs"])
        out = buf.getvalue()
        self.assertEqual(code, 1)
        self.assertIn("--check-adopter-docs requires --adapter", out)

    def test_main_check_adopter_docs_cli_integration(self):
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            adapter = project / ".content-system"
            adapter.mkdir()
            write_adapter(adapter)
            (project / "diagram.png").write_bytes(b"png")
            # 1. Stale bootstrap stub fails
            (project / "README.md").write_text(
                "# Octo\n\n"
                "Product implementation starts with the login/workspace slice after that bootstrap is accepted.\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main([
                    "--root", str(ROOT),
                    "--adapter", str(adapter),
                    "--project-root", str(project),
                    "--check-adopter-docs",
                ])
            out = buf.getvalue()
            self.assertEqual(code, 1)
            self.assertIn("INVALID", out)
            self.assertIn("bootstrap", out)

            # 2. Fresh README referencing asset passes
            (project / "README.md").write_text(
                "# Octo Control Plane\n\n"
                "> **One place to reach workspaces, files, and background jobs.**\n\n"
                "Personal files and work projects often end up scattered across disks. "
                "Octo gives them one durable workspace boundary while keeping storage replaceable.\n\n"
                "![Diagram](diagram.png)\n\n"
                "## Why this exists\n\n"
                "Developers lose track of raw files across systems. Octo provides unified metadata.\n\n"
                "## How it works\n\n"
                "The platform API catalogs files into an operational database.\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main([
                    "--root", str(ROOT),
                    "--adapter", str(adapter),
                    "--project-root", str(project),
                    "--check-adopter-docs",
                ])
            out = buf.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("VALID", out)


if __name__ == "__main__":
    unittest.main()
