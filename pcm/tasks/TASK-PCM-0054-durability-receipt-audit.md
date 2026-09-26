# TASK-PCM-0054 — Durability Receipt Audit

<!-- continuity:task {"acceptance":["Filing slice merged under six required hosted contexts with merge receipt on #169 (enforcement matrix at 690b7f8 with path:line evidence; three backfilled receipt ids recorded).","Owner decision recorded on #169: default-on receipts vs additive `continuity receipt audit` vs keep-as-convention; no CLI change before it.","If implementation approved: red-first audit proves exit non-zero on a pushed SHA lacking a keyed comment, zero when covered, graceful degrade offline; full suite at baseline."],"depends_on":[],"goal":"Close the durable-publication enforcement gap: pushed SHAs without a keyed leaf-issue receipt are invisible to every tool; give dogfood and adopters one deterministic receipt-gap audit (Refs #169).","id":"PCM-0054","issue_url":"https://github.com/Pukujan/project-continuity-modules/issues/169","next_action":"Implement approved audit slice on task/PCM-0054-receipt-audit (harness 0a04011); owner decision 5842002712 already approves the additive command.","owner":"owner/Astra planning","priority":"P2","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"The 2026-09-25 durability audit found three contract-required merge receipts never posted and no command noticed; Git-side durability is enforced in publish_checkpoint, issue-log durability is prose + opt-in flags only."} -->

- Status: active
- Owner: owner/Astra planning
- Priority: P2
- Depends on: none

## Goal

Close the durable-publication enforcement gap: pushed SHAs without a keyed leaf-issue receipt are invisible to every tool; give dogfood and adopters one deterministic receipt-gap audit (Refs #169).

## Why

The 2026-09-25 durability audit found three contract-required merge receipts never posted and no command noticed; Git-side durability is enforced in publish_checkpoint, issue-log durability is prose + opt-in flags only.

## Allowed files

- Filing slice (merged in `0fb5aca`): this task file, `checkpoints/CURRENT.md`, `.continuity/documents.json`, `docs/CONTINUITY_INDEX.md` (generated). Docs slice (named in the filed audit record): the stale "Issue #67 remains open" sentence corrected in all 9 guidance copies — `AGENTS.md`, `HANDOFF.md`, `src/continuity/cli.py` (`GITHUB_PROGRESSION_GUIDANCE`), `templates/v1/{minimal/PROJECT.md,minimal/HANDOFF.md,software/AGENTS.md,software/README.md}`, `.github/{pull_request_template.md,ISSUE_TEMPLATE/task.md}` — required-phrase test `automatic issue-comment synchronization is not implemented` kept intact. Implementation slice (only after the owner answers the design question on #169): `src/continuity/cli.py`, `tests/test_receipt_audit.py` (new), plus regenerated catalog/index.
- Amendment 2026-09-26 01:2xZ: the guidance-text fix in the docs slice edited `src/continuity/cli.py` but touched only the `GITHUB_PROGRESSION_GUIDANCE` string constant — no behavior, schema, or flag change — so it needs no #169 decision; the code-path restriction stands.

## Human outcome

A fresh session running one deterministic command learns, from the repository and the live issue alone, whether every pushed increment on a task branch actually produced its keyed leaf-issue receipt — so "durable means published" stops depending on writer memory in PCM and in every adopter repository that runs `continuity validate`.

## Scope and boundaries

- In scope: record the enforcement-gap finding with code-provenance (publish_checkpoint enforces push; receipt posting is opt-in; validate has no receipt rule); backfill evidence references; define the bounded design question for the receipt-gap audit.
- Out of scope: any cli.py/schema change before the owner answers on #169 (default-on posting vs audit-only vs status-quo convention); no autonomous polling; no other-host adapters.
- Dependencies/uncertainty: depends on none; related #67 (receipt route frozen opt-in by owner decision 5827958268 — this task proposes an ADDITIVE detector, not reversal), #162 acceptance-2 pattern, #166 caveat.

## Acceptance criteria

- [x] Filing slice merged under six required hosted contexts with merge receipt on #169: task projection + CURRENT entry record the enforcement matrix (code-enforced: branch/uncommitted/stale-base/sanitizer/push; convention+opt-in: receipt posting, merge-window discipline) with path:line evidence at `690b7f8`, and the three backfilled receipt ids (5841258606, 5841258803, 5841258608). DELIVERED: filing merged `0fb5aca` (#170, receipt 5841456903); docs slice merged `d5021a3` (#173, tool-posted push receipt 5841654302, merge receipt 5841856423); catalog registration correction + baseline-naming/version-identity fixes recorded append-only in 5841856422.
- [x] Owner decision recorded on #169 (comment 5842002712): additive `continuity receipt audit` command; receipts stay opt-in (#67 freeze semantics unchanged); implementation branch cut only after the decision.
- [x] Implementation (approved via 5842002712): red-first harness `411dbfc` failed before, then tests/test_receipt_audit.py 10/10 OK — gap -> exit 1 with MISSING lines; v2-marker, manual-comment short-sha-prefix, and request-id coverage -> clean; unproven lookup -> NOTE, never fabricating gaps; branch-not-on-origin -> NOTE; mismatched --repository vs github origin -> wrong-ledger error. Real-repo smoke: AUDIT_CLEAN exit 0 on surviving origin branch task/PCM-0053-stale-base-guard against #166 (push b87e019 covered by receipt 5841072961). Full discover 274 = six known macOS-environmental names, zero new; ruff@0.6.9 = two pre-existing ISC003.

## Evidence and sources

- Observed 2026-09-25 ~23:55Z audit: `git log --all --not --remotes=origin` → 11 commits, per-file superseded check clean (zero true-local-only); `gh pr view` #163/#164/#165/#167/#168 all MERGED six contexts; comment listing on #162/#166 proved receipts for 1bb3cb4/f4ffd6f/690b7f8 absent before backfill.
- Code provenance at `690b7f8` (cli 0.5.0): `publish_checkpoint` src/continuity/cli.py:3095-3177 (branch req :3115, uncommitted refuse :3121, stale-base :3127-3135, sanitizer :3144-3147, push :3176); `require_receipt_pair` cli.py:2924-2929 returns None when flags omitted; `validate_repo` cli.py:1556+ has no receipt rule; `GITHUB_PROGRESSION_GUIDANCE` cli.py:45-59 injected by `agents_template` cli.py:595.
- Leaf #169 body carries the full problem statement and proposal.

## Related records

- Leaf #169 (PCM-0054); parent: none; depends: none; related #67, #162, #166, #139.
- Primary writer: owner/Astra (omp session); branch task/PCM-0053-closeout (filing increment rides the PCM-0053 closeout push); source issue revision: #169 body at filing; as-of 2026-09-25T23:58Z.
- Receipt lineage (supersedes the earlier citation "request pcm-0054-filed-20260925", which was never a real request id — correction recorded on #169 in 5841856422): filing increment rode the PCM-0053 closeout checkpoint push `2f8dc7a` (request pcm-0053-closeout-20260925, receipt 5841406124 on #166) and merged in `0fb5aca` (receipt 5841456903 on #169); docs slice used request pcm-0054-docs-20260926, push `6af92aa`, tool receipt 5841654302, merge `d5021a3` (receipt 5841856423).

## Docs slice (stale #67 prose correction)

The filed record named this one-line prose defect; it is now corrected in all 9 copies of the guidance block: "Issue #67 remains open" -> "#67 is CLOSED (owner freeze decision 2026-09-25) and its unmet guaranteed-completion acceptance transferred to #110" (observed: #67 CLOSED/COMPLETED; #110 OPEN). The `tests/test_github_progression_policy.py` REQUIRED phrase "automatic issue-comment synchronization is not implemented" is preserved in every copy; guidance/records tests 33 OK; full discover 259 = six known environmental failures; docs render --check SYNCHRONIZED.

## Checkpoint log

No checkpoints yet.

### 2026-09-26 00:46:29 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["Acceptance 2 on #169 (owner decision) unchanged; PCM-0046 arms still provider-429."],"changed":["AGENTS.md, HANDOFF.md, src/continuity/cli.py (GITHUB_PROGRESSION_GUIDANCE only), templates/v1/minimal/PROJECT.md, templates/v1/minimal/HANDOFF.md, templates/v1/software/AGENTS.md, templates/v1/software/README.md, .github/pull_request_template.md, .github/ISSUE_TEMPLATE/task.md, checkpoints/CURRENT.md, tasks/TASK-PCM-0054-durability-receipt-audit.md, docs/CONTINUITY_INDEX.md"],"completed":["Stale guidance sentence 'Issue #67 remains open' corrected in all 9 copies (AGENTS, HANDOFF, GITHUB_PROGRESSION_GUIDANCE in cli.py, 4 templates, 2 .github templates): #67 is CLOSED (owner freeze) and the unmet guaranteed-completion acceptance transferred to #110; REQUIRED contract phrase preserved in every copy; task projection documents the slice."],"decisions":["Docs-only slice: no opt-in/default-on semantics changed; acceptance-2 owner question on #169 untouched."],"evidence":["gh issue view 67 -> CLOSED (COMPLETED), 110 -> OPEN; tests.test_github_progression_policy + issue-log-format + records-policy 33 OK; full discover 259 = six known macOS-environmental failures; docs render --check SYNCHRONIZED."],"next_action":"Open PR for task/PCM-0054-guidance-prose, verify six contexts + auto-merge, post merge receipt on #169.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0054","timestamp":"2026-09-26T00:46:29Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"56eb838af16d16b62b3b4245b004007d146c3d0b1d925818a59b60f96308c59f","request_id":"pcm-0054-docs-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0054"} -->

Completed:
- Stale guidance sentence 'Issue #67 remains open' corrected in all 9 copies (AGENTS, HANDOFF, GITHUB_PROGRESSION_GUIDANCE in cli.py, 4 templates, 2 .github templates): #67 is CLOSED (owner freeze) and the unmet guaranteed-completion acceptance transferred to #110; REQUIRED contract phrase preserved in every copy; task projection documents the slice.

Evidence:
- gh issue view 67 -> CLOSED (COMPLETED), 110 -> OPEN; tests.test_github_progression_policy + issue-log-format + records-policy 33 OK; full discover 259 = six known macOS-environmental failures; docs render --check SYNCHRONIZED.

Decisions:
- Docs-only slice: no opt-in/default-on semantics changed; acceptance-2 owner question on #169 untouched.

Changed:
- AGENTS.md, HANDOFF.md, src/continuity/cli.py (GITHUB_PROGRESSION_GUIDANCE only), templates/v1/minimal/PROJECT.md, templates/v1/minimal/HANDOFF.md, templates/v1/software/AGENTS.md, templates/v1/software/README.md, .github/pull_request_template.md, .github/ISSUE_TEMPLATE/task.md, checkpoints/CURRENT.md, tasks/TASK-PCM-0054-durability-receipt-audit.md, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- Acceptance 2 on #169 (owner decision) unchanged; PCM-0046 arms still provider-429.

Next:
- Open PR for task/PCM-0054-guidance-prose, verify six contexts + auto-merge, post merge receipt on #169.

### 2026-09-26 01:21:06 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["Acceptance 2 on #169 (owner decision); PCM-0046 arms provider-429 (~04:05Z)."],"changed":["tasks/TASK-PCM-0054-durability-receipt-audit.md, tasks/TASK-PCM-0055-receipt-json-encoding.md, checkpoints/CURRENT.md, docs/CONTINUITY_INDEX.md"],"completed":["Projection sync: acceptance 1 checked with delivered evidence (filing 0fb5aca + docs slice d5021a3; receipts 5841456903/5841654302/5841856423); false request-id citation replaced with corrected lineage; allowed-files amendment 2 (guidance-text fix needs no #169 decision); audit-correction pointer 5841856422 (PR #170 catalog claim, PR #172 citation, baseline names 5F+1E, 0.5.0 version identity); DB-posture question + answer recorded on #144 (5841877756). PCM-0055 closed out on this branch (cac15b4)."],"decisions":["Acceptance 2 stays owner-gated; DuckDB/OTEL analytics-substrate question to be filed as its own decision issue rather than folded here."],"evidence":["detached-worktree baseline discover at 690b7f8: same six broken names as current 259-test discover (worktrees 4F+1E, test_cli 2F) \u2014 zero regressions; gh comments API verified all cited ids; validate = device-local pcm-pinned error only."],"next_action":"Merge PR task/PCM-0054-projection-sync under six contexts, post merge receipt on #169, then owner answers the pending decision briefs (#162 5840695558, #169 acceptance 2, #144 O1-O4, #142, #143, #166 caveat).","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0054","timestamp":"2026-09-26T01:21:06Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"7fb29414aada88d1261c00d19520e72766f7be8de74dc96d0d3ad03b8dc69757","request_id":"pcm-0054-sync-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0054"} -->

Completed:
- Projection sync: acceptance 1 checked with delivered evidence (filing 0fb5aca + docs slice d5021a3; receipts 5841456903/5841654302/5841856423); false request-id citation replaced with corrected lineage; allowed-files amendment 2 (guidance-text fix needs no #169 decision); audit-correction pointer 5841856422 (PR #170 catalog claim, PR #172 citation, baseline names 5F+1E, 0.5.0 version identity); DB-posture question + answer recorded on #144 (5841877756). PCM-0055 closed out on this branch (cac15b4).

Evidence:
- detached-worktree baseline discover at 690b7f8: same six broken names as current 259-test discover (worktrees 4F+1E, test_cli 2F) — zero regressions; gh comments API verified all cited ids; validate = device-local pcm-pinned error only.

Decisions:
- Acceptance 2 stays owner-gated; DuckDB/OTEL analytics-substrate question to be filed as its own decision issue rather than folded here.

Changed:
- tasks/TASK-PCM-0054-durability-receipt-audit.md, tasks/TASK-PCM-0055-receipt-json-encoding.md, checkpoints/CURRENT.md, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- Acceptance 2 on #169 (owner decision); PCM-0046 arms provider-429 (~04:05Z).

Next:
- Merge PR task/PCM-0054-projection-sync under six contexts, post merge receipt on #169, then owner answers the pending decision briefs (#162 5840695558, #169 acceptance 2, #144 O1-O4, #142, #143, #166 caveat).

### 2026-09-26 03:56:43 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["None; PCM-0046 arms window ~04:05Z (pool probe 03:5xZ: 429 retry ~12min at spawn, then ExecAudit also 429 at 03:59Z \u2014 arms themselves untested)."],"changed":["src/continuity/cli.py, tasks/TASK-PCM-0054-durability-receipt-audit.md (tests/test_receipt_audit.py committed at 411dbfc)"],"completed":["continuity receipt audit implemented per owner decision 5842002712: receipt_coverage + audit_receipt_gaps + checkpoint_request_ids_at + audit_task_receipts + parser/dispatch; 10 red-first cases green; real-repo smoke AUDIT_CLEAN on PCM-0053 branch vs #166; criteria 2-3 checked. Status stays active until the PR merges (completion discipline)."],"decisions":["Coverage join = sha (full/prefix) or v2 request id; degraded lookups NEVER emit verdicts; non-github remotes auditable only with explicit --repository matching the task's issue_url ledger."],"evidence":["discover 274 tests = six known macOS-environmental names; receipt suites OK; ruff@0.6.9 two pre-existing ISC003; smoke: audit on origin/task/PCM-0053-stale-base-guard -> AUDIT_CLEAN exit 0; degraded NOTE path and wrong-ledger error exercised in tests."],"next_action":"Open PR task/PCM-0054-receipt-audit, arm auto-merge after final push, merge receipt on #169, then close out PCM-0054.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0054","timestamp":"2026-09-26T03:56:43Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"d3819c3139d6456f72b98e69c4649b28ea946ff94b39e9898773d94ae7b8e037","request_id":"pcm-0054-audit-20260926","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0054"} -->

Completed:
- continuity receipt audit implemented per owner decision 5842002712: receipt_coverage + audit_receipt_gaps + checkpoint_request_ids_at + audit_task_receipts + parser/dispatch; 10 red-first cases green; real-repo smoke AUDIT_CLEAN on PCM-0053 branch vs #166; criteria 2-3 checked. Status stays active until the PR merges (completion discipline).

Evidence:
- discover 274 tests = six known macOS-environmental names; receipt suites OK; ruff@0.6.9 two pre-existing ISC003; smoke: audit on origin/task/PCM-0053-stale-base-guard -> AUDIT_CLEAN exit 0; degraded NOTE path and wrong-ledger error exercised in tests.

Decisions:
- Coverage join = sha (full/prefix) or v2 request id; degraded lookups NEVER emit verdicts; non-github remotes auditable only with explicit --repository matching the task's issue_url ledger.

Changed:
- src/continuity/cli.py, tasks/TASK-PCM-0054-durability-receipt-audit.md (tests/test_receipt_audit.py committed at 411dbfc)

Blocked/uncertain:
- None; PCM-0046 arms window ~04:05Z (pool probe 03:5xZ: 429 retry ~12min at spawn, then ExecAudit also 429 at 03:59Z — arms themselves untested).

Next:
- Open PR task/PCM-0054-receipt-audit, arm auto-merge after final push, merge receipt on #169, then close out PCM-0054.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
