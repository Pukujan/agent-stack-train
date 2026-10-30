"""Backward-compatible lightweight checkpoint epistemics (#217 / owner decision #144)."""
from __future__ import annotations

import hashlib
import shutil
import tempfile
import unittest
from pathlib import Path

from continuity.cli import (
    ContinuityError,
    build_parser,
    checkpoint_metadata,
    checkpoint_payload_sha256,
    checkpoint_records,
    checkpoint_task,
    validate_checkpoint_structure,
)

ROOT = Path(__file__).parent / "fixtures" / "valid-minimal"


def metadata(**extra):
    config = {"protocol_version": "0.1.0-draft"}
    return checkpoint_metadata(
        config, "PCM-0001", "example-agent", "2026-10-08T12:00:00Z",
        ["bounded job"], ["test returned 0"], ["no approved changes"],
        ["source/test.py"], [], "resume after review", **extra
    )


class CheckpointEpistemicsTests(unittest.TestCase):
    def test_default_metadata_is_byte_compatible_in_shape_and_digest(self):
        m = metadata()
        self.assertNotIn("evidence_class", m)
        self.assertNotIn("supersedes", m)
        self.assertNotIn("as_of", m)
        old_keys = (
            "protocol_version", "task_id", "agent", "completed", "evidence",
            "decisions", "changed", "blocked", "next_action"
        )
        old_payload = {key: m[key] for key in old_keys}
        # This reproduces the previous implementation's payload representation.
        # Verify against the CLI's canonical serializer rather than assuming its spacing.
        from continuity.cli import _json
        digest = hashlib.sha256(_json(old_payload).encode("utf-8")).hexdigest()
        self.assertEqual(checkpoint_payload_sha256(m), digest)

    def test_new_optional_fields_are_in_digest(self):
        m = metadata(evidence_class="observed", supersedes="prior-request", as_of="2026-10-07T12:00:00Z")
        initial = checkpoint_payload_sha256(m)
        for key, new_value in [
            ("evidence_class", "inferred"),
            ("supersedes", "other-request"),
            ("as_of", "2026-10-06T12:00:00Z"),
        ]:
            changed = dict(m, **{key: new_value})
            self.assertNotEqual(initial, checkpoint_payload_sha256(changed))

    def test_invalid_class_rejected(self):
        with self.assertRaisesRegex(ContinuityError, "evidence_class"):
            metadata(evidence_class="assumed")
        with self.assertRaisesRegex(ContinuityError, "supersedes"):
            metadata(supersedes="")

    def test_parser_exposes_optional_fields(self):
        args = build_parser().parse_args([
            "checkpoint", "PCM-0001", "--agent", "fixture", "--next", "review",
            "--evidence-class", "inferred", "--supersedes", "old-request",
            "--as-of", "2026-10-07T00:00:00Z"
        ])
        self.assertEqual("inferred", args.evidence_class)
        self.assertEqual("old-request", args.supersedes)
        self.assertEqual("2026-10-07T00:00:00Z", args.as_of)

    def test_new_checkpoint_records_fields_and_detects_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            shutil.copytree(ROOT, root, dirs_exist_ok=True)
            kw = dict(evidence_class="observed", supersedes="old-request", as_of="2026-10-07T00:00:00Z")
            path = checkpoint_task(
                root, "PCM-0001", "fixture", "2026-10-08T12:00:00Z",
                ["completed"], ["evidence"], ["decision"], ["changed"], [],
                "review before next task", request_id="new-request", **kw
            )
            first = path.read_text(encoding="utf-8")
            records = checkpoint_records(first)
            meta, operation = records[-1]
            self.assertIsNotNone(meta)
            self.assertIsNotNone(operation)
            self.assertEqual("observed", meta["evidence_class"])
            self.assertEqual("old-request", meta["supersedes"])
            self.assertEqual("2026-10-07T00:00:00Z", meta["as_of"])
            self.assertEqual([], validate_checkpoint_structure(root, path, first))

            same = checkpoint_task(
                root, "PCM-0001", "fixture", "2026-10-09T12:00:00Z",
                ["completed"], ["evidence"], ["decision"], ["changed"], [],
                "review before next task", request_id="new-request", **kw
            )
            self.assertEqual(first, same.read_text(encoding="utf-8"))
            with self.assertRaisesRegex(ContinuityError, "different checkpoint payload"):
                checkpoint_task(
                    root, "PCM-0001", "fixture", "2026-10-08T12:00:00Z",
                    ["completed"], ["evidence"], ["decision"], ["changed"], [],
                    "review before next task", request_id="new-request",
                    evidence_class="inferred", supersedes="old-request",
                    as_of="2026-10-07T00:00:00Z"
                )
            tampered = first.replace('"evidence_class":"observed"', '"evidence_class":"inferred"')
            self.assertNotEqual(tampered, first)
            self.assertTrue(any("digest does not match" in e
                                for e in validate_checkpoint_structure(root, path, tampered)))


if __name__ == "__main__":
    unittest.main()
