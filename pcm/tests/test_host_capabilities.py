from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from continuity.cli import classify_host, host_capabilities, init_repo, main

ROOT = Path(__file__).parents[1]
STACK = ROOT.parent

# The sentence every generated or checked-in guidance copy carries, so an adopter on
# another host is told which duties stop running there (PCM-0060, #182).
HONESTY = "git-only durability"


def git_repo(remote: str | None) -> Path:
    root = Path(tempfile.mkdtemp(prefix="continuity-host-"))
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    if remote:
        subprocess.run(["git", "-C", str(root), "remote", "add", "origin", remote], check=True)
    return root


class ClassifyHostTests(unittest.TestCase):
    def test_remote_forms_name_their_host(self) -> None:
        cases = {
            "https://github.com/acme/app.git": ("github", "github.com"),
            "git@github.com:acme/app.git": ("github", "github.com"),
            "https://gitlab.com/acme/app.git": ("gitlab", "gitlab.com"),
            "git@gitlab.example.org:acme/app.git": ("gitlab", "gitlab.example.org"),
            "ssh://git@codeberg.org/acme/app.git": ("gitea-forgejo", "codeberg.org"),
            "https://forgejo.internal:3000/acme/app": ("gitea-forgejo", "forgejo.internal"),
            "https://git.example.net/acme/app.git": ("other", "git.example.net"),
            "/srv/git/app.git": ("local", None),
            "file:///srv/git/app.git": ("local", None),
            "": ("none", None),
        }
        for remote, expected in cases.items():
            with self.subTest(remote=remote):
                self.assertEqual(classify_host(remote), expected)


class CapabilityTests(unittest.TestCase):
    def test_github_origin_keeps_every_duty(self) -> None:
        caps = dict(host_capabilities("https://github.com/acme/app.git", {}))
        self.assertTrue(caps["issue authority"].startswith("yes"))
        self.assertTrue(caps["issue receipts"].startswith("yes"))
        self.assertTrue(caps["verified worktree cleanup"].startswith("yes"))
        self.assertTrue(caps["git durability"].startswith("yes"))

    def test_gitlab_origin_states_what_degrades(self) -> None:
        caps = dict(host_capabilities("https://gitlab.com/acme/app.git", {}))
        self.assertTrue(caps["git durability"].startswith("yes"))
        for duty in ("issue authority", "issue receipts", "verified worktree cleanup"):
            with self.subTest(duty=duty):
                self.assertTrue(caps[duty].startswith(("unsupported", "refused")), caps[duty])

    def test_declared_github_tracker_keeps_issue_authority(self) -> None:
        config = {"trackers": {"github": True, "github_repository": "acme/tracker"}}
        caps = dict(host_capabilities("https://gitlab.com/acme/app.git", config))
        self.assertTrue(caps["issue authority"].startswith("yes"))
        self.assertTrue(caps["verified worktree cleanup"].startswith("refused"))

    def test_no_origin_means_local_only(self) -> None:
        caps = dict(host_capabilities("", {}))
        self.assertTrue(caps["git durability"].startswith("local only"))


class PreflightReportTests(unittest.TestCase):
    def run_preflight(self, root: Path) -> str:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(["preflight", "--root", str(root)])
        return out.getvalue()

    def test_preflight_prints_the_host_and_its_capabilities(self) -> None:
        root = git_repo("https://gitlab.com/acme/app.git")
        self.addCleanup(shutil.rmtree, root, True)
        init_repo(root, "minimal", "App", "APP")
        output = self.run_preflight(root)
        self.assertIn("HOST: gitlab (gitlab.com)", output)
        self.assertIn("CAPABILITY: issue authority: unsupported", output)

    def test_preflight_warns_when_config_claims_authority_the_host_lacks(self) -> None:
        root = git_repo("https://gitlab.com/acme/app.git")
        self.addCleanup(shutil.rmtree, root, True)
        init_repo(root, "minimal", "App", "APP", github_authority=True)
        output = self.run_preflight(root)
        self.assertIn("WARNING: .continuity/config.json turns on GitHub issue authority", output)

    def test_preflight_on_github_raises_no_warning(self) -> None:
        root = git_repo("https://github.com/acme/app.git")
        self.addCleanup(shutil.rmtree, root, True)
        init_repo(root, "minimal", "App", "APP")
        output = self.run_preflight(root)
        self.assertIn("HOST: github (github.com)", output)
        self.assertNotIn("WARNING:", output)


class InitAndGuidanceTests(unittest.TestCase):
    def test_init_on_another_host_says_what_it_will_not_do(self) -> None:
        root = git_repo("git@gitlab.example.org:acme/app.git")
        self.addCleanup(shutil.rmtree, root, True)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(["init", "--root", str(root), "--profile", "minimal", "--task-prefix", "APP"])
        self.assertIn("NOTE: origin is gitlab (gitlab.example.org)", out.getvalue())

    def test_init_on_github_prints_no_host_note(self) -> None:
        root = git_repo("https://github.com/acme/app.git")
        self.addCleanup(shutil.rmtree, root, True)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            main(["init", "--root", str(root), "--profile", "minimal", "--task-prefix", "APP"])
        self.assertNotIn("NOTE: origin is", out.getvalue())

    def test_every_guidance_copy_states_the_fallback(self) -> None:
        copies = [p for p in STACK.rglob("*.md")
                  if "worktrees" not in p.relative_to(STACK).parts
                  and "<!-- pcm:github-progression:end -->" in p.read_text(encoding="utf-8", errors="ignore")]
        self.assertTrue(copies)
        for path in copies:
            with self.subTest(path=str(path.relative_to(STACK))):
                self.assertIn(HONESTY, path.read_text(encoding="utf-8").lower())

    def test_generated_guidance_states_the_fallback(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-host-init-"))
        self.addCleanup(shutil.rmtree, root, True)
        init_repo(root, "software", "App", "APP", github_authority=True)
        for rel in ("AGENTS.md", "HANDOFF.md"):
            with self.subTest(path=rel):
                self.assertIn(HONESTY, (root / rel).read_text(encoding="utf-8").lower())

    def test_spec_documents_the_four_operation_adapter_seam(self) -> None:
        spec = (ROOT / "SPEC.md").read_text(encoding="utf-8")
        self.assertIn("### 8.3 Host adapter seam", spec)
        section = spec.split("### 8.3 Host adapter seam", 1)[1].split("\n## ", 1)[0].lower()
        for operation in ("resolve the default branch", "verify issue identity",
                          "post a keyed receipt", "confirm a merge"):
            with self.subTest(operation=operation):
                self.assertIn(operation, section)


if __name__ == "__main__":
    unittest.main()
