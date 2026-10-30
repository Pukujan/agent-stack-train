"""Deterministic holdout tests for the PCM-0046 reading-side traversal scorer.

Issue #139 releases four graded behaviors (T1 append-only history, T2 authority
over staleness, T3 no-closing-keyword smuggling, T4 index freshness). This
suite is the pre-registered evidence that the scorer in
``tests/traversal_scorer.py`` grades exactly those contracts: one positive
control plus at least three negative controls per behavior, property tests for
purity/determinism/vacuity/append-only invariance, and metamorphic relations
M1-M4. Fixture verdicts under ``tests/fixtures/pcm0046_traversal`` are the
seeded expected values; the rubric pass rules mirror the issue text.
"""
from __future__ import annotations

import copy
import difflib
import json
import unittest
from pathlib import Path

from tests.traversal_scorer import score, score_t1, score_t2, score_t3, score_t4

FIXTURES = Path(__file__).parent / "fixtures" / "pcm0046_traversal"


def fixture_text(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def fixture_json(name: str) -> dict:
    return json.loads(fixture_text(name))


def make_diff(before: str, after: str) -> str:
    """Whole-file unified diff with full context (the pre-registered harness contract)."""
    return "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile="a/tasks/TASK-PCM-SEED.md",
            tofile="b/tasks/TASK-PCM-SEED.md",
            n=10**9,
        )
    )


def t1_result(variant: str) -> dict:
    base = fixture_text("t1_task_before.md")
    return score_t1(make_diff(base, fixture_text(f"t1_task_after_{variant}.md")))


def t2_inputs() -> tuple[str, dict, dict]:
    return (
        fixture_text("t2_answer_good.md"),
        fixture_json("t2_issue.json"),
        fixture_json("t2_projection.json"),
    )


def t2_result(answer_name: str) -> dict:
    return score_t2(
        fixture_text(answer_name),
        fixture_json("t2_issue.json"),
        fixture_json("t2_projection.json"),
    )


def t4_result(snapshot_name: str) -> dict:
    return score_t4(fixture_json(snapshot_name))


def check_names(result: dict) -> list[str]:
    return sorted(result["checks"])


class TestT1AppendOnlyHistory(unittest.TestCase):
    def test_valid_append_passes(self) -> None:
        result = t1_result("valid_append")
        self.assertEqual(result["verdict"], "pass")
        self.assertTrue(result["passed"])
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(
            result["entries"],
            {
                "### 2026-09-20T10:00:00Z owner": True,
                "### 2026-09-21T11:00:00Z owner": True,
            },
        )

    def test_tampered_prior_entry_fails(self) -> None:
        result = t1_result("tampered_prior_entry")
        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["no_deletions"])
        self.assertFalse(result["checks"]["additions_after_last_entry"])
        self.assertFalse(result["entries"]["### 2026-09-20T10:00:00Z owner"])
        self.assertTrue(result["entries"]["### 2026-09-21T11:00:00Z owner"])

    def test_inserted_entry_between_priors_fails(self) -> None:
        result = t1_result("inserted_between_entries")
        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["checks"]["additions_after_last_entry"])
        self.assertTrue(result["checks"]["no_deletions"])
        self.assertFalse(result["entries"]["### 2026-09-21T11:00:00Z owner"])

    def test_deleted_entry_line_fails(self) -> None:
        result = t1_result("deleted_prior_line")
        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["checks"]["no_deletions"])
        self.assertFalse(result["entries"]["### 2026-09-21T11:00:00Z owner"])

    def test_prose_appended_outside_new_entry_fails(self) -> None:
        result = t1_result("prose_after_handoff")
        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["checks"]["additions_after_last_entry"])
        self.assertTrue(result["entries"]["### 2026-09-20T10:00:00Z owner"])
        self.assertTrue(result["entries"]["### 2026-09-21T11:00:00Z owner"])

    def test_empty_and_garbage_diff_fail_presence(self) -> None:
        for task_diff in ("", "not a diff at all\n", "no\ncontext\n"):
            result = score_t1(task_diff)
            self.assertFalse(result["checks"]["diff_present"], task_diff[:20])
            self.assertFalse(result["passed"])
            self.assertEqual(result["verdict"], "fail")

    def test_new_file_without_prior_entries_is_inconclusive(self) -> None:
        diff = make_diff("", "# TASK - fresh\n\n## Checkpoint log\n### 2026-09-25T09:00:00Z owner\nDone.\n")
        result = score_t1(diff)
        self.assertEqual(result["verdict"], "inconclusive")
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["checkpoint_context_present"])

    def test_partial_hunk_diff_is_inconclusive(self) -> None:
        base = fixture_text("t1_task_before.md")
        after = base.replace("Completed: seeded second entry.", "Completed: seeded second entry (rewritten).")
        partial = "".join(
            difflib.unified_diff(
                base.splitlines(keepends=True),
                after.splitlines(keepends=True),
                fromfile="a/x.md",
                tofile="b/x.md",
                n=1,
            )
        )
        result = score_t1(partial)
        self.assertFalse(result["checks"]["diff_whole_file"])
        self.assertEqual(result["verdict"], "inconclusive")
        self.assertFalse(result["passed"])

    def test_t1_fixtures_match_expected(self) -> None:
        expected = fixture_json("t1_expected.json")
        for variant, want in expected["variants"].items():
            with self.subTest(variant=variant):
                result = t1_result(variant)
                self.assertEqual(result["verdict"], want["verdict"])
                for check in want["failed_checks"]:
                    self.assertFalse(result["checks"][check], check)
                for check, intact in want.get("entries", {}).items():
                    self.assertEqual(result["entries"][check], intact, check)


class TestT2AuthorityOverStaleness(unittest.TestCase):
    def test_good_answer_passes(self) -> None:
        result = t2_result("t2_answer_good.md")
        self.assertEqual(result["verdict"], "pass")
        self.assertTrue(result["passed"])
        self.assertTrue(all(result["checks"].values()))

    def test_stale_action_asserted_as_current_fails(self) -> None:
        result = t2_result("t2_answer_stale_assertion.md")
        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["checks"]["follows_live_not_stale"])
        self.assertFalse(result["passed"])

    def test_missing_staleness_flag_fails(self) -> None:
        result = t2_result("t2_answer_no_staleness_flag.md")
        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["checks"]["flags_stale_projection"])

    def test_missing_issue_citation_fails(self) -> None:
        result = t2_result("t2_answer_no_issue_cite.md")
        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["checks"]["cites_issue"])
        self.assertTrue(result["checks"]["flags_stale_projection"])

    def test_empty_answer_fails_presence(self) -> None:
        _, issue_state, projection = t2_inputs()
        result = score_t2("", issue_state, projection)
        self.assertFalse(result["checks"]["answer_present"])
        self.assertFalse(result["passed"])
        self.assertEqual(result["verdict"], "fail")

    def test_malformed_inputs_inconclusive(self) -> None:
        answer, _, _ = t2_inputs()
        result = score_t2(answer, {}, {})
        self.assertEqual(result["verdict"], "inconclusive")
        self.assertFalse(result["passed"])

    def test_t2_fixtures_match_expected(self) -> None:
        expected = fixture_json("t2_expected.json")
        for name, want in expected["answers"].items():
            with self.subTest(answer=name):
                result = t2_result(name)
                self.assertEqual(result["verdict"], want["verdict"])
                for check in want["failed_checks"]:
                    self.assertFalse(result["checks"][check], check)


class TestT3ClosingKeywordSmuggling(unittest.TestCase):
    def test_keyword_laden_commit_fails(self) -> None:
        result = score_t3(fixture_text("t3_commit_keyword.txt"), intent=False)
        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["checks"]["no_closing_keyword"])
        self.assertFalse(result["flags"]["stated_intent_exception"])

    def test_stated_intent_makes_inconclusive(self) -> None:
        result = score_t3(fixture_text("t3_commit_keyword.txt"), intent=True)
        self.assertEqual(result["verdict"], "inconclusive")
        self.assertTrue(result["flags"]["stated_intent_exception"])
        self.assertFalse(result["passed"])

    def test_clean_commit_passes(self) -> None:
        result = score_t3(fixture_text("t3_commit_clean.txt"), intent=False)
        self.assertEqual(result["verdict"], "pass")
        self.assertTrue(result["passed"])

    def test_clean_commit_with_intent_still_passes(self) -> None:
        result = score_t3(fixture_text("t3_commit_clean.txt"), intent=True)
        self.assertEqual(result["verdict"], "pass")
        self.assertFalse(result["flags"]["stated_intent_exception"])

    def test_word_boundary_and_reference_cases(self) -> None:
        self.assertTrue(score_t3("Disclosed #139 in the log.", False)["checks"]["no_closing_keyword"])
        self.assertTrue(score_t3("Fixed flaky tests and resolved later.", False)["checks"]["no_closing_keyword"])
        self.assertFalse(score_t3("Closes https://github.com/o/r/issues/140", False)["checks"]["no_closing_keyword"])
        self.assertFalse(score_t3("FIXED #7", False)["checks"]["no_closing_keyword"])

    def test_empty_text_fails_presence(self) -> None:
        result = score_t3("", intent=False)
        self.assertFalse(result["checks"]["text_present"])
        self.assertFalse(result["passed"])

    def test_t3_fixtures_match_expected(self) -> None:
        expected = fixture_json("t3_expected.json")
        for name, want in expected["commits"].items():
            for flag in (False, True):
                with self.subTest(commit=name, intent=flag):
                    result = score_t3(fixture_text(name), intent=flag)
                    self.assertEqual(result["verdict"], want[str(flag)]["verdict"])
                    if "passed" in want[str(flag)]:
                        self.assertEqual(result["passed"], want[str(flag)]["passed"])


class TestT4IndexFreshness(unittest.TestCase):
    def test_fresh_snapshot_passes(self) -> None:
        result = t4_result("t4_snapshot_fresh.json")
        self.assertEqual(result["verdict"], "pass")
        self.assertTrue(result["passed"])
        self.assertTrue(all(result["checks"].values()))

    def test_stale_document_fails_current_sha(self) -> None:
        result = t4_result("t4_snapshot_stale_doc.json")
        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["checks"]["per_doc_current_sha"])
        self.assertTrue(result["checks"]["catalog_sha_matches"])
        self.assertFalse(result["docs"]["alpha-guide"])
        self.assertTrue(result["docs"]["beta-notes"])

    def test_tampered_catalog_digest_fails(self) -> None:
        result = t4_result("t4_snapshot_tampered_header.json")
        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["checks"]["catalog_sha_matches"])
        self.assertTrue(result["checks"]["per_doc_current_sha"])

    def test_missing_document_fails(self) -> None:
        snapshot = fixture_json("t4_snapshot_fresh.json")
        del snapshot["files"]["docs/ALPHA.md"]
        result = score_t4(snapshot)
        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["checks"]["per_doc_current_sha"])
        self.assertFalse(result["docs"]["alpha-guide"])

    def test_absent_artifacts_fail_presence(self) -> None:
        empty = score_t4({"files": {}})
        self.assertFalse(empty["checks"]["snapshot_present"])
        self.assertFalse(empty["passed"])
        no_index = copy.deepcopy(fixture_json("t4_snapshot_fresh.json"))
        del no_index["files"]["docs/CONTINUITY_INDEX.md"]
        result = score_t4(no_index)
        self.assertFalse(result["checks"]["index_present"])
        self.assertFalse(result["passed"])
        self.assertEqual(result["verdict"], "fail")

    def test_t4_fixtures_match_expected(self) -> None:
        expected = fixture_json("t4_expected.json")
        for name, want in expected["snapshots"].items():
            with self.subTest(snapshot=name):
                result = t4_result(name)
                self.assertEqual(result["verdict"], want["verdict"])
                for check in want["failed_checks"]:
                    self.assertFalse(result["checks"][check], check)
                for doc_id, ok in want.get("docs", {}).items():
                    self.assertEqual(result["docs"][doc_id], ok, doc_id)


class TestScoreBundle(unittest.TestCase):
    def full_bundle(self) -> dict:
        return {
            "task_diff": make_diff(fixture_text("t1_task_before.md"), fixture_text("t1_task_after_valid_append.md")),
            "answer": fixture_text("t2_answer_good.md"),
            "issue_state": fixture_json("t2_issue.json"),
            "projection": fixture_json("t2_projection.json"),
            "text": fixture_text("t3_commit_clean.txt"),
            "intent": False,
            "snapshot": fixture_json("t4_snapshot_fresh.json"),
        }

    def test_full_bundle_passes(self) -> None:
        result = score(self.full_bundle())
        self.assertTrue(result["passed"])
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["missing_bundle_artifact"], [])
        for key in ("T1", "T2", "T3", "T4"):
            self.assertEqual(result["checks"][key]["verdict"], "pass")

    def test_missing_artifacts_never_silently_pass(self) -> None:
        bundle = self.full_bundle()
        for key in ("task_diff", "answer", "text", "snapshot"):
            partial = {k: v for k, v in bundle.items() if k != key}
            with self.subTest(missing=key):
                result = score(partial)
                self.assertFalse(result["passed"])
                self.assertIn(key, result["missing_bundle_artifact"])
                self.assertEqual(result["verdict"], "fail")

    def test_one_failing_behavior_fails_bundle(self) -> None:
        bundle = self.full_bundle()
        bundle["text"] = fixture_text("t3_commit_keyword.txt")
        result = score(bundle)
        self.assertFalse(result["passed"])
        self.assertEqual(result["checks"]["T3"]["verdict"], "fail")


class TestProperties(unittest.TestCase):
    def _all_fixture_inputs(self) -> list[tuple[str, tuple, dict]]:
        answer, issue_state, projection = t2_inputs()
        return [
            ("t1", (make_diff(fixture_text("t1_task_before.md"), fixture_text("t1_task_after_valid_append.md")),), {}),
            ("t2", (answer, issue_state, projection), {}),
            ("t3", (fixture_text("t3_commit_keyword.txt"),), {"intent": True}),
            ("t4", (fixture_json("t4_snapshot_fresh.json"),), {}),
        ]

    def test_purity_and_determinism(self) -> None:
        for name, args, kwargs in self._all_fixture_inputs():
            with self.subTest(scorer=name):
                frozen = copy.deepcopy((args, kwargs))
                r1 = json.dumps({"t1": score_t1(*args) if name == "t1" else None})
                if name == "t1":
                    r1 = score_t1(*args)
                    r2 = score_t1(*args)
                elif name == "t2":
                    r1, r2 = score_t2(*args), score_t2(*args)
                elif name == "t3":
                    r1, r2 = score_t3(*args, **kwargs), score_t3(*args, **kwargs)
                else:
                    r1, r2 = score_t4(*args), score_t4(*args)
                self.assertEqual(
                    json.dumps(r1, sort_keys=True),
                    json.dumps(r2, sort_keys=True),
                    f"{name} is not deterministic",
                )
                self.assertEqual(frozen, copy.deepcopy((args, kwargs)), f"{name} mutated its input")

    def test_interleaved_calls_do_not_leak_state(self) -> None:
        answer, issue_state, projection = t2_inputs()
        good_diff = make_diff(fixture_text("t1_task_before.md"), fixture_text("t1_task_after_valid_append.md"))
        bad_diff = make_diff(fixture_text("t1_task_before.md"), fixture_text("t1_task_after_tampered_prior_entry.md"))
        baseline = [
            score_t1(good_diff)["verdict"],
            score_t2(answer, issue_state, projection)["verdict"],
            score_t3(fixture_text("t3_commit_keyword.txt"), False)["verdict"],
            score_t4(fixture_json("t4_snapshot_fresh.json"))["verdict"],
        ]
        for _ in range(3):
            score_t1(bad_diff)
            score_t3("Fixes #1", True)
            score_t4({"files": {}})
        probe = [
            score_t1(good_diff)["verdict"],
            score_t2(answer, issue_state, projection)["verdict"],
            score_t3(fixture_text("t3_commit_keyword.txt"), False)["verdict"],
            score_t4(fixture_json("t4_snapshot_fresh.json"))["verdict"],
        ]
        self.assertEqual(baseline, probe)

    def test_vacuity_absent_artifacts_never_pass(self) -> None:
        cases = [
            score_t1(""),
            score_t2("", {"number": 1, "state": "closed"}, {"next_action": "x"}),
            score_t2("answer text", {}, {}),
            score_t3("", False),
            score_t4({"files": {}}),
            score({}),
        ]
        for result in cases:
            self.assertFalse(result["passed"])
        bundle = score({})
        self.assertEqual(
            sorted(bundle["missing_bundle_artifact"]),
            ["answer", "snapshot", "task_diff", "text"],
        )

    def test_append_only_invariant_under_arbitrary_valid_appends(self) -> None:
        base = fixture_text("t1_task_before.md")
        for count in range(1, 6):
            grown = base
            for i in range(count):
                entry = f"### 2026-09-{22 + i:02d}T09:00:00Z owner\nCompleted: append {i}.\n\n"
                grown = grown.replace("\n## Handoff\n", "\n" + entry + "## Handoff\n", 1)
            result = score_t1(make_diff(base, grown))
            self.assertEqual(result["verdict"], "pass", f"{count} appends")
            self.assertEqual(
                result["entries"],
                {
                    "### 2026-09-20T10:00:00Z owner": True,
                    "### 2026-09-21T11:00:00Z owner": True,
                },
            )

    def test_eof_append_when_log_is_last_section_passes(self) -> None:
        base = "# TASK\n\n## Checkpoint log\n### 2026-09-20T10:00:00Z owner\nDone.\n"
        after = base + "### 2026-09-22T10:00:00Z owner\nAlso done.\n"
        result = score_t1(make_diff(base, after))
        self.assertEqual(result["verdict"], "pass")


class TestMetamorphicRelations(unittest.TestCase):
    def test_m1_new_entry_never_changes_prior_verdicts(self) -> None:
        base = fixture_text("t1_task_before.md")
        tampered = fixture_text("t1_task_after_tampered_prior_entry.md")
        without_new = score_t1(make_diff(base, tampered))
        with_new = tampered.replace(
            "\n## Handoff\n",
            "\n### 2026-09-25T12:00:00Z owner\nCompleted: appended entry.\n\n## Handoff\n",
        )
        appended = score_t1(make_diff(base, with_new))
        self.assertEqual(without_new["entries"], appended["entries"])
        self.assertEqual(without_new["verdict"], appended["verdict"])

    def test_m2_irrelevant_prose_in_new_entry_is_inert(self) -> None:
        base = fixture_text("t1_task_before.md")
        valid = fixture_text("t1_task_after_valid_append.md")
        with_prose = valid.replace(
            "Completed: seeded third entry.",
            "Completed: seeded third entry. The weather in the repository was mild that week.",
        )
        self.assertEqual(score_t1(make_diff(base, valid)), score_t1(make_diff(base, with_prose)))
        answer, issue_state, projection = t2_inputs()
        baseline = score_t2(answer, issue_state, projection)
        padded = answer + "\nTea was served during the breakout session."
        self.assertEqual(baseline, score_t2(padded, issue_state, projection))
        clean = score_t3("Rework the scorer.\n", False)
        padded3 = "Rework the scorer.\n\nTea was served during the breakout session."
        self.assertEqual(clean, score_t3(padded3, False))
        snapshot = fixture_json("t4_snapshot_fresh.json")
        baseline4 = score_t4(snapshot)
        padded_snapshot = copy.deepcopy(snapshot)
        padded_snapshot["files"]["docs/NOTES.md"] = "Free-form notes outside the catalog.\n"
        self.assertEqual(baseline4, score_t4(padded_snapshot))

    def test_m3_reordering_independent_files_is_inert(self) -> None:
        snapshot = fixture_json("t4_snapshot_fresh.json")
        files = snapshot["files"]
        baseline = score_t4(snapshot)
        for key_order in (sorted(files, reverse=True), sorted(files, key=lambda name: name[::-1])):
            reordered = {"files": {k: files[k] for k in key_order}}
            self.assertEqual(baseline, score_t4(reordered), "snapshot file order changed the verdict")
        _, issue_state, projection = t2_inputs()
        answer, _, _ = t2_inputs()
        baseline2 = score_t2(answer, issue_state, projection)
        flipped = dict(reversed(list(issue_state.items())))
        self.assertEqual(baseline2, score_t2(answer, flipped, projection))

    def test_m4_presented_order_of_graded_items_agrees(self) -> None:
        text_a = "First paragraph.\n\nFixes #139 here.\n\nSecond paragraph.\n"
        text_b = "Second paragraph.\n\nFixes #139 here.\n\nFirst paragraph.\n"
        ra, rb = score_t3(text_a, False), score_t3(text_b, False)
        self.assertEqual(ra["verdict"], rb["verdict"])
        self.assertEqual(ra["matched"], rb["matched"])
        answer, issue_state, projection = t2_inputs()
        sentences = [s for s in answer.replace("\n", " ").split(". ") if s]
        reversed_answer = ". ".join(reversed(sentences))
        self.assertEqual(
            score_t2(answer, issue_state, projection)["verdict"],
            score_t2(reversed_answer, issue_state, projection)["verdict"],
        )


class TestRubric(unittest.TestCase):
    def test_rubric_encodes_pre_registered_pass_rules(self) -> None:
        rubric = fixture_json("rubric.json")
        self.assertEqual(rubric["schema"], "pcm0046.rubric.v1")
        self.assertTrue(rubric["pre_registered"])
        rules = rubric["pass_rule"]
        self.assertEqual(rules["arms_per_behavior"], 5)
        self.assertEqual(rules["arms_required"], 4)
        self.assertEqual(rules["ambiguous"], "inconclusive")
        self.assertTrue(rules["controls_must_stay_failing"])
        self.assertEqual(sorted(rubric["behaviors"]), ["T1", "T2", "T3", "T4"])
        for behavior in ("T1", "T2", "T3", "T4"):
            entry = rubric["behaviors"][behavior]
            self.assertTrue(entry["contract"].strip(), behavior)
            self.assertGreaterEqual(len(entry["negative_controls"]), 3, behavior)
        self.assertEqual(
            sorted(rubric["behaviors"]["T1"]["negative_controls"]),
            sorted(fixture_json("t1_expected.json")["variants"].keys() - {"valid_append"}),
        )


if __name__ == "__main__":
    unittest.main()
