---
name: human-output-naming
description: >-
  MUST load before writing generated artifact filenames, asset-manifest paths,
  or committed media basenames. Official short name: hon (also HON); canonical
  module id remains human-output-naming. Produces speakable basenames (identity
  first; omit defaults) plus a required per-feature filename legend. Optional
  machine-safe twin via style=safe_twin. Never opaque p0/hex stems or robot
  key=value stems. Use human-sounding writing (hsw) for label wording voice;
  this module owns the filesystem shape and legend companion.
---

# Human output naming

Official short name: **hon** (also HON). Canonical module id remains
`human-output-naming`.

**MUST load** this module before naming any surface routed to it in
[`docs/WRITING_ROUTING.md`](../../docs/WRITING_ROUTING.md) /
[`docs/writing-routing.json`](../../docs/writing-routing.json) or the sibling
filename contract [`docs/HUMAN_OUTPUT_NAMING.md`](../../docs/HUMAN_OUTPUT_NAMING.md)
(`required_load: true`). Soft = no NLP CI grade of prose labels; the basename
shape **and** the per-feature legend **are** testable.

## When to use

- Generated artifact / output filenames (audio, images, video, demos)
- `asset-manifest.json` `path` values for **new** assets
- Committed media basenames humans skim in a folder
- Writing or updating a **filename legend** for the feature/module that emits those files

## When not to use

- Issue / PR / commit **titles** and docs prose → load `human-sounding-writing` (**hsw**)
- README / product entry story → load `writing-direction`
- PCM task / checkpoint path conventions (sibling ownership; not this module)

## Before / after

| Rejected | Speakable (default) | Optional safe twin |
| --- | --- | --- |
| `song_food-p0-00e86d.mp3` (hashy junk) | `Song Food.mp3` | `song-food.mp3` (identity only) |
| `song-food_pitch-plus-8st_speed-0pct.mp3` (robot key=value) | `Song Food – up 8.mp3` | `song-food--up-8.mp3` |
| same robot stem with speed | `Song Food – up 8, 20% faster.mp3` | `song-food--up-8--20-pct-faster.mp3` |

Rules: **identity → pitch → speed**; **omit default dims**; hash never the
basename (optional field/suffix only after human labels). Folders by identity
are optional; the basename still repeats the identity.

## Filename legend (required companion)

Every feature/module that claims new generated assets **MUST** ship a legend:

- Helper / docs: `docs/filename-legends/<feature>.md` and
  `docs/filename-legends/<feature>.json`
- Adopter adapter: `.content-system/filename-legends/<feature>.json`
  (markdown twin encouraged alongside)

Each legend:

1. Plain-language **glossary** of filename tokens/phrases used by that feature
2. **Associated file paths** that use those terms (divided by module/feature —
   not one global dump)

Sample: [`docs/filename-legends/voice-audio-song-food.md`](../../docs/filename-legends/voice-audio-song-food.md).

## Python API

Importable helper: [`scripts/human_filename.py`](../../scripts/human_filename.py)

```python
from scripts.human_filename import build_basename, is_hashy_junk_basename

build_basename("Song Food", "mp3")
# -> "Song Food.mp3"

build_basename("Song Food", "mp3", pitch=8)
# -> "Song Food – up 8.mp3"

build_basename("Song Food", "mp3", pitch=8, speed_pct=20)
# -> "Song Food – up 8, 20% faster.mp3"

build_basename("Song Food", "mp3", pitch=8, speed_pct=20, style="safe_twin")
# -> "song-food--up-8--20-pct-faster.mp3"

assert is_hashy_junk_basename("song_food-p0-00e86d.mp3")
```

Optional kwargs: `disambiguator=`, `content_hash=` — appended only after the
human labels when a true collision remains. Compatibility wrapper:
`build_basename_from_dimensions` maps `line` / `pitch` / `speed` keys onto the
speakable API (defaults still omitted).

## Operational rules

1. **Speakable by default.** Identity first; add pitch then speed only when
   non-default. Do not emit robot `key-value` stems.
2. **Optional safe twin** via `style="safe_twin"` when a tool cannot store
   spaces / en dashes; keep the speakable name in the legend and prefer it in
   manifests when the filesystem allows.
3. **Legend required** per feature/module when new generated assets are claimed
   (helper ≥ 0.5.5). Listed paths must match speakable or safe-twin helper
   output; hashy junk and robot stems are rejected in new entries.
4. **Determinism:** same identity + pitch + speed + style → same basename.
5. **Hash suffix last:** if two distinct configs somehow still collide, append a
   short content hash **after** the human labels — never instead of them.
6. **Manifest:** store the human path in `asset-manifest` / verifiable output
   records; keep `hash` as a separate field.
7. **Label voice:** prefer pronounceable words (HSW voice for *what* you call
   dimensions). Do not invent README-style bold rules for filenames.
8. **History:** do not rewrite published blob history. Stop emitting new hashy
   or robot basenames on helper pins ≥ 0.5.5.

## Final review

- Can a newcomer read the basename aloud without decoding folklore?
- Are default pitch/speed omitted?
- Does a per-feature legend explain every token and list the associated paths?
- Is any short hex or robot `pitch-…_speed-…` stem the discriminator? If yes, fix.
