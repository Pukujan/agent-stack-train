# Continuity path naming (binding for new paths)

**PCM owns continuity / claim / adopter source-path conventions.** This document is binding for **new** continuity-managed filesystem paths: task files, claim-related paths, adopter source folders, and new checkpoint *prose filenames* when created. It does **not** rewrite merged history or rename historical published blobs.

Generated **artifact / media filenames** are **not** owned here. Those belong to Content Generation Modules (CGM): [content-generation-modules#26](https://github.com/Pukujan/content-generation-modules/issues/26). Adopters that generate content must pin and apply that helper; PCM must not reimplement it.

Aligns with the pronounceable file/folder row in adopter `HUMAN_NAMING` guidance (for example JEV) without vendoring CGM.

## Rule

For every **new** continuity-managed file or folder name:

1. Prefer **pronounceable words** a newcomer can say aloud (`claim_activity_edges.md`, `task-handoff-notes.md`).
2. Keep **existing public paths stable** unless an explicit rename is in the issue/PR scope.
3. Apply the rule **forward-only** — leave merged history and already-published paths alone.
4. Do **not** use agent milestone codes, opaque short hashes, or collapsed multi-dimension tokens as the **main basename stem**.

## Ownership split

| Surface | Owner | Where |
| --- | --- | --- |
| Continuity / claim / adopter **source paths** (tasks, claims, folders, new prose filenames) | **PCM** | This document; hooked from [`TARGET_ADOPTION.md`](TARGET_ADOPTION.md) and init templates |
| **Generated artifact / media filenames** (audio, images, asset-manifest paths) | **CGM** | [content-generation-modules#26](https://github.com/Pukujan/content-generation-modules/issues/26) |

## Reject (bad examples)

These patterns are **forbidden** as the primary stem of a new continuity-managed path:

| Bad pattern | Why |
| --- | --- |
| `m5_kg_…` / `m5_kg_*` | Agent milestone / opaque codes as the basename |
| `*-[0-9a-f]{6}.mp3` (e.g. `song_food-p0-00e86d.mp3`) | Opaque short hash as the discriminator; also CGM artifact territory |
| Bare hex or hash-only stems | Not pronounceable; not skimmable |
| Collapsed pitch-vs-speed tokens as one opaque label | Multi-dimension collision risk; CGM #26 owns the fix for generated media |

## Prefer (good examples)

| Good path | Why |
| --- | --- |
| `claim_activity_edges.md` | Readable claim-related prose name |
| `task-handoff-notes.md` | Pronounceable task/doc name |
| `adopter-source-layout/` | Folder a newcomer can say aloud |
| Readable task filenames that state the outcome in words | Matches PCM issue-log readability for paths |

## Before / after

| Before (reject for new paths) | After (prefer) |
| --- | --- |
| `tasks/m5_kg_claim_pack.md` | `tasks/claim_activity_edges.md` |
| `docs/m4cat_handoff.md` | `docs/task-handoff-notes.md` |
| `artifacts/song_food-p0-00e86d.mp3` | Use CGM #26 helper (e.g. labeled segments such as `song-food_pitch-plus-8st_speed-0pct.mp3`) — **do not invent a PCM media helper** |

## Related

- Adoption checklist and ACS hotload note: [`TARGET_ADOPTION.md`](TARGET_ADOPTION.md)
- ACS / full-adopter filenames row: [`acs-hotload-path-checklist.md`](acs-hotload-path-checklist.md)
- Sibling CGM work: [content-generation-modules#26](https://github.com/Pukujan/content-generation-modules/issues/26)
- PCM leaf: [project-continuity-modules#213](https://github.com/Pukujan/project-continuity-modules/issues/213)
