# Human output naming

Contract for **generated artifact filenames**, **asset-manifest paths**, and
**committed media basenames**. Companion to the soft writing router: titles and
docs use **hsw**; filesystem names use **hon** (`human-output-naming`).

Machine-readable twin: [`docs/human-output-naming.json`](human-output-naming.json)
(`content-generation.human-output-naming.v1`). Skill:
[`modules/human-output-naming/SKILL.md`](../modules/human-output-naming/SKILL.md).
Python API: [`scripts/human_filename.py`](../scripts/human_filename.py).
Filename legends: [`docs/filename-legends/`](filename-legends/).

## Why this exists

After HSW adoption, issue titles and docs became human-readable, but adopters
still emitted junk like `song_food-p0-00e86d.mp3`. The first 0.5.5 draft replaced
that with robot key=value stems (`song-food_pitch-plus-8st_speed-0pct.mp3`) —
still not speakable. Humans need basenames they can say aloud, plus a
**per-feature legend** that explains the words.

## Speakable naming (default)

| Situation | Basename |
| --- | --- |
| Defaults only | `Song Food.mp3` |
| Pitch only | `Song Food – up 8.mp3` |
| Pitch + speed | `Song Food – up 8, 20% faster.mp3` |
| Optional safe twin | `song-food--up-8--20-pct-faster.mp3` |

Rules: **identity → pitch → speed**; **omit default dims**; hash never the
basename (optional field/suffix only after human labels). Folders by identity
are optional; the basename still repeats the identity.

Rejected:

| Shape | Example |
| --- | --- |
| Hashy junk | `song_food-p0-00e86d.mp3` |
| Robot key=value | `song-food_pitch-plus-8st_speed-0pct.mp3` |

## Filename legend (required companion)

Per **module or feature** (not one global dump):

| Location | Who |
| --- | --- |
| `docs/filename-legends/<feature>.md` + `.json` | Helper samples + shared docs |
| `.content-system/filename-legends/<feature>.json` | Adopter adapter (markdown twin encouraged) |

Each legend contains:

1. Plain-language **glossary** of tokens/phrases that feature uses
2. **Associated file paths** that use those terms

Sample: [`filename-legends/voice-audio-song-food.md`](filename-legends/voice-audio-song-food.md).

## Surfaces (MUST load `human-output-naming` / **hon**)

| Surface | Rule |
| --- | --- |
| Generated artifact filenames | Call `build_basename` (or equivalent) before write |
| asset-manifest `path` values (new entries) | Store the speakable (or safe-twin) path; keep `hash` as a field |
| Committed media basenames | Same speakable shape in git |
| Filename legends | Required when new generated assets are claimed (helper ≥ 0.5.5) |

Soft enforcement for *label prose*; structural basename shape + legend presence
**are** validated for helper pins ≥ **0.5.5**.

## Apply checklist

1. Identify the naming surface (artifact file, manifest path, committed media).
2. Choose identity; set pitch/speed only when non-default.
3. **MUST** load `modules/human-output-naming/SKILL.md` and call
   `scripts/human_filename.build_basename` (default speakable; optional
   `style="safe_twin"`).
4. Write or update the **per-feature** filename legend (glossary + file list).
5. Record the human path in the manifest; keep content hash as a separate field
   (optional short hash **suffix** only after human labels).
6. Do not rewrite published blob history to rename old files unless a scoped
   migration says so.

## Short name

**hon** / **HON** is the official short name for `human-output-naming`. Agents
asked for "hon" load this module. The canonical module id and folder remain
`human-output-naming`.

## Validator / ACS

- Full helper check requires the 8th module `human-output-naming`, the
  importable `scripts/human_filename.py` API, and at least one sample legend
  under `docs/filename-legends/`.
- Legend file paths must match speakable or safe-twin helper output; hashy junk
  and robot key=value stems are rejected in new legend / manifest entries.
- Adapter smoke (helper ≥ 0.5.5): reject classic `name-pN-<6hex>.ext` and robot
  stems in asset-manifest paths; when new assets claim a `feature`, require the
  matching `.content-system/filename-legends/<feature>.json` and path membership.
- See [`docs/ACS_VERIFY.md`](ACS_VERIFY.md) and
  [`docs/WRITING_ROUTING.md`](WRITING_ROUTING.md).

## Non-goals

- No forced rewrite of already-published blobs.
- No PCM task/checkpoint path conventions (sibling ownership).
- No NLP grade of label wording in CI.
- No single global filename dump — legends stay divided by module/feature.
