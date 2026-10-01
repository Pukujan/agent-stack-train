# Current Repository Checkpoint

<!-- continuity:current {"active_task":"OIO-0002","active_task_file":"tasks/TASK-OIO-0002-template-routing-and-consistency.md","protocol_version":"0.1.0-draft","schema":"project-continuity.current.v1"} -->

This is an as-of projection; live GitHub issues own progression. Link the owning leaf, parent ancestry and dependencies for active work.

## Program state

Phase: adopted as a clean stack adopter, now closing its two remaining adoption gaps. The repository holds the three-plane observational-issue form, its triage, the release train (`stack-releases.json`), and its own pins (`stack-manifest.json`). The PCM continuity scaffold, the CGM adapter (`.content-system/`), and the ACS hotloader reference are in place. The README carries the narrative assets.

## Completed

- OIO-0001: continuity protocol initialized (PCM CLI 0.6.0).
- OIO-0001: CGM adapter pinned to the 0.5.7 baseline; the pinned validator returns VALID.
- OIO-0001: three narrative assets generated and recorded in `.content-system/asset-manifest.json`.
- OIO-0001: `stack-releases.json` and `stack-manifest.json` written; merged 2026-10-01 in PR #3 (squash `043f2e2`).

## Active

- OIO-0002 (issue #4): name OIO as the form's publisher and fail the `gates` check closed when `stack-manifest.json` disagrees with `stack-releases.json`.

## Queued

- none.

## Blockers

None known.

## Next atomic action

Open the PR for `task/OIO-0002-template-routing-and-consistency`, confirm the `gates` job passes, then merge.
