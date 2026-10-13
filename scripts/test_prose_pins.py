#!/usr/bin/env python3
"""A stack document may not restate a component pin the certified set does not name.

These pin the match rule the train's CI runs against every stack checkout. The
hard part is not catching the stale pin -- a naive SHA matcher does that -- it is
not catching the *legitimate* commit reference beside it: a permalink to a frozen
revision, a SHA named as evidence, a schema marker's own version, a module's
versioned directory, and the train README's own history of PCM 0.6.0. Issue
agent-stack-train#16 warns that a noisy check gets disabled, so every "does not
false-positive" test here is a regression guard on that noise, not padding.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_prose_pins as check  # noqa: E402

PCM = "project-continuity-modules"
CGM = "content-generation-modules"
ACS = "agent-custom-setup"
OIO = "observational-issue-ops"

# The live certified set as of 2026-10-11 (agent-stack-train#16 reproduction).
PCM_SHA = "85e6aa7a889b57aeef270213c37258194717e358"
CGM_SHA = "5c8c5f167098d04cf96fb1fe449880001a1edd14"
ACS_SHA = "3df982adc008b9caa4b3a9991f77486393c9a30b"
OIO_SHA = "402a46ec9544fddacb8cc366b07c7fc44b096b69"


def certified() -> dict:
    return {
        PCM: {"version": "0.7.0", "commit": PCM_SHA, "cli": "0.7.0"},
        CGM: {"version": "0.5.12", "commit": CGM_SHA},
        ACS: {"version": "0.2.0", "commit": ACS_SHA},
        OIO: {"version": "0.1.0", "commit": OIO_SHA},
    }


def problems(document: str) -> list[str]:
    return check.prose_pin_problems(document, certified())


class StalePinFails(unittest.TestCase):
    def test_a_commit_that_is_no_longer_certified_is_drift(self) -> None:
        document = "| **PCM** - `project-continuity-modules` (CLI 0.7.0 @ `776b468...`) | Continuity. |"
        errors = problems(document)
        self.assertTrue(errors, "a stale commit pin must fail")
        self.assertTrue(any("776b468" in error for error in errors))

    def test_a_matching_commit_pin_passes(self) -> None:
        document = f"| **PCM** - `project-continuity-modules` (CLI 0.7.0 @ `{PCM_SHA[:7]}`) | Continuity. |"
        self.assertEqual(problems(document), [])

    def test_a_full_matching_commit_pin_passes(self) -> None:
        document = f"| **PCM** - `project-continuity-modules` (CLI 0.7.0 @ `{PCM_SHA}`) | Continuity. |"
        self.assertEqual(problems(document), [])

    def test_a_version_only_drift_fails(self) -> None:
        """The sharpest case: PCM CLI 0.6.0 where the certified CLI is 0.7.0."""
        document = "- **Full-stack wiring** - PCM CLI 0.6.0 (@ `4e23854`): PR-only delivery."
        errors = problems(document)
        self.assertTrue(any("0.6.0" in error and "0.7.0" in error for error in errors))

    def test_a_superseded_commit_inside_a_copyable_command_fails(self) -> None:
        document = "#    --skip-cgm-validate and passes --cgm-root <checkout at 6831f91e>"
        errors = problems(document)
        self.assertTrue(any("6831f91e" in error for error in errors))

    def test_a_stale_version_paired_with_a_component_fails_without_a_sha(self) -> None:
        document = "| **Hotloader** | Pins PCM CLI 0.6.0 and Content Generation Modules 0.5.12. |"
        errors = problems(document)
        self.assertEqual(len(errors), 1, "only PCM is stale; CGM 0.5.12 is current")
        self.assertTrue(any("0.6.0" in error and PCM in error for error in errors))

    def test_a_version_is_attributed_to_the_nearest_component_before_it(self) -> None:
        """A line listing two components judges each version against its own."""
        document = "Pins PCM CLI 0.7.0 and Content Generation Modules 0.5.12."
        self.assertEqual(problems(document), [])
        swapped = "Pins PCM CLI 0.5.12 and Content Generation Modules 0.7.0."
        errors = problems(swapped)
        self.assertTrue(any(PCM in error and "0.5.12" in error for error in errors))
        self.assertTrue(any(CGM in error and "0.7.0" in error for error in errors))


class LegitimateReferencesPass(unittest.TestCase):
    """The issue's "Risk Introduced by a Proposed Change": these must NOT flag."""

    def test_a_permalink_to_a_frozen_revision_does_not_false_positive(self) -> None:
        document = (
            "follow the ACS [HOTLOAD.md]"
            f"(https://github.com/Pukujan/agent-custom-setup/blob/{ACS_SHA}/"
            "modules/coordination/multi-agent-hotload/v0.1.0/HOTLOAD.md) install order."
        )
        self.assertEqual(problems(document), [])

    def test_a_permalink_to_a_stale_revision_still_does_not_false_positive(self) -> None:
        """A permalink freezes whatever revision it names; that is its purpose."""
        document = (
            "follow the ACS [HOTLOAD.md]"
            "(https://github.com/Pukujan/agent-custom-setup/blob/264117398e7754d7e91076481cd664b5e197c1d4/"
            "modules/coordination/multi-agent-hotload/v0.1.0/HOTLOAD.md) install order."
        )
        self.assertEqual(problems(document), [])

    def test_a_sha_named_as_evidence_does_not_false_positive(self) -> None:
        """A commit cited as history, with no component name and no pin cue."""
        document = "The mesh advanced in commit 83379c6 on 2026-10-10."
        self.assertEqual(problems(document), [])

    def test_a_policy_marker_schema_version_does_not_false_positive(self) -> None:
        document = '<!-- pcm:policy {"id":"continuity-records","policy_version":"1.3.0","protocol_version":"0.1.0-draft"} -->'
        self.assertEqual(problems(document), [])

    def test_a_module_versioned_directory_does_not_false_positive(self) -> None:
        document = "[`HOTLOAD.md`](modules/coordination/multi-agent-hotload/v0.1.0/HOTLOAD.md)"
        self.assertEqual(problems(document), [])

    def test_an_unpaired_version_mention_does_not_false_positive(self) -> None:
        """A lease, a count, a schema generation: no component, no pin."""
        document = "The boss lease is 30 minutes and the pack has eight modules."
        self.assertEqual(problems(document), [])

    def test_the_train_readme_history_line_does_not_false_positive(self) -> None:
        """The train README's own warning names PCM 0.6.0 as history."""
        document = (
            "Versions are not copied into this README, because a copied table is how the "
            "2026-10-01 snapshot stayed on PCM 0.6.0 after 0.7.0 had shipped."
        )
        self.assertEqual(problems(document), [])

    def test_a_current_pin_stated_correctly_passes(self) -> None:
        document = f"- **CGM** - `content-generation-modules` (0.5.12 @ `{CGM_SHA[:8]}`, eight modules)."
        self.assertEqual(problems(document), [])


class PureAndDefensive(unittest.TestCase):
    def test_an_empty_certified_set_invents_no_drift(self) -> None:
        document = "| **PCM** - project-continuity-modules (CLI 9.9.9 @ `deadbeef`). |"
        self.assertEqual(check.prose_pin_problems(document, {}), [])

    def test_a_malformed_certified_entry_is_skipped_not_crashed(self) -> None:
        document = "Pins PCM CLI 0.7.0."
        self.assertEqual(check.prose_pin_problems(document, {PCM: "not-a-dict"}), [])

    def test_the_function_is_pure_over_text_and_certified_set(self) -> None:
        """No filesystem or network: the same call twice gives the same answer."""
        document = "| **PCM** - project-continuity-modules (CLI 0.6.0 @ `1111111`). |"
        self.assertEqual(problems(document), problems(document))

    def test_a_short_sha_prefix_names_the_full_commit(self) -> None:
        document = f"Pins PCM CLI 0.7.0 at `{PCM_SHA[:7]}`."
        self.assertEqual(problems(document), [])

    def test_line_numbers_survive_stripping(self) -> None:
        """Blanking a permalink keeps length, so the reported line is the true one."""
        document = (
            "First line.\n"
            "Second line.\n"
            "| **PCM** - project-continuity-modules (CLI 0.7.0 @ `776b468`). |\n"
        )
        errors = problems(document)
        self.assertTrue(any(error.startswith("line 3:") for error in errors))


class CliWiring(unittest.TestCase):
    def test_console_safe_folds_unicode_punctuation_for_cp1252(self) -> None:
        self.assertEqual(check.console_safe("dash — en – ellipsis …"), "dash - en - ellipsis ...")


if __name__ == "__main__":
    unittest.main()
