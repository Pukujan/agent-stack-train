# TASK-PCM-0026 — Retry-safe GitHub receipts

<!-- continuity:task {"acceptance":["Implement the bounded publisher adapter and failure/retry tests defined by issue 67 without a scheduler.","Publish synchronized docs/checkpoint and verify required CI, auto-merge and issue reconciliation."],"depends_on":["PCM-0025"],"goal":"Publish retry-safe GitHub leaf and parent checkpoint receipts after verified pushes.","id":"PCM-0026","issue_url":"https://github.com/Pukujan/project-continuity-modules/issues/67","next_action":"Verify hosted checks for the opt-in receipt docs, then reconcile issue 67. Do not close it until the remaining acceptance gaps are explicit.","owner":"Astra planning; Kilo staff execute released assignments; issue 67","priority":"P2","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Manual receipts are mandatory today; automation needs separately tested failure and retry semantics."} -->

## Scope and lineage

Active projection of leaf [#67](https://github.com/Pukujan/project-continuity-modules/issues/67), parent [#53](https://github.com/Pukujan/project-continuity-modules/issues/53), prerequisite [#66 / PCM-0025](https://github.com/Pukujan/project-continuity-modules/issues/66). Branch: `task/PCM-0026-github-receipts`. Astra accepted the prerequisite and reserved this branch. Staff added the research note while the planning process was idle. Publisher implementation has not started.

The bounded scope is post-push receipt identity, retry/lost-response/partial-parent-update handling, safe actor/lineage checks, and deterministic failure tests. Manual receipts remain mandatory meanwhile. No scheduler, local source of truth or second-account requirement.

## Checkpoint log

No checkpoints yet.

## Handoff

Research note: `docs/research/PCM-0026-issue-67-retry-safe-receipts.md`. Opt-in `--receipt-repo`, `--receipt-issue`, and `--receipt-parent` look up comments before posting, refuse secret-like bodies, and stop when another writer holds the marker. Default checkpoint behavior is unchanged. Issue #67 remains open.
