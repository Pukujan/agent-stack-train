# TASK-PCM-0063 — T2 Staleness Guidance Decision

<!-- continuity:task {"acceptance": ["Owner records the A/B/C decision on #189.", "If A: T2-v2 holdout design pre-registered in docs/plans before any guidance edit; rule text in the guidance families generator + all copies, pinned by the policy test; re-measured arms reported honestly with inconclusive counts; six contexts + receipt on #189.", "(proposed) Pass bar unchanged at >=4/5 arms; baseline controls must still fail."], "depends_on": [], "goal": "Decide the read-time staleness-reconciliation rule the T2 holdout proved missing: what an agent must do when a stale projection and the live issue disagree (Refs #189).", "id": "PCM-0063", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/189", "next_action": "Owner picks option A (rule + pre-registered T2-v2 holdout), B (rule text only), or C (documented acceptance of the gap) on #189.", "owner": "owner/Astra planning", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "active", "why": "PCM-0046 hidden arms: T2 measured 0/5 — every fresh agent asserted the stale next action as current though the live issue state was attached; three stated the contradiction in their own words and still recommended it. Guidance today is write-time only."} -->

- Status: active
- Owner: owner/Astra planning
- Priority: P2
- Depends on: none

## Goal

Decide the read-time staleness-reconciliation rule the T2 holdout proved missing: what an agent must do when a stale projection and the live issue disagree (Refs #189).

## Why

PCM-0046 hidden arms: T2 measured 0/5 — every fresh agent asserted the stale next action as current though the live issue state was attached; three stated the contradiction in their own words and still recommended it. Guidance today is write-time only.

## Allowed files

After the owner answer on #189: src/continuity/cli.py (guidance generator), all checked-in guidance copies (AGENTS.md, HANDOFF.md, templates/v1/**, .github/**), docs/ISSUE_LOG_FORMAT.md if wording crosses tiers, tests/test_github_progression_policy.py (REQUIRED-pin), docs/plans/ for the T2-v2 pre-registration; this increment changes only this task file. Out: validate/CLI behavior, schemas.

## Human outcome

A fresh agent handed a stale status document and the live issue it references states the contradiction and follows the live fact, instead of recommending an action the issue history already invalidated (T2 measured 0/5 before this task).

## Scope and boundaries

- In scope: the A/B/C decision record on #189; if A, the pre-registered T2-v2 design and guidance-text slice.
- Out of scope: any code change to validate/preflight; reopening #139; adopting a database or crawler for staleness.
- Dependencies/uncertainty: depends on #139 evidence (CLOSED, accepted history); owner gate on #189.

## Acceptance criteria

- [ ] Owner records the A/B/C decision on #189.
- [ ] If A: T2-v2 holdout design pre-registered in docs/plans before any guidance edit; rule text in the guidance families generator + all copies, pinned by the policy test; re-measured arms reported honestly with inconclusive counts; six contexts + receipt on #189.
- [ ] (proposed) Pass bar unchanged at >=4/5 arms; baseline controls must still fail.

## Evidence and sources

T2 tallies + per-arm answers in accepted history at docs/plans/PCM-0046-arms-results/ (merge 969be11); counter-signal (3 arms saw the contradiction, none acted) recorded on #139 comment 5845193587.

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none): leaf #189 (PCM-0063); parent: none (evidence child of closed #139; research answer appended to #137 at 5845214460).
- Primary writer / branch / source issue revision / as-of status: owner/Astra (omp session); branch task/PCM-0063-projections (projection increment only, no code); source: live issue bodies; as-of 2026-09-26T11:35Z.
- Related PR/CI evidence and push receipt (request ID / SHA): none yet (decision gate); arms evidence rides PCM-0046 (PRs #188/#192/#193).

## Checkpoint log

No checkpoints yet.

### 2026-09-26 11:35:36 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":[],"changed":["tasks/TASK-PCM-0063-*.md, tasks/TASK-PCM-0064-*.md, tasks/TASK-PCM-0065-*.md (new), tasks/TASK-PCM-0059/0060/0062 (projections), checkpoints/CURRENT.md, docs/CONTINUITY_INDEX.md"],"completed":["PCM-0063/0064/0065 task files created via continuity task new and filled from their leaf issues (#189/#190/#191): acceptance, human outcome, allowed files, lineage, evidence \u2014 no template placeholders left. PCM-0059/0060/0062 decision-task projections filled from #181/#182/#185 (placeholder acceptance/human-outcome/lineage replaced). CURRENT projection re-pinned: PCM-0046 lifecycle COMPLETE (#192 0be407e, #193 aa9a3a2, receipts 5845513494/5845795082, worktree REMOVED); next-action is the ranked owner-decision queue."],"decisions":["Projection-only increment; each decision task's real implementation slices wait for their owner answers; PCM-0065 acceptance now references the durable overrides.json pattern."],"evidence":["continuity task new produced ids PCM-0063/64/65 matching issues; docs render --check SYNCHRONIZED; suite 274 = six known macOS-environmental names zero new; git worktree list shows PCM-0046 tree gone; continuity receipt audit PCM-0046 AUDIT_CLEAN on installed 0.6.0."],"next_action":"Open PR, arm auto-merge after this final push; on merge, post receipt on #189.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0063","timestamp":"2026-09-26T11:35:36Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"25e024afed313ba7b65d012b6e21a6febc4d6581bd3248b8c2af4c9f32de984f","request_id":"pcm-0063-projections-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0063"} -->

Completed:
- PCM-0063/0064/0065 task files created via continuity task new and filled from their leaf issues (#189/#190/#191): acceptance, human outcome, allowed files, lineage, evidence — no template placeholders left. PCM-0059/0060/0062 decision-task projections filled from #181/#182/#185 (placeholder acceptance/human-outcome/lineage replaced). CURRENT projection re-pinned: PCM-0046 lifecycle COMPLETE (#192 0be407e, #193 aa9a3a2, receipts 5845513494/5845795082, worktree REMOVED); next-action is the ranked owner-decision queue.

Evidence:
- continuity task new produced ids PCM-0063/64/65 matching issues; docs render --check SYNCHRONIZED; suite 274 = six known macOS-environmental names zero new; git worktree list shows PCM-0046 tree gone; continuity receipt audit PCM-0046 AUDIT_CLEAN on installed 0.6.0.

Decisions:
- Projection-only increment; each decision task's real implementation slices wait for their owner answers; PCM-0065 acceptance now references the durable overrides.json pattern.

Changed:
- tasks/TASK-PCM-0063-*.md, tasks/TASK-PCM-0064-*.md, tasks/TASK-PCM-0065-*.md (new), tasks/TASK-PCM-0059/0060/0062 (projections), checkpoints/CURRENT.md, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- none

Next:
- Open PR, arm auto-merge after this final push; on merge, post receipt on #189.

### 2026-09-26 12:15:02 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":[],"changed":[".continuity/documents.json, docs/CONTINUITY_INDEX.md, docs/plans/PCM-0046-arms-results/{REPORT.md,meta.json}"],"completed":["Post-review hygiene increment: PCM-0063/0064/0065 registered in the document catalog (siblings 0059/0060/0062 had records; docs find could not surface the new ones), AGENTS.md task-ID/writer/branch comments posted on #190/#191, REPORT.md gained an append-only corrections section (vacuous AUDIT_CLEAN dogfood claim disclaimed, T2 lexical-vs-behavioral check split, 05:42Z->~09:42Z timezone slip, meta isolation=clean understatement for the four repo-reading T4 arms), and #139's sync receipt corrected append-only."],"decisions":["All fixes are additive (catalog records, appended REPORT section, issue comments); no prior published claim edited in place, per append-only doctrine. T2's rubric limitation feeds #189's T2-v2 design note rather than re-scoring anything."],"evidence":["continuity docs add -> 3x REGISTERED; docs render --check SYNCHRONIZED; suite 274 = six known macOS-environmental names (test_worktrees 4F+1E, test_cli 2F), zero new; validate INVALID only the pre-existing device-local /private/tmp/pcm-pinned foreign worktree; posted comments visible via API (139/190/191 listings)."],"next_action":"Open PR, arm auto-merge after this final push, post merge receipt on #189.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0063","timestamp":"2026-09-26T12:15:02Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"37d77c1790b23a977d0bc9300c587e02bfdd49958b799a17a3ad6543e0945e8c","request_id":"pcm-0063-hygiene-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0063"} -->

Completed:
- Post-review hygiene increment: PCM-0063/0064/0065 registered in the document catalog (siblings 0059/0060/0062 had records; docs find could not surface the new ones), AGENTS.md task-ID/writer/branch comments posted on #190/#191, REPORT.md gained an append-only corrections section (vacuous AUDIT_CLEAN dogfood claim disclaimed, T2 lexical-vs-behavioral check split, 05:42Z->~09:42Z timezone slip, meta isolation=clean understatement for the four repo-reading T4 arms), and #139's sync receipt corrected append-only.

Evidence:
- continuity docs add -> 3x REGISTERED; docs render --check SYNCHRONIZED; suite 274 = six known macOS-environmental names (test_worktrees 4F+1E, test_cli 2F), zero new; validate INVALID only the pre-existing device-local /private/tmp/pcm-pinned foreign worktree; posted comments visible via API (139/190/191 listings).

Decisions:
- All fixes are additive (catalog records, appended REPORT section, issue comments); no prior published claim edited in place, per append-only doctrine. T2's rubric limitation feeds #189's T2-v2 design note rather than re-scoring anything.

Changed:
- .continuity/documents.json, docs/CONTINUITY_INDEX.md, docs/plans/PCM-0046-arms-results/{REPORT.md,meta.json}

Blocked/uncertain:
- none

Next:
- Open PR, arm auto-merge after this final push, post merge receipt on #189.

### 2026-09-26 12:37:54 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":[],"changed":["docs/plans/PCM-0046-arms-results/{isolation-audit.json,REPORT.md}"],"completed":["Cited-evidence gap closed: scored.json/overrides.json T4 reasons cite isolation-audit.json, which previously tracked only bundle paths and showed those arms clean; the audit now carries an additive per-arm repo_source_reads field regenerated from the same session logs (T4-1:4, T4-3:3, T4-4:4, T4-5:5 tool calls on src/continuity/cli.py, tests/traversal_scorer.py, fixtures, plan) plus a _fields legend. REPORT corrections extended: item 6 supersedes the 'three arms' counter-signal with the verified 5/5 (each committed answer states the issue closed); item 7 replaces correction 4's too-broad framing with the narrow defect \u2014 zero-commit gets AUDIT_CLEAN (cli.py:3166-3167) while not-on-origin gets the NOTE (:3155), and visibility is one branch."],"decisions":["Additive field + appended corrections rather than rewriting the merged correction 4; the refined framing lives as correction 7 pointing to it."],"evidence":["T2 count re-read directly from the five committed answer files; line cites observed from current cli.py at 3148/3155/3166-3167; docs render --check SYNCHRONIZED; prior correction items 1-4 untouched (append-only)."],"next_action":"Open PR, arm auto-merge after this final push, post merge receipt on #189.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0063","timestamp":"2026-09-26T12:37:54Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"ba58e8e5b21ccc9b297f4a259886090a9083f401a73b57eb87f0ba5680409af3","request_id":"pcm-0063-evidencefix-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0063"} -->

Completed:
- Cited-evidence gap closed: scored.json/overrides.json T4 reasons cite isolation-audit.json, which previously tracked only bundle paths and showed those arms clean; the audit now carries an additive per-arm repo_source_reads field regenerated from the same session logs (T4-1:4, T4-3:3, T4-4:4, T4-5:5 tool calls on src/continuity/cli.py, tests/traversal_scorer.py, fixtures, plan) plus a _fields legend. REPORT corrections extended: item 6 supersedes the 'three arms' counter-signal with the verified 5/5 (each committed answer states the issue closed); item 7 replaces correction 4's too-broad framing with the narrow defect — zero-commit gets AUDIT_CLEAN (cli.py:3166-3167) while not-on-origin gets the NOTE (:3155), and visibility is one branch.

Evidence:
- T2 count re-read directly from the five committed answer files; line cites observed from current cli.py at 3148/3155/3166-3167; docs render --check SYNCHRONIZED; prior correction items 1-4 untouched (append-only).

Decisions:
- Additive field + appended corrections rather than rewriting the merged correction 4; the refined framing lives as correction 7 pointing to it.

Changed:
- docs/plans/PCM-0046-arms-results/{isolation-audit.json,REPORT.md}

Blocked/uncertain:
- none

Next:
- Open PR, arm auto-merge after this final push, post merge receipt on #189.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
