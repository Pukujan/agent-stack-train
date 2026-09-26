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

- Filing slice (this increment): this task file, `checkpoints/CURRENT.md`, `.continuity/documents.json`, `docs/CONTINUITY_INDEX.md` (generated). Implementation slice (only after the owner answers the design question on #169): `src/continuity/cli.py`, `tests/test_receipt_audit.py` (new), plus regenerated catalog/index.

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

## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
