"""Deterministic tests for the PCM-0039 hidden diagram-guidance holdout scorer.

Positive and negative control records are inline; the scenario fixture is
checked for privacy (no leakage of the hidden rubric vocabulary) and the
rubric fixture is checked against the scorer's check names.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.diagram_holdout_scorer import (
    CHECKS,
    applicable,
    extract_fences,
    is_wide,
    label_words,
    node_count,
    score,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "pcm0039_diagram_holdout"

GOOD = """# Issue log: parent receipt POST timeout on checkpoint push

Leaf receipt r-4417 posted cleanly at 2026-09-24T21:14:07Z (HTTP 201); the
parent receipt POST timed out after 30 seconds with no response body.

1. 21:14:07Z checkpoint push of commit 8f31c2d starts the receipt pipeline.
2. 21:14:23Z leaf receipt posted on issue 231 with HTTP 201.
3. 21:14:39Z parent receipt POST times out; no response body.
4. 21:16:02Z retry lookup lists comments on issue 231 and finds nothing.
5. 21:19:10Z manual re-post with the retained idempotency key returns HTTP 200.

```mermaid
graph TD
A[checkpoint push] --> B[leaf receipt posted]
B --> C{parent POST timed out}
C --> D[retry lookup found nothing]
D --> E[manual re-post with idempotency key]
```

Counter-signal: the timeline event at 21:17:44Z showed the comment already
existed before the re-post, so the original POST may have landed.
"""


def _graph(node_count: int, statement: str = "graph TD") -> str:
    lines = [statement]
    for index in range(1, node_count):
        lines.append(f"N{index}[step {index}] --> N{index + 1}[step {index + 1}]")
    return "```mermaid\n" + "\n".join(lines) + "\n```"


def _steps(count: int) -> str:
    return "\n".join(f"{index}. step {index}" for index in range(1, count + 1))


class DiagramHoldoutScorerTests(unittest.TestCase):
    def test_good_record_passes_every_check(self) -> None:
        self.assertEqual(score(GOOD), dict.fromkeys(CHECKS, True))
        self.assertEqual(applicable(GOOD), list(CHECKS))

    def test_wide_flowchart_without_details_fails_exactly_two_checks(self) -> None:
        record = _steps(4) + "\n\n" + _graph(6, "flowchart LR") + "\n"
        scored = score(record)
        self.assertFalse(scored["direction_ok"])
        self.assertFalse(scored["details_when_wide"])
        self.assertEqual([name for name, passed in scored.items() if not passed], ["direction_ok", "details_when_wide"])

    def test_wide_flowchart_with_details_only_fails_direction(self) -> None:
        record = (
            "<details>\n<summary>flow</summary>\n\n"
            + _graph(6, "flowchart LR")
            + "\n\n</details>\n\n"
            + _steps(4)
            + "\n"
        )
        scored = score(record)
        self.assertFalse(scored["direction_ok"])
        self.assertTrue(scored["details_when_wide"])

    def test_big_graph_without_text_alternative_fails_size_and_text(self) -> None:
        scored = score("Narrative only, no ordered steps:\n\n" + _graph(10) + "\n")
        self.assertFalse(scored["size_ok"])
        self.assertFalse(scored["text_alternative"])
        self.assertEqual([name for name, passed in scored.items() if not passed], ["size_ok", "text_alternative"])

    def test_broken_fence_and_renderer_link_fail_shape_and_link(self) -> None:
        record = (
            _steps(4)
            + "\n\n```mermaid\ngraph TD\nA[push] --> B[receipt]\nA--> \n```\n\n"
            + "Rendered: https://viewscreen.githubusercontent.com/?text=abc\n"
        )
        scored = score(record)
        self.assertFalse(scored["syntax_shape_ok"])
        self.assertFalse(scored["no_renderer_link"])
        self.assertEqual(
            [name for name, passed in scored.items() if not passed],
            ["no_renderer_link", "syntax_shape_ok"],
        )

    def test_lr_with_four_nodes_needs_no_details(self) -> None:
        scored = score(_steps(4) + "\n\n" + _graph(4, "flowchart LR") + "\n")
        self.assertTrue(scored["direction_ok"])
        self.assertTrue(scored["details_when_wide"])

    def test_size_boundary_eight_passes_nine_fails(self) -> None:
        self.assertTrue(score(_graph(8))["size_ok"])
        self.assertFalse(score(_graph(9))["size_ok"])

    def test_seven_word_label_fails_size(self) -> None:
        record = (
            "```mermaid\n"
            "graph TD\n"
            "A[checkpoint push receipt timeout retry lookup manual fix] --> B[done]\n"
            "```\n"
        )
        self.assertFalse(score(record)["size_ok"])

    def test_absent_diagram_fails_presence_check(self) -> None:
        scored = score(_steps(5) + "\n")
        self.assertFalse(scored["diagram_present"])
        self.assertTrue(scored["direction_ok"])
        self.assertTrue(scored["details_when_wide"])
        for name, passed in scored.items():
            if name != "diagram_present":
                self.assertTrue(passed, name)

    def test_indented_fences_with_branch_labels_pass(self) -> None:
        # Regression: the holdout's real candidate outputs indent every fence
        # line and use `-->|label|` edges; the shape check must accept them.
        record = (
            _steps(5)
            + "\n\n```mermaid\n"
            + "    graph TD\n"
            + "    A[Checkpoint push starts] --> B[Leaf receipt posted]\n"
            + "    B --> C{Retry or resolve manually}\n"
            + "    C -->|Retry| D[Automatic retry risks duplicate]\n"
            + "    C -->|Manual| E[Marker time decides]\n"
            + "```\n"
        )
        scored = score(record)
        for name, passed in scored.items():
            self.assertTrue(passed, name)

    def test_helper_functions_report_fence_facts(self) -> None:
        inside = "<details>\n<summary>flow</summary>\n\n```mermaid\ngraph TD\nA[start] --> B[done]\n```\n\n</details>\n"
        fences = extract_fences(inside)
        self.assertEqual(len(fences), 1)
        self.assertEqual(node_count(fences[0]), 2)
        self.assertEqual(label_words(fences[0]), 1)
        self.assertFalse(is_wide(fences[0]))
        wide = extract_fences("```mermaid\nflowchart LR\nA --> B\n```")[0]
        self.assertTrue(is_wide(wide))

    def test_scenario_fixture_does_not_leak_rubric_vocabulary(self) -> None:
        text = (FIXTURES / "scenario.md").read_text(encoding="utf-8").lower()
        for banned in ("mermaid", "diagram", "<details>", "graph td", "flowchart"):
            self.assertNotIn(banned, text)
        words = len(text.split())
        self.assertGreaterEqual(words, 250)
        self.assertLessEqual(words, 400)

    def test_rubric_matches_scorer_check_names(self) -> None:
        rubric = json.loads((FIXTURES / "rubric.json").read_text(encoding="utf-8"))
        self.assertEqual(rubric["checks"], list(CHECKS))
        self.assertEqual(rubric["pass_rule"], "all applicable checks pass")
        self.assertEqual(rubric["notes"], "hidden from participants")
        self.assertEqual(applicable("anything"), rubric["checks"])

    def test_scoring_is_deterministic(self) -> None:
        self.assertEqual(score(GOOD), score(GOOD))
        self.assertEqual(score(GOOD), dict.fromkeys(CHECKS, True))


if __name__ == "__main__":
    unittest.main()
