from __future__ import annotations

import unittest

from continuity.cli import ContinuityError, ReceiptSighting, stop_on_concurrent_markers

MARKER = "<!-- pcm:receipt-v2 repository=Pukujan/project-continuity-modules -->"


class ReceiptConflictTests(unittest.TestCase):
    def test_multiple_markers_stop_and_include_links(self) -> None:
        sightings = [
            ReceiptSighting(MARKER, "Pukujan", "https://example.test/1"),
            ReceiptSighting(MARKER, "other", "https://example.test/2"),
        ]
        with self.assertRaises(ContinuityError) as caught:
            stop_on_concurrent_markers(sightings, MARKER, "Pukujan")
        message = str(caught.exception)
        self.assertIn("not an atomic lock", message)
        self.assertIn("https://example.test/1", message)
        self.assertIn("https://example.test/2", message)
        self.assertNotIn("exactly-once", message)

    def test_another_actor_stops(self) -> None:
        sightings = [ReceiptSighting(MARKER, "other", "https://example.test/1")]
        with self.assertRaises(ContinuityError):
            stop_on_concurrent_markers(sightings, MARKER, "Pukujan")

    def test_same_actor_does_not_stop(self) -> None:
        sightings = [ReceiptSighting(MARKER, "Pukujan", "https://example.test/1")]
        stop_on_concurrent_markers(sightings, MARKER, "Pukujan")


if __name__ == "__main__":
    unittest.main()
