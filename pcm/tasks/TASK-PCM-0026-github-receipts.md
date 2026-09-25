# TASK-PCM-0026 — Retry-safe GitHub receipts

<!-- continuity:task {"acceptance": ["Implement the bounded publisher adapter and failure/retry tests defined by issue 67 without a scheduler.", "Publish synchronized docs/checkpoint and verify required CI, auto-merge and issue reconciliation."], "depends_on": ["PCM-0025"], "goal": "Publish retry-safe GitHub leaf and parent checkpoint receipts after verified pushes.", "id": "PCM-0026", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/67", "next_action": "None: #67 CLOSED/COMPLETED (freeze 5827958268; closeout 5828375079; RESULT-09 retraction 5830207263; PR #112 at 18ce782). Continuation belongs to #110 (5830169411).", "owner": "Astra planning; Kilo staff execute released assignments; issue 67", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "completed", "why": "Manual receipts are mandatory today; automation needs separately tested failure and retry semantics."} -->

## Scope and lineage

Active projection of leaf [#67](https://github.com/Pukujan/project-continuity-modules/issues/67), parent [#53](https://github.com/Pukujan/project-continuity-modules/issues/53), prerequisite [#66 / PCM-0025](https://github.com/Pukujan/project-continuity-modules/issues/66) CLOSED/COMPLETED. Working branch: `task/PCM-0026-task09-local` in the permanent checkout (receipt slices #80–#97 landed through earlier task branches; #67 names `task/PCM-0026-post-push-plan` as the planning-owner branch). Primary writer: owner/Astra planning with owner-authorized subagent execution replacing the Windows staff model on this device (owner direction 2026-09-25).

The bounded scope was post-push receipt identity, retry/lost-response/partial-parent-update handling, safe actor/lineage checks, and deterministic failure tests. The opt-in lookup-before-post route merged in #80–#97; [OWNER-17](https://github.com/Pukujan/project-continuity-modules/issues/67#issuecomment-5824990832) released TASK-09 (disabled admission evaluator) as a local candidate. The [owner freeze decision](https://github.com/Pukujan/project-continuity-modules/issues/67#issuecomment-5827958268) closes automatic first-send/publisher work in favor of the merged manual+opt-in contract; crash-safe automation continues only through [#110](https://github.com/Pukujan/project-continuity-modules/issues/110).

## Checkpoint log

See appended `continuity checkpoint` entries below.

### 2026-09-25 06:58:03 UTC — owner/Astra planning; subagent execution

<!-- continuity:checkpoint {"agent":"owner/Astra planning; subagent execution","blocked":["None."],"changed":["tasks/TASK-PCM-0026-github-receipts.md; src/continuity/receipt_admission.py and tests/test_receipt_admission.py (new, from candidate commits)."],"completed":["Recorded RESULT-09 + correction on #67, owner freeze decision closing automation scope, and synchronized task projection; admission evaluator commits dede388/4159087 ready for publication."],"decisions":["Freeze automatic first-send receipts per owner direction 2026-09-25; opt-in manual receipts remain the operating contract; #110 owns ambiguity completion."],"evidence":["https://github.com/Pukujan/project-continuity-modules/issues/67#issuecomment-5827724217 and #issuecomment-5827958268; focused suite 22 OK on python3.12; ruff/mypy/compileall/validate clean."],"next_action":"Push task branch, open PR to main with Refs #67, enable auto-merge, verify required checks, then publish leaf/parent receipts and close #67.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0026","timestamp":"2026-09-25T06:58:03Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"eb5fe81c14ffe137ba9a997afa384387a1e57bfe6918b9b73e3f4aead9ea4be7","request_id":"pcm0026-freeze-publish-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0026"} -->

Completed:
- Recorded RESULT-09 + correction on #67, owner freeze decision closing automation scope, and synchronized task projection; admission evaluator commits dede388/4159087 ready for publication.

Evidence:
- https://github.com/Pukujan/project-continuity-modules/issues/67#issuecomment-5827724217 and #issuecomment-5827958268; focused suite 22 OK on python3.12; ruff/mypy/compileall/validate clean.

Decisions:
- Freeze automatic first-send receipts per owner direction 2026-09-25; opt-in manual receipts remain the operating contract; #110 owns ambiguity completion.

Changed:
- tasks/TASK-PCM-0026-github-receipts.md; src/continuity/receipt_admission.py and tests/test_receipt_admission.py (new, from candidate commits).

Blocked/uncertain:
- None.

Next:
- Push task branch, open PR to main with Refs #67, enable auto-merge, verify required checks, then publish leaf/parent receipts and close #67.

### 2026-09-25 07:02:45 UTC — owner/Astra planning; subagent execution

<!-- continuity:checkpoint {"agent":"owner/Astra planning; subagent execution","blocked":["None."],"changed":["tasks/TASK-PCM-0026-github-receipts.md; src/continuity/receipt_admission.py; tests/test_receipt_admission.py."],"completed":["Recorded RESULT-09 plus correction on #67 and the owner freeze decision; synchronized the task projection; admission evaluator commits dede388/4159087 now publishing."],"decisions":["Freeze automatic first-send receipts per owner direction 2026-09-25; the merged opt-in manual receipts remain the operating contract; crash-safe automation continues only via #110. Subagents replace the Windows staff model on this device."],"evidence":["https://github.com/Pukujan/project-continuity-modules/issues/67#issuecomment-5827724217 and https://github.com/Pukujan/project-continuity-modules/issues/67#issuecomment-5827958268; focused suite 22 OK on python3.12; ruff/mypy/compileall/validate/index checks clean."],"next_action":"Open the PR, verify exact required checks and auto-merge, publish leaf/parent receipts keyed to the pushed SHA, then close #67 and reconcile #53.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0026","timestamp":"2026-09-25T07:02:45Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"e5b36861691f70b135a21540d86ae2f1eccc5824380f9f40526c5e2df72aba9a","request_id":"pcm0026-freeze-publish-v2-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0026"} -->

Completed:
- Recorded RESULT-09 plus correction on #67 and the owner freeze decision; synchronized the task projection; admission evaluator commits dede388/4159087 now publishing.

Evidence:
- https://github.com/Pukujan/project-continuity-modules/issues/67#issuecomment-5827724217 and https://github.com/Pukujan/project-continuity-modules/issues/67#issuecomment-5827958268; focused suite 22 OK on python3.12; ruff/mypy/compileall/validate/index checks clean.

Decisions:
- Freeze automatic first-send receipts per owner direction 2026-09-25; the merged opt-in manual receipts remain the operating contract; crash-safe automation continues only via #110. Subagents replace the Windows staff model on this device.

Changed:
- tasks/TASK-PCM-0026-github-receipts.md; src/continuity/receipt_admission.py; tests/test_receipt_admission.py.

Blocked/uncertain:
- None.

Next:
- Open the PR, verify exact required checks and auto-merge, publish leaf/parent receipts keyed to the pushed SHA, then close #67 and reconcile #53.

## Handoff

Research note: `docs/research/PCM-0026-issue-67-retry-safe-receipts.md`. Opt-in `--receipt-repo`, `--receipt-issue`, and `--receipt-parent` look up comments before posting, refuse secret-like bodies, and stop when another writer holds the marker. Default checkpoint behavior is unchanged. RESULT-09 and its correction: [comments 5827724217 and 5827958268](https://github.com/Pukujan/project-continuity-modules/issues/67#issuecomment-5827958268). Pending: publish `task/PCM-0026-task09-local` (evaluator commits `dede388`, `4159087`), PR/CI/auto-merge, receipts, then close #67 per the owner freeze decision and reconcile #53 lineage.
