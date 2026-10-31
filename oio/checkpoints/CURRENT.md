# Current Repository Checkpoint

<!-- continuity:current {"active_task":null,"active_task_file":null,"protocol_version":"0.1.0-draft","schema":"project-continuity.current.v1"} -->

This is an as-of projection; live GitHub issues own progression. Link the owning leaf, parent ancestry and dependencies for active work.

Older state: [`history/2026-10.md`](history/2026-10.md) and earlier months in `history/`.

## Program state

Phase: OIO has shipped a prepacked observational/operational issue ontology and safe adopter installer. The installer includes explicit source classes, account authority, project-scoped hierarchical priority paths, evidence-based risk/release review lanes, and protected-repository boundaries. OIO consumes PCM and CGM; ACS HOTLOAD is pinned and documented, but the local ACS runtime integration is not certified complete. Parent issue #17 remains open for broader governance research.

## Active

- none.

## Queued

- none.

## Blockers

- OIO pins the current ACS HOTLOAD module source but does not contain the runtime assignment, lease, watchdog, claim-queue, and claim-to-PR integration required for `hotload_check.py`; do not claim ACS runtime readiness.
- The scheduled `Stay on the mesh` sync cannot update its own branch: every scheduled run commits the corrected `stack-mesh.json` but the push is rejected (`stale info`) because a `mesh/sync` branch already exists at an older commit, so the mesh still drifts until a human refreshes the pin. Tracked on issue #37; the fix is in the train's reusable workflow.

## Next atomic action

Await human verification of the Windows-install → Linux-`--check` round trip on issue #41 before closing it. The train at `Pukujan/agent-stack-train` is now `status: certified` (recorded 2026-10-07); ACS runtime integration remains uncertified.
