from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from continuity.cli import receipt_checkpoint_line


class ReceiptCheckpointLinkTests(unittest.TestCase):
    def test_checkpoint_inside_the_repo_is_a_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checkpoint = root / "tasks" / "TASK-PCM-0026-github-receipts.md"
            checkpoint.parent.mkdir()
            checkpoint.write_text("task", encoding="utf-8")
            self.assertEqual(
                receipt_checkpoint_line(root, checkpoint),
                "tasks/TASK-PCM-0026-github-receipts.md",
            )

    def test_checkpoint_outside_the_repo_is_not_invented(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as other:
            self.assertEqual(receipt_checkpoint_line(Path(directory), Path(other) / "task.md"), "not supplied")


if __name__ == "__main__":
    unittest.main()
