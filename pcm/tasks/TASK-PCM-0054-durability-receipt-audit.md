# TASK-PCM-0054 — Durability Receipt Audit

<!-- continuity:task {"acceptance":["replace this with observable, task-specific acceptance checks"],"depends_on":[],"goal":"Close the durable-publication enforcement gap: pushed SHAs without a keyed leaf-issue receipt are invisible to every tool; give dogfood and adopters one deterministic receipt-gap audit (Refs #169).","id":"PCM-0054","issue_url":"https://github.com/Pukujan/project-continuity-modules/issues/169","next_action":"define scope and observable acceptance checks, then begin bounded work","owner":"owner/Astra planning","priority":"P2","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"The 2026-09-25 durability audit found three contract-required merge receipts never posted and no command noticed; Git-side durability is enforced in publish_checkpoint, issue-log durability is prose + opt-in flags only."} -->

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

## Human outcome

A fresh session running one deterministic command learns, from the repository and the live issue alone, whether every pushed increment on a task branch actually produced its keyed leaf-issue receipt — so "durable means published" stops depending on writer memory in PCM and in every adopter repository that runs `continuity validate`.

## Scope and boundaries

- In scope: record the enforcement-gap finding with code-provenance (publish_checkpoint enforces push; receipt posting is opt-in; validate has no receipt rule); backfill evidence references; define the bounded design question for the receipt-gap audit.
- Out of scope: any cli.py/schema change before the owner answers on #169 (default-on posting vs audit-only vs status-quo convention); no autonomous polling; no other-host adapters.
- Dependencies/uncertainty: depends on none; related #67 (receipt route frozen opt-in by owner decision 5827958268 — this task proposes an ADDITIVE detector, not reversal), #162 acceptance-2 pattern, #166 caveat.

## Acceptance criteria

- [ ] Filing slice merged under six required hosted contexts with merge receipt on #169: task projection + CURRENT entry record the enforcement matrix (code-enforced: branch/uncommitted/stale-base/sanitizer/push; convention+opt-in: receipt posting, merge-window discipline) with path:line evidence at `690b7f8`, and the three backfilled receipt ids (5841258606, 5841258803, 5841258608).
- [ ] Owner decision recorded on #169 (one of: default-on receipts when `trackers.github=true` / additive `continuity receipt audit` command / explicit keep-as-convention) — mirrors the #162 acceptance-2 gate; no CLI change before it.
- [ ] If implementation approved: red-first tests prove audit exits non-zero on a local bare-remote fixture with a pushed SHA lacking a keyed comment, zero when the marker exists, and degrades without network; full suite stays at baseline.

## Evidence and sources

- Observed 2026-09-25 ~23:55Z audit: `git log --all --not --remotes=origin` → 11 commits, per-file superseded check clean (zero true-local-only); `gh pr view` #163/#164/#165/#167/#168 all MERGED six contexts; comment listing on #162/#166 proved receipts for 1bb3cb4/f4ffd6f/690b7f8 absent before backfill.
- Code provenance at `690b7f8` (cli 0.5.0): `publish_checkpoint` src/continuity/cli.py:3095-3177 (branch req :3115, uncommitted refuse :3121, stale-base :3127-3135, sanitizer :3144-3147, push :3176); `require_receipt_pair` cli.py:2924-2929 returns None when flags omitted; `validate_repo` cli.py:1556+ has no receipt rule; `GITHUB_PROGRESSION_GUIDANCE` cli.py:45-59 injected by `agents_template` cli.py:595.
- Leaf #169 body carries the full problem statement and proposal.

## Related records

- Leaf #169 (PCM-0054); parent: none; depends: none; related #67, #162, #166, #139.
- Primary writer: owner/Astra (omp session); branch task/PCM-0053-closeout (filing increment rides the PCM-0053 closeout push); source issue revision: #169 body at filing; as-of 2026-09-25T23:58Z.
- Push receipt: continuity checkpoint request pcm-0054-filed-20260925 (posted to #169 after push).

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

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
