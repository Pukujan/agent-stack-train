# TASK-PCM-0053 — Stale Base Guard

<!-- continuity:task {"acceptance": ["publish_checkpoint refuses (exit non-zero, no commit, no push) when a path touched by the branch or this checkpoint also changed upstream on the origin default branch since the fork, naming the files and the --allow-stale-base opt-out", "Non-overlapping upstream advances, up-to-date branches, and --allow-stale-base opt-outs publish normally; unresolvable/offline origin degrades to proceeding (push error only), never a stale-base refusal; recovery receipts skip the guard", "Red-first deterministic tests in tests/test_checkpoint_stale_base.py (5 cases); existing checkpoint/hygiene/retry suites and full discover stay at the known baseline; six required hosted contexts on the candidate"], "depends_on": [], "goal": "Make continuity checkpoint refuse to publish when the increment overlaps upstream changes on a stale local base.", "id": "PCM-0053", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/166", "next_action": "Open PR for task/PCM-0053-stale-base-guard, verify six required contexts + auto-merge, post merge receipt on #166.", "owner": "owner/Astra planning", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "completed", "why": "A worker branched from a stale local origin/main while the live default had advanced; the same local-outranks-remote class mis-closed #139 via a stale CLI. The guard closes the silent-revert window before push."} -->

- Status: completed
- Owner: owner/Astra planning
- Priority: P2
- Depends on: none

## Goal

Make continuity checkpoint refuse to publish when the increment overlaps upstream changes on a stale local base.

## Why

A worker branched from a stale local origin/main while the live default had advanced; the same local-outranks-remote class mis-closed #139 via a stale CLI. The guard closes the silent-revert window before push.

## Allowed files

- src/continuity/cli.py (publish_checkpoint + _stale_base_overlap + flag), tests/test_checkpoint_stale_base.py (new), tasks/TASK-PCM-0053-stale-base-guard.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md (generated).

## Human outcome

A fresh session that forgot `git fetch origin` learns before its checkpoint commits: the tool names the exact files where its stale base would silently overwrite accepted history, and says rebase (or opt out loudly). The GitHub-authoritative invariant stops depending on writer memory.

## Scope and boundaries

- In scope: overlap-based staleness refusal in the checkpoint publish path; --allow-stale-base opt-out; degraded-mode NOTE for unresolvable origins.
- Out of scope: auto-rebase; GitHub API staleness checks; the #162 version-drift gate; AGENTS/SPEC normative wording (owner decision territory).
- Dependencies/uncertainty: race window narrowed, not closed — hosted CI conflict detection remains the last line (recorded as honest caveat on #166).

## Acceptance criteria

- [x] publish_checkpoint refuses overlapping stale bases, naming files + opt-out (tests: overlap refused, no commit, no push).
- [x] Non-overlap/fresh/opt-out publish; offline origin proceeds past the guard; recovery skips it.
- [x] PR under six required hosted contexts + auto-merge, merge receipt on #166 — MERGED at squash `3d1d50a` (six contexts green); CURRENT-final sync PR #168 merged at `690b7f8`; receipts 5841072961 (push+merge) and 5841258608 (#168 sync, backfilled 23:5xZ durability audit).

## Evidence and sources

RED: 2 failures + 1 error before the guard (overlap not refused; TypeError on unknown kwarg). GREEN: tests.test_checkpoint_stale_base 5/5 OK; test_checkpoint_hygiene + test_checkpoint_retries OK; full discover 257 tests = exactly the six known macOS-environmental failures, identical at baseline f4ffd6f. ruff: only the two pre-existing ISC003 findings remain (uvx ruff@0.6.9); new code clean. Issue #166 carries the incident observations (22:1xZ stale base, 22:56Z stranded commit).

## Reproduction details (only when needed)

`PYTHONPATH=src python3.12 -m unittest tests.test_checkpoint_stale_base`; fixtures are local bare-remote clones (no network).

## Related records

- Leaf #166 (PCM-0053); parent: none; depends on none; related #162 (sibling stale-tool incident), #139/#161/#164/#165 (observed instances).
- Primary writer: owner/Astra; branch task/PCM-0053-stale-base-guard; source issue revision: #166 body at filing; as-of 2026-09-25T23:20Z.
- Push receipt: continuity checkpoint request pcm-0053-guard-20260925.
- Closeout evidence: durability audit 2026-09-25 ~23:55Z — branch content per-file superseded check clean, all five merge PRs verified merged, missing receipts backfilled; merge-window discipline + no-machine-check-for-missing-receipt recorded on #166 (5841072961) and queued as PCM-0054 (Refs #169).

## Checkpoint log

No checkpoints yet.

### 2026-09-25 23:25:32 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":["None for this slice; provider pool still 429 for PCM-0046 arms (sibling task)."],"changed":["src/continuity/cli.py, tests/test_checkpoint_stale_base.py (new), tasks/TASK-PCM-0053-stale-base-guard.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md"],"completed":["Stale-base guard implemented red-first in publish_checkpoint: _stale_base_overlap fetches the origin default branch, forks at merge-base, and refuses (no commit, no push) when any path touched since the fork or staged by this checkpoint also changed upstream \u2014 error names the files and the --allow-stale-base opt-out; unresolvable origins degrade to proceeding; recovery receipts skip the guard. Dogfooded live: this checkpoint published through the freshly installed guard (overlap-free branch, clean pass \u2014 the positive control on the real publish path)."],"decisions":["Overlap-scoped refusal (not general staleness) to keep parallel non-conflicting task branches false-positive-free; guard is git-only, no gh calls, per #166 boundaries."],"evidence":["RED before guard: 2 failures + 1 error in tests.test_checkpoint_stale_base; GREEN: 5/5 OK; test_checkpoint_hygiene + test_checkpoint_retries OK; full discover 257 = six known macOS-environmental failures identical at baseline f4ffd6f; ruff on changed files: no new findings (two pre-existing ISC003 in cli.py unchanged); continuity docs render --check SYNCHRONIZED at product commit 0e05a13? see git log at entry write time."],"next_action":"Open PR for task/PCM-0053-stale-base-guard, verify six required contexts + auto-merge, post merge receipt on #166 and close-out evidence for acceptance criterion 3.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0053","timestamp":"2026-09-25T23:25:32Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"06c81f8c1a0497cd1668392aba86ec65dcc616a7da3c9d13b4b2610a55e8d712","request_id":"pcm-0053-guard-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0053"} -->

Completed:
- Stale-base guard implemented red-first in publish_checkpoint: _stale_base_overlap fetches the origin default branch, forks at merge-base, and refuses (no commit, no push) when any path touched since the fork or staged by this checkpoint also changed upstream — error names the files and the --allow-stale-base opt-out; unresolvable origins degrade to proceeding; recovery receipts skip the guard. Dogfooded live: this checkpoint published through the freshly installed guard (overlap-free branch, clean pass — the positive control on the real publish path).

Evidence:
- RED before guard: 2 failures + 1 error in tests.test_checkpoint_stale_base; GREEN: 5/5 OK; test_checkpoint_hygiene + test_checkpoint_retries OK; full discover 257 = six known macOS-environmental failures identical at baseline f4ffd6f; ruff on changed files: no new findings (two pre-existing ISC003 in cli.py unchanged); continuity docs render --check SYNCHRONIZED at product commit 0e05a13? see git log at entry write time.

Decisions:
- Overlap-scoped refusal (not general staleness) to keep parallel non-conflicting task branches false-positive-free; guard is git-only, no gh calls, per #166 boundaries.

Changed:
- src/continuity/cli.py, tests/test_checkpoint_stale_base.py (new), tasks/TASK-PCM-0053-stale-base-guard.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- None for this slice; provider pool still 429 for PCM-0046 arms (sibling task).

Next:
- Open PR for task/PCM-0053-stale-base-guard, verify six required contexts + auto-merge, post merge receipt on #166 and close-out evidence for acceptance criterion 3.

### 2026-09-26 00:10:04 UTC — owner/Astra

<!-- continuity:checkpoint {"agent":"owner/Astra","blocked":[],"changed":["tasks/TASK-PCM-0053-stale-base-guard.md, tasks/TASK-PCM-0054-durability-receipt-audit.md (new), checkpoints/CURRENT.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md"],"completed":["Closeout increment: acceptance 3 evidenced (PR #167 merged 3d1d50a six contexts; #168 sync 690b7f8; receipts 5841072961 + 5841258608); task projection marked completed; CURRENT carries the full durability-audit finding + enforcement matrix; PCM-0054/#169 filed for the receipt-gap enforcement proposal."],"decisions":["Merge-window discipline caveat (arm auto-merge only after final push) stays a record, not code; gap class + detector proposal routed to PCM-0054/#169 per the #162 acceptance-2 pattern (no CLI change before owner decision)."],"evidence":["Audit at 690b7f8: git log --all --not --remotes=origin per-file superseded check zero true-local-only; gh pr view #163/#164/#165/#167/#168 all MERGED; backfilled receipt ids 5841258606/5841258803/5841258608; validate = only pre-existing device-local pcm-pinned error."],"next_action":"Open closeout PR for task/PCM-0053-closeout, enable auto-merge, verify six contexts, post merge receipt on Refs #166.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0053","timestamp":"2026-09-26T00:10:04Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"cdf5d139fb13cfadbefc5cc23793b4bf2b8883fd0525e37b33fce11a9163c293","request_id":"pcm-0053-closeout-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0053"} -->

Completed:
- Closeout increment: acceptance 3 evidenced (PR #167 merged 3d1d50a six contexts; #168 sync 690b7f8; receipts 5841072961 + 5841258608); task projection marked completed; CURRENT carries the full durability-audit finding + enforcement matrix; PCM-0054/#169 filed for the receipt-gap enforcement proposal.

Evidence:
- Audit at 690b7f8: git log --all --not --remotes=origin per-file superseded check zero true-local-only; gh pr view #163/#164/#165/#167/#168 all MERGED; backfilled receipt ids 5841258606/5841258803/5841258608; validate = only pre-existing device-local pcm-pinned error.

Decisions:
- Merge-window discipline caveat (arm auto-merge only after final push) stays a record, not code; gap class + detector proposal routed to PCM-0054/#169 per the #162 acceptance-2 pattern (no CLI change before owner decision).

Changed:
- tasks/TASK-PCM-0053-stale-base-guard.md, tasks/TASK-PCM-0054-durability-receipt-audit.md (new), checkpoints/CURRENT.md, .continuity/documents.json, docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- none

Next:
- Open closeout PR for task/PCM-0053-closeout, enable auto-merge, verify six contexts, post merge receipt on Refs #166.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
