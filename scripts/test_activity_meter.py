#!/usr/bin/env python3
"""Stdlib tests for the GitHub activity meter (#108)."""
from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import activity_meter as meter  # noqa: E402

NOW = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)
SINCE = NOW - timedelta(days=7)


def stamp(days_ago: float) -> str:
    return (NOW - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def node(days_ago: float, *comments: float) -> dict:
    return {"createdAt": stamp(days_ago), "comments": {"nodes": [{"createdAt": stamp(c)} for c in comments]}}


class SummarizeTests(unittest.TestCase):
    def test_counts_only_what_was_created_in_the_window(self) -> None:
        repo = {"issues": {"nodes": [node(1, 1, 2, 30), node(30, 3)]},
                "pullRequests": {"nodes": [node(2, 2), node(8)]}}
        self.assertEqual(meter.summarize(repo, SINCE), {"issues": 1, "pulls": 1, "comments": 4, "truncated": False})

    def test_an_empty_or_hidden_repository_counts_zero(self) -> None:
        self.assertEqual(meter.summarize({"issues": None, "pullRequests": {"nodes": []}}, SINCE),
                         {"issues": 0, "pulls": 0, "comments": 0, "truncated": False})

    def test_a_full_page_of_recent_items_is_marked_undercounted(self) -> None:
        repo = {"issues": {"nodes": [node(1)] * meter.PAGE}, "pullRequests": {"nodes": []}}
        self.assertTrue(meter.summarize(repo, SINCE)["truncated"])

    def test_counts_do_not_depend_on_node_order(self) -> None:
        nodes = [node(1, 1), node(3, 2, 9), node(9, 1), node(0.5)]
        a = meter.summarize({"issues": {"nodes": nodes}, "pullRequests": {"nodes": nodes[:2]}}, SINCE)
        b = meter.summarize({"issues": {"nodes": nodes[::-1]}, "pullRequests": {"nodes": nodes[1::-1]}}, SINCE)
        self.assertEqual(a, b)


class TableTests(unittest.TestCase):
    def test_marks_a_repository_over_the_limit_and_one_it_could_not_read(self) -> None:
        busy = {"issues": 10, "pulls": 60, "comments": 100, "truncated": False}
        quiet = {"issues": 2, "pulls": 2, "comments": 3, "truncated": False}
        text = meter.table([("o/busy", busy), ("o/quiet", quiet), ("o/gone", None)], days=7, warn=20)
        self.assertIn("| o/busy | 10 | 60 | 100 | 24.3 | 6.0 | 10.0 | **over** |", text)
        self.assertIn("| o/quiet | 2 | 2 | 3 | 1.0 | 1.0 | 1.5 |  |", text)
        self.assertIn("| o/gone | | | | | | | could not read |", text)

    def test_every_adopter_and_this_repository_are_measured(self) -> None:
        names = meter.repositories()
        self.assertIn(meter.SELF, names)
        self.assertEqual(names, sorted(set(names)))
        self.assertEqual(meter.repositories(meter.SELF), [meter.SELF])


if __name__ == "__main__":
    unittest.main()
