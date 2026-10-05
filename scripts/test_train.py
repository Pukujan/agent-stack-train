#!/usr/bin/env python3
"""Stdlib tests for the train refresh and the adopter check."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_manifest  # noqa: E402
import refresh_train  # noqa: E402

OWNER = "Pukujan"
PCM_SHA = "197f7ba8dab34e9738f85a510a673bc2522b1899"
CGM_SHA = "b487b48c12c375ad8a82016f8bb50fb3c109b443"
ACS_SHA = "c15e53fc17e8158e9182709d5d3b6f255bcc11f2"
OIO_SHA = "469adf1e9cb12b004424118c77270e3ca0e71217"


def spec() -> dict:
    return json.loads((refresh_train.COMPONENTS_PATH).read_text(encoding="utf-8"))


def pages() -> dict[str, str]:
    cgm = {
        "version": "0.5.12",
        "modules": ["brand-foundation", "content-context", "writing-direction", "human-sounding-writing", "human-output-naming", "visual-direction", "image-generation", "html-demo"],
    }
    acs = {"version": "0.2.0"}
    blobs = {
        f"https://api.github.com/repos/{OWNER}/project-continuity-modules/commits/main": {"sha": PCM_SHA},
        f"https://api.github.com/repos/{OWNER}/content-generation-modules/commits/main": {"sha": CGM_SHA},
        f"https://api.github.com/repos/{OWNER}/agent-custom-setup/commits/main": {"sha": ACS_SHA},
        f"https://api.github.com/repos/{OWNER}/observational-issue-ops/commits/main": {"sha": OIO_SHA},
        f"https://api.github.com/repos/{OWNER}/project-continuity-modules/contents/src/continuity/__init__.py?ref={PCM_SHA}": '__version__ = "0.7.0"\n',
        f"https://api.github.com/repos/{OWNER}/project-continuity-modules/contents/PROJECT.md?ref={PCM_SHA}": '{"protocol_version":"0.1.0-draft"}\n{"protocol_version":"0.1.0-draft"}\n',
        f"https://api.github.com/repos/{OWNER}/content-generation-modules/contents/system-version.json?ref={CGM_SHA}": json.dumps(cgm),
        f"https://api.github.com/repos/{OWNER}/agent-custom-setup/contents/registry.json?ref={ACS_SHA}": json.dumps(acs),
        f"https://api.github.com/repos/{OWNER}/observational-issue-ops/releases/latest": {"tag_name": "v0.1.0"},
    }
    return {url: body if isinstance(body, str) else json.dumps(body) for url, body in blobs.items()}


class RefreshTests(unittest.TestCase):
    def test_build_train_reads_default_branch_heads(self) -> None:
        served = pages()

        def fetch(url: str) -> str:
            if url not in served:
                raise AssertionError(url)
            return served[url]

        train = refresh_train.build_train(spec(), fetch, "2026-10-05T12:00:00Z")
        self.assertEqual(train["release_train"], "current")
        self.assertEqual(train["status"], "certified")
        pcm = train["certified"]["project-continuity-modules"]
        self.assertEqual(pcm["version"], "0.7.0")
        self.assertEqual(pcm["cli"], "0.7.0")
        self.assertEqual(pcm["commit"], PCM_SHA)
        self.assertEqual(pcm["protocol_version"], "0.1.0-draft")
        cgm = train["certified"]["content-generation-modules"]
        self.assertEqual(cgm["modules"], 8)
        self.assertEqual(cgm["commit"], CGM_SHA)
        acs = train["certified"]["agent-custom-setup"]
        self.assertEqual(acs["version"], "0.2.0")
        self.assertEqual(acs["module"], "multi-agent-hotload")
        self.assertEqual(train["certified"]["observational-issue-ops"]["version"], "0.1.0")

    def test_unchanged_heads_do_not_rewrite_recorded_at(self) -> None:
        served = pages()
        train = refresh_train.build_train(spec(), served.get, "2026-10-05T12:00:00Z")
        again, changed = refresh_train.refresh(spec(), train, served.get, "2026-10-06T00:00:00Z")
        self.assertFalse(changed)
        self.assertEqual(again["recorded_at"], "2026-10-05T12:00:00Z")

    def test_a_moved_head_is_a_change(self) -> None:
        served = pages()
        train = refresh_train.build_train(spec(), served.get, "2026-10-05T12:00:00Z")
        moved = dict(served)
        moved[f"https://api.github.com/repos/{OWNER}/project-continuity-modules/commits/main"] = json.dumps(
            {"sha": "a" * 40}
        )
        moved[f"https://api.github.com/repos/{OWNER}/project-continuity-modules/contents/src/continuity/__init__.py?ref={'a' * 40}"] = '__version__ = "0.8.0"\n'
        moved[f"https://api.github.com/repos/{OWNER}/project-continuity-modules/contents/PROJECT.md?ref={'a' * 40}"] = '{"protocol_version":"0.1.0-draft"}\n'
        updated, changed = refresh_train.refresh(spec(), train, moved.get, "2026-10-06T00:00:00Z")
        self.assertTrue(changed)
        self.assertEqual(updated["certified"]["project-continuity-modules"]["version"], "0.8.0")
        self.assertEqual(updated["recorded_at"], "2026-10-06T00:00:00Z")

    def test_two_protocol_versions_fail(self) -> None:
        served = pages()
        served[f"https://api.github.com/repos/{OWNER}/project-continuity-modules/contents/PROJECT.md?ref={PCM_SHA}"] = (
            '{"protocol_version":"0.1.0-draft"}\n{"protocol_version":"0.2.0"}\n'
        )
        with self.assertRaises(refresh_train.RefreshError):
            refresh_train.build_train(spec(), served.get, "2026-10-05T12:00:00Z")


class CheckTests(unittest.TestCase):
    def train(self) -> dict:
        served = pages()
        return refresh_train.build_train(spec(), served.get, "2026-10-05T12:00:00Z")

    def manifest(self, **overrides) -> dict:
        document = {
            "schema_version": check_manifest.MANIFEST_SCHEMA,
            "adopter": "example",
            "release_train": "current",
            "source": "https://raw.githubusercontent.com/Pukujan/agent-stack-train/main/stack-releases.json",
            "pins": {name: {} for name in self.train()["certified"]},
        }
        document.update(overrides)
        return document

    def test_empty_pins_follow_the_train(self) -> None:
        self.assertEqual(check_manifest.check(self.manifest(), self.train(), "train"), [])

    def test_a_copied_old_version_disagrees(self) -> None:
        manifest = self.manifest()
        manifest["pins"]["project-continuity-modules"] = {"version": "0.6.0", "commit": "4" * 40}
        errors = check_manifest.check(manifest, self.train(), "train")
        self.assertTrue(any("0.6.0" in error for error in errors))
        self.assertTrue(any("0.7.0" in error for error in errors))

    def test_a_missing_component_disagrees(self) -> None:
        manifest = self.manifest()
        del manifest["pins"]["observational-issue-ops"]
        errors = check_manifest.check(manifest, self.train(), "train")
        self.assertTrue(any("observational-issue-ops" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
