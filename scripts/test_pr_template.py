"""The repository's own pull-request template is PCM's generated one (#47).

GitHub reads templates only from the repository root's `.github/`, so the
components' copies never reach this repository's pull requests.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pcm" / "src"))

from continuity.cli import github_pr_template  # noqa: E402


class RootTemplateTests(unittest.TestCase):
    def test_the_root_template_is_pcms(self) -> None:
        root = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
        self.assertEqual(root, github_pr_template(), "copy pcm/.github/pull_request_template.md to .github/")


if __name__ == "__main__":
    unittest.main()
