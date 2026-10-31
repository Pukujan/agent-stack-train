#!/usr/bin/env python3
"""Stdlib tests for the adopter check against a release-train document."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_manifest  # noqa: E402

PCM_SHA = "197f7ba8dab34e9738f85a510a673bc2522b1899"
CGM_SHA = "b487b48c12c375ad8a82016f8bb50fb3c109b443"
ACS_SHA = "c15e53fc17e8158e9182709d5d3b6f255bcc11f2"
OIO_SHA = "469adf1e9cb12b004424118c77270e3ca0e71217"


def example_train() -> dict:
    """A small train with fixed values, so these tests do not move with stack-releases.json."""
    return {
        "schema_version": check_manifest.TRAIN_SCHEMA,
        "release_train": "current",
        "published_by": "https://github.com/Pukujan/agent-stack-train",
        "recorded_at": "2026-10-05T12:00:00Z",
        "status": "certified",
        "certified": {
            "project-continuity-modules": {
                "version": "0.7.0",
                "commit": PCM_SHA,
                "cli": "0.7.0",
                "protocol_version": "0.1.0-draft",
                "role": "Execution continuity.",
            },
            "content-generation-modules": {
                "version": "0.5.12",
                "commit": CGM_SHA,
                "modules": 8,
                "role": "Narrative and styling authority.",
            },
            "agent-custom-setup": {
                "version": "0.2.0",
                "commit": ACS_SHA,
                "module": "multi-agent-hotload",
                "role": "Install surface.",
            },
            "observational-issue-ops": {
                "version": "0.1.0",
                "commit": OIO_SHA,
                "role": "Issue-log ticketing system.",
            },
        },
    }


class CheckTests(unittest.TestCase):
    def train(self) -> dict:
        return example_train()

    def manifest(self, **overrides) -> dict:
        document = {
            "schema_version": check_manifest.MANIFEST_SCHEMA,
            "adopter": "example",
            "release_train": "current",
            "source": "https://raw.githubusercontent.com/Pukujan/agent-stack-train/main/stack-releases.json",
            "pins": {name: {} for name in self.train()["certified"]},
        }
        document.update(overrides)
        return document

    def test_empty_pins_follow_the_train(self) -> None:
        self.assertEqual(check_manifest.check(self.manifest(), self.train(), "train"), [])

    def test_a_copied_old_version_disagrees(self) -> None:
        manifest = self.manifest()
        manifest["pins"]["project-continuity-modules"] = {"version": "0.6.0", "commit": "4" * 40}
        errors = check_manifest.check(manifest, self.train(), "train")
        self.assertTrue(any("0.6.0" in error for error in errors))
        self.assertTrue(any("0.7.0" in error for error in errors))

    def test_a_missing_component_disagrees(self) -> None:
        manifest = self.manifest()
        del manifest["pins"]["observational-issue-ops"]
        errors = check_manifest.check(manifest, self.train(), "train")
        self.assertTrue(any("observational-issue-ops" in error for error in errors))

    def test_an_uncertified_pin_disagrees(self) -> None:
        manifest = self.manifest()
        manifest["pins"]["not-a-component"] = {}
        errors = check_manifest.check(manifest, self.train(), "train")
        self.assertTrue(any("'not-a-component', which the train does not certify" in e for e in errors))

    def stack_train(self) -> dict:
        train = self.train()
        train["certified"][check_manifest.STACK] = {"version": "1.0.0", "commit": "5" * 40, "role": "stack"}
        return train

    def test_a_stack_pin_alone_follows_the_train(self) -> None:
        manifest = self.manifest(pins={check_manifest.STACK: {}})
        self.assertEqual(check_manifest.check(manifest, self.stack_train(), "train"), [])

    def test_component_pins_still_agree_once_the_stack_is_certified(self) -> None:
        self.assertEqual(check_manifest.check(self.manifest(), self.stack_train(), "train"), [])

    def test_a_stack_pin_fails_until_the_train_certifies_it(self) -> None:
        manifest = self.manifest(pins={check_manifest.STACK: {}})
        errors = check_manifest.check(manifest, self.train(), "train")
        self.assertEqual(errors, ["manifest pins 'agent-stack-train', which the train does not certify"])

    def test_a_stack_pin_is_not_mixed_with_component_pins(self) -> None:
        pins = {check_manifest.STACK: {}, "project-continuity-modules": {}}
        errors = check_manifest.check(self.manifest(pins=pins), self.stack_train(), "train")
        self.assertEqual(len(errors), 1)
        self.assertIn("pin it alone", errors[0])

    def test_a_copied_old_stack_commit_disagrees(self) -> None:
        manifest = self.manifest(pins={check_manifest.STACK: {"commit": "6" * 40}})
        errors = check_manifest.check(manifest, self.stack_train(), "train")
        self.assertTrue(any("agent-stack-train: pinned commit" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
