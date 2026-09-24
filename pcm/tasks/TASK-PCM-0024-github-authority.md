# TASK-PCM-0024 — Make GitHub authoritative and prove reliable continuation

<!-- continuity:task {"acceptance":["Amend the normative specification and adopter guidance so GitHub issues are required and authoritative for PCM-governed task scope and lifecycle; keep merged repository history authoritative for accepted code","Deterministic tests verify the authority rule reaches generated guidance and conflict-safe adoption","A disposable GitHub adoption proves pushed checkpoints, required CI, automatic merge, issue closeout, and safe cleanup, including failure behavior","Fresh sessions without parent-chat history reliably find the authoritative issue, repository handoff, actual status, and next action; record observable baseline/candidate evidence and uncertainty","Add a reproducible larger-repository stress profile while keeping differential tests limited to a named trusted reference and tests proportional to the claim","Required local and hosted quality gates pass, changes merge automatically, and final task/checkpoint/handoff state is reconciled before issue #53 closes"],"depends_on":[],"goal":"Make GitHub the required authority for PCM project tracking and prove that a fresh session can continue the GitHub-owned task through tested, merged delivery and safe cleanup.","id":"PCM-0024","issue_url":"https://github.com/Pukujan/project-continuity-modules/issues/53","next_action":"Resolve the hosted Linux MyPy and generated-index failures on PR #56, then complete the two-user adoption, fresh-session holdouts, stress profile, and closeout evidence.","owner":"Codex PCM session; GitHub issue #53","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"The current SPEC treats external trackers as optional mirrors, while the owner requires GitHub authority. A fresh agent must be able to recover task scope/status and complete the push, CI, merge, closeout, and cleanup path without chat history or contradictory local state."} -->

- Status: active per owner direction; PCM-0018 / #33 cleanup remains separately blocked
- Owner: Codex PCM session; GitHub issue #53
- Priority: P1
- Prior sequencing dependency on PCM-0018 was explicitly overridden by the owner to proceed; #33 remains open with cleanup follow-up recorded.

## Human outcome

A new session should be able to identify the authorized work from GitHub, resume from the repository’s compact checkpoint, and carry the task through required checks, automatic merge, closeout, and safe cleanup without depending on this chat.

## Scope and boundaries

- Issue [#53](https://github.com/Pukujan/project-continuity-modules/issues/53) owns the full scope and acceptance criteria.
- This task is active, but GitHub authority is **not implemented yet**. Do not describe the policy as shipped until its implementation merges.
- PCM-0018 / issue #33 has recorded its pinned baseline/candidate evidence. Its residual disposable-copy cleanup and closeout remain open; do not represent #33 as completed.
- Retain the existing human-first issue policy (#32), fresh-session fairness policy (#39), and bounded worktree lifecycle. Do not create an issue per test type or modify unrelated target repositories.

## Acceptance criteria

- [ ] Implement and test the GitHub authority and delivery contract in the normative spec and generated adopter guidance.
- [ ] Verify the policy and end-to-end issue → checkpoint/push → required CI → automatic merge → issue closeout → safe cleanup path in a disposable adoption.
- [ ] Record independent no-history fresh-session results and a reproducible large-repository stress measurement; label what a single run cannot establish.
- [ ] Run local and hosted quality gates, merge automatically, then reconcile task/current/handoff state and clean task-owned resources before closing #53.

## Related records

- Authoritative task issue: [#53](https://github.com/Pukujan/project-continuity-modules/issues/53)
- PCM-0018 evidence/cleanup follow-up: [#33](https://github.com/Pukujan/project-continuity-modules/issues/33)
- Human-first record policy: [#32](https://github.com/Pukujan/project-continuity-modules/issues/32)
- Fresh-session holdout method: [#39](https://github.com/Pukujan/project-continuity-modules/issues/39)

## Checkpoint log

### 2026-09-24 — cross-platform CI failure follow-up

Completed:
- Inspected the first hosted PR runs and found Linux MyPy rejected the
  Windows-only `msvcrt.locking` attributes. Changed the platform-specific import
  to a dynamically typed import; local MyPy now passes.
- CI also found the generated document index differs on Linux. Added a bounded
  unified diff to validator errors so the next hosted run identifies the exact
  divergent lines; root cause is not yet established.

Evidence:
- PR #56 first hosted runs: workflow runs 35954192442, 35954212054, and
  35954226873. The Linux MyPy error was `msvcrt` missing `locking`, `LK_NBLCK`,
  and `LK_UNLCK`; the Linux validator reported an out-of-date generated index.
- Issue #53 failure status is recorded at
  https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5807488436.
- After the lock import fix, local MyPy and Ruff passed, repository validation
  passed, and the 17 worktree tests passed. The new index diff diagnostic has
  not yet run in hosted CI.

Decisions:
- Do not enable/assume auto-merge while required hosted checks fail. Resolve
  the index mismatch from the captured diff; do not bypass the validator.

Changed:
- `src/continuity/cli.py`

Blocked/uncertain:
- Cross-platform document-index divergence remains unexplained pending the
  next hosted error detail; PR #56 stays open.

Next:
- Run final local checks, commit and push this fix, then inspect the Linux
  index diff and correct its cause before considering merge.

### 2026-09-24 — authority and local workspace enforcement slice

Completed:
- Updated the normative spec, README, adoption guidance, generated guidance, and
  checked-in software/minimal templates: GitHub issues own task scope/lifecycle;
  merged default-branch history owns accepted code; PR checks and merge evidence
  own delivery. Checkpoint pushes are synchronous; CI/auto-merge run
  asynchronously behind required review/check gates.
- Added optional `issue_url` task metadata. GitHub-origin repositories enable
  issue authority at init; active CURRENT tasks require a matching same-repo
  issue URL. Added `continuity issue verify` as a read-only live GitHub check.
- Added a private per-device checkout registry (`workspace register/list/
  unregister`); managed worktree creation searches it and Git registrations,
  reuses one clean unlocked task branch, and stops for dirty/conflicting/
  ambiguous matches. A task-keyed OS file lock prevents concurrent local
  creation for the same repository/task.
- Added deterministic coverage for issue links/live verification, generated
  guidance, cross-root reuse, dirty checkout refusal, and concurrent resolution.

Evidence:
- `continuity issue verify PCM-0024 --root .` -> issue #53 OPEN with matching URL.
- Final full suite: 70 tests passed. Also `continuity validate --root .`, Ruff,
  MyPy, compileall, and `git diff --check` passed.
- `python tests/package_smoke.py --root .` -> wheel and source archive on Python
  3.12 both passed minimal/software generation and PCM-0018 feature parity.
- Issue progress recorded at
  https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5807314523.
- Final local gate update recorded at
  https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5807394746.

Decisions:
- A physical path remains private local state and is never copied into shared
  issues, commits, PRs, or handoffs. The local registry is explicit and does not
  scan drives. Reuse is conditional on a unique, clean, unlocked, same-remote,
  same-task/ref match.
- GitHub task authority is opt-in through `trackers.github`; this preserves
  non-GitHub adopters while making GitHub remotes authoritative by default.
- The CLI/package source candidate is 0.4.0; protocol remains 0.1.0-draft.

Changed:
- SPEC, README, AGENTS, HANDOFF, CURRENT, TARGET_ADOPTION, VERSIONING, task and
  config schema implementations, CLI, templates, and deterministic tests.

Blocked/uncertain:
- Two-user hosted adoption, async PR/CI/auto-merge/issue closeout proof,
  fresh-session holdouts, large-repository stress evidence, and hosted gates
  remain open. This is an implementation slice, not issue #53 completion.

Next:
- Publish this implementation slice as a review PR and continue with the
  disposable two-user adoption, fresh-session holdouts, stress profile, and
  hosted CI/merge/closeout evidence; keep issue #53 open until all pass.

### 2026-09-24 — activation by owner direction

Completed:
- Activated PCM-0024 after the user directed implementation to proceed, reusing
  the existing checkout on `task/PCM-0024-github-authority`; no worktree was
  created.
- Published interim #33 evidence and cleanup status through PR #55. GitHub
  closed #33 when PR #55 merged, so it was immediately reopened with an
  explanatory comment because cleanup is incomplete.

Evidence:
- PR #55 is merged at `e8ec41e16f98e708e967eed5d0bb3f723b1611ed`; required
  quality, Python 3.11/3.12 tests, package, package-parity, and auto-merge
  checks passed.
- Issue #33 is OPEN after explicit reopen; its baseline/candidate reports are
  recorded and cleanup residual remains documented.
- `checkpoints/CURRENT.md` now identifies PCM-0024 as the active task on this
  branch; PCM-0018 is blocked on the separately recorded cleanup action.

Decisions:
- Proceed with PCM-0024 per owner direction while keeping issue #33 open and
  its cleanup/closeout incomplete; do not represent PCM-0018 as complete.
- Keep accepted code and project state in merged Git history; private local
  checkout locations will not be copied into shared records.

Changed:
- `tasks/TASK-PCM-0024-github-authority.md`; `tasks/TASK-PCM-0018-document-discovery.md`;
  `checkpoints/CURRENT.md`; `HANDOFF.md`

Blocked/uncertain:
- PCM-0018 candidate trial clone remains and its baseline directory retains a
  hidden `.git` marker. The automatic review blocked a cleanup operation.

Next:
- Amend SPEC, README, adoption templates, generated agent guidance, the
  machine-readable authority manifest, and deterministic policy/adoption tests.

### 2026-09-24 04:05:59 UTC — Codex

<!-- continuity:checkpoint {"agent":"Codex","blocked":[],"changed":["SPEC, README, AGENTS, HANDOFF, CURRENT, TARGET_ADOPTION, VERSIONING, task schema, CLI, templates, and tests"],"completed":["Implemented GitHub issue authority, read-only issue verification, private checkout registry, safe worktree reuse and local task locking; updated adopter guidance and tests."],"decisions":["no new decisions"],"evidence":["70 tests passed; Ruff, MyPy, compileall, package parity, continuity validation, and document-index synchronization passed; issue #53 verified OPEN."],"next_action":"Open a review PR for this implementation slice; complete the two-user hosted adoption, fresh-session holdouts, large-repository stress profile, and hosted CI/merge/closeout evidence before closing #53.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0024","timestamp":"2026-09-24T04:05:59Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"3193b27ec1fce98be03145c500f6619f2e9bb5c93d3af9b491bde9c7ed24c383","request_id":"f49dcd53bbc1486ba79fd440c838ec54","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0024"} -->

Completed:
- Implemented GitHub issue authority, read-only issue verification, private checkout registry, safe worktree reuse and local task locking; updated adopter guidance and tests.

Evidence:
- 70 tests passed; Ruff, MyPy, compileall, package parity, continuity validation, and document-index synchronization passed; issue #53 verified OPEN.

Decisions:
- no new decisions

Changed:
- SPEC, README, AGENTS, HANDOFF, CURRENT, TARGET_ADOPTION, VERSIONING, task schema, CLI, templates, and tests

Blocked/uncertain:
- none

Next:
- Open a review PR for this implementation slice; complete the two-user hosted adoption, fresh-session holdouts, large-repository stress profile, and hosted CI/merge/closeout evidence before closing #53.

### 2026-09-24 04:11:31 UTC — Codex

<!-- continuity:checkpoint {"agent":"Codex","blocked":["Hosted generated-index mismatch root cause is pending next CI diff; do not bypass validator or merge."],"changed":["src/continuity/cli.py; tasks/TASK-PCM-0024-github-authority.md"],"completed":["Fixed Linux-only MyPy issue by dynamically importing Windows lock API; added unified diff details to generated-index validation failures; local quality and worktree checks pass."],"decisions":["no new decisions"],"evidence":["PR #56 hosted runs 35954192442, 35954212054, 35954226873 showed Linux msvcrt typing and generated-index mismatch. Local Ruff, MyPy, compileall, validation, and 17 worktree tests passed after changes."],"next_action":"Inspect PR #56 hosted Linux index diff and resolve the true source of platform divergence before enabling merge.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0024","timestamp":"2026-09-24T04:11:31Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"001c1597b554a93ddc7de47058e22d9147742cf8566ec96ce7f270ecc5a4af18","request_id":"168ea88485764289a17aad8eb4ec2990","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0024"} -->

Completed:
- Fixed Linux-only MyPy issue by dynamically importing Windows lock API; added unified diff details to generated-index validation failures; local quality and worktree checks pass.

Evidence:
- PR #56 hosted runs 35954192442, 35954212054, 35954226873 showed Linux msvcrt typing and generated-index mismatch. Local Ruff, MyPy, compileall, validation, and 17 worktree tests passed after changes.

Decisions:
- no new decisions

Changed:
- src/continuity/cli.py; tasks/TASK-PCM-0024-github-authority.md

Blocked/uncertain:
- Hosted generated-index mismatch root cause is pending next CI diff; do not bypass validator or merge.

Next:
- Inspect PR #56 hosted Linux index diff and resolve the true source of platform divergence before enabling merge.

## Handoff

Read issue #53, PROJECT, CURRENT, this task, and only relevant policy/test records. Confirm current GitHub state; do not rely on prior chat. Issue #33 remains open for cleanup/closeout, but does not block this owner-directed task.
