from __future__ import annotations

import unittest

from continuity.cli import parse_receipt_marker, render_receipt_marker

IDENTITY = {
    "repository": "Pukujan/project-continuity-modules",
    "task_id": "PCM-0026",
    "request_id": "receipt-001",
    "pushed_sha": "736667f" + "a" * 33,
    "destination": "67",
    "kind": "leaf",
    "payload_sha256": "c" * 64,
}


class ReceiptIdentityTests(unittest.TestCase):
    def test_t01_marker_contains_every_identity_field(self) -> None:
        marker = render_receipt_marker(**IDENTITY)
        for value in IDENTITY.values():
            self.assertIn(value, marker)
        self.assertTrue(marker.startswith("<!-- pcm:receipt-v2 "))

    def test_t02_same_inputs_render_the_same_marker(self) -> None:
        self.assertEqual(render_receipt_marker(**IDENTITY), render_receipt_marker(**IDENTITY))

    def test_t03_changed_payload_is_a_different_marker(self) -> None:
        changed = dict(IDENTITY, payload_sha256="d" * 64)
        self.assertNotEqual(render_receipt_marker(**IDENTITY), render_receipt_marker(**changed))

    def test_t04_historical_receipt_marker_is_not_parsed_as_v2(self) -> None:
        historical = "<!-- pcm:receipt PCM-0025 pcm0025-policy-20260924 merge:9328f36 -->"
        self.assertIsNone(parse_receipt_marker(historical))

    def test_t05_unrelated_text_does_not_match(self) -> None:
        self.assertIsNone(parse_receipt_marker("a checkpoint was pushed"))
        parsed = parse_receipt_marker(f"note\n{render_receipt_marker(**IDENTITY)}\ntrail")
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.payload_sha256, IDENTITY["payload_sha256"])


if __name__ == "__main__":
    unittest.main()
