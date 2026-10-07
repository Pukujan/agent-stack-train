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
    heads = {
        "project-continuity-modules": (PCM_SHA, "src/continuity/__init__.py"),
        "content-generation-modules": (CGM_SHA, "system-version.json"),
        "agent-custom-setup": (ACS_SHA, "registry.json"),
        "observational-issue-ops": (OIO_SHA, "ontology/oio-project.json"),
    }
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
    # Each head here changed something besides the mesh, so the walk-back in
    # certifiable_sha certifies the head itself. The mesh-only case is covered
    # by CertifiableShaTests.
    for repo, (sha, path) in heads.items():
        blobs[f"https://api.github.com/repos/{OWNER}/{repo}/commits?sha=main&per_page=30"] = [{"sha": sha}]
        blobs[f"https://api.github.com/repos/{OWNER}/{repo}/commits/{sha}"] = {"files": [{"filename": path}]}
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


class CertifiableShaTests(unittest.TestCase):
    """A mesh rewrite must not move the certified commit.

    Certifying it would move this component's head, which makes every sibling
    rewrite its mesh, which moves their heads -- a loop the mesh can never
    settle. These pin the walk-back and its fail-safe.
    """

    def history(self, shas: list[str], files: dict[str, list[str]]) -> dict[str, str]:
        served = {f"https://api.github.com/repos/{OWNER}/example/commits/main": json.dumps({"sha": shas[0]})}
        served[f"https://api.github.com/repos/{OWNER}/example/commits?sha=main&per_page=30"] = json.dumps(
            [{"sha": sha} for sha in shas]
        )
        for sha in shas:
            served[f"https://api.github.com/repos/{OWNER}/example/commits/{sha}"] = json.dumps(
                {"files": [{"filename": name} for name in files[sha]]}
            )
        return served

    def certifiable(self, served: dict[str, str]) -> str:
        def fetch(url: str) -> str:
            if url not in served:
                raise AssertionError(url)
            return served[url]

        return refresh_train.certifiable_sha(OWNER, "example", "main", fetch)

    def test_a_mesh_only_head_certifies_the_last_substantive_commit(self) -> None:
        substantive, mesh = "a" * 40, "b" * 40
        served = self.history(
            [mesh, substantive],
            {mesh: ["stack-mesh.json"], substantive: ["src/continuity/__init__.py"]},
        )
        self.assertEqual(self.certifiable(served), substantive)

    def test_a_substantive_head_is_certified_itself(self) -> None:
        substantive, older = "a" * 40, "b" * 40
        served = self.history(
            [substantive, older],
            {substantive: ["src/continuity/__init__.py"], older: ["README.md"]},
        )
        self.assertEqual(self.certifiable(served), substantive)

    def test_consecutive_mesh_rewrites_are_all_skipped(self) -> None:
        substantive = "a" * 40
        meshes = ["b" * 40, "c" * 40, "d" * 40]
        served = self.history(
            meshes + [substantive],
            {sha: ["stack-mesh.json"] for sha in meshes}
            | {substantive: ["registry.json"]},
        )
        self.assertEqual(self.certifiable(served), substantive)

    def test_a_commit_that_also_changes_another_file_is_substantive(self) -> None:
        """Only a change confined to the mesh is skipped."""
        head = "a" * 40
        served = self.history(
            [head],
            {head: ["stack-mesh.json", ".github/workflows/ci.yml"]},
        )
        self.assertEqual(self.certifiable(served), head)

    def test_unreadable_history_falls_back_to_the_head(self) -> None:
        """A failure to read the log certifies the head -- churnier, never wrong.

        A rate-limited or unauthorised listing answers with a JSON object, not
        the array of commits, which is what the API returns in production.
        """
        head = "a" * 40
        served = {f"https://api.github.com/repos/{OWNER}/example/commits/main": json.dumps({"sha": head})}
        served[f"https://api.github.com/repos/{OWNER}/example/commits?sha=main&per_page=30"] = json.dumps(
            {"message": "API rate limit exceeded"}
        )
        self.assertEqual(self.certifiable(served), head)

    def test_a_listing_that_does_not_start_at_the_head_is_not_walked(self) -> None:
        head, other = "a" * 40, "b" * 40
        served = {f"https://api.github.com/repos/{OWNER}/example/commits/main": json.dumps({"sha": head})}
        served[f"https://api.github.com/repos/{OWNER}/example/commits?sha=main&per_page=30"] = json.dumps(
            [{"sha": other}]
        )
        self.assertEqual(self.certifiable(served), head)


if __name__ == "__main__":
    unittest.main()
