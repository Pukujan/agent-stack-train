# TASK-PCM-0063 — T2 Staleness Guidance Decision

<!-- continuity:task {"acceptance": ["Owner records the A/B/C decision on #189.", "If A: T2-v2 holdout design pre-registered in docs/plans before any guidance edit; rule text in the guidance families generator + all copies, pinned by the policy test; re-measured arms reported honestly with inconclusive counts; six contexts + receipt on #189.", "(proposed) Pass bar unchanged at >=4/5 arms; baseline controls must still fail."], "depends_on": [], "goal": "Decide the read-time staleness-reconciliation rule the T2 holdout proved missing: what an agent must do when a stale projection and the live issue disagree (Refs #189).", "id": "PCM-0063", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/189", "next_action": "Owner picks option A (rule + pre-registered T2-v2 holdout), B (rule text only), or C (documented acceptance of the gap) on #189.", "owner": "owner/Astra planning", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "active", "why": "PCM-0046 hidden arms: T2 measured 0/5 — every fresh agent asserted the stale next action as current though the live issue state was attached; all five stated the contradiction in their own words and still recommended it (REPORT.md correction 6 supersedes the original three-arm count). Guidance today is write-time only."} -->

- Status: active
- Owner: owner/Astra planning
- Priority: P2
- Depends on: none

## Goal

Decide the read-time staleness-reconciliation rule the T2 holdout proved missing: what an agent must do when a stale projection and the live issue disagree (Refs #189).

## Why

PCM-0046 hidden arms: T2 measured 0/5 — every fresh agent asserted the stale next action as current though the live issue state was attached; all five stated the contradiction in their own words and still recommended it (REPORT.md correction 6 supersedes the initial three-arm count). Guidance today is write-time only.

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

T2 tallies + per-arm answers in accepted history at docs/plans/PCM-0046-arms-results/ (merge 969be11); counter-signal (all five stated the closed-issue fact, none acted on it; correction 6 supersedes the initial count) recorded on #139 comment 5845193587.

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

### 2026-09-26 13:15:26 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":[],"changed":["docs/plans/PCM-0046-arms-results/{isolation-audit.json,REPORT.md,meta.json}"],"completed":["Device-absolute-path breach fixed in current head: 4 repo_source_reads entries normalized to repo-relative form, disclosed as REPORT correction 8 (not silently amended). Provenance chain repaired: meta.json _artifacts_sha256 re-pinned to current bytes with _pin_history recording the superseded digests (scored.json changed by #192 overrides; isolation-audit.json by #196 field + this normalization) and the original first-capture map preserved verbatim. Full-directory leak scan: zero /Users hits outside ignored __pycache__."],"decisions":["Amend-current-head (accepted correction) for data-hygiene since the #151 precedent strips this class, with append-only disclosure; no rewrite of any published verdict."],"evidence":["python normalization replaced exactly 4 prefixes; re-pin verification loop: zero stale pins; grep -rc over the results directory: 0 hits; docs render --check SYNCHRONIZED; suite 274 = six known names."],"next_action":"Open PR, arm auto-merge after this final push, post merge receipt on #189 and a pointer on #191.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0063","timestamp":"2026-09-26T13:15:26Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"3a3c32e415d52b75c65da708dc1a7a7c105d19e882ef807999bd1d2753cc80e5","request_id":"pcm-0063-pathfix-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0063"} -->

Completed:
- Device-absolute-path breach fixed in current head: 4 repo_source_reads entries normalized to repo-relative form, disclosed as REPORT correction 8 (not silently amended). Provenance chain repaired: meta.json _artifacts_sha256 re-pinned to current bytes with _pin_history recording the superseded digests (scored.json changed by #192 overrides; isolation-audit.json by #196 field + this normalization) and the original first-capture map preserved verbatim. Full-directory leak scan: zero /Users hits outside ignored __pycache__.

Evidence:
- python normalization replaced exactly 4 prefixes; re-pin verification loop: zero stale pins; grep -rc over the results directory: 0 hits; docs render --check SYNCHRONIZED; suite 274 = six known names.

Decisions:
- Amend-current-head (accepted correction) for data-hygiene since the #151 precedent strips this class, with append-only disclosure; no rewrite of any published verdict.

Changed:
- docs/plans/PCM-0046-arms-results/{isolation-audit.json,REPORT.md,meta.json}

Blocked/uncertain:
- none

Next:
- Open PR, arm auto-merge after this final push, post merge receipt on #189 and a pointer on #191.

### 2026-09-26 13:42:26 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":[],"changed":["docs/plans/PCM-0015-implementation-plan.md, docs/plans/PCM-0046-arms-results/{REPORT.md,meta.json}, .continuity/documents.json, docs/CONTINUITY_INDEX.md"],"completed":["Correction 9 states plainly that the #197 redaction cannot and does not rewrite history: the device path stays reachable at 5d6d9ad, no force-push per contract, head clean. Repo-wide rescan (scope advisory) found a SECOND pre-existing breach the first scan's prefix missed: PCM-0015 implementation plan line 11 carried another machine's Windows home path (C:/Users/pujan/...) since b379ba3; sanitized with the verification claims intact, disclosed as correction 10, catalog entry refreshed. meta.json _pin_history placeholder minute replaced with the observed 13:15Z/d33cb35 value; manifest re-pinned with superseded-entry chain for REPORT.md corrections 9-10."],"decisions":["Sanitize-in-place + numbered disclosure (records rule bans private absolute paths; the withheld string carried no verification load), rather than leaving a blanket clean claim."],"evidence":["grep -r for C:/Users/ and the macOS prefix across docs/.continuity/checkpoints/tasks: 0 remaining hits (ignored __pycache__ aside); pins loop zero stale; docs render --check SYNCHRONIZED after refresh pcm-0015-plan; suite at six known names."],"next_action":"Open PR, arm auto-merge after this final push, post merge receipt on #189 and the gate note on #191.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0063","timestamp":"2026-09-26T13:42:26Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"cf42ab8df0c923b3f3c30f0c2d2d1cf639794d429e89878abfd6d2b039ec67de","request_id":"pcm-0063-residual-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0063"} -->

Completed:
- Correction 9 states plainly that the #197 redaction cannot and does not rewrite history: the device path stays reachable at 5d6d9ad, no force-push per contract, head clean. Repo-wide rescan (scope advisory) found a SECOND pre-existing breach the first scan's prefix missed: PCM-0015 implementation plan line 11 carried another machine's Windows home path (C:/Users/pujan/...) since b379ba3; sanitized with the verification claims intact, disclosed as correction 10, catalog entry refreshed. meta.json _pin_history placeholder minute replaced with the observed 13:15Z/d33cb35 value; manifest re-pinned with superseded-entry chain for REPORT.md corrections 9-10.

Evidence:
- grep -r for C:/Users/ and the macOS prefix across docs/.continuity/checkpoints/tasks: 0 remaining hits (ignored __pycache__ aside); pins loop zero stale; docs render --check SYNCHRONIZED after refresh pcm-0015-plan; suite at six known names.

Decisions:
- Sanitize-in-place + numbered disclosure (records rule bans private absolute paths; the withheld string carried no verification load), rather than leaving a blanket clean claim.

Changed:
- docs/plans/PCM-0015-implementation-plan.md, docs/plans/PCM-0046-arms-results/{REPORT.md,meta.json}, .continuity/documents.json, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- none

Next:
- Open PR, arm auto-merge after this final push, post merge receipt on #189 and the gate note on #191.

### 2026-09-26 14:20:40 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":[],"changed":["tasks/TASK-PCM-0063-t2-staleness-guidance-decision.md (revert+this entry), docs/plans/PCM-0046-arms-results/{REPORT.md,meta.json}, .continuity/documents.json, docs/CONTINUITY_INDEX.md"],"completed":["Supersedes the unmerged entry pushed at 5acc4db: its 'sanitized in place' claim failed closed. Editing the recorded path string broke that entry's payload digest (validate: 'checkpoint 5 payload digest does not match'; PR #199 CI runs 36246963173/36247044038, test 3.11+3.12 fail) \u2014 the append-only invariant PCM-0046 measured enforced itself on this remediation within one hour. The task file is reverted to its merged (1d91487) content; the abbreviated foreign path therefore remains in one recorded, hash-immutable checkpoint entry on tracked head, disclosed rather than removed. Procedure defect filed as #201 (A: composition-time payload scan \u2014 recommended; B: digest-verifiable supersession class; C: rejected), superseding duplicate #200. REPORT.md correction 11 rewritten to tell this truth; manifest re-pinned; gate-(B) note 5846995405 posted to #191."],"decisions":["Prevention is the only rule-compliant lever under an immutable chain: post-hoc in-place edits are structurally impossible for checkpoint text, so scanning happens before hashing (#201 option A)."],"evidence":["gh run logs quote the digest error verbatim; grep over tasks/docs/checkpoints/.continuity: the only remaining tracked occurrence is inside the immutable 1d91487-era entry itself (REPORT.md and meta now 0); docs render --check after refresh; suite baseline six known names."],"next_action":"Push to update PR #199 (auto-merge stays armed); verify green on the new head; on merge, receipts on #189 and #201.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0063","timestamp":"2026-09-26T14:20:40Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"4639f584d641b937db168dfd393938e9b3cfec54f5f7265d0263bd9c11944ff5","request_id":"pcm-0063-revert-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0063"} -->

Completed:
- Supersedes the unmerged entry pushed at 5acc4db: its 'sanitized in place' claim failed closed. Editing the recorded path string broke that entry's payload digest (validate: 'checkpoint 5 payload digest does not match'; PR #199 CI runs 36246963173/36247044038, test 3.11+3.12 fail) — the append-only invariant PCM-0046 measured enforced itself on this remediation within one hour. The task file is reverted to its merged (1d91487) content; the abbreviated foreign path therefore remains in one recorded, hash-immutable checkpoint entry on tracked head, disclosed rather than removed. Procedure defect filed as #201 (A: composition-time payload scan — recommended; B: digest-verifiable supersession class; C: rejected), superseding duplicate #200. REPORT.md correction 11 rewritten to tell this truth; manifest re-pinned; gate-(B) note 5846995405 posted to #191.

Evidence:
- gh run logs quote the digest error verbatim; grep over tasks/docs/checkpoints/.continuity: the only remaining tracked occurrence is inside the immutable 1d91487-era entry itself (REPORT.md and meta now 0); docs render --check after refresh; suite baseline six known names.

Decisions:
- Prevention is the only rule-compliant lever under an immutable chain: post-hoc in-place edits are structurally impossible for checkpoint text, so scanning happens before hashing (#201 option A).

Changed:
- tasks/TASK-PCM-0063-t2-staleness-guidance-decision.md (revert+this entry), docs/plans/PCM-0046-arms-results/{REPORT.md,meta.json}, .continuity/documents.json, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- none

Next:
- Push to update PR #199 (auto-merge stays armed); verify green on the new head; on merge, receipts on #189 and #201.

### 2026-09-26 15:12:27 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":[],"changed":["tasks/TASK-PCM-0063-t2-staleness-guidance-decision.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md"],"completed":["Projection factual sync: marker why and Evidence line carried the pre-correction 'three arms' counter-signal count; REPORT.md correction 6 (merged 4044c80) established 5/5 from the committed answer files. Task markers are schema-checked, not digest-chained, so this is a legitimate current-state correction of my own live projection rather than an edit to any published checkpoint record. Owed-note from post-merge review now closed instead of deferred, per the explicit-completion requirement; no REPORT or history change needed (correction 6 already supersedes at the source)."],"decisions":["Small dedicated increment rather than fourth correction-fold: the advisory's own alternative (note as owed) leaves a knowingly inconsistent record I own; user directive is complete work."],"evidence":["grep: 'three stated'/'3 arms' gone from non-immutable fields; the two surviving hits sit only inside the hash-immutable 13:42:26Z entry (disclosed, unremovable pending #201); docs refresh pcm-0063-decision + render SYNCHRONIZED; suite at six known names."],"next_action":"Open PR, arm auto-merge after this final push, post merge receipt on #189.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0063","timestamp":"2026-09-26T15:12:27Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"c6ee2f3f6463ad15748bc662e4d67aacfc9305494f0e01189236059e0d2ef775","request_id":"pcm-0063-countsync-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0063"} -->

Completed:
- Projection factual sync: marker why and Evidence line carried the pre-correction 'three arms' counter-signal count; REPORT.md correction 6 (merged 4044c80) established 5/5 from the committed answer files. Task markers are schema-checked, not digest-chained, so this is a legitimate current-state correction of my own live projection rather than an edit to any published checkpoint record. Owed-note from post-merge review now closed instead of deferred, per the explicit-completion requirement; no REPORT or history change needed (correction 6 already supersedes at the source).

Evidence:
- grep: 'three stated'/'3 arms' gone from non-immutable fields; the two surviving hits sit only inside the hash-immutable 13:42:26Z entry (disclosed, unremovable pending #201); docs refresh pcm-0063-decision + render SYNCHRONIZED; suite at six known names.

Decisions:
- Small dedicated increment rather than fourth correction-fold: the advisory's own alternative (note as owed) leaves a knowingly inconsistent record I own; user directive is complete work.

Changed:
- tasks/TASK-PCM-0063-t2-staleness-guidance-decision.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- none

Next:
- Open PR, arm auto-merge after this final push, post merge receipt on #189.

### 2026-09-26 15:23:35 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":[],"changed":["docs/plans/PCM-0046-arms-results/{REPORT.md,meta.json}"],"completed":["Correction 12 appended: (a) the feared second published surface (squash commit message of 1d91487) was queried via the commits API and contains zero occurrences - composition discipline held for commit messages even where it failed for checkpoint payloads; (b) the PCM-0063 count-sync owed-note is closed on the record (fixed in b1fb4f0), not deferred; (c) meta note timestamp reworded to '~13:15Z (approximate, just before the checkpoint commit)' per review nit rather than asserting the commit time as the re-pin instant."],"decisions":["Folded this correction into the current touch instead of leaving the commit-message question open in the record; no rewrite, no new micro-cycle beyond this single increment."],"evidence":["commits API for 1d91487 and 4044c80: 0 username hits each (re-checked on main b1fb4f0 after the countsync merge, which itself contains no new literal); ledger of the foreign username: full form 0 tracked/0 commit messages, abbreviated form exactly 2 hits inside the one immutable entry, all disclosed in corrections 8-12; docs render --check SYNCHRONIZED; suite 274 at six known names; pins loop zero stale."],"next_action":"Open PR, arm auto-merge after this final push, post merge receipt on #189, then stop: remaining queue is owner-gated (#201, #189-191, #181/182/185, #144/142/143).","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0063","timestamp":"2026-09-26T15:23:35Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"3a7b66ba9a5a1a07c870566a4f3ee14a9a72a3708a08819b3f994ffd3e86df87","request_id":"pcm-0063-c12-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0063"} -->

Completed:
- Correction 12 appended: (a) the feared second published surface (squash commit message of 1d91487) was queried via the commits API and contains zero occurrences - composition discipline held for commit messages even where it failed for checkpoint payloads; (b) the PCM-0063 count-sync owed-note is closed on the record (fixed in b1fb4f0), not deferred; (c) meta note timestamp reworded to '~13:15Z (approximate, just before the checkpoint commit)' per review nit rather than asserting the commit time as the re-pin instant.

Evidence:
- commits API for 1d91487 and 4044c80: 0 username hits each (re-checked on main b1fb4f0 after the countsync merge, which itself contains no new literal); ledger of the foreign username: full form 0 tracked/0 commit messages, abbreviated form exactly 2 hits inside the one immutable entry, all disclosed in corrections 8-12; docs render --check SYNCHRONIZED; suite 274 at six known names; pins loop zero stale.

Decisions:
- Folded this correction into the current touch instead of leaving the commit-message question open in the record; no rewrite, no new micro-cycle beyond this single increment.

Changed:
- docs/plans/PCM-0046-arms-results/{REPORT.md,meta.json}

Blocked/uncertain:
- none

Next:
- Open PR, arm auto-merge after this final push, post merge receipt on #189, then stop: remaining queue is owner-gated (#201, #189-191, #181/182/185, #144/142/143).

### 2026-09-26 15:44:30 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":[],"changed":["tasks/TASK-PCM-0063-t2-staleness-guidance-decision.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md"],"completed":["Final live-record field synced: the prose Why paragraph (line 16) carried the superseded 'three stated' count while the marker why and Evidence lines were fixed in b1fb4f0; now reads all-five with the correction-6 pointer. Attempts in two earlier increments mis-assessed this field as already fixed (the countsync2 claim was wrong, and that commit was discarded before merge for other reasons) - disclosed so the record reflects exactly when each field converged: this entry."],"decisions":["Correction-12's 'closed in full' claim about the count-sync ledger was premature by one field; the immutable corrections 6/12 are not edited - this entry and the corrected prose are the record."],"evidence":["grep on origin/main 49c157e showed the stale prose before this branch; after: zero live-field hits, remaining occurrences only inside hash-immutable checkpoint entries describing history; docs refresh + render SYNCHRONIZED; suite 274 at six known names; validate single pre-existing device-local error."],"next_action":"Open PR, arm auto-merge after this final push, post merge receipt on #189. Queue then fully owner-gated.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0063","timestamp":"2026-09-26T15:44:30Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"0aed36f1a9f2fb8854df16affe9b2c65add03e20e3038d32c72a8f623b7b6703","request_id":"pcm-0063-whysync-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0063"} -->

Completed:
- Final live-record field synced: the prose Why paragraph (line 16) carried the superseded 'three stated' count while the marker why and Evidence lines were fixed in b1fb4f0; now reads all-five with the correction-6 pointer. Attempts in two earlier increments mis-assessed this field as already fixed (the countsync2 claim was wrong, and that commit was discarded before merge for other reasons) - disclosed so the record reflects exactly when each field converged: this entry.

Evidence:
- grep on origin/main 49c157e showed the stale prose before this branch; after: zero live-field hits, remaining occurrences only inside hash-immutable checkpoint entries describing history; docs refresh + render SYNCHRONIZED; suite 274 at six known names; validate single pre-existing device-local error.

Decisions:
- Correction-12's 'closed in full' claim about the count-sync ledger was premature by one field; the immutable corrections 6/12 are not edited - this entry and the corrected prose are the record.

Changed:
- tasks/TASK-PCM-0063-t2-staleness-guidance-decision.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- none

Next:
- Open PR, arm auto-merge after this final push, post merge receipt on #189. Queue then fully owner-gated.

### 2026-09-26 15:58:29 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":[],"changed":["tasks/TASK-PCM-0063-t2-staleness-guidance-decision.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md"],"completed":["Supersedes paragraph, delivered as promised by #189 audit comment 5847664853: (a) the #204 checkpoint entry (push 8432493) opened 'the prior countsync increment fixed the marker why field and Evidence line but its prose Why paragraph still carried the pre-correction count' - false premise; b1fb4f0 had already rewritten line 16 identically, so #204's only effective delta to this file was catalog/index churn. That entry is hash-immutable and stands as recorded history; this paragraph supersedes its claim. (b) Correction 12's 'closed in full' ledger sentence was premature by the same non-assessment; not edited (published), superseded here per append-only. (c) Line 16 on current head 642b1ad verified correct text ('all five stated ... correction 6 supersedes the initial three-arm count'); non-immutable grep for the stale count: zero hits."],"decisions":["One final amendment entry instead of editing published text; no manifest re-pin performed - this increment changes no pinned artifact, per the explicit stop-repinning guidance."],"evidence":["gh pr view 204 -> MERGED 642b1ad 15:46:27Z; sed -n '16p' before/after b1fb4f0 diff comparison (git show b1fb4f0 task file line 16 vs 49c157e: identical); published-surface sweep (issue comments since 12:00Z + PR bodies/comments for #195-#204): zero occurrences outside immutable entries."],"next_action":"Open PR #205, arm auto-merge after this final push; on merge, one receipt on #189; then STOP: remaining queue fully owner-gated (#201 options A/B, #189-191, #181/182/185, #144/142/143/#135, #171/#110/#33).","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0063","timestamp":"2026-09-26T15:58:29Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"91cc2fc3e47be605875b83045812ed71f9a7b36595f108788bb25b5cc6dcc162","request_id":"pcm-0063-amend3-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0063"} -->

Completed:
- Supersedes paragraph, delivered as promised by #189 audit comment 5847664853: (a) the #204 checkpoint entry (push 8432493) opened 'the prior countsync increment fixed the marker why field and Evidence line but its prose Why paragraph still carried the pre-correction count' - false premise; b1fb4f0 had already rewritten line 16 identically, so #204's only effective delta to this file was catalog/index churn. That entry is hash-immutable and stands as recorded history; this paragraph supersedes its claim. (b) Correction 12's 'closed in full' ledger sentence was premature by the same non-assessment; not edited (published), superseded here per append-only. (c) Line 16 on current head 642b1ad verified correct text ('all five stated ... correction 6 supersedes the initial three-arm count'); non-immutable grep for the stale count: zero hits.

Evidence:
- gh pr view 204 -> MERGED 642b1ad 15:46:27Z; sed -n '16p' before/after b1fb4f0 diff comparison (git show b1fb4f0 task file line 16 vs 49c157e: identical); published-surface sweep (issue comments since 12:00Z + PR bodies/comments for #195-#204): zero occurrences outside immutable entries.

Decisions:
- One final amendment entry instead of editing published text; no manifest re-pin performed - this increment changes no pinned artifact, per the explicit stop-repinning guidance.

Changed:
- tasks/TASK-PCM-0063-t2-staleness-guidance-decision.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- none

Next:
- Open PR #205, arm auto-merge after this final push; on merge, one receipt on #189; then STOP: remaining queue fully owner-gated (#201 options A/B, #189-191, #181/182/185, #144/142/143/#135, #171/#110/#33).

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
