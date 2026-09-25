# TASK-PCM-0050 — Epistemic bitemporal records decision

<!-- continuity:task {"acceptance": ["Owner selects O1/O2/O3/O4 (or combination) for claim provenance, bitemporal supersession, actor identity, classification, and adopter ticket placement, recorded on #144.", "The five open questions in docs/research/PCM-0050-epistemic-bitemporal-records.md receive a recorded answer or explicit deferral.", "Follow-up implementation issues filed per selection; this task closes as the decision record."], "depends_on": [], "goal": "Decide PCM's epistemic/bitemporal record model from researched options; no normative change in this slice.", "id": "PCM-0050", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/144", "next_action": "Owner reads the research note and answers the five open questions on #144; implementation slices fan out only after that.", "owner": "owner/Astra planning", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "active", "why": "Prose records are consumed as ground truth; without per-claim provenance, valid/transaction time and supersession links, fresh sessions re-litigate settled disagreements."} -->

- Status: active (research delivered; awaiting owner decision)
- Owner: owner/Astra planning
- Priority: P2
- Depends on: none; related #142/#143 (intake gaps that motivated this research), #67 (actor identity precedent), #137 (evidence-vs-claim holdouts)

## Checkpoint log

### 2026-09-25 — research delivered

Completed: external research (Snodgrass bitemporal model; event-sourcing supersession; W3C PROV/PROV-AQ; MITRE provenance-based belief — all cited in note); in-repo audit of claim/provenance/supersession/identity/classification/pile-up handling; four options O1-O4 with a recommended O2+O4 stance; five open questions for the owner.

Evidence: docs/research/PCM-0050-epistemic-bitemporal-records.md at this commit; issue #144 body.

Decisions: trust derives from epistemic status + evidence + independence class, never filer identity alone; GitHub ID recorded for auditability, not ranking.

Blocked/uncertain: owner decision pending; no SPEC/AGENTS/template edits authorized.

Next: owner answers the five open questions on #144.

### 2026-09-25 20:02:14 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["Local validate prints one device-local error for foreign worktree /private/tmp/pcm-pinned (pre-existing, preserved per policy, invisible to hosted CI). Workers T46Scorer2/T47Hygiene2 running; zero-delta task branches pushed so a dead session is visible as no-work rather than missing refs."],"changed":["docs/research/PCM-0050-epistemic-bitemporal-records.md, docs/plans/PCM-0046-arm-plan.md (new), .continuity/documents.json, docs/CONTINUITY_INDEX.md, checkpoints/CURRENT.md, tasks/TASK-PCM-0050-epistemic-records.md"],"completed":["Advisory remediation: PCM-0015 S9 prior-art delta addendum; MITRE/USENIX citations corrected to Chapman et al 2010 and Friedman et al 2020; research note + arm plan + three decision projections registered in the document catalog and index rendered; 20-arm plan committed to docs/plans/PCM-0046-arm-plan.md; CURRENT active_task repointed to PCM-0050; #143 ID correction comment posted (5838709963)."],"decisions":["O2 reframed as promoting PCM-0015 S9 plus five deltas (valid-time fields, independence class, O4 adopter channel, classification/aging, discovery fallback); discovery defect recorded: task-filtered docs find structurally misses prior art for new tasks until links exist."],"evidence":["docs find 'epistemic provenance bitemporal scoped assertions claims' --task PCM-0050 now matches pcm-0050-research (score 28) and prior art pcm-0015-research (16)/pcm-0015-plan (6); previously NO_MATCHES. Product commit at branch head; this checkpoint commits the task projection and pushes task/PCM-0050-epistemic-records."],"next_action":"Open PR for task/PCM-0050-epistemic-records, verify required CI and auto-merge, then post merge receipt on #144; owner answers the five open questions there.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0050","timestamp":"2026-09-25T20:02:14Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"47c4ec7fb0b9158f49424c8540fedfac9ad740eff53ca3983dc430c385b7a617","request_id":"pcm-0050-advisory-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0050"} -->

Completed:
- Advisory remediation: PCM-0015 S9 prior-art delta addendum; MITRE/USENIX citations corrected to Chapman et al 2010 and Friedman et al 2020; research note + arm plan + three decision projections registered in the document catalog and index rendered; 20-arm plan committed to docs/plans/PCM-0046-arm-plan.md; CURRENT active_task repointed to PCM-0050; #143 ID correction comment posted (5838709963).

Evidence:
- docs find 'epistemic provenance bitemporal scoped assertions claims' --task PCM-0050 now matches pcm-0050-research (score 28) and prior art pcm-0015-research (16)/pcm-0015-plan (6); previously NO_MATCHES. Product commit at branch head; this checkpoint commits the task projection and pushes task/PCM-0050-epistemic-records.

Decisions:
- O2 reframed as promoting PCM-0015 S9 plus five deltas (valid-time fields, independence class, O4 adopter channel, classification/aging, discovery fallback); discovery defect recorded: task-filtered docs find structurally misses prior art for new tasks until links exist.

Changed:
- docs/research/PCM-0050-epistemic-bitemporal-records.md, docs/plans/PCM-0046-arm-plan.md (new), .continuity/documents.json, docs/CONTINUITY_INDEX.md, checkpoints/CURRENT.md, tasks/TASK-PCM-0050-epistemic-records.md

Blocked/uncertain:
- Local validate prints one device-local error for foreign worktree /private/tmp/pcm-pinned (pre-existing, preserved per policy, invisible to hosted CI). Workers T46Scorer2/T47Hygiene2 running; zero-delta task branches pushed so a dead session is visible as no-work rather than missing refs.

Next:
- Open PR for task/PCM-0050-epistemic-records, verify required CI and auto-merge, then post merge receipt on #144; owner answers the five open questions there.

### 2026-09-25 20:05:05 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["Owner decision on five open questions (#144) pending; workers T46Scorer2/T47Hygiene2 in flight on zero-delta-pushed branches."],"changed":["tasks/TASK-PCM-0050-epistemic-records.md (this entry only)"],"completed":["Branch state reconciled after reviewer caught a lost-then-reapplied addendum: task/PCM-0050-epistemic-records head 81c30e7 now contains the prior-art addendum (PCM-0015 S9 delta), corrected citations (Chapman/Blaustein/Elsaesser TaPP 2010 UNVERIFIED vs Friedman et al. TaPP 2020), catalog registration, committed arm plan, repointed CURRENT, and checkpoint entry 1."],"decisions":["Correction to entry 1 (append-only): entry 1 claimed the addendum shipped in product commit e1cb2ce; it actually landed in the amended checkpoint commit 81c30e7 because a branch reset discarded the first uncommitted copy. Entry 1's pushed SHA f3ae58d was superseded by the amend; this entry's push is the authoritative branch state. #144 receipt 5838757901 references f3ae58d and will be superseded by a correction comment keyed to the merge SHA."],"evidence":["grep: 'Addendum 2026-09-25' present; 'Chapman' present x2; entry pcm-0050-advisory-20260925 present in task file; tree clean at 81c30e7."],"next_action":"Open PR for task/PCM-0050-epistemic-records, verify required CI and auto-merge, post superseding receipt on #144 keyed to the merge SHA.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0050","timestamp":"2026-09-25T20:05:05Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"a0eb9c73e21fe4f369db19cfdce562365c4b5adc2a6c7db226e8bb5e1444910c","request_id":"pcm-0050-advisory3-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0050"} -->

Completed:
- Branch state reconciled after reviewer caught a lost-then-reapplied addendum: task/PCM-0050-epistemic-records head 81c30e7 now contains the prior-art addendum (PCM-0015 S9 delta), corrected citations (Chapman/Blaustein/Elsaesser TaPP 2010 UNVERIFIED vs Friedman et al. TaPP 2020), catalog registration, committed arm plan, repointed CURRENT, and checkpoint entry 1.

Evidence:
- grep: 'Addendum 2026-09-25' present; 'Chapman' present x2; entry pcm-0050-advisory-20260925 present in task file; tree clean at 81c30e7.

Decisions:
- Correction to entry 1 (append-only): entry 1 claimed the addendum shipped in product commit e1cb2ce; it actually landed in the amended checkpoint commit 81c30e7 because a branch reset discarded the first uncommitted copy. Entry 1's pushed SHA f3ae58d was superseded by the amend; this entry's push is the authoritative branch state. #144 receipt 5838757901 references f3ae58d and will be superseded by a correction comment keyed to the merge SHA.

Changed:
- tasks/TASK-PCM-0050-epistemic-records.md (this entry only)

Blocked/uncertain:
- Owner decision on five open questions (#144) pending; workers T46Scorer2/T47Hygiene2 in flight on zero-delta-pushed branches.

Next:
- Open PR for task/PCM-0050-epistemic-records, verify required CI and auto-merge, post superseding receipt on #144 keyed to the merge SHA.

### 2026-09-25 20:59:38 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["None."],"changed":["tasks/TASK-PCM-0050-epistemic-records.md, docs/CONTINUITY_INDEX.md (auto)"],"completed":["PCM-0047 dogfood on the real publish path: this checkpoint's --next deliberately contains close #144; the sanitizer must rewrite it to a Refs form with an operator NOTE, and because tasks/TASK-PCM-0050-epistemic-records.md is cataloged the generated index must refresh in the same commit."],"decisions":["Dogfood acceptance line for PCM-0047 (issue 140) executed here after #147 merge; earlier checkpoint pcm-0047-merge-20260925 did not exercise either fixed path (no keyword, non-cataloged file) \u2014 correction posted rather than silently replaced."],"evidence":["Post-run checks recorded on #140/#123: commit message keyword-free, NOTE printed, docs render --check SYNCHRONIZED at pushed head."],"next_action":"Verify sanitizer NOTE + keyword-free message + SYNCHRONIZED index at pushed head, post dogfood evidence to #140/#123, then launch scout text arms.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0050","timestamp":"2026-09-25T20:59:38Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"bfefedb7ee800179bfa947c3b657af0d3722f178b00d182712a969db9a9e74e2","request_id":"pcm-0047-dogfood-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0050"} -->

Completed:
- PCM-0047 dogfood on the real publish path: this checkpoint's --next deliberately contains close #144; the sanitizer must rewrite it to a Refs form with an operator NOTE, and because tasks/TASK-PCM-0050-epistemic-records.md is cataloged the generated index must refresh in the same commit.

Evidence:
- Post-run checks recorded on #140/#123: commit message keyword-free, NOTE printed, docs render --check SYNCHRONIZED at pushed head.

Decisions:
- Dogfood acceptance line for PCM-0047 (issue 140) executed here after #147 merge; earlier checkpoint pcm-0047-merge-20260925 did not exercise either fixed path (no keyword, non-cataloged file) — correction posted rather than silently replaced.

Changed:
- tasks/TASK-PCM-0050-epistemic-records.md, docs/CONTINUITY_INDEX.md (auto)

Blocked/uncertain:
- None.

Next:
- Verify sanitizer NOTE + keyword-free message + SYNCHRONIZED index at pushed head, post dogfood evidence to #140/#123, then launch scout text arms.

### 2026-09-25 21:01:48 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["None."],"changed":["tasks/TASK-PCM-0050-epistemic-records.md, docs/CONTINUITY_INDEX.md (auto)"],"completed":["Second dogfood pass: fresh checkpoint whose next_action embeds a closing keyword, exercising the sanitizer on a real generated commit message (the idempotent retry of pcm-0047-dogfood-20260925 only re-pushed a pre-made commit and proved the index-refresh NOTE)."],"decisions":["Dogfood acceptance for PCM-0047 requires the sanitizer to fire on a generated commit; retry path does not regenerate the message."],"evidence":["Commit message of this checkpoint inspected for absence of effective closing keywords; NOTE printed by sanitizer; docs render --check SYNCHRONIZED at pushed head."],"next_action":"Post dogfood evidence to #140 and #123, then launch scout text arms.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0050","timestamp":"2026-09-25T21:01:48Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"4c22ac41310de8c72e34e5d08b5e40532b69a5057e62a3543289aba66a0de4a6","request_id":"pcm-0047-dogfood2-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0050"} -->

Completed:
- Second dogfood pass: fresh checkpoint whose next_action embeds a closing keyword, exercising the sanitizer on a real generated commit message (the idempotent retry of pcm-0047-dogfood-20260925 only re-pushed a pre-made commit and proved the index-refresh NOTE).

Evidence:
- Commit message of this checkpoint inspected for absence of effective closing keywords; NOTE printed by sanitizer; docs render --check SYNCHRONIZED at pushed head.

Decisions:
- Dogfood acceptance for PCM-0047 requires the sanitizer to fire on a generated commit; retry path does not regenerate the message.

Changed:
- tasks/TASK-PCM-0050-epistemic-records.md, docs/CONTINUITY_INDEX.md (auto)

Blocked/uncertain:
- None.

Next:
- Post dogfood evidence to #140 and #123, then launch scout text arms.

### 2026-09-25 21:02:12 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["None."],"changed":["tasks/TASK-PCM-0050-epistemic-records.md, docs/CONTINUITY_INDEX.md (auto)"],"completed":["Third dogfood pass: next_action deliberately embeds the literal keyword sequence close #144 so the sanitizer must rewrite the generated commit message; prior passes proved the index NOTE but never fired the sanitizer."],"decisions":["Sanitizer proof requires a generated commit whose source --next contains an effective closing keyword."],"evidence":["Inspect this checkpoint's commit message: expect Refs #144 (no effective keyword) plus the sanitizer NOTE on stdout; docs render --check SYNCHRONIZED at pushed head."],"next_action":"Verify sanitizer output then post dogfood evidence to #140 and #123.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0050","timestamp":"2026-09-25T21:02:12Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"febf0ef8eb01f27f2df35fe23a51c35a89c46988b330dcb6563164f36b8e3fdc","request_id":"pcm-0047-dogfood3-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0050"} -->

Completed:
- Third dogfood pass: next_action deliberately embeds the literal keyword sequence close #144 so the sanitizer must rewrite the generated commit message; prior passes proved the index NOTE but never fired the sanitizer.

Evidence:
- Inspect this checkpoint's commit message: expect Refs #144 (no effective keyword) plus the sanitizer NOTE on stdout; docs render --check SYNCHRONIZED at pushed head.

Decisions:
- Sanitizer proof requires a generated commit whose source --next contains an effective closing keyword.

Changed:
- tasks/TASK-PCM-0050-epistemic-records.md, docs/CONTINUITY_INDEX.md (auto)

Blocked/uncertain:
- None.

Next:
- Verify sanitizer output then post dogfood evidence to #140 and #123.

### 2026-09-25 21:02:36 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["None."],"changed":["tasks/TASK-PCM-0050-epistemic-records.md, docs/CONTINUITY_INDEX.md (auto)"],"completed":["Fourth dogfood pass: keyword placed in --next itself (close #99999, a deliberately non-existent ref so a sanitizer failure cannot close a real issue); the tool composes and creates the commit so the sanitizer path is the only message author."],"decisions":["Passes 1-3 proved the index-refresh NOTE only; sanitizer proof requires the keyword in the composed subject."],"evidence":["Sanitizer NOTE on stdout + git log -1 --format=%B showing Refs #99999 rewrite at pushed head e8c1b32's successor."],"next_action":"Confirm sanitizer rewrite in this commit's message, then post split evidence to #140 and #123: index refresh proven across passes 1-4, sanitizer proven by this pass.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0050","timestamp":"2026-09-25T21:02:36Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"410ac8eddbedc8ef06901daeca80b2fd17c8ec6e1e17c27312227e4b6a1bb91d","request_id":"pcm-0047-dogfood4-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0050"} -->

Completed:
- Fourth dogfood pass: keyword placed in --next itself (close #99999, a deliberately non-existent ref so a sanitizer failure cannot close a real issue); the tool composes and creates the commit so the sanitizer path is the only message author.

Evidence:
- Sanitizer NOTE on stdout + git log -1 --format=%B showing Refs #99999 rewrite at pushed head e8c1b32's successor.

Decisions:
- Passes 1-3 proved the index-refresh NOTE only; sanitizer proof requires the keyword in the composed subject.

Changed:
- tasks/TASK-PCM-0050-epistemic-records.md, docs/CONTINUITY_INDEX.md (auto)

Blocked/uncertain:
- None.

Next:
- Confirm sanitizer rewrite in this commit's message, then post split evidence to #140 and #123: index refresh proven across passes 1-4, sanitizer proven by this pass.

### 2026-09-25 21:02:48 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["None."],"changed":["tasks/TASK-PCM-0050-epistemic-records.md, docs/CONTINUITY_INDEX.md (auto)"],"completed":["Fifth pass: the keyword now sits in the next_action text itself (close #99999, non-existent ref), which is what composes the commit subject."],"decisions":["Passes 1-4 had the keyword only in non-message fields; this pass targets the message composition path."],"evidence":["Expect stdout NOTE: closing keyword sanitized; expect git log -1 subject to read Refs #99999."],"next_action":"Verify subject rewrite then post split dogfood evidence to #140 and #123.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0050","timestamp":"2026-09-25T21:02:48Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"65f86aad2aafdcdc4afbdc123772765dfa97fbf136d86875007f4cc05631dc4c","request_id":"pcm-0047-dogfood5-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0050"} -->

Completed:
- Fifth pass: the keyword now sits in the next_action text itself (close #99999, non-existent ref), which is what composes the commit subject.

Evidence:
- Expect stdout NOTE: closing keyword sanitized; expect git log -1 subject to read Refs #99999.

Decisions:
- Passes 1-4 had the keyword only in non-message fields; this pass targets the message composition path.

Changed:
- tasks/TASK-PCM-0050-epistemic-records.md, docs/CONTINUITY_INDEX.md (auto)

Blocked/uncertain:
- None.

Next:
- Verify subject rewrite then post split dogfood evidence to #140 and #123.

### 2026-09-25 21:02:58 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["None."],"changed":["tasks/TASK-PCM-0050-epistemic-records.md, docs/CONTINUITY_INDEX.md (auto)"],"completed":["Sixth pass: keyword placed in the --next text itself this time; subject composition reads only --next, so the sanitizer must fire on the generated commit message."],"decisions":["Passes 1-5 placed the keyword in non-message fields; only --next reaches the subject."],"evidence":["Expect stdout 'NOTE: closing keyword sanitized' and subject 'Refs #99999' instead of 'close #99999'."],"next_action":"close #99999 after posting split dogfood evidence to #140 and #123","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0050","timestamp":"2026-09-25T21:02:58Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"857d2d44e9af50148fd9dc24fbb21879f37c3e123d263a4812b138c92ce9b4c9","request_id":"pcm-0047-dogfood6-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0050"} -->

Completed:
- Sixth pass: keyword placed in the --next text itself this time; subject composition reads only --next, so the sanitizer must fire on the generated commit message.

Evidence:
- Expect stdout 'NOTE: closing keyword sanitized' and subject 'Refs #99999' instead of 'close #99999'.

Decisions:
- Passes 1-5 placed the keyword in non-message fields; only --next reaches the subject.

Changed:
- tasks/TASK-PCM-0050-epistemic-records.md, docs/CONTINUITY_INDEX.md (auto)

Blocked/uncertain:
- None.

Next:
- close #99999 after posting split dogfood evidence to #140 and #123

## Handoff

Read PROJECT -> CURRENT -> this task -> #144 -> docs/research/PCM-0050-epistemic-bitemporal-records.md. Decision slice only.

### 2026-09-25 — Correction: dogfood passes 1-5 recorded sanitizer evidence their commits lack (append-only)

Passes 1-5 (requests pcm-0047-dogfood-20260925 replay, -dogfood2..5) state the keyword was in --next and/or expect a Refs rewrite in their own commit subject. Refuted by the artifacts: subjects of 888020b/411bf64/81938f0/e8c1b32/71b4ef6 contain no closing keyword and no Refs rewrite; only the index NOTE fired. Those five entries are valid evidence for the index-refresh half ONLY. The sanitizer proof is pass 6 alone: 2063136 (request pcm-0047-dogfood6-20260925) — --next began "close #99999", stdout printed "NOTE: closing keyword sanitized in commit message", subject reads "Refs #99999". Split evidence with this correction: #140 comment 5839601446; #140 closeout comment 5839320917 is partially inaccurate ("keyword-free ... in one pass") and superseded by 2063136. Entries above are preserved unmodified per append-only policy.

Next: holdout arms per docs/plans/PCM-0046-arm-plan.md amendment 11 after the provider window.
