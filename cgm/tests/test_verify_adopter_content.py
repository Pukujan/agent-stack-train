#!/usr/bin/env python3
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts.verify_adopter_content import (
    check_adopter_content,
    check_adopter_readme_structure,
    check_docs_hsw_tells,
    check_human_output_naming,
    check_manifest_assets_referenced,
    check_manifest_hero_asset_format,
    check_readme_freshness,
    check_readme_hero_format,
    main,
)


class VerifyAdopterContentTests(unittest.TestCase):
    def test_readme_freshness_accepts_clean_substantive_readme(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            readme = (
                "# Octo Control Plane\n\n"
                "> **One place to reach workspaces, files, and background jobs.**\n\n"
                "Personal files, work projects, and AI agents often end up scattered across "
                "local disks and unrelated cloud drives. Octo gives them one durable workspace "
                "boundary while keeping underlying storage replaceable.\n\n"
                "## Why this exists\n\n"
                "Developers and researchers lose track of raw files across workstations. "
                "Octo provides unified metadata and scoped access links.\n\n"
                "## How it works\n\n"
                "Files uploaded through the platform API are cataloged into an operational "
                "database and archived to configured object storage.\n"
            )
            (root / "README.md").write_text(readme, encoding="utf-8")
            errors = check_readme_freshness(root)
            self.assertEqual(errors, [])

    def test_readme_freshness_rejects_missing_readme(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            errors = check_readme_freshness(root)
            self.assertTrue(any("missing README.md" in e for e in errors))

    def test_readme_freshness_rejects_stale_bootstrap_stub(self):
        # The exact failure case reported in CGM #33 (octo-database)
        stubs = [
            (
                "# Octo\n\n"
                "Repository governance and planning are being initialized under issue #2. "
                "Product implementation starts with the login/workspace slice after that bootstrap is accepted.\n"
            ),
            (
                "# Project\n\n"
                "Work begins after that bootstrap is accepted.\n"
            ),
            (
                "# Project\n\n"
                "Features land after the bootstrap PR is merged.\n"
            ),
            (
                "# Project\n\n"
                "This repository is currently a minimal bootstrap stub for testing.\n"
            ),
        ]
        for stub_text in stubs:
            with self.subTest(stub=stub_text[:40]):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    (root / "README.md").write_text(stub_text, encoding="utf-8")
                    errors = check_readme_freshness(root)
                    self.assertTrue(
                        any("bootstrap" in e or "planning" in e for e in errors),
                        f"Expected bootstrap error for: {stub_text}, got: {errors}",
                    )

    def test_readme_freshness_rejects_unfilled_template_placeholders(self):
        placeholders = [
            "# Project name\n\n> **One sentence that names the human situation and the concrete promise.**\n\nA real description.\n",
            "# Octo\n\n![Hero](path/to/hero.png)\n\nDetailed description of the product and its features.\n",
            "# Octo\n\n![Visual](path/to/supporting-visual.png)\n\nDetailed description of product features.\n",
            "# Octo\n\n| Claim | Source |\n| [One material product claim] | [Direct citation] |\n\nA substantive description.\n",
            "# Octo\n\nStart with a situation the reader recognizes. Ground the example in repository evidence.\n",
            "# Octo\n\nSay who this is for, what the project helps them do, and what the project is not.\n",
        ]
        for text in placeholders:
            with self.subTest(snippet=text[:30]):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir)
                    (root / "README.md").write_text(text, encoding="utf-8")
                    errors = check_readme_freshness(root)
                    self.assertTrue(
                        any("unfilled template" in e for e in errors),
                        f"Expected unfilled template error for: {text}, got: {errors}",
                    )

    def test_readme_freshness_rejects_too_short_readme(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "README.md").write_text("# Octo\n\nA tool.\n", encoding="utf-8")
            errors = check_readme_freshness(root)
            self.assertTrue(any("suspiciously short" in e for e in errors))

    def test_manifest_assets_referenced_accepts_when_all_assets_present(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            adapter = project / ".content-system"
            adapter.mkdir()
            manifest = {
                "schema_version": "content-generation.asset-manifest.v1",
                "assets": [
                    {"path": "docs/assets/workspace-dashboard.svg", "role": "supporting"},
                    {"path": "assets/hero.png", "role": "hero"},
                ],
            }
            (adapter / "asset-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (project / "README.md").write_text(
                "# Demo\n\n![Hero](assets/hero.png)\n\nSee the workspace view below:\n\n"
                "![Dashboard](docs/assets/workspace-dashboard.svg)\n",
                encoding="utf-8",
            )
            errors = check_manifest_assets_referenced(adapter, project)
            self.assertEqual(errors, [])

    def test_manifest_assets_referenced_rejects_unreferenced_registered_asset(self):
        # CGM #33: workspace-dashboard.svg registered in asset-manifest but not embedded in docs/README
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            adapter = project / ".content-system"
            adapter.mkdir()
            manifest = {
                "schema_version": "content-generation.asset-manifest.v1",
                "assets": [
                    {"path": "docs/assets/workspace-dashboard.svg", "role": "supporting"},
                ],
            }
            (adapter / "asset-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (project / "README.md").write_text(
                "# Demo\n\nThis is a substantive README without embedding the asset.\n"
                "It covers the problem, the solution, the architecture, and testing details.\n",
                encoding="utf-8",
            )
            errors = check_manifest_assets_referenced(adapter, project)
            self.assertTrue(
                any("workspace-dashboard.svg" in e and "never referenced" in e for e in errors),
                f"Expected unreferenced asset error, got: {errors}",
            )

    def test_manifest_assets_referenced_skips_rejected_assets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            adapter = project / ".content-system"
            adapter.mkdir()
            manifest = {
                "schema_version": "content-generation.asset-manifest.v1",
                "assets": [
                    {
                        "path": "assets/draft-hero-rejected.png",
                        "role": "hero",
                        "review": "rejected",
                    },
                ],
            }
            (adapter / "asset-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (project / "README.md").write_text(
                "# Demo\n\nA substantive README without rejected assets.\n",
                encoding="utf-8",
            )
            errors = check_manifest_assets_referenced(adapter, project)
            self.assertEqual(errors, [])

    def test_human_output_naming_rejects_opaque_and_junk_basenames(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            docs = project / "docs"
            docs.mkdir()
            (docs / "diagram-p0-123456.png").write_bytes(b"png")
            (docs / "audio_pitch-plus-8st_speed-0pct.mp3").write_bytes(b"mp3")
            (docs / "a1b2c3d4e5f67890.svg").write_bytes(b"svg")
            (docs / "clean-diagram.png").write_bytes(b"png")

            errors = check_human_output_naming(project)
            self.assertTrue(any("hashy junk" in e for e in errors))
            self.assertTrue(any("robot key=value" in e for e in errors))
            self.assertTrue(any("opaque hex hash" in e for e in errors))
            # clean-diagram.png should not be flagged
            self.assertFalse(any("clean-diagram" in e for e in errors))

    def test_docs_hsw_tells_rejects_tool_dump_and_ai_jargon(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            docs = project / "docs"
            docs.mkdir()
            bad_doc = (
                "# Architecture\n\n"
                "I will now run the test suite to verify our changes.\n\n"
                "This serves as a testament to the groundbreaking technology.\n\n"
                "Here is a code block showing how tool calls work internally:\n"
                "```python\n"
                "# Inside code block, tool_call is allowed\n"
                "def tool_call():\n"
                "    return True\n"
                "```\n"
            )
            (docs / "architecture.md").write_text(bad_doc, encoding="utf-8")
            errors = check_docs_hsw_tells(project)
            self.assertTrue(any("agent/tool-dump tell" in e for e in errors))
            self.assertTrue(any("testament" in e or "groundbreaking" in e for e in errors))

    def test_check_adopter_content_integration_clean(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            adapter = project / ".content-system"
            adapter.mkdir()
            manifest = {
                "schema_version": "content-generation.asset-manifest.v1",
                "assets": [
                    {"path": "assets/workspace-dashboard.png", "role": "hero"},
                ],
            }
            (adapter / "asset-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            assets = project / "assets"
            assets.mkdir()
            (assets / "workspace-dashboard.png").write_bytes(b"\x89PNG\r\n\x1a\n")
            readme = (
                "# Octo Control Plane\n\n"
                "> **One place to reach workspaces, files, and background jobs.**\n\n"
                "Personal files, work projects, and AI agents often end up scattered across "
                "local disks and unrelated cloud drives. Octo gives them one durable workspace "
                "boundary while keeping underlying storage replaceable.\n\n"
                "![Dashboard](assets/workspace-dashboard.png)\n\n"
                "## Why this exists\n\n"
                "Developers and researchers lose track of raw files across workstations. "
                "Octo provides unified metadata and scoped access links.\n\n"
                "## How it works\n\n"
                "Files uploaded through the platform API are cataloged into an operational "
                "database and archived to configured object storage.\n"
            )
            (project / "README.md").write_text(readme, encoding="utf-8")

            errors = check_adopter_content(adapter, project)
            self.assertEqual(errors, [])

    def test_main_cli_returns_zero_on_valid_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            adapter = project / ".content-system"
            adapter.mkdir()
            manifest = {"schema_version": "content-generation.asset-manifest.v1", "assets": []}
            (adapter / "asset-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            readme = (
                "# Octo Control Plane\n\n"
                "> **One place to reach workspaces, files, and background jobs.**\n\n"
                "Personal files, work projects, and AI agents often end up scattered across "
                "local disks and unrelated cloud drives. Octo gives them one durable workspace "
                "boundary while keeping underlying storage replaceable.\n\n"
                "## Why this exists\n\n"
                "Developers lose track of raw files. Octo provides unified metadata.\n"
            )
            (project / "README.md").write_text(readme, encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                exit_code = main([
                    "--adapter", str(adapter),
                    "--project-root", str(project),
                ])
            out = buf.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("ADOPTER_VERIFY status=OK", out)
            self.assertIn("VALID: adopter content contract OK", out)

    def test_main_cli_returns_one_on_stale_bootstrap(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            adapter = project / ".content-system"
            adapter.mkdir()
            manifest = {"schema_version": "content-generation.asset-manifest.v1", "assets": []}
            (adapter / "asset-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            readme = (
                "# Octo\n\n"
                "Repository governance and planning are being initialized under issue #2. "
                "Product implementation starts with the login/workspace slice after that bootstrap is accepted.\n"
            )
            (project / "README.md").write_text(readme, encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                exit_code = main([
                    "--adapter", str(adapter),
                    "--project-root", str(project),
                ])
            out = buf.getvalue()
            self.assertEqual(exit_code, 1)
            self.assertIn("ADOPTER_VERIFY status=FAIL", out)
            self.assertIn("INVALID: adopter content check failed", out)

    def test_manifest_hero_asset_accepts_png(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = Path(tmpdir) / ".content-system"
            adapter.mkdir()
            manifest = {
                "schema_version": "content-generation.asset-manifest.v1",
                "assets": [{"path": "assets/hero-story.png", "role": "hero"}],
            }
            (adapter / "asset-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(check_manifest_hero_asset_format(adapter), [])

    def test_manifest_hero_asset_rejects_svg(self):
        # CGM #34: workspace-dashboard.svg registered as the hero banner in octo-database
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = Path(tmpdir) / ".content-system"
            adapter.mkdir()
            manifest = {
                "schema_version": "content-generation.asset-manifest.v1",
                "assets": [{"path": "docs/assets/workspace-dashboard.svg", "role": "hero"}],
            }
            (adapter / "asset-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            errors = check_manifest_hero_asset_format(adapter)
            self.assertTrue(any("must be a PNG" in e and "workspace-dashboard.svg" in e for e in errors), errors)

    def test_manifest_hero_asset_rejects_svg_orientation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = Path(tmpdir) / ".content-system"
            adapter.mkdir()
            manifest = {
                "schema_version": "content-generation.asset-manifest.v1",
                "assets": [{"path": "assets/hero-story.png", "role": "hero", "orientation": "svg"}],
            }
            (adapter / "asset-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            errors = check_manifest_hero_asset_format(adapter)
            self.assertTrue(any("must be a PNG" in e for e in errors), errors)

    def test_manifest_hero_asset_rejects_non_png_raster(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = Path(tmpdir) / ".content-system"
            adapter.mkdir()
            manifest = {
                "schema_version": "content-generation.asset-manifest.v1",
                "assets": [{"path": "assets/hero-story.jpg", "role": "hero"}],
            }
            (adapter / "asset-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            errors = check_manifest_hero_asset_format(adapter)
            self.assertTrue(any(".png extension" in e for e in errors), errors)

    def test_manifest_hero_asset_ignores_non_hero_roles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = Path(tmpdir) / ".content-system"
            adapter.mkdir()
            manifest = {
                "schema_version": "content-generation.asset-manifest.v1",
                "assets": [{"path": "docs/assets/flow.svg", "role": "supporting"}],
            }
            (adapter / "asset-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(check_manifest_hero_asset_format(adapter), [])

    def test_readme_hero_format_rejects_svg_hero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "README.md").write_text(
                "# Octo\n\n![Dashboard](docs/assets/workspace-dashboard.svg)\n\n"
                "A substantive description of the product and its audience.\n",
                encoding="utf-8",
            )
            errors = check_readme_hero_format(project)
            self.assertTrue(any("must be a PNG image, not an SVG" in e for e in errors), errors)

    def test_readme_hero_format_accepts_png_hero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "README.md").write_text(
                "# Octo\n\n![Dashboard](assets/hero-story.png)\n\n"
                "A substantive description of the product and its audience.\n",
                encoding="utf-8",
            )
            self.assertEqual(check_readme_hero_format(project), [])

    def test_readme_hero_format_requires_registered_hero_reference(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            adapter = project / ".content-system"
            adapter.mkdir()
            manifest = {
                "schema_version": "content-generation.asset-manifest.v1",
                "assets": [{"path": "assets/hero-story.png", "role": "hero"}],
            }
            (adapter / "asset-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (project / "README.md").write_text(
                "# Octo\n\n![Other](assets/some-other.png)\n\n"
                "A substantive description of the product and its audience.\n",
                encoding="utf-8",
            )
            errors = check_readme_hero_format(project, adapter)
            self.assertTrue(any("must reference registered PNG hero asset" in e for e in errors), errors)

    def test_adopter_readme_structure_accepts_complete_readme(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            readme = (
                "# Octo Control Plane\n\n"
                "> **One place to reach workspaces, files, and background jobs.**\n\n"
                "![Hero](assets/hero-story.png)\n\n"
                "Personal files, work projects, and AI agents often end up scattered across "
                "local disks and unrelated cloud drives.\n\n"
                "## Why this exists\n\n"
                "Developers and researchers lose track of raw files across workstations.\n\n"
                "## What works today\n\n"
                "| Capability | Status |\n| --- | --- |\n| Scoped links | shipped |\n\n"
                "## Boundaries\n\n"
                "Octo does not replace object storage or provide offline access.\n"
            )
            (project / "README.md").write_text(readme, encoding="utf-8")
            self.assertEqual(check_adopter_readme_structure(project), [])

    def test_adopter_readme_structure_rejects_svg_hero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            readme = (
                "# Octo\n\n![Hero](docs/assets/workspace-dashboard.svg)\n\n"
                "## Why this exists\n\n"
                "A problem narrative long enough to be substantive for the reader.\n\n"
                "| Capability | Status |\n| --- | --- |\n| Links | shipped |\n\n"
                "## Boundaries\n\n"
                "It does not do offline sync.\n"
            )
            (project / "README.md").write_text(readme, encoding="utf-8")
            errors = check_adopter_readme_structure(project)
            self.assertTrue(any("must be a PNG image, not an SVG" in e for e in errors), errors)

    def test_adopter_readme_structure_rejects_missing_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            (project / "README.md").write_text(
                "# Octo\n\nA short developer spec with no narrative structure at all.\n",
                encoding="utf-8",
            )
            errors = check_adopter_readme_structure(project)
            self.assertTrue(any("hero banner" in e for e in errors), errors)
            self.assertTrue(any("problem narrative" in e for e in errors), errors)
            self.assertTrue(any("status/evidence table" in e for e in errors), errors)
            self.assertTrue(any("boundaries section" in e for e in errors), errors)

    def test_adopter_content_structure_gate_off_by_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            adapter = project / ".content-system"
            adapter.mkdir()
            manifest = {"schema_version": "content-generation.asset-manifest.v1", "assets": []}
            (adapter / "asset-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (project / "README.md").write_text(
                "# Octo\n\nA short developer spec with no narrative structure at all.\n",
                encoding="utf-8",
            )
            errors = check_adopter_content(adapter, project)
            self.assertFalse(any("problem narrative" in e for e in errors), errors)
            errors_gated = check_adopter_content(adapter, project, check_readme_structure_enabled=True)
            self.assertTrue(any("problem narrative" in e for e in errors_gated), errors_gated)

    def test_main_cli_check_adopter_readme_flag(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            adapter = project / ".content-system"
            adapter.mkdir()
            manifest = {"schema_version": "content-generation.asset-manifest.v1", "assets": []}
            (adapter / "asset-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (project / "README.md").write_text(
                "# Octo\n\nA short developer spec with no narrative structure at all.\n",
                encoding="utf-8",
            )
            buf = io.StringIO()
            with redirect_stdout(buf):
                exit_code = main([
                    "--adapter", str(adapter),
                    "--project-root", str(project),
                    "--check-adopter-readme",
                ])
            out = buf.getvalue()
            self.assertEqual(exit_code, 1)
            self.assertIn("boundaries section", out)


if __name__ == "__main__":
    unittest.main()
