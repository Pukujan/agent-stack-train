#!/usr/bin/env python3
"""Stdlib tests for which files reach Octo and how a gateway timeout is handled."""
from __future__ import annotations

import sys
import unittest
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import octo_sync as sync  # noqa: E402

NOW = datetime(2026, 10, 31, 12, tzinfo=timezone.utc)
A, B = "sha256:" + "a" * 64, "sha256:" + "b" * 64


def remote(hash_=A, chunks=3, age=timedelta(hours=1), doc="d1") -> sync.Remote:
    return sync.Remote(doc, hash_, chunks, NOW - age)


class MemoryPathTests(unittest.TestCase):
    def test_memory_files_are_selected(self) -> None:
        for path in ("pcm/checkpoints/CURRENT.md", "checkpoints/CURRENT.md",
                     "acs/checkpoints/history/2026-10.md", "oio/tasks/TASK-OIO-0005-installer.md",
                     "pcm/PROJECT.md", "pcm/docs/research/PCM-0050-epistemic-bitemporal-records.md"):
            with self.subTest(path=path):
                self.assertTrue(sync.is_memory_path(path))

    def test_templates_code_and_deep_copies_are_not(self) -> None:
        for path in ("pcm/templates/v1/minimal/PROJECT.md", "pcm/src/continuity/cli.py",
                     "acs/modules/x/tasks/TASK-1.md", "pcm/tasks/README.md", "README.md",
                     "pcm/docs/plans/PCM-0046-arm-plan.md"):
            with self.subTest(path=path):
                self.assertFalse(sync.is_memory_path(path))


class PlanTests(unittest.TestCase):
    def actions(self, local, remote_docs):
        return {s.path: s.action for s in sync.plan(local, remote_docs, NOW)}

    def test_new_and_changed_files_are_sent(self) -> None:
        got = self.actions({"pcm/PROJECT.md": A, "acs/PROJECT.md": B}, {"acs/PROJECT.md": remote(A)})
        self.assertEqual(got, {"pcm/PROJECT.md": "ingest", "acs/PROJECT.md": "ingest"})

    def test_an_unchanged_indexed_file_is_skipped(self) -> None:
        self.assertEqual(self.actions({"pcm/PROJECT.md": A}, {"pcm/PROJECT.md": remote(A)}),
                         {"pcm/PROJECT.md": "skip"})

    def test_a_file_gone_from_git_is_deleted(self) -> None:
        got = sync.plan({}, {"pcm/tasks/TASK-PCM-1-x.md": remote()}, NOW)
        self.assertEqual([(s.action, s.document_id) for s in got], [("delete", "d1")])

    def test_documents_that_are_not_memory_paths_are_left_alone(self) -> None:
        self.assertEqual(sync.plan({}, {"someone-elses-notes.md": remote()}, NOW), [])

    def test_a_version_still_indexing_is_left_to_finish(self) -> None:
        got = self.actions({"pcm/PROJECT.md": A}, {"pcm/PROJECT.md": remote(chunks=0, age=timedelta(minutes=2))})
        self.assertEqual(got, {"pcm/PROJECT.md": "skip"})

    def test_a_version_stuck_without_chunks_is_sent_again(self) -> None:
        got = self.actions({"pcm/PROJECT.md": A}, {"pcm/PROJECT.md": remote(chunks=0, age=timedelta(hours=2))})
        self.assertEqual(got, {"pcm/PROJECT.md": "reingest"})


class FakeOcto:
    def __init__(self, error, finished_after: int):
        self.error, self.finished_after, self.polls = error, finished_after, 0

    def ingest(self, path, text):
        if self.error:
            raise self.error

    def documents(self, only=None):
        self.polls += 1
        done = self.polls >= self.finished_after
        return {"pcm/PROJECT.md": remote(A, chunks=4 if done else 0, age=timedelta(0))}


def fake_clock():
    t = [0.0]

    def sleep(seconds):
        t[0] += seconds

    return sleep, lambda: t[0]


class SendTests(unittest.TestCase):
    def gateway(self, code=524):
        return urllib.error.HTTPError("u", code, "timeout", {}, None)

    def test_a_clean_ingest_needs_no_wait(self) -> None:
        octo = FakeOcto(None, 1)
        self.assertEqual(sync.send(octo, "pcm/PROJECT.md", "x", A), "indexed")
        self.assertEqual(octo.polls, 0)

    def test_a_cloudflare_timeout_waits_for_octo_instead_of_failing(self) -> None:
        sleep, clock = fake_clock()
        octo = FakeOcto(self.gateway(), finished_after=3)
        self.assertEqual(sync.send(octo, "pcm/PROJECT.md", "x", A, sleep, clock), "indexed after a gateway timeout")
        self.assertEqual(octo.polls, 3)

    def test_a_timeout_that_never_finishes_is_reported(self) -> None:
        sleep, clock = fake_clock()
        with self.assertRaises(TimeoutError):
            sync.send(FakeOcto(self.gateway(), finished_after=10_000), "pcm/PROJECT.md", "x", A, sleep, clock)

    def test_other_http_errors_are_not_swallowed(self) -> None:
        with self.assertRaises(urllib.error.HTTPError):
            sync.send(FakeOcto(self.gateway(403), 1), "pcm/PROJECT.md", "x", A)


class NoKeyTests(unittest.TestCase):
    def test_without_the_key_the_sync_skips_and_passes(self) -> None:
        import contextlib, io, os
        saved = os.environ.pop(sync.KEY_ENV, None)
        try:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(sync.main([]), 0)
            self.assertIn("Skipped", out.getvalue())
        finally:
            if saved is not None:
                os.environ[sync.KEY_ENV] = saved


if __name__ == "__main__":
    unittest.main()
