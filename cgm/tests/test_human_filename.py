"""Unit tests for speakable generated artifact filenames (issue #26)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.human_filename import (
    build_basename,
    build_basename_from_dimensions,
    build_relative_path,
    is_accepted_basename,
    is_hashy_junk_basename,
    is_robot_key_value_basename,
    pitch_phrase,
    sanitize_label,
    speed_phrase,
)
from scripts.validate_content_system import (
    check_asset_manifest_human_paths,
    check_human_output_naming_contract,
    is_hashy_junk_basename as validate_is_hashy,
    is_robot_key_value_basename as validate_is_robot,
)


ROOT = Path(__file__).resolve().parents[1]


class HumanFilenameUnitTests(unittest.TestCase):
    def test_speakable_defaults_omitted(self):
        self.assertEqual(build_basename("Song Food", "mp3"), "Song Food.mp3")
        self.assertEqual(build_basename("Song Food", "mp3", pitch=0, speed_pct=0), "Song Food.mp3")
        self.assertEqual(build_basename("Song Food", "mp3", pitch="+0st", speed_pct="0%"), "Song Food.mp3")

    def test_speakable_pitch_and_speed(self):
        self.assertEqual(build_basename("Song Food", "mp3", pitch=8), "Song Food – up 8.mp3")
        self.assertEqual(
            build_basename("Song Food", "mp3", pitch=8, speed_pct=20),
            "Song Food – up 8, 20% faster.mp3",
        )
        self.assertEqual(
            build_basename("Song Food", "mp3", pitch=-4, speed_pct=-10),
            "Song Food – down 4, 10% slower.mp3",
        )

    def test_safe_twin(self):
        self.assertEqual(
            build_basename("Song Food", "mp3", pitch=8, style="safe_twin"),
            "song-food--up-8.mp3",
        )
        self.assertEqual(
            build_basename("Song Food", "mp3", pitch=8, speed_pct=20, style="safe_twin"),
            "song-food--up-8--20-pct-faster.mp3",
        )

    def test_pitch_speed_matrix_unique_and_speakable(self):
        pitches = [None, 8, -4]
        speeds = [None, 20, 10]
        names = set()
        for pitch in pitches:
            for speed in speeds:
                name = build_basename("Song Food", "mp3", pitch=pitch, speed_pct=speed)
                self.assertFalse(is_hashy_junk_basename(name))
                self.assertFalse(is_robot_key_value_basename(name))
                self.assertTrue(is_accepted_basename(name))
                self.assertNotRegex(name, r"-p\d+-[0-9a-f]{6}\.")
                self.assertNotIn("pitch-", name)
                self.assertNotIn("speed-", name)
                names.add(name)
        self.assertEqual(len(names), len(pitches) * len(speeds))

    def test_deterministic_same_inputs(self):
        a = build_basename("Song Food", "mp3", pitch=8, speed_pct=20)
        b = build_basename("Song Food", "mp3", pitch="+8st", speed_pct="20%")
        self.assertEqual(a, b)

    def test_collision_fixture_formerly_shared_p0_stem(self):
        # Two configs that folklore flattened to …-p0-….mp3 now diverge.
        defaults = build_basename("Song Food", "mp3", pitch=0, speed_pct=0)
        pitched = build_basename("Song Food", "mp3", pitch=8, speed_pct=0)
        self.assertEqual(defaults, "Song Food.mp3")
        self.assertEqual(pitched, "Song Food – up 8.mp3")
        self.assertNotEqual(defaults, pitched)

    def test_hash_suffix_only_after_human_labels(self):
        name = build_basename("Song Food", "mp3", pitch=8, content_hash="00e86dabcdef")
        self.assertTrue(name.startswith("Song Food – up 8 "))
        self.assertIn("00e86d", name)
        self.assertTrue(name.endswith(".mp3"))
        self.assertFalse(is_hashy_junk_basename(name))

    def test_phrases_and_sanitize(self):
        self.assertEqual(pitch_phrase(8), "up 8")
        self.assertIsNone(pitch_phrase(0))
        self.assertEqual(speed_phrase(20), "20% faster")
        self.assertIsNone(speed_phrase(0))
        self.assertEqual(sanitize_label("Song Food"), "song-food")
        self.assertEqual(sanitize_label("20% faster"), "20-pct-faster")

    def test_relative_path_and_dimensions_compat(self):
        path = build_relative_path(
            "Song Food",
            "mp3",
            parent="generated/audio",
            pitch=8,
        )
        self.assertEqual(path, "generated/audio/Song Food – up 8.mp3")
        compat = build_basename_from_dimensions(
            [("line", "Song Food"), ("pitch", "+8st"), ("speed", "0%")],
            "mp3",
        )
        self.assertEqual(compat, "Song Food – up 8.mp3")

    def test_reject_hashy_and_robot(self):
        self.assertTrue(is_hashy_junk_basename("song_food-p0-00e86d.mp3"))
        self.assertTrue(is_hashy_junk_basename("song_food-p20-8eb807.wav"))
        self.assertTrue(validate_is_hashy("nested/song_food-p0-00e86d.mp3"))
        self.assertTrue(is_robot_key_value_basename("song-food_pitch-plus-8st_speed-0pct.mp3"))
        self.assertTrue(validate_is_robot("song-food_pitch-plus-8st_speed-20pct.mp3"))
        self.assertFalse(is_robot_key_value_basename("Song Food – up 8.mp3"))
        self.assertFalse(is_hashy_junk_basename("Song Food – up 8.mp3"))
        self.assertFalse(is_hashy_junk_basename("song_food-p0.mp3"))


class FilenameContractTests(unittest.TestCase):
    def test_helper_checkout_has_filename_contract_and_legend(self):
        self.assertEqual(check_human_output_naming_contract(ROOT), [])
        sample = ROOT / "docs" / "filename-legends" / "voice-audio-song-food.json"
        self.assertTrue(sample.is_file())
        self.assertTrue(sample.with_suffix(".md").is_file())

    def test_validator_fails_closed_when_helper_api_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            staging = Path(directory)
            (staging / "modules" / "human-output-naming").mkdir(parents=True)
            (staging / "modules" / "human-output-naming" / "SKILL.md").write_text(
                "# hon\n", encoding="utf-8"
            )
            (staging / "docs").mkdir()
            (staging / "docs" / "HUMAN_OUTPUT_NAMING.md").write_text("# doc\n", encoding="utf-8")
            # Claim the API in the contract, but omit scripts/human_filename.py
            (staging / "docs" / "human-output-naming.json").write_text(
                (
                    '{"schema_version":"content-generation.human-output-naming.v1",'
                    '"application":"must_load","module":"human-output-naming",'
                    '"surfaces":["generated artifact filenames","asset-manifest paths",'
                    '"committed media basenames","filename legends"],'
                    '"basename_styles":{"default":"speakable","optional":"safe_twin"},'
                    '"filename_legends":{"schema_version":"content-generation.filename-legend.v1"},'
                    '"python_api":{"path":"scripts/human_filename.py",'
                    '"required_symbols":["build_basename","build_basename_from_dimensions",'
                    '"build_relative_path","is_accepted_basename","is_hashy_junk_basename",'
                    '"is_robot_key_value_basename","pitch_phrase","sanitize_label","speed_phrase"]},'
                    '"apply_checklist":["a","b","c"]}'
                ),
                encoding="utf-8",
            )
            errors = check_human_output_naming_contract(staging)
            self.assertTrue(
                any("helper module/API is missing" in e for e in errors),
                errors,
            )

    def test_adapter_smoke_rejects_hashy_and_robot_at_0_5_5(self):
        hashy = {
            "assets": [
                {"path": "song_food-p0-00e86d.mp3", "role": "audio", "hash": "ab" * 32},
            ]
        }
        robot = {
            "assets": [
                {
                    "path": "song-food_pitch-plus-8st_speed-0pct.mp3",
                    "role": "audio",
                    "hash": "ab" * 32,
                },
            ]
        }
        self.assertTrue(any("hashy junk basename" in e for e in check_asset_manifest_human_paths(hashy, (0, 5, 5))))
        self.assertTrue(
            any("robot key=value basename" in e for e in check_asset_manifest_human_paths(robot, (0, 5, 5)))
        )
        # Pre-0.5.5 pins are not forced to rename historical paths.
        self.assertEqual(check_asset_manifest_human_paths(hashy, (0, 5, 4)), [])

    def test_adapter_smoke_accepts_speakable_and_requires_feature_legend(self):
        speakable = build_basename("Song Food", "mp3", pitch=8)
        manifest = {
            "assets": [
                {"path": speakable, "role": "audio", "hash": "cd" * 32, "feature": "voice-audio-song-food"},
            ]
        }
        self.assertEqual(check_asset_manifest_human_paths(manifest, (0, 5, 5)), [])

        with tempfile.TemporaryDirectory() as directory:
            adapter = Path(directory)
            # Claiming a feature without a legend fails closed.
            missing = check_asset_manifest_human_paths(manifest, (0, 5, 5), adapter_root=adapter)
            self.assertTrue(any("filename legend" in e or "feature" in e for e in missing), missing)

            legend_dir = adapter / "filename-legends"
            legend_dir.mkdir()
            (legend_dir / "voice-audio-song-food.json").write_text(
                json.dumps(
                    {
                        "schema_version": "content-generation.filename-legend.v1",
                        "feature": "voice-audio-song-food",
                        "glossary": [{"token": "Song Food", "meaning": "identity"}],
                        "files": [
                            {
                                "path": speakable,
                                "identity": "Song Food",
                                "pitch": 8,
                                "speed_pct": None,
                                "style": "speakable",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                check_asset_manifest_human_paths(manifest, (0, 5, 5), adapter_root=adapter),
                [],
            )


if __name__ == "__main__":
    unittest.main()
