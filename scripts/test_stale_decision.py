#!/usr/bin/env python3
"""Stdlib tests for the trace encoder and the stale-decision baseline harness."""
from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import otlp  # noqa: E402
import stale_decision as sd  # noqa: E402

STALE = "Execute the hosted two-user acceptance on the parent issue"


class EncoderTests(unittest.TestCase):
    def test_varints_match_the_protobuf_spec(self) -> None:
        self.assertEqual(otlp._varint(1), b"\x01")
        self.assertEqual(otlp._varint(300), b"\xac\x02")
        self.assertEqual(len(otlp._varint(-1)), 10)

    def test_values_keep_their_types(self) -> None:
        self.assertEqual(otlp._any_value("a"), b"\x0a\x01a")
        self.assertEqual(otlp._any_value(True), b"\x10\x01")
        self.assertEqual(otlp._any_value(5), b"\x18\x05")
        self.assertEqual(otlp._any_value(0.5), b"\x21" + struct.pack("<d", 0.5))

    def test_a_child_shares_its_parents_trace_and_names_it(self) -> None:
        root = otlp.Span("root")
        child = root.child("child")
        self.assertEqual(child.trace_id, root.trace_id)
        self.assertEqual(child.parent_id, root.span_id)
        self.assertIn(root.span_id, child.end().encode())

    def test_an_error_sets_the_error_status(self) -> None:
        encoded = otlp.Span("x").end(error="boom").encode()
        self.assertTrue(encoded.endswith(b"\x7a\x08" + b"\x12\x04boom\x18\x02"))

    def test_the_request_names_the_service(self) -> None:
        self.assertIn(b"service.name", otlp.export_request([otlp.Span("x").end()], "svc"))


class HarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        sd.stage(self.base, 2)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, arm: str, text: str) -> None:
        (self.base / arm / "answer.txt").write_text(text)

    def test_staging_matches_the_original_t2_bundle(self) -> None:
        self.assertEqual(sd.arms(self.base), ["bare-1", "bare-2", "guided-1", "guided-2"])
        current = (self.base / "bare-1" / "CURRENT.md").read_text()
        self.assertIn("Status: open.", current)
        self.assertIn(STALE, current)
        self.assertEqual(json.loads((self.base / "bare-1" / "issue.json").read_text())["state"], "closed")

    def test_only_guided_arms_get_the_guidance(self) -> None:
        self.assertFalse((self.base / "bare-1" / "GUIDANCE.md").exists())
        self.assertIn("GitHub-owned progression", (self.base / "guided-1" / "GUIDANCE.md").read_text())
        self.assertTrue(sd.prompt_for(self.base, "guided-1").startswith("Read "))
        self.assertNotIn("GUIDANCE", sd.prompt_for(self.base, "bare-1"))

    def test_the_judge_never_sees_the_condition(self) -> None:
        for arm in sd.arms(self.base):
            self.write(arm, f"Read {self.base / arm}/CURRENT.md and .../{arm}/issue.json.")
        prompt = sd.judge_prompt(self.base)
        self.assertNotIn("bare", prompt)
        self.assertNotIn("guided", prompt)
        self.assertEqual(sorted(sd.blind_ids(self.base).values()), sorted(sd.arms(self.base)))

    def test_recommending_the_stale_action_fails_even_with_the_right_words(self) -> None:
        self.write("bare-1", f"#53 is closed, so CURRENT.md is stale. Next: {STALE.lower()}.")
        ids = {arm: jid for jid, arm in sd.blind_ids(self.base).items()}
        (self.base / "judge.json").write_text(json.dumps({ids["bare-1"]: {
            "recommends_stale": True, "states_issue_closed": True, "flags_contradiction": True, "reason": "r"}}))
        row = sd.score(self.base)["bare-1"]
        self.assertEqual(row["follows_live"], "fail")
        self.assertEqual(row["t2_lexical"]["verdict"], "fail")

    def test_a_paraphrased_correct_answer_passes_on_meaning(self) -> None:
        self.write("bare-1", "Issue #53 is closed; the status file no longer reflects reality. Confirm closure.")
        ids = {arm: jid for jid, arm in sd.blind_ids(self.base).items()}
        (self.base / "judge.json").write_text(json.dumps({ids["bare-1"]: {
            "recommends_stale": False, "states_issue_closed": True, "flags_contradiction": True, "reason": "r"}}))
        row = sd.score(self.base)["bare-1"]
        self.assertEqual(row["follows_live"], "pass")
        self.assertEqual(row["t2_lexical"]["verdict"], "fail")  # no "stale"/"superseded": the word match misses it

    def test_missing_answers_and_judgements_are_inconclusive_not_passed(self) -> None:
        counts = sd.tallies(sd.score(self.base))
        self.assertEqual(counts["bare"]["follows_live"]["inconclusive"], 2)
        self.assertEqual(counts["guided"]["t2_lexical"]["pass"], 0)


if __name__ == "__main__":
    unittest.main()
