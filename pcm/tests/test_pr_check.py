from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from continuity.cli import github_pr_template, main
from continuity.pr_check import branch_issue, check_pr_body

GOOD = """Checkpoints could not be published from a component folder, so agents committed them by hand.

## Human outcome

Checkpoints publish from any component folder.

## Before and after

**Before:** the path was relative to the folder and never matched Git's. **After:** it is relative to the top.

<details>
<summary>Diagram</summary>

```mermaid
graph TD
  A[Checkpoint written] --> B{Path base}
  B --> C[Refused]
  B --> D[Published]
```

</details>

## Change and scope

One function.

## What stays unchanged

Everything else.

## Verification

Tests pass.

Closes #38
"""


class PullRequestShapeTests(unittest.TestCase):
    def test_a_reader_first_description_passes(self) -> None:
        self.assertEqual(check_pr_body(GOOD, 38), ([], []))

    def test_the_unfilled_template_fails(self) -> None:
        errors, _ = check_pr_body(github_pr_template())
        self.assertTrue(any("problem sentence" in error for error in errors))
        self.assertTrue(any("template text left unfilled" in error for error in errors))
        self.assertTrue(any("name the issue" in error for error in errors))

    def test_an_opening_reference_or_heading_fails(self) -> None:
        for opening in ("Refs #34", "Closes #12", "## Summary"):
            errors, _ = check_pr_body(opening + "\n\n" + GOOD)
            self.assertTrue(any("open with" in error for error in errors), opening)

    def test_comments_do_not_count_as_the_opening(self) -> None:
        errors, _ = check_pr_body("<!-- guidance -->\n\n" + GOOD)
        self.assertEqual(errors, [])

    def test_each_required_section_is_named_when_missing(self) -> None:
        errors, _ = check_pr_body(GOOD.replace("## What stays unchanged", "## Other"))
        self.assertIn("missing section `## What stays unchanged`", errors)

    def test_finishing_work_should_close_its_issue(self) -> None:
        _, warnings = check_pr_body(GOOD.replace("Closes #38", "Refs #38"), 38)
        self.assertTrue(any("`Closes #38`" in warning for warning in warnings))
        _, warnings = check_pr_body(GOOD, 41)
        self.assertTrue(any("#41 is not named" in warning for warning in warnings))

    def test_no_issue_reference_fails(self) -> None:
        errors, _ = check_pr_body(GOOD.replace("Closes #38", ""))
        self.assertTrue(any("name the issue" in error for error in errors))

    def test_wide_or_unwrapped_diagrams_warn(self) -> None:
        wide = GOOD.replace("graph TD", "graph LR")
        wide = wide.replace("  B --> D[Published]", "  B --> D[Published]\n  D --> E[Done]")
        _, warnings = check_pr_body(wide)
        self.assertTrue(any("graph TD" in warning for warning in warnings))
        unwrapped = GOOD.replace("<details>\n<summary>Diagram</summary>\n", "").replace("</details>\n", "")
        _, warnings = check_pr_body(unwrapped)
        self.assertTrue(any("<details>" in warning for warning in warnings))

    def test_branch_names_carry_their_issue(self) -> None:
        self.assertEqual(branch_issue("fix/47-pr-shape"), 47)
        self.assertEqual(branch_issue("task/PCM-0001-retry"), None)
        self.assertEqual(branch_issue("main"), None)

    def test_the_command_exits_nonzero_on_errors(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            good = Path(folder) / "good.md"
            good.write_text(GOOD, encoding="utf-8")
            bad = Path(folder) / "bad.md"
            bad.write_text("Refs #1\n", encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main(["pr-check", "--body-file", str(good), "--branch", "fix/38-x"]), 0)
                self.assertEqual(main(["pr-check", "--body-file", str(bad)]), 1)
            self.assertIn("PR SHAPE OK", out.getvalue())
            self.assertIn("ERROR: open with the problem", out.getvalue())


if __name__ == "__main__":
    unittest.main()
