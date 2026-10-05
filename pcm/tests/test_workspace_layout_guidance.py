"""PCM-0234: every guidance copy names the project-folder worktree path.

PCM #234 moved managed worktrees from a path inside the checkout to the project
folder: the canonical checkout is `<project>/main` and task worktrees sit beside
it at `<project>/worktrees/<TASK-ID>`. The CLI and its generated templates were
updated, but several hand-maintained guidance copies kept the superseded
`<canonical-root>/pcm/worktree/<TASK-ID>` path — a copy that tells an agent to
put a worktree where `continuity validate` now rejects it.

These tests scan the shipped guidance (not append-only task records, which keep
their historical wording on purpose) so the old path cannot come back.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Guidance a reader or agent is told to follow. Task files under tasks/ are
# append-only history and are deliberately excluded.
GUIDANCE_FILES = (
    "SPEC.md",
    "AGENTS.md",
    "HANDOFF.md",
    "docs/ARCHITECTURE.md",
    "docs/HANDOFF_PROTOCOL.md",
    "templates/v1/minimal/HANDOFF.md",
    "templates/v1/software/AGENTS.md",
)

SUPERSEDED = ("pcm/worktree/", "canonical-root>/pcm")


class SupersededWorktreePathTests(unittest.TestCase):
    def test_no_guidance_copy_names_the_superseded_path(self) -> None:
        for relative in GUIDANCE_FILES:
            text = (ROOT / relative).read_text(encoding="utf-8")
            for phrase in SUPERSEDED:
                with self.subTest(path=relative, phrase=phrase):
                    self.assertNotIn(phrase, text)

    def test_worktree_guidance_names_the_project_folder(self) -> None:
        # Every guidance copy that mentions a task worktree must name the
        # project-folder location, so the instruction and the validator agree.
        for relative in GUIDANCE_FILES:
            text = (ROOT / relative).read_text(encoding="utf-8")
            if "worktree" not in text.lower():
                continue
            with self.subTest(path=relative):
                self.assertIn("<project>/worktrees/", text)


if __name__ == "__main__":
    unittest.main()
