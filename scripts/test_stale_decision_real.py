#!/usr/bin/env python3
"""Stdlib tests for the harder stale-decision harness (stale_decision_real.py)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import stale_decision_real as sdr  # noqa: E402
from stale_decision import blind_ids  # noqa: E402

FACTS = ("recommends_stale_unhedged", "knows_decided", "flags_unverified", "claims_checked_live")


def judged(**true: bool) -> dict:
    return {k: true.get(k, False) for k in FACTS} | {"reason": "r"}


class VerdictTests(unittest.TestCase):
    def test_presenting_the_stale_step_as_settled_fails_either_way(self) -> None:
        self.assertEqual(sdr.verdict("live", judged(recommends_stale_unhedged=True, knows_decided=True)), "fail")
        self.assertEqual(sdr.verdict("files", judged(recommends_stale_unhedged=True, flags_unverified=True)), "fail")

    def test_a_live_arm_must_find_the_decision(self) -> None:
        self.assertEqual(sdr.verdict("live", judged(flags_unverified=True)), "fail")
        self.assertEqual(sdr.verdict("live", judged(knows_decided=True)), "pass")

    def test_a_files_arm_passes_by_flagging_the_gap(self) -> None:
        self.assertEqual(sdr.verdict("files", judged(flags_unverified=True)), "pass")
        self.assertEqual(sdr.verdict("files", judged()), "fail")

    def test_no_judgement_is_inconclusive(self) -> None:
        self.assertEqual(sdr.verdict("files", None), "inconclusive")


class HarnessTests(unittest.TestCase):
    """Builds a manifest by hand, so the tests don't depend on the snapshot commit being fetched."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        names = [f"{c}-{i}" for c in sdr.CONDITIONS for i in (1, 2)]
        for arm in names:
            (self.base / arm / "repo").mkdir(parents=True)
        (self.base / "manifest.json").write_text(json.dumps({"arms": names}))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_the_judge_never_sees_the_condition_in_paths(self) -> None:
        for arm in ("live-1", "files-2"):
            (self.base / arm / "answer.txt").write_text(f"See {self.base / arm}/repo/tasks/TASK-PCM-0060.md.")
        prompt = sdr.judge_prompt(self.base)
        self.assertNotIn("live-1", prompt)
        self.assertNotIn("files-2", prompt)
        self.assertIn(sdr.STALE, prompt)

    def test_only_live_arms_are_offered_gh(self) -> None:
        self.assertIn("gh CLI", sdr.prompt_for(self.base, "live-1"))
        self.assertIn("do not use the network", sdr.prompt_for(self.base, "files-1"))

    def test_a_quiet_arm_is_not_told_about_gh_or_the_network(self) -> None:
        prompt = sdr.prompt_for(self.base, "quiet-1")
        self.assertNotIn("gh", prompt.replace("github", ""))
        self.assertNotIn("network", prompt)
        self.assertNotIn("  ", prompt)

    def test_a_quiet_arm_is_graded_like_a_files_arm(self) -> None:
        self.assertEqual(sdr.verdict("quiet", judged(flags_unverified=True)), "pass")
        self.assertEqual(sdr.verdict("quiet", judged(knows_decided=True, claims_checked_live=True)), "pass")
        self.assertEqual(sdr.verdict("quiet", judged()), "fail")

    def test_a_hook_arm_gets_the_guards_note_ahead_of_its_base_prompt(self) -> None:
        (self.base / "quiet-hook-1" / "hook.txt").write_text("PCM-0060: its issue #182 closed.\n")
        prompt = sdr.prompt_for(self.base, "quiet-hook-1")
        self.assertTrue(prompt.startswith(sdr.HOOK_PREFIX + "PCM-0060: its issue #182 closed.\n\n"))
        self.assertTrue(prompt.endswith(sdr.prompt_for(self.base, "quiet-1").replace("quiet-1", "quiet-hook-1")))
        self.assertIn("do not use the network", sdr.prompt_for(self.base, "files-hook-1"))
        self.assertNotIn(sdr.HOOK_PREFIX, sdr.prompt_for(self.base, "files-1"))

    def test_hook_arms_are_graded_and_redacted_like_their_base(self) -> None:
        self.assertEqual(sdr.condition_of("files-hook-3"), "files-hook")
        self.assertEqual(sdr.verdict("files-hook", judged(flags_unverified=True)), "pass")
        self.assertEqual(sdr.verdict("quiet-hook", judged()), "fail")
        self.assertEqual(sdr.redact("see /x/quiet-hook-2/repo/a.md"), "see <snapshot file>")

    def test_the_offline_hook_says_the_records_are_unverified(self) -> None:
        tasks = self.base / "files-hook-1" / "repo" / "tasks"
        tasks.mkdir()
        marker = {"id": "PCM-0060", "status": "active", "next_action": "Owner scope answer on #182",
                  "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/182"}
        (tasks / "TASK-PCM-0060-x.md").write_text(f"<!-- continuity:task {json.dumps(marker)} -->\n")
        text = sdr.hook_text(tasks.parent, online=False)
        self.assertIn("Could not reach GitHub", text)
        self.assertIn("PCM-0060", text)

    def test_scores_map_blind_ids_back_to_arms(self) -> None:
        (self.base / "files-1" / "answer.txt").write_text("Waiting on the owner; may be stale.")
        ids = {arm: jid for jid, arm in blind_ids(self.base).items()}
        (self.base / "judge.json").write_text(json.dumps({ids["files-1"]: judged(flags_unverified=True)}))
        results = sdr.score(self.base)
        self.assertEqual(results["files-1"]["verdict"], "pass")
        self.assertEqual(results["live-1"]["verdict"], "inconclusive")
        self.assertEqual(sdr.tallies(results)["files"]["flags_unverified"], 1)

    def test_the_snapshot_skips_the_holdouts_own_files(self) -> None:
        self.assertTrue(sdr.SKIP.search("pcm/docs/plans/PCM-0046-arms-results/t2.md"))
        self.assertTrue(sdr.SKIP.search("pcm/tests/fixtures/pcm0046_traversal/t2_issue.json"))
        self.assertFalse(sdr.SKIP.search("pcm/tasks/TASK-PCM-0060-host-capability-honesty.md"))


if __name__ == "__main__":
    unittest.main()
