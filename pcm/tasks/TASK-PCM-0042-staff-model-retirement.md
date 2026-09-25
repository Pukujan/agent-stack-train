# TASK-PCM-0042 — Staff model retirement

<!-- continuity:task {"acceptance": ["docs/ASTRA_GROK_STAFF.md deleted and catalog de-registered with index regenerated and validate VALID", "module-doc example neutralized (fictional ABC-0001, no real writer name or task ID)", "CURRENT records the retirement with the ownership pointer to inference-recommendation-engine", "historical task/checkpoint/issue prose untouched (append-only)", "local gates green (unittest discovery with only the six known macOS-environmental failures, ruff, mypy, compileall, validate, index sync) and the six required hosted contexts pass on the exact merge candidate"], "depends_on": [], "goal": "Retire the one-time Astra/Grok staff-model document so no cold-start session adopts it as live guidance; orchestration recommendations belong to inference-recommendation-engine", "id": "PCM-0042", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/129", "next_action": "None: #129 CLOSED (receipt 5837807514) after PR #132 merged at aa02a4c859f3aa1642d9be33af36c05c4a177168 with six contexts green; accidental-keyword closure disclosed and evidenced on #123.", "owner": "owner/Astra planning", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "completed", "why": "The document claims to be current operating guidance for a fresh session while describing a retired Windows-only inbox model with private paths; it already caused owner corrections this month and will confuse future sessions"} -->

- Status: completed 2026-09-25 (#129 CLOSED)
- Owner: owner/Astra planning
- Priority: P2
- Depends on: none

## Human outcome

A cold-start session reading `continuity docs find "staff model"` no longer receives a stale orchestration contract; PCM's live execution model is owner-authorized subagents under `docs/AGENT_LIFECYCLE.md`, and agent-orchestration recommendations live with `Pukujan/inference-recommendation-engine` per the owner.

## Scope and boundaries

Delete `docs/ASTRA_GROK_STAFF.md`; de-register its catalog record; neutralize the shipped module-doc example that named `PCM-0042`/`Astra`; append the retirement note to CURRENT. **Non-goals:** no rewrite of historical task/checkpoint/issue prose (append-only); no changes to `docs/AGENT_LIFECYCLE.md`; no IRE repository edits; no HANDOFF refresh (tracked separately).

## Evidence and sources

Hypothesis test recorded in [#129](https://github.com/Pukujan/project-continuity-modules/issues/129) (2026-09-25): zero mechanical dependencies (`grep` over `tests/ src/ AGENTS.md templates/ .github/` → no hits); live references only in catalog + generated index; `cli.py:1234` requires file+record removal together; demonstrated confusion risk (two owner corrections this session); private Windows paths violate the records policy. Provenance preserved by merged Git history (the file's own commits) and the linked issues.

## Checkpoint log

See the appended `continuity checkpoint` entries; retirement executed and delivered via PR #132 at `aa02a4c859f3aa1642d9be33af36c05c4a177168` (run 36175420479, six required contexts pass).

### 2026-09-25 18:45:13 UTC — owner/Astra planning

<!-- continuity:checkpoint {"agent":"owner/Astra planning","blocked":["None."],"changed":["docs/ASTRA_GROK_STAFF.md (deleted); .continuity/documents.json; docs/CONTINUITY_INDEX.md; docs/ISSUE_LOG_FORMAT.md; checkpoints/CURRENT.md; tasks/TASK-PCM-0042-staff-model-retirement.md."],"completed":["Executed the tested retirement plan: doc deleted, catalog de-registered, example neutralized, CURRENT note appended; historical task/checkpoint prose untouched per append-only."],"decisions":["Deletion (not archival edit) justified: zero mechanical dependencies, live-guidance claim false, private Windows paths violate the records policy; Git history preserves provenance."],"evidence":["grep ASTRA_GROK_STAFF|astra-grok-staff in docs/index/catalog -> 0; validate VALID; render SYNCHRONIZED; 196-test discovery with only the six known macOS-environmental failures; ruff/mypy/compileall clean."],"next_action":"Open PR Refs #129, verify six contexts + merge, post receipts, close #129.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0042","timestamp":"2026-09-25T18:45:13Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"fae3bff18d432de9cd464ea3213fb4a39fa4f30077aa334bbd2d20fdfd714be2","request_id":"pcm0042-retirement-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0042"} -->

Completed:
- Executed the tested retirement plan: doc deleted, catalog de-registered, example neutralized, CURRENT note appended; historical task/checkpoint prose untouched per append-only.

Evidence:
- grep ASTRA_GROK_STAFF|astra-grok-staff in docs/index/catalog -> 0; validate VALID; render SYNCHRONIZED; 196-test discovery with only the six known macOS-environmental failures; ruff/mypy/compileall clean.

Decisions:
- Deletion (not archival edit) justified: zero mechanical dependencies, live-guidance claim false, private Windows paths violate the records policy; Git history preserves provenance.

Changed:
- docs/ASTRA_GROK_STAFF.md (deleted); .continuity/documents.json; docs/CONTINUITY_INDEX.md; docs/ISSUE_LOG_FORMAT.md; checkpoints/CURRENT.md; tasks/TASK-PCM-0042-staff-model-retirement.md.

Blocked/uncertain:
- None.

Next:
- Open PR Refs #129, verify six contexts + merge, post receipts, close #129.

### 2026-09-25 18:49:20 UTC — owner/Astra planning

<!-- continuity:checkpoint {"agent":"owner/Astra planning","blocked":["None."],"changed":["tasks/TASK-PCM-0042-staff-model-retirement.md; checkpoints/CURRENT.md."],"completed":["Marked PCM-0042 completed; CURRENT active task cleared."],"decisions":["no new decisions"],"evidence":["PR #132 merged at aa02a4c; six contexts run 36175420479; receipt 5837807514; #123 second-instance evidence posted."],"next_action":"Merge the closeout PR under required checks; the retirement chain is then complete.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0042","timestamp":"2026-09-25T18:49:20Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"3d282652eb78f466097ce175251b3896c9aef365a42174bcc5d081765747c446","request_id":"pcm0042-closeout-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0042"} -->

Completed:
- Marked PCM-0042 completed; CURRENT active task cleared.

Evidence:
- PR #132 merged at aa02a4c; six contexts run 36175420479; receipt 5837807514; #123 second-instance evidence posted.

Decisions:
- no new decisions

Changed:
- tasks/TASK-PCM-0042-staff-model-retirement.md; checkpoints/CURRENT.md.

Blocked/uncertain:
- None.

Next:
- Merge the closeout PR under required checks; the retirement chain is then complete.

## Handoff

Read PROJECT → CURRENT → this task → #129. Complete: receipt posted (5837807514); #129 closed (accidental keyword mechanism disclosed on the receipt and on #123 as a second instance).
