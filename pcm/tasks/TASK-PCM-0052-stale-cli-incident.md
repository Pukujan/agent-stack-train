# TASK-PCM-0052 — Stale CLI sanitizer-bypass incident

<!-- continuity:task {"acceptance": ["Incident recorded with provenance (SHAs, comment ids, tool versions) on #162 and in this task; #123 addendum posted; collateral audit names every issue touched by the #161 merge", "Version-drift gate decision recorded on #162: implement refuse-with-opt-out in continuity checkpoint, add an observability field, or an explicit owner decision to keep it a device convention; no CLI/schema change before that decision"], "depends_on": [], "goal": "Record and correct the PCM-0052 incident where a stale installed continuity CLI (0.4.0, pre-sanitizer) composed PR #161's checkpoint commit with a raw close keyword and the merge auto-closed active issue #139.", "id": "PCM-0052", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/162", "next_action": "Owner decides acceptance 2 on #162 (gate mechanism vs convention); until then no cli.py edits.", "owner": "owner/Astra planning", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "active", "why": "A just-shipped safety property silently did not apply because PATH resolved to an older binary; the same drift can close or reopen issues arbitrarily on any dogfood session."} -->

- Status: active (incident recorded; gate decision pending)
- Owner: owner/Astra planning
- Priority: P2
- Depends on: none; related #123 (same hazard class, different root cause), #139 (collateral, reopened), #160/#161 (merge that fired it)

## Checkpoint log

### 2026-09-25 22:35:48 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["Owner decision needed on #162 (version-drift gate vs device convention) before any CLI change; PCM-0046 arms still provider-rate-gated (~04:00Z 2026-09-26)."],"changed":["tasks/TASK-PCM-0052-stale-cli-incident.md (new), checkpoints/CURRENT.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md"],"completed":["Acceptance 1 on #162: incident recorded with provenance (d854175 raw close keyword; squash 60f2426 auto-closed #139 22:21:16Z; reopened 22:24:42Z; correction 5840516734; addendum 5840566391 on #123); collateral audit clean (only #122/#123 intended closeouts plus #139 touched since 22:00Z); stale uv-tool 0.4.0 CLI reinstalled from checkout at 0.5.0 with sanitize_closing_keywords verified live in the tool env; CURRENT projection corrected to remove the hazard wording (close-keyword text replaced by explicit-comment procedure) and register PCM-0052."],"decisions":["Gate mechanism (acceptance 2) deferred to owner on #162; no cli.py/schema edits in this increment. Task-file checkpoint markers are authored only by the CLI, never hand-written."],"evidence":["sanitize_closing_keywords('... close #139.') returns '... Refs #139.' (1 replacement) under ~/.local/share/uv/tools/project-continuity/bin/python; this checkpoint's own commit message passed the 0.5.0 sanitizer path; docs render --check SYNCHRONIZED; continuity validate shows only the pre-existing device-local /private/tmp/pcm-pinned error."],"next_action":"Open PR for task/PCM-0052-stale-cli-incident, enable auto-merge, verify six contexts, then post merge receipt on #162 with the exact squash SHA.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0052","timestamp":"2026-09-25T22:35:48Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"87e7743d34b898d063fd1ca1188d5b37ee9fb6200f82f9c78e6946a498e5bf20","request_id":"pcm-0052-incident-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0052"} -->

Completed:
- Acceptance 1 on #162: incident recorded with provenance (d854175 raw close keyword; squash 60f2426 auto-closed #139 22:21:16Z; reopened 22:24:42Z; correction 5840516734; addendum 5840566391 on #123); collateral audit clean (only #122/#123 intended closeouts plus #139 touched since 22:00Z); stale uv-tool 0.4.0 CLI reinstalled from checkout at 0.5.0 with sanitize_closing_keywords verified live in the tool env; CURRENT projection corrected to remove the hazard wording (close-keyword text replaced by explicit-comment procedure) and register PCM-0052.

Evidence:
- sanitize_closing_keywords('... close #139.') returns '... Refs #139.' (1 replacement) under ~/.local/share/uv/tools/project-continuity/bin/python; this checkpoint's own commit message passed the 0.5.0 sanitizer path; docs render --check SYNCHRONIZED; continuity validate shows only the pre-existing device-local /private/tmp/pcm-pinned error.

Decisions:
- Gate mechanism (acceptance 2) deferred to owner on #162; no cli.py/schema edits in this increment. Task-file checkpoint markers are authored only by the CLI, never hand-written.

Changed:
- tasks/TASK-PCM-0052-stale-cli-incident.md (new), checkpoints/CURRENT.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- Owner decision needed on #162 (version-drift gate vs device convention) before any CLI change; PCM-0046 arms still provider-rate-gated (~04:00Z 2026-09-26).

Next:
- Open PR for task/PCM-0052-stale-cli-incident, enable auto-merge, verify six contexts, then post merge receipt on #162 with the exact squash SHA.

### 2026-09-25 22:52:01 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["Acceptance 2 owner decision on #162 unchanged."],"changed":["tasks/TASK-PCM-0052-stale-cli-incident.md"],"completed":["Dated correction to checkpoint entry pcm-0052-incident-20260925: its Evidence line claimed continuity validate showed only the device-local pcm-pinned error; at that same commit (2758479) validate reported TWO errors \u2014 the second was this task marker carrying a forbidden title key (schemas/v1/task.schema.json additionalProperties:false), fixed at 8bfeea5 before any PR opened. Binary provenance per run now recorded: 22:20Z checkpoint d854175 composed by uv-tool 0.4.0 (no sanitizer NOTE, raw keyword fired); 22:35Z checkpoint 2758479 composed after reinstall from checkout at 0.5.0 (index-regeneration NOTE printed; subject keyword-free because the source --next contained none). Pass-6 commit 2063136 (21:02Z) printed a sanitizer NOTE in a prior session whose PATH binary was not re-observed in this session; #123 addendum wording (stale installed binary) remains correct for the 22:20Z incident, and the pass-6 attribution stands as recorded on #140/#123."],"decisions":["Preserve the original entry unedited; correction appended. No rewrite of published history in this increment; forward commits only."],"evidence":["Re-ran continuity validate on a worktree of 2758479: 2 errors (unexpected key title + pcm-pinned). At current head: 1 error (pcm-pinned only, device-local, invisible to hosted CI which passed six contexts on #163)."],"next_action":"Open correction PR for this branch, auto-merge after six contexts, post merge receipt on #162; owner answers decision brief 5840695558 meanwhile.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0052","timestamp":"2026-09-25T22:52:01Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"f9e1d78e8cca6641425e5aaf9f47c8cde9eb3f9e54c11ba48475916071f0716b","request_id":"pcm-0052-correction-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0052"} -->

Completed:
- Dated correction to checkpoint entry pcm-0052-incident-20260925: its Evidence line claimed continuity validate showed only the device-local pcm-pinned error; at that same commit (2758479) validate reported TWO errors — the second was this task marker carrying a forbidden title key (schemas/v1/task.schema.json additionalProperties:false), fixed at 8bfeea5 before any PR opened. Binary provenance per run now recorded: 22:20Z checkpoint d854175 composed by uv-tool 0.4.0 (no sanitizer NOTE, raw keyword fired); 22:35Z checkpoint 2758479 composed after reinstall from checkout at 0.5.0 (index-regeneration NOTE printed; subject keyword-free because the source --next contained none). Pass-6 commit 2063136 (21:02Z) printed a sanitizer NOTE in a prior session whose PATH binary was not re-observed in this session; #123 addendum wording (stale installed binary) remains correct for the 22:20Z incident, and the pass-6 attribution stands as recorded on #140/#123.

Evidence:
- Re-ran continuity validate on a worktree of 2758479: 2 errors (unexpected key title + pcm-pinned). At current head: 1 error (pcm-pinned only, device-local, invisible to hosted CI which passed six contexts on #163).

Decisions:
- Preserve the original entry unedited; correction appended. No rewrite of published history in this increment; forward commits only.

Changed:
- tasks/TASK-PCM-0052-stale-cli-incident.md

Blocked/uncertain:
- Acceptance 2 owner decision on #162 unchanged.

Next:
- Open correction PR for this branch, auto-merge after six contexts, post merge receipt on #162; owner answers decision brief 5840695558 meanwhile.

## Handoff

Read PROJECT -> CURRENT -> this task -> #162 (incident facts + decision options) -> #123 addendum. Correction slice only; no CLI edits until the owner answers acceptance 2.
