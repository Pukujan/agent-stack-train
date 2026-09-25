"""PCM-0053: checkpoint must refuse to publish from a stale base that overlaps
accepted upstream history, and must degrade to a NOTE when origin is offline.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from continuity.cli import ContinuityError, checkpoint_task, publish_checkpoint

FIXTURE = Path(__file__).parent / "fixtures" / "valid-minimal"


class StaleBaseGuardTests(unittest.TestCase):
    def make_repo(self) -> tuple[Path, Path]:
        root = Path(tempfile.mkdtemp(prefix="continuity-sbg-"))
        self.addCleanup(shutil.rmtree, root, True)
        shutil.copytree(FIXTURE, root, dirs_exist_ok=True)
        remote = Path(tempfile.mkdtemp(prefix="continuity-sbg-remote-"))
        self.addCleanup(shutil.rmtree, remote, True)
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", remote], check=True)
        subprocess.run(["git", "init", "-q", "-b", "main", root], check=True)
        subprocess.run(["git", "-C", root, "config", "user.email", "fixture@example.invalid"], check=True)
        subprocess.run(["git", "-C", root, "config", "user.name", "Fixture"], check=True)
        subprocess.run(["git", "-C", root, "add", "."], check=True)
        subprocess.run(["git", "-C", root, "commit", "-qm", "fixture"], check=True)
        subprocess.run(["git", "-C", root, "remote", "add", "origin", str(remote)], check=True)
        subprocess.run(["git", "-C", root, "push", "-q", "-u", "origin", "main"], check=True)
        subprocess.run(["git", "-C", root, "checkout", "-q", "-b", "task/PCM-0001-guard"], check=True)
        return root, remote

    def change_upstream(self, remote: Path, rel: str, text: str) -> None:
        other = Path(tempfile.mkdtemp(prefix="continuity-sbg-upstream-"))
        self.addCleanup(shutil.rmtree, other, True)
        subprocess.run(["git", "clone", "-q", "-b", "main", str(remote), str(other)], check=True)
        subprocess.run(["git", "-C", other, "config", "user.email", "other@example.invalid"], check=True)
        subprocess.run(["git", "-C", other, "config", "user.name", "Other"], check=True)
        (other / rel).write_text(text, encoding="utf-8")
        subprocess.run(["git", "-C", other, "add", "--", rel], check=True)
        subprocess.run(["git", "-C", other, "commit", "-qm", "upstream change"], check=True)
        subprocess.run(["git", "-C", other, "push", "-q", "origin", "main"], check=True)

    def edit_here(self, root: Path, rel: str, text: str) -> None:
        (root / rel).write_text(text, encoding="utf-8")
        subprocess.run(["git", "-C", root, "add", "--", rel], check=True)
        subprocess.run(["git", "-C", root, "commit", "-qm", "product change"], check=True)

    def add_checkpoint(self, root: Path, request_id: str) -> Path:
        return checkpoint_task(
            root,
            "PCM-0001",
            "test-agent",
            "2026-09-25T23:00:00Z",
            ["guard work"],
            ["deterministic test passed"],
            ["stale bases refuse"],
            ["SPEC.md"],
            [],
            "run the suite",
            request_id=request_id,
        )

    def remote_ref(self, remote: Path, branch: str) -> str:
        result = subprocess.run(
            ["git", "--git-dir", str(remote), "rev-parse", "--verify", f"refs/heads/{branch}"],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() if result.returncode == 0 else ""

    def head(self, root: Path) -> str:
        return subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip()

    def test_overlapping_upstream_edit_is_refused_naming_the_file(self) -> None:
        root, remote = self.make_repo()
        self.change_upstream(remote, "SPEC.md", "# upstream spec rewrite\n")
        self.edit_here(root, "SPEC.md", "# local spec rewrite\n")
        task = self.add_checkpoint(root, "overlap-refuse")
        before = self.head(root)

        with self.assertRaises(ContinuityError) as caught:
            publish_checkpoint(root, task, "PCM-0001", "run the suite", request_id="overlap-refuse")

        message = str(caught.exception)
        self.assertIn("stale base", message)
        self.assertIn("SPEC.md", message)
        self.assertIn("--allow-stale-base", message)
        self.assertEqual(self.head(root), before)
        self.assertEqual(self.remote_ref(remote, "task/PCM-0001-guard"), "")

    def test_non_overlapping_upstream_edit_publishes(self) -> None:
        root, remote = self.make_repo()
        self.change_upstream(remote, "HANDOFF.md", "# upstream handoff\n")
        self.edit_here(root, "SPEC.md", "# local spec\n")
        task = self.add_checkpoint(root, "no-overlap")

        commit = publish_checkpoint(root, task, "PCM-0001", "run the suite", request_id="no-overlap")

        self.assertEqual(self.remote_ref(remote, "task/PCM-0001-guard"), commit)

    def test_allow_stale_base_publishes_over_an_overlap(self) -> None:
        root, remote = self.make_repo()
        self.change_upstream(remote, "SPEC.md", "# upstream spec rewrite\n")
        self.edit_here(root, "SPEC.md", "# local spec rewrite\n")
        task = self.add_checkpoint(root, "opt-out")

        commit = publish_checkpoint(
            root, task, "PCM-0001", "run the suite", request_id="opt-out", allow_stale_base=True
        )

        self.assertEqual(self.remote_ref(remote, "task/PCM-0001-guard"), commit)

    def test_up_to_date_branch_publishes(self) -> None:
        root, remote = self.make_repo()
        self.edit_here(root, "SPEC.md", "# local only\n")
        task = self.add_checkpoint(root, "fresh-base")

        commit = publish_checkpoint(root, task, "PCM-0001", "run the suite", request_id="fresh-base")

        self.assertEqual(self.remote_ref(remote, "task/PCM-0001-guard"), commit)

    def test_unreachable_origin_degrades_to_note_and_no_stale_refusal(self) -> None:
        root, remote = self.make_repo()
        self.edit_here(root, "SPEC.md", "# local spec\n")
        task = self.add_checkpoint(root, "offline")
        missing = remote.parent / "no-such-remote"
        subprocess.run(["git", "-C", root, "remote", "set-url", "origin", str(missing)], check=True)

        with self.assertRaises(ContinuityError) as caught:
            publish_checkpoint(root, task, "PCM-0001", "run the suite", request_id="offline")

        self.assertIn("git push", str(caught.exception).lower())
        self.assertNotIn("stale base", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
