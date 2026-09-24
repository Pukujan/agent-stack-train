# TASK-PCM-0026 — Retry-safe GitHub receipts

<!-- continuity:task {"acceptance":["Implement the bounded publisher adapter and failure/retry tests defined by issue 67 without a scheduler.","Publish synchronized docs/checkpoint and verify required CI, auto-merge and issue reconciliation."],"depends_on":["PCM-0025"],"goal":"Publish retry-safe GitHub leaf and parent checkpoint receipts after verified pushes.","id":"PCM-0026","issue_url":"https://github.com/Pukujan/project-continuity-modules/issues/67","next_action":"After issue 66 is delivered, verify issue 67 and scope the smallest existing-publisher adapter.","owner":"unassigned; issue 67","priority":"P2","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"queued","why":"Manual receipts are mandatory today; automation needs separately tested failure and retry semantics."} -->

## Scope and lineage

Queued projection of leaf [#67](https://github.com/Pukujan/project-continuity-modules/issues/67), parent [#53](https://github.com/Pukujan/project-continuity-modules/issues/53), prerequisite [#66 / PCM-0025](https://github.com/Pukujan/project-continuity-modules/issues/66). Intended branch: `task/PCM-0026-github-receipts`. Implementation is unassigned and has not started. Read live issue acceptance before work.

The bounded scope is post-push receipt identity, retry/lost-response/partial-parent-update handling, safe actor/lineage checks, and deterministic failure tests. Manual receipts remain mandatory meanwhile. No scheduler, local source of truth or second-account requirement.

## Checkpoint log

No checkpoints yet.

## Handoff

Verify live issue 67 after policy issue 66 is delivered; do not infer current lifecycle from this as-of projection.
