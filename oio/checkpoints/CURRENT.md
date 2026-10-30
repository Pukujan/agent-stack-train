# Current Repository Checkpoint

<!-- continuity:current {"active_task":null,"active_task_file":null,"protocol_version":"0.1.0-draft","schema":"project-continuity.current.v1"} -->

This is an as-of projection; live GitHub issues own progression. Link the owning leaf, parent ancestry and dependencies for active work.

## Program state

Phase: OIO has shipped a prepacked observational/operational issue ontology and safe adopter installer. The installer includes explicit source classes, account authority, project-scoped hierarchical priority paths, evidence-based risk/release review lanes, and protected-repository boundaries. OIO consumes PCM and CGM; ACS HOTLOAD is pinned and documented, but the local ACS runtime integration is not certified complete. Parent issue #17 remains open for broader governance research.

## Completed

- OIO-0001 (issue #1): continuity protocol initialized (PCM CLI 0.6.0); CGM adapter pinned to the 0.5.7 baseline at that historical merge; three narrative assets generated and recorded in `.content-system/asset-manifest.json`; the release train and OIO's pins written. Merged 2026-10-01 in PR #3 (squash `043f2e2`).
- OIO-0002 (issue #4): the form names `Pukujan/observational-issue-ops` as its publisher, and the required `gates` check failed closed when the manifest and the release train disagreed. Merged 2026-10-01 in PR #7 (squash `bf6402e`).
- OIO-0003 (issue #9): OIO began as an issue-log ticketing system, covering observational and operational records; its current ontology narrows that scope and distinguishes proposals/incident records; the release train moved to `Pukujan/agent-stack-train` and OIO's manifest repointed at it. Merged 2026-10-01 in PR #11 (squash `2a836a5`).
- OIO-0004 (issue #13): the README hero was regenerated as a PNG (with `google/gemini-3-pro-image`) to meet the current CGM adopter-README hero contract, replacing the JPG; the references in the README, the adapter, and the prompt record were updated. Merged 2026-10-02 in PR #14 (squash `c65c69b`).
- OIO-0005 (issue #18): shipped the prepacked observational/operational ontology, validated adopter extension scaffold, target-confined installer, local form/triage and 36-test disposable-adopter coverage. Merged 2026-10-03 in PR #19 (squash `e965d36`). The `gates` CI check passed on the PR head; the installer is ready for an explicitly targeted adopter installation. ACS runtime integration remains uncertified.
- OIO-0006 (issue #32): ported the installer to Windows with the anti-redirection control preserved — the platform-dispatched `_TargetFS` refuses a symlink, junction, or reparse point at every managed path component and re-verifies parent identity around each replacement — plus a `windows-latest` CI leg aggregated into `gates`. Merged 2026-10-06 in PR #33 (squash `e2e30ec`).
- OIO-0007 (issue #41): made the managed-file integrity contract line-ending independent — the installer writes LF-canonical bytes and hashes them, `--check` compares content after EOL normalization with a distinct note for an EOL-only difference (a real content edit is still refused), a legacy CRLF-digest manifest migrates through a normal re-install, and `.gitattributes` pins LF checkout for the source. Merged 2026-10-10 in PR #42 (squash `27b954f`); required check `gates` passed on both platform legs.

## Active

- none.

## Queued

- none.

## Blockers

- OIO pins the current ACS HOTLOAD module source but does not contain the runtime assignment, lease, watchdog, claim-queue, and claim-to-PR integration required for `hotload_check.py`; do not claim ACS runtime readiness.
- The scheduled `Stay on the mesh` sync cannot update its own branch: every scheduled run commits the corrected `stack-mesh.json` but the push is rejected (`stale info`) because a `mesh/sync` branch already exists at an older commit, so the mesh still drifts until a human refreshes the pin. Tracked on issue #37; the fix is in the train's reusable workflow.

## Next atomic action

Await human verification of the Windows-install → Linux-`--check` round trip on issue #41 before closing it. The train at `Pukujan/agent-stack-train` is now `status: certified` (recorded 2026-10-07); ACS runtime integration remains uncertified.
