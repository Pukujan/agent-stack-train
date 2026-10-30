# Filename legend: Song Food voice/audio

Feature id: `voice-audio-song-food`  
Module: `human-output-naming` (**hon**)  
Machine-readable twin: [`voice-audio-song-food.json`](voice-audio-song-food.json)

This is a **per-feature** legend — not a global dump. Each voice/audio-style
feature (or other module surface) keeps its own glossary and file list.

## Glossary (plain language)

| Token / phrase | What it means |
| --- | --- |
| **Song Food** | The clip identity (line / piece name). Always leads the basename. |
| **up 8** | Pitch raised by 8 semitones from the default. |
| **down 4** | Pitch lowered by 4 semitones from the default. |
| **20% faster** | Playback speed increased by 20% from the default. |
| **10% slower** | Playback speed decreased by 10% from the default. |
| **–** (en dash) | Separates identity from non-default pitch/speed phrases (speakable style). |
| **`--`** | Machine-safe twin separator between identity and modifier segments. |

## Rules (short)

1. Identity first; then pitch; then speed.
2. Omit default pitch and default speed from the basename.
3. Hash is never the basename — optional short suffix only after human labels.
4. Folders by identity are optional; the basename still repeats the identity.

## Associated files

| Path | Style | Note |
| --- | --- | --- |
| `Song Food.mp3` | speakable | Defaults omitted |
| `Song Food – up 8.mp3` | speakable | Pitch only |
| `Song Food – up 8, 20% faster.mp3` | speakable | Pitch + speed |
| `song-food--up-8--20-pct-faster.mp3` | safe_twin | Optional machine-safe twin |

## Rejected shapes (do not add)

| Rejected | Why |
| --- | --- |
| `song_food-p0-00e86d.mp3` | Opaque hashy junk |
| `song-food_pitch-plus-8st_speed-0pct.mp3` | Robot key=value stem — not speakable |

## How to regenerate

```python
from scripts.human_filename import build_basename

build_basename("Song Food", "mp3")
build_basename("Song Food", "mp3", pitch=8)
build_basename("Song Food", "mp3", pitch=8, speed_pct=20)
build_basename("Song Food", "mp3", pitch=8, speed_pct=20, style="safe_twin")
```
