from __future__ import annotations

import io
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

from continuity.cli import main
from continuity.current_size import CURRENT_MAX_BYTES, archive_current, current_size_errors

FIXTURE = Path(__file__).parent / "fixtures" / "valid-minimal"
MARKER = '<!-- continuity:current {"active_task": null} -->'


def long_current(paragraphs: int = 40) -> str:
    note = "Program state 2026-09-{:02d}: an old note that later notes superseded. "
    old = "\n\n".join(note.format(n) * 3 for n in range(paragraphs))
    done = "\n".join(f"- TASK-{n:04d} merged." for n in range(80))
    return (
        f"# Current Repository Checkpoint\n\n{MARKER}\n\n"
        f"## Program state\n\nPhase: adoption.\n\n{old}\n\n"
        f"## Completed\n\n{done}\n\n"
        "## Historical next action (superseded)\n\nDo the old thing.\n\n"
        "## Blockers\n\nNone known.\n\n"
        "## Next atomic action\n\nShip the cap.\n"
    )


class CurrentSizeTests(unittest.TestCase):
    def write(self, text: str) -> Path:
        folder = Path(tempfile.mkdtemp(prefix="continuity-current-size-"))
        self.addCleanup(shutil.rmtree, folder, True)
        path = folder / "checkpoints" / "CURRENT.md"
        path.parent.mkdir()
        path.write_text(text, encoding="utf-8")
        return path

    def test_a_short_current_passes_and_a_long_one_names_the_fix(self) -> None:
        self.assertEqual(current_size_errors(self.write("# Current\n\nShort.\n")), [])
        errors = current_size_errors(self.write(long_current()))
        self.assertEqual(len(errors), 1)
        self.assertIn("continuity current archive", errors[0])

    def test_archive_keeps_the_present_and_moves_the_rest(self) -> None:
        path = self.write(long_current())
        history, moved = archive_current(path, date(2026, 10, 31))

        self.assertEqual(history, path.parent / "history" / "2026-10.md")
        text = path.read_text(encoding="utf-8")
        self.assertEqual(current_size_errors(path), [])
        self.assertIn(MARKER, text)
        self.assertIn("Phase: adoption.", text)
        self.assertIn("## Next atomic action\n\nShip the cap.", text)
        self.assertIn("## Blockers", text)
        self.assertIn("history/2026-10.md", text)
        self.assertNotIn("## Completed", text)
        self.assertNotIn("superseded)", text)

        archived = history.read_text(encoding="utf-8")
        self.assertIn("## Archived from CURRENT.md on 2026-10-31", archived)
        self.assertIn("### Completed", archived)
        self.assertIn("### Program state (continued)", archived)
        self.assertIn("TASK-0079 merged.", archived)
        self.assertEqual(moved, 3)

    def test_adopter_heading_names_for_the_present_are_kept(self) -> None:
        # nyc-map-agent names its present-tense sections "In flight" and "Next" (#61).
        done = "\n".join(f"- PR {n} merged." for n in range(80))
        path = self.write(
            f"# Current repository checkpoint\n\n{MARKER}\n\n"
            "## Current projection\n\nWhere the work stands.\n\n"
            f"## Completed recently\n\n{done}\n\n"
            "## In flight\n\n- PR 7 is open.\n\n"
            "## Next\n\nMerge PR 7.\n"
        )
        archive_current(path, date(2026, 10, 31))
        kept = path.read_text(encoding="utf-8")
        for heading in ("## Current projection", "## In flight", "## Next"):
            self.assertIn(heading, kept)
        self.assertNotIn("## Completed recently", kept)

    def test_a_second_archive_appends_and_keeps_one_link(self) -> None:
        path = self.write(long_current())
        archive_current(path, date(2026, 10, 31))
        path.write_text(path.read_text(encoding="utf-8") + "\n## Completed\n\n- TASK-0100 merged.\n", encoding="utf-8")
        history, _ = archive_current(path, date(2026, 10, 31))

        self.assertEqual(path.read_text(encoding="utf-8").count("Older state:"), 1)
        self.assertEqual(history.read_text(encoding="utf-8").count("## Archived from CURRENT.md"), 2)

    def test_nothing_to_archive_leaves_current_alone(self) -> None:
        text = f"# Current\n\n{MARKER}\n\n## Next atomic action\n\nShip.\n"
        path = self.write(text)
        self.assertEqual(archive_current(path, date(2026, 10, 31)), (None, 0))
        self.assertEqual(path.read_text(encoding="utf-8"), text)

    def test_validate_fails_an_oversized_current_and_the_command_fixes_it(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="continuity-current-validate-"))
        self.addCleanup(shutil.rmtree, root, True)
        shutil.copytree(FIXTURE, root, dirs_exist_ok=True)
        current = root / "checkpoints" / "CURRENT.md"
        original = current.read_text(encoding="utf-8")
        current.write_text(original + "\n## Completed\n\n" + "- done.\n" * (CURRENT_MAX_BYTES // 8), encoding="utf-8")

        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(main(["validate", "--root", str(root)]), 1)
            self.assertEqual(main(["current", "archive", "--root", str(root), "--date", "2026-10-31"]), 0)
            self.assertEqual(main(["validate", "--root", str(root)]), 0)
        self.assertIn("CURRENT is", out.getvalue())
        self.assertIn("ARCHIVED: 2 section(s)", out.getvalue())  # the fixture has its own Completed


if __name__ == "__main__":
    unittest.main()
