# TASK-OIO-0004 — Upgrade the README hero to the CGM PNG contract

<!-- continuity:task {"acceptance":["the README hero is a PNG generated with the best available image model and the JPG is removed","every hero reference is updated: README.md, .content-system/asset-manifest.json, .content-system/visual-style.json, and the prompt record","the manifest records the exact title and subtitle, the SHA-256 of the new PNG, and the provider","continuity validate --root . returns VALID and the pinned CGM validator returns VALID","the increment is pushed through a merged PR on a task branch"],"depends_on":["OIO-0003"],"goal":"Replace OIO's JPG README hero with a regenerated PNG that satisfies the CGM adopter-README hero contract, and update every reference to it","id":"OIO-0004","issue_url":"https://github.com/Pukujan/observational-issue-ops/issues/13","next_action":"open the pull request on the task branch and request auto-merge after the required gates pass","owner":"owner/Pukujan","priority":"P3","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"CGM's adopter-README contract requires the hero banner to be a PNG; OIO's hero is a JPG, so the checked-in README does not satisfy the current CGM README spec even though its pinned 0.5.7 CI still passes"} -->

- Status: active
- Owner: owner/Pukujan
- Priority: P3
- Depends on: OIO-0003 (the issue-log definition, merged)

## Goal

Replace OIO's JPG README hero with a regenerated PNG that satisfies the CGM adopter-README hero contract, and update every reference to it.

## Why

OIO's README hero is `docs/assets/oio-hero-banner.jpg`. CGM's adopter-README contract requires the **hero banner to be a PNG** — a non-PNG raster hero is rejected (the rule landed in CGM 0.5.9 and is enforced by the current CGM `main`). OIO pins CGM 0.5.7, so its `gates` CI still passes, but the checked-in README does not satisfy the current CGM README spec. This increment brings the hero to the current contract without moving the pin.

## Allowed files

- `README.md`
- `.content-system/asset-manifest.json`, `.content-system/visual-style.json`
- `docs/assets/oio-hero-banner.png` (add), `docs/assets/oio-hero-banner.jpg` (delete), `docs/assets/oio-hero-banner.jpg.json` (delete)
- `docs/assets/prompts/oio-hero-banner.md`
- `checkpoints/`, `tasks/`, `HANDOFF.md`

## Human outcome

The README's lead visual is a PNG generated with the best available image model, on the same art direction as the two supporting visuals, and every reference to the old JPG is gone. The two supporting visuals are unchanged.

## Scope and boundaries

- In scope: the hero image file, its prompt record, and the references to it.
- Out of scope: changing OIO's CGM pin or any certified version; the two supporting visuals; the form, triage, or stack manifest.
- Dependencies/uncertainty: the PNG rule is enforced by CGM `main`; the pinned 0.5.7 validator does not check hero format, so the improvement is verified against CGM `main`.

## Acceptance criteria

- [x] The README hero is a PNG generated with the best available image model and the JPG is removed.
- [x] Every hero reference is updated: `README.md`, `.content-system/asset-manifest.json`, `.content-system/visual-style.json`, and the prompt record.
- [x] The manifest records the exact title and subtitle, the SHA-256 of the new PNG, and the provider.
- [x] `continuity validate --root .` returns VALID and the pinned CGM validator returns VALID.
- [ ] The increment is pushed through a merged PR on a task branch.

## Evidence and sources

- Leaf owning issue: [#13](https://github.com/Pukujan/observational-issue-ops/issues/13).
- Rule: CGM `scripts/verify_adopter_content.py` — `check_manifest_hero_asset_format` and `_hero_visual_errors` require `.png` for a `hero`-role asset.
- Pin: CGM 0.5.7 (`c069613`), which predates the PNG rule.

## Related records

- Leaf owning issue: [#13](https://github.com/Pukujan/observational-issue-ops/issues/13). Parent ancestry: none (top-level deliverable). Dependencies: OIO-0003 (merged).
- Primary writer / branch / source issue revision / as-of status: agent session / `task/OIO-0004-readme-hero-png` / issue #13 as filed / in-progress.

## Checkpoint log

- 2026-10-02: hero regenerated as a PNG with `google/gemini-3-pro-image` (via OpenRouter), replacing the JPG; references updated in the README, adapter, and prompt record; both validators pass.
