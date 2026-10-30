# TASK-PCM-0010 — Continuity bookkeeping must not become an execution gate

<!-- continuity:task {"acceptance":["blind disposable-repository reproduction is recorded without exposing the suspected root cause to the test agent","execution-versus-bookkeeping and repository-lineage/worktree semantics are normative in the protocol and generated guidance","canonical continuity read/write failures degrade to deterministic diagnostics rather than uncaught crashes","an authorized alternate checkout can receive a validated recovery receipt without creating a competing project identity","recovery receipts can be reconciled into the canonical task once writable","deterministic regression tests cover unavailable state, recovery receipt, reconciliation, and existing checkpoint behavior","a fresh-session blind rerun of the same scenario passes after the fix","normal checkpoint delivery commits and pushes the task branch instead of leaving durable state only in a local worktree","CI validates lint, typing, tests, compilation, and package building on pushed branches","pull-request automation enables merge only after required CI jobs pass","PCM-0009 remains separately scoped and its helper-target boundary work is not silently rewritten","full test suite, self-validation, and continuity state are recorded before handoff"],"depends_on":["PCM-0009"],"goal":"Make continuity bookkeeping degrade gracefully when canonical state is temporarily unavailable, so safe authorized work can continue across one repository/task lineage and an alternate execution checkout.","id":"PCM-0010","next_action":"No further PCM-0010 action; delivery and issue #17 closeout are recorded in merged PRs #18, #16, and #37.","owner":"PCM-0010 implementation and closeout sessions; GitHub issue #17","priority":"P0","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"completed","why":"Issue #17 records repeated cases where checkpoint/write failures and physical-worktree assumptions blocked otherwise-safe execution. PCM must state that execution outranks bookkeeping and provide a minimal recoverable path when canonical continuity files are unavailable."} -->

- Status: completed
- Owner: PCM-0010 implementation and closeout sessions; GitHub issue #17
- Priority: P0
- Depends on: PCM-0009
- GitHub issue: #17
- Suggested branch: `task/PCM-0010-continuity-bookkeeping`

## Goal

Make continuity bookkeeping degrade gracefully when canonical state is temporarily unavailable, so safe authorized work can continue across one repository/task lineage and an alternate execution checkout.

## Why

Issue #17 records repeated cases where checkpoint/write failures and physical-worktree assumptions blocked otherwise-safe execution. PCM must state that execution outranks bookkeeping and provide a minimal recoverable path when canonical continuity files are unavailable.

## Allowed files

- `AGENTS.md`
- `README.md`
- `SPEC.md`
- `HANDOFF.md`
- `docs/HANDOFF_PROTOCOL.md`
- `docs/BLIND_TEST_PCM-0010.md`
- `docs/VERSIONING.md`
- `.github/workflows/ci.yml`
- `pyproject.toml`
- `src/continuity/cli.py`
- `schemas/v1/recovery.schema.json`
- `templates/**`
- `tests/**`
- this task and `checkpoints/CURRENT.md`

Do not modify Eval Lab, hades-v2, harness-on-steroids, inference-recommendation-engine, or any unrelated target repository.

## Acceptance criteria

- [x] blind disposable-repository reproduction is recorded without exposing the suspected root cause to the test agent;
- [x] execution-versus-bookkeeping and repository-lineage/worktree semantics are normative in the protocol and generated guidance;
- [x] canonical continuity read/write failures degrade to deterministic diagnostics rather than uncaught crashes;
- [x] an authorized alternate checkout can receive a validated recovery receipt without creating a competing project identity;
- [x] recovery receipts can be reconciled into the canonical task once writable;
- [x] deterministic regression tests cover unavailable state, recovery receipt, reconciliation, and existing checkpoint behavior;
- [x] a fresh-session blind rerun of the same scenario passes after the fix;
- [x] normal checkpoint push, CI quality/test/package gates, and automatic merge behavior are verified;
- [x] PCM-0009 remains separately scoped and its helper-target boundary work is not silently rewritten;
- [x] full test suite, self-validation, and continuity state are recorded before handoff.

## Checkpoint log

### 2026-09-23 02:00 UTC — Codex PCM-0010 investigation

<!-- continuity:checkpoint {"agent":"Codex PCM-0010 investigation","blocked":[],"changed":["none; disposable fixtures only"],"completed":["Read issue #17, PCM main state, and the separate PCM-0009 candidate branch/PR state.","Created a disposable PCM-adopted target with an alternate checkout from the same Git lineage.","Reproduced baseline CLI failure when canonical checkpoint state was unavailable: checkpoint crashed with an uncaught PermissionError; baseline preflight also crashed when the canonical task could not be read.","Ran fresh blind sessions against the disposable scenario."],"decisions":["Keep PCM-0009 as a separate predecessor branch/PR and develop PCM-0010 on a new branch based on that candidate.","Treat repository/task lineage, branch/ref, commit history, and remote identity as authoritative; worktree paths are execution views.","Record the blind result as a partial baseline reproduction: one fresh agent kept the physical primary checkout as canonical and changed its read-only attribute to force bookkeeping, while a stronger access-denied run succeeded only when explicitly directed to the authorized alternate."],"evidence":["GitHub issue #17 -> open PCM-0010 release gate and required blind scenario.","PCM-0009 PR #16 -> open; branch fix/PCM-0009-helper-target-boundary; 9 commits; candidate package version 0.2.0 and protocol version 0.1.0-draft.","Baseline `python -m continuity checkpoint DCD-0001` against a read-only canonical task -> uncaught PermissionError, exit 1, no recovery record.","Baseline `continuity preflight` against an access-denied canonical task -> uncaught PermissionError while validating task content.","Fresh blind baseline session 01a0cc68-1a32-7860-a5c0-14ce36001dfc -> completed in primary after changing the read-only attribute; no alternate lineage/recovery was used.","Fresh stronger access-denied session 01a0cc6b-e1c2-7d53-9764-18d4039820a4 -> completed in authorized alternate and preserved the task lineage; primary task remained access-denied."],"next_action":"Finish deterministic implementation and run the same blind prompt against the post-fix candidate.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0010","timestamp":"2026-09-23T02:00:00Z"} -->

Completed:
- Read issue #17, PCM main state, and the separate PCM-0009 candidate branch/PR state.
- Created a disposable PCM-adopted target with an alternate checkout from the same Git lineage.
- Reproduced baseline CLI failure when canonical checkpoint state was unavailable: checkpoint crashed with an uncaught `PermissionError`; baseline preflight also crashed when the canonical task could not be read.
- Ran fresh blind sessions against the disposable scenario.

Evidence:
- GitHub issue #17 -> open PCM-0010 release gate and required blind scenario.
- PCM-0009 PR #16 -> open; branch `fix/PCM-0009-helper-target-boundary`; 9 commits; candidate package version 0.2.0 and protocol version 0.1.0-draft.
- Baseline `python -m continuity checkpoint DCD-0001` against a read-only canonical task -> uncaught `PermissionError`, exit 1, no recovery record.
- Baseline `continuity preflight` against an access-denied canonical task -> uncaught `PermissionError` while validating task content.
- Fresh blind baseline session `01a0cc68-1a32-7860-a5c0-14ce36001dfc` -> completed in primary after changing the read-only attribute; no alternate lineage/recovery was used.
- Fresh stronger access-denied session `01a0cc6b-e1c2-7d53-9764-18d4039820a4` -> completed in authorized alternate and preserved the task lineage; primary task remained access-denied.

Decisions:
- Keep PCM-0009 as a separate predecessor branch/PR and develop PCM-0010 on a new branch based on that candidate.
- Treat repository/task lineage, branch/ref, commit history, and remote identity as authoritative; worktree paths are execution views.
- Record the blind result as a partial baseline reproduction: one fresh agent kept the physical primary checkout as canonical and changed its read-only attribute to force bookkeeping, while a stronger access-denied run succeeded only when explicitly directed to the authorized alternate.

Changed:
- none in PCM; disposable fixtures only.

Blocked/uncertain:
- none; the stronger baseline blind run did not reproduce stopping/permission-loop behavior, so the agent-level result is recorded as partial reproduction while the CLI/validator failure is direct and deterministic.

Next:
- Finish deterministic implementation and run the same blind prompt against the post-fix candidate.

### 2026-09-23 04:25:00 UTC — Codex PCM-0010 implementation and blind verification

<!-- continuity:checkpoint {"agent":"Codex PCM-0010 implementation and blind verification","blocked":[],"changed":["AGENTS.md; HANDOFF.md; README.md; SPEC.md; checkpoints/CURRENT.md; docs/HANDOFF_PROTOCOL.md; docs/VERSIONING.md; docs/BLIND_TEST_PCM-0010.md; schemas/v1/recovery.schema.json; src/continuity/cli.py; templates/v1/minimal/HANDOFF.md; templates/v1/software/AGENTS.md; tests/test_cli.py; tasks/TASK-PCM-0010-continuity-bookkeeping.md"],"completed":["Added degraded-continuity protocol guidance with execution-over-bookkeeping and repository-lineage/worktree semantics.","Added deterministic CanonicalUnavailable handling, DEGRADED_TARGET preflight classification, recovery receipt schema, checkpoint fallback, and recovery reconciliation CLI.","Added regression coverage for unavailable canonical state, recovery receipt, reconciliation, and existing append-only checkpoint behavior.","Reran the same fresh-session blind scenario: the agent used the authorized alternate, did not modify storage or request permission, wrote a .continuity/recovery receipt, and left no ad-hoc checkpoint file."],"decisions":["Keep PCM-0009 as a separate predecessor scope; PCM-0010 adds only degraded-continuity behavior and does not rewrite the helper-target boundary task.","Push meaningful commits when authorized, but do not make remote availability or a physical worktree an execution gate; a recovery receipt is the explicit local fallback."],"evidence":["PYTHONPATH=src python -m unittest discover -s tests -v -> 13 tests passed.","PYTHONPATH=src python -m continuity validate --root . -> VALID.","git diff --check -> exit 0.","Post-fix blind session 01a0cc7a-9644-73a1-9396-551bf6d4f73b -> completed safely in the authorized alternate and wrote DPF-0001-2026-09-23T041827Z.json.","Post-fix alternate validation -> VALID; recovery reconcile -> exit 0; canonical validation after reconciliation -> VALID; receipt status -> reconciled."],"next_action":"Review the diff, run the full suite once more from a clean task state, commit the PCM-0010 branch, and leave it ready for PR review.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0010","timestamp":"2026-09-23T04:25:00Z"} -->

Completed:
- Added degraded-continuity protocol guidance with execution-over-bookkeeping and repository-lineage/worktree semantics.
- Added deterministic CanonicalUnavailable handling, DEGRADED_TARGET preflight classification, recovery receipt schema, checkpoint fallback, and recovery reconciliation CLI.
- Added regression coverage for unavailable canonical state, recovery receipt, reconciliation, and existing append-only checkpoint behavior.
- Reran the same fresh-session blind scenario: the agent used the authorized alternate, did not modify storage or request permission, wrote a .continuity/recovery receipt, and left no ad-hoc checkpoint file.

Evidence:
- PYTHONPATH=src python -m unittest discover -s tests -v -> 13 tests passed.
- PYTHONPATH=src python -m continuity validate --root . -> VALID.
- git diff --check -> exit 0.
- Post-fix blind session 01a0cc7a-9644-73a1-9396-551bf6d4f73b -> completed safely in the authorized alternate and wrote DPF-0001-2026-09-23T041827Z.json.
- Post-fix alternate validation -> VALID; recovery reconcile -> exit 0; canonical validation after reconciliation -> VALID; receipt status -> reconciled.

Decisions:
- Keep PCM-0009 as a separate predecessor scope; PCM-0010 adds only degraded-continuity behavior and does not rewrite the helper-target boundary task.
- Push meaningful commits when authorized, but do not make remote availability or a physical worktree an execution gate; a recovery receipt is the explicit local fallback.

Changed:
- AGENTS.md; HANDOFF.md; README.md; SPEC.md; checkpoints/CURRENT.md; docs/HANDOFF_PROTOCOL.md; docs/VERSIONING.md; docs/BLIND_TEST_PCM-0010.md; schemas/v1/recovery.schema.json; src/continuity/cli.py; templates/v1/minimal/HANDOFF.md; templates/v1/software/AGENTS.md; tests/test_cli.py; tasks/TASK-PCM-0010-continuity-bookkeeping.md

Blocked/uncertain:
- none

Next:
- Review the diff, run the full suite once more from a clean task state, commit the PCM-0010 branch, and leave it ready for PR review.

### 2026-09-23 04:35:00 UTC — Codex PCM-0010 final verification

<!-- continuity:checkpoint {"agent":"Codex PCM-0010 final verification","blocked":[],"changed":["tasks/TASK-PCM-0010-continuity-bookkeeping.md; checkpoints/CURRENT.md; HANDOFF.md"],"completed":["Committed the PCM-0010 implementation as b4702df (PCM-0010: degrade continuity bookkeeping safely).","Recorded the final full test, compilation, validation, and blind-rerun evidence in the task state."],"decisions":["Leave PCM-0009 PR #16 as a separate predecessor; PCM-0010 is ready for review on its own branch."],"evidence":["b4702df contains only PCM-0010 protocol/tooling/task-state changes; no unrelated target repository was modified.","PYTHONPATH=src python -m unittest discover -s tests -v -> 13 tests passed.","python -m compileall -q src tests -> exit 0.","PYTHONPATH=src python -m continuity validate --root . -> VALID.","Fresh blind post-fix session 01a0cc7a-9644-73a1-9396-551bf6d4f73b used alternate checkout and wrote/reconciled a validated recovery receipt."],"next_action":"Open a PR or perform human review of commit b4702df and its final verification checkpoint.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0010","timestamp":"2026-09-23T04:35:00Z"} -->

Completed:
- Committed the PCM-0010 implementation as b4702df (PCM-0010: degrade continuity bookkeeping safely).
- Recorded the final full test, compilation, validation, and blind-rerun evidence in the task state.

Evidence:
- b4702df contains only PCM-0010 protocol/tooling/task-state changes; no unrelated target repository was modified.
- PYTHONPATH=src python -m unittest discover -s tests -v -> 13 tests passed.
- python -m compileall -q src tests -> exit 0.
- PYTHONPATH=src python -m continuity validate --root . -> VALID.
- Fresh blind post-fix session 01a0cc7a-9644-73a1-9396-551bf6d4f73b used alternate checkout and wrote/reconciled a validated recovery receipt.

Decisions:
- Leave PCM-0009 PR #16 as a separate predecessor; PCM-0010 is ready for review on its own branch.

Changed:
- tasks/TASK-PCM-0010-continuity-bookkeeping.md; checkpoints/CURRENT.md; HANDOFF.md

Blocked/uncertain:
- none

Next:
- Open a PR or perform human review of commit b4702df and its final verification checkpoint.

### 2026-09-23 04:41:44 UTC — Codex PCM-0010 CI/CD delivery

<!-- continuity:checkpoint {"agent":"Codex PCM-0010 CI/CD delivery","blocked":[],"changed":[".github/workflows/ci.yml","pyproject.toml","src/continuity/cli.py","tests/test_cli.py","PCM guidance and task state"],"completed":["Replaced optional checkpoint pushes with mandatory checkpoint commit-and-push delivery.","Added GitHub CI quality, test, compilation, package, and automatic pull-request merge jobs.","Added deterministic regression coverage for checkpoint publication to a Git remote."],"decisions":["A normal checkpoint is not durable until the task branch is pushed; remote failure is degraded continuity, not a second canonical worktree."],"evidence":["Ruff -> all checks passed.","MyPy src -> no issues found.","PYTHONPATH=src python -m unittest discover -s tests -q -> 14 tests passed.","PYTHONPATH=src python -m continuity validate --root . -> VALID."],"next_action":"Open the pushed pull request and verify required CI jobs plus automatic merge behavior.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0010","timestamp":"2026-09-23T04:41:44Z"} -->

Completed:
- Replaced optional checkpoint pushes with mandatory checkpoint commit-and-push delivery.
- Added GitHub CI quality, test, compilation, package, and automatic pull-request merge jobs.
- Added deterministic regression coverage for checkpoint publication to a Git remote.

Evidence:
- Ruff -> all checks passed.
- MyPy src -> no issues found.
- PYTHONPATH=src python -m unittest discover -s tests -q -> 14 tests passed.
- PYTHONPATH=src python -m continuity validate --root . -> VALID.

Decisions:
- A normal checkpoint is not durable until the task branch is pushed; remote failure is degraded continuity, not a second canonical worktree.

Changed:
- .github/workflows/ci.yml
- pyproject.toml
- src/continuity/cli.py
- tests/test_cli.py
- PCM guidance and task state

Blocked/uncertain:
- none

Next:
- Open the pushed pull request and verify required CI jobs plus automatic merge behavior.

### 2026-09-23 04:43:15 UTC — Codex PCM-0010 hosted CI verification

<!-- continuity:checkpoint {"agent":"Codex PCM-0010 hosted CI verification","blocked":[],"changed":[".github/workflows/ci.yml"],"completed":["Fixed the automatic merge job to pass GitHub's repository context explicitly."],"decisions":["Automatic merge is performed by the CI workflow only after quality, both test versions, and package jobs succeed."],"evidence":["Hosted quality, test (3.11), test (3.12), and package jobs all passed on PR #18.","The first hosted auto-merge attempt failed only because gh had no repository context; the failure is now corrected."],"next_action":"Verify the new hosted run enables automatic merge and observe the final PR state.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0010","timestamp":"2026-09-23T04:43:15Z"} -->

Completed:
- Fixed the automatic merge job to pass GitHub's repository context explicitly.

Evidence:
- Hosted quality, test (3.11), test (3.12), and package jobs all passed on PR #18.
- The first hosted auto-merge attempt failed only because gh had no repository context; the failure is now corrected.

Decisions:
- Automatic merge is performed by the CI workflow only after quality, both test versions, and package jobs succeed.

Changed:
- .github/workflows/ci.yml

Blocked/uncertain:
- none

Next:
- Verify the new hosted run enables automatic merge and observe the final PR state.

### 2026-09-23 — Verified delivery and issue closeout

Completed:
- Rechecked the original issue and found its implementation, regression tests, and blind results already recorded in the task history; no implementation was repeated.
- The baseline directly reproduced uncaught `PermissionError` failures in `continuity checkpoint` and `continuity preflight` when canonical task state was unavailable.
- The baseline blind agent also kept the physical primary checkout as canonical and changed its read-only attribute to force checkpoint availability. The stronger access-denied run only continued in the alternate when explicitly directed; this was correctly recorded as a partial behavioral reproduction, not a stop/permission-loop reproduction.
- The fix added deterministic degraded-continuity diagnostics, an authorized-alternate recovery receipt, reconciliation, and execution-over-bookkeeping guidance.
- The fresh post-fix blind agent used the already-authorized alternate, did not repair storage or request permission, wrote a recovery receipt, and reconciled it successfully.
- Verified PR #18's CI and merge into the PCM-0009 candidate branch; verified PR #16 then integrated that branch into protected `main`.

Evidence:
- Baseline and post-fix session IDs, expected signals, outcomes, receipt ID, and reconciliation evidence are recorded above.
- PR #18 merged at `72bd4be` into `fix/PCM-0009-helper-target-boundary`; quality, Python 3.11/3.12 tests, package build, and automatic merge passed.
- PR #16 merged at `93c0549` into `main`; its quality, Python 3.11/3.12 tests, package build, and automatic merge passed.
- Current `main` contains the protocol/CLI/tests; original issue #17's release gate is satisfied.

Decisions:
- Treat the original CLI failure as reproduced and the agent-level behavior as partially reproduced; ship the scoped fix and record the narrower behavioral evidence honestly.
- Issue #17 was closed after this bookkeeping closeout merged in PR #37 at `cf76827`. Keep PCM-0009 separate; its issue #15 stays open because that issue also mentions a target-repository remediation prohibited by the current scope.

Changed:
- `tasks/TASK-PCM-0010-continuity-bookkeeping.md`; `checkpoints/CURRENT.md`; `HANDOFF.md`.

Blocked/uncertain:
- The post-fix blind run passed, but the baseline agent did not demonstrate every listed failure signal; only the physical-path/read-only behavior and direct CLI exceptions were observed.

Next:
- No further PCM-0010 action. Continue with one separately scoped open issue; preserve PCM-0009 history and do not modify target repositories without authorization.

## Handoff

Read `PROJECT.md` → `checkpoints/CURRENT.md` → this task → `AGENTS.md` → `SPEC.md` → `docs/HANDOFF_PROTOCOL.md` → `docs/BLIND_TEST_PCM-0010.md`. Keep PCM-0009 separate and do not modify unrelated target repositories.
