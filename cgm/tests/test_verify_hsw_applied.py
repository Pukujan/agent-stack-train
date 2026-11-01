"""Tests for scripts/verify_hsw_applied.py — always-on HSW gate for every CGM adopter."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts.verify_hsw_applied import (
    check_always_on_contract,
    main,
)

ROOT = Path(__file__).resolve().parents[1]


class VerifyHswAppliedTests(unittest.TestCase):
    def test_contract_mode_passes_on_helper_checkout(self):
        self.assertEqual(check_always_on_contract(ROOT), [])
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["--root", str(ROOT), "--mode", "contract"])
        out = buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("HSW_VERIFY mode=contract status=OK", out)
        self.assertIn("VALID: HSW always-on contract OK", out)

    def test_always_on_fields_present_in_writing_routing(self):
        contract = json.loads((ROOT / "docs" / "writing-routing.json").read_text(encoding="utf-8"))
        inject = contract["acs_prompt_inject"]
        self.assertIs(inject["always_on"], True)
        self.assertIs(inject["opt_in_forbidden"], True)
        self.assertIn("every", str(inject.get("audience", "")).lower())
        surfaces = {str(s).lower() for s in inject["surfaces"]}
        self.assertTrue(any("pull request" in s for s in surfaces))
        self.assertFalse(any("html" in s for s in surfaces))  # retired for HTML (#81)
        block = inject["system_block"].lower()
        self.assertIn("always-on", block)
        self.assertIn("human-sounding-writing", block)
        self.assertIn("opt-in is forbidden", block)
        self.assertIs(contract["always_on_system_block"]["always_on"], True)
        self.assertTrue(contract["acs_verify_entrypoint"].get("hsw_automation"))

    def test_rejects_missing_always_on(self):
        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory) / "cgm"
            (staging / "modules" / "human-sounding-writing").mkdir(parents=True)
            (staging / "modules" / "human-sounding-writing" / "SKILL.md").write_text("# hsw\n", encoding="utf-8")
            (staging / "docs").mkdir()
            bad = {
                "schema_version": "content-generation.writing-routing.v1",
                "human_facing_default": {
                    "load": "human-sounding-writing",
                    "required_load": True,
                    "default_on": True,
                    "covers": ["every human-facing prose task", "GitHub and docs prose"],
                },
                "routes": [
                    {
                        "id": "github_and_docs_prose",
                        "surfaces": ["pull request titles", "commit messages"],
                        "load": "human-sounding-writing",
                    }
                ],
                "acs_prompt_inject": {
                    "instruction": "MUST load hsw for every adopter",
                    "fields": ["routes"],
                    # missing always_on / opt_in_forbidden / system_block
                },
                "acs_verify_entrypoint": {"writing": "x", "full_helper": "y"},
            }
            (staging / "docs" / "writing-routing.json").write_text(json.dumps(bad), encoding="utf-8")
            errors = check_always_on_contract(staging)
            self.assertTrue(any("always_on" in e for e in errors), errors)
            self.assertTrue(any("opt_in_forbidden" in e for e in errors), errors)
            self.assertTrue(any("system_block" in e for e in errors), errors)

    def test_rejects_html_on_the_prose_route(self):
        contract = json.loads((ROOT / "docs" / "writing-routing.json").read_text(encoding="utf-8"))
        for route in contract["routes"]:
            if route["id"] == "github_and_docs_prose":
                route["surfaces"].append("HTML reports")
        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory) / "cgm"
            (staging / "modules" / "human-sounding-writing").mkdir(parents=True)
            (staging / "modules" / "human-sounding-writing" / "SKILL.md").write_text("# hsw\n", encoding="utf-8")
            (staging / "docs").mkdir()
            (staging / "docs" / "writing-routing.json").write_text(json.dumps(contract), encoding="utf-8")
            errors = check_always_on_contract(staging)
            self.assertTrue(any("html reports" in e for e in errors), errors)

    def test_html_mode_is_gone(self):
        with self.assertRaises(SystemExit):
            main(["--root", str(ROOT), "--mode", "acs-html"])


if __name__ == "__main__":
    unittest.main()
