# TASK-PCM-0024 — Make GitHub authoritative and prove reliable continuation

<!-- continuity:task {"acceptance":["Amend the normative specification and adopter guidance so GitHub issues are required and authoritative for PCM-governed task scope and lifecycle; keep merged repository history authoritative for accepted code","Deterministic tests verify the authority rule reaches generated guidance and conflict-safe adoption","A disposable GitHub adoption proves pushed checkpoints, required CI, automatic merge, issue closeout, and safe cleanup, including failure behavior","Fresh sessions without parent-chat history reliably find the authoritative issue, repository handoff, actual status, and next action; record observable baseline/candidate evidence and uncertainty","Add a reproducible larger-repository stress profile while keeping differential tests limited to a named trusted reference and tests proportional to the claim","Required local and hosted quality gates pass, changes merge automatically, and final task/checkpoint/handoff state is reconciled before issue #53 closes"],"depends_on":[],"goal":"Make GitHub the required authority for PCM project tracking and prove that a fresh session can continue the GitHub-owned task through tested, merged delivery and safe cleanup.","id":"PCM-0024","issue_url":"https://github.com/Pukujan/project-continuity-modules/issues/53","next_action":"Complete independent no-history issue-53 holdouts and a real two-user, separate-drive adoption; verify checkout reuse, writer arbitration, required checks, auto-merge and cleanup. Use an independently authenticated collaborator; this session has only the owner account.","owner":"Codex PCM session; GitHub issue #53","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"The current SPEC treats external trackers as optional mirrors, while the owner requires GitHub authority. A fresh agent must be able to recover task scope/status and complete the push, CI, merge, closeout, and cleanup path without chat history or contradictory local state."} -->

- Status: active per owner direction; PCM-0018 / #33 cleanup remains separately blocked
- Owner: Codex PCM session; GitHub issue #53
- Priority: P1
- Prior sequencing dependency on PCM-0018 was explicitly overridden by the owner to proceed; #33 remains open with cleanup follow-up recorded.

## Human outcome

A new session should be able to identify the authorized work from GitHub, resume from the repository’s compact checkpoint, and carry the task through required checks, automatic merge, closeout, and safe cleanup without depending on this chat.

## Scope and boundaries

- Issue [#53](https://github.com/Pukujan/project-continuity-modules/issues/53) owns the full scope and acceptance criteria.
- GitHub authority, private per-device checkout registration, safe existing-checkout reuse, writer serialization, and delivery guidance merged in PR #56 at `4033b49`. This issue remains open because multi-user and fresh-session acceptance evidence is incomplete.
- PCM-0018 / issue #33 has recorded its pinned baseline/candidate evidence. Its residual disposable-copy cleanup and closeout remain open; do not represent #33 as completed.
- Retain the existing human-first issue policy (#32), fresh-session fairness policy (#39), and bounded worktree lifecycle. Do not create an issue per test type or modify unrelated target repositories.

## Acceptance criteria

- [x] Implement and test the GitHub authority and delivery contract in the normative spec and generated adopter guidance (PR #56, merged at `4033b49`; hosted required checks passed).
- [ ] Verify the policy and end-to-end issue → checkpoint/push → required CI → automatic merge → issue closeout → safe cleanup path in a disposable adoption.
- [ ] Record independent no-history fresh-session results for the GitHub-authority promise and a reproducible large-repository stress measurement; label what a single run cannot establish. A local stress profile and measurement are recorded; the no-history issue-53 holdouts remain outstanding.
- [ ] Run local and hosted quality gates, merge automatically, then reconcile task/current/handoff state and clean task-owned resources before closing #53.

## Related records

- Authoritative task issue: [#53](https://github.com/Pukujan/project-continuity-modules/issues/53)
- PCM-0018 evidence/cleanup follow-up: [#33](https://github.com/Pukujan/project-continuity-modules/issues/33)
- Human-first record policy: [#32](https://github.com/Pukujan/project-continuity-modules/issues/32)
- Fresh-session holdout method: [#39](https://github.com/Pukujan/project-continuity-modules/issues/39)

## Checkpoint log

### 2026-09-24 — stress, stale-writer, and multi-task follow-up

Completed:
- Added a reproducible synthetic profile for 5,000 indexed documents and 2,000 checkpoint records, plus provisional human-usable latency, size, storage, and memory guardrails.
- Optimized context-pack source retrieval with a single clean-state check and batched Git archive; pack validation checks selected files while validating all catalog records' schema, task links, and path shape.
- Added regression tests proving a stale writer cannot overwrite the remote checkpoint, one registered checkout on another drive is reused, and distinct task IDs receive separate task worktrees.

Evidence:
- `python tests/pcm0024_stress_profile.py` (Python 3.12.10, Windows 11, 5,000 docs, 2,000 seed checkpoints, 40 repetitions): lookup p95 77.637 ms; checkpoint append p95 461.396 ms; context pack 6,916.171 ms / 1,905,540 bytes; traced Python peak 31,686,050 bytes; fixture file storage excluding `.git` 9,532,017 bytes. Full reproduction and limits: `docs/benchmarks/PCM-0024-stress-profile.md`.
- `python -m unittest discover -s tests -v`: 72 passed in 75.679 seconds. Targeted checkpoint (6), worktree (18), and document-catalog (12) suites also passed. Ruff, MyPy, compileall, and `continuity validate --root .` passed.
- `python tests/package_smoke.py --root .`: wheel and source archive both passed minimal/software generation and PCM-0018 feature parity on Python 3.12.
- GitHub branch protection requires `quality`, Python 3.11/3.12 tests, package, and Python 3.11/3.12 package-parity checks; enforce-admins is enabled. `gh auth status` exposes only the owner's active account in this session, so the second-user adoption cannot be claimed.

Decisions:
- Keep issue #53 open until independent fresh-session proof and an actual second authorized user on a separate drive exercise the hosted collaboration/merge/cleanup path. Same-user, separate-root tests do not substitute for that acceptance criterion.
- Keep stress thresholds provisional and out of timing-sensitive CI; this is a one-machine synthetic baseline, not a repeatability or production-scale claim.

Changed:
- `src/continuity/cli.py`; `tests/test_checkpoint_retries.py`; `tests/test_worktrees.py`; `tests/pcm0024_stress_profile.py`; `docs/benchmarks/PCM-0024-stress-profile.md`; document catalog and index.

Blocked/uncertain:
- A second independently authenticated collaborator/device is not available in the current session; no second-user race or separate-drive hosted adoption is claimed.
- Independent no-history holdouts specifically for issue #53 remain outstanding. Existing #33 baseline/candidate evidence is linked but does not prove the GitHub-authority promise.
- Full suite, wheel/sdist package parity, and local static/continuity checks passed.

Next:
- Commit and push this follow-up on the existing PCM task branch, then open a PR linked to #53 without closing it. After merge, run independent issue-53 holdouts and arrange the real two-user adoption using an authorized collaborator.

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

### 2026-09-24 04:41:43 UTC — Codex

<!-- continuity:checkpoint {"agent":"Codex","blocked":["A second independently authenticated collaborator and independent no-history issue-53 holdouts remain outstanding."],"changed":["src/continuity/cli.py; tests/test_checkpoint_retries.py; tests/test_worktrees.py; tests/pcm0024_stress_profile.py; docs/benchmarks/PCM-0024-stress-profile.md; PROJECT.md; HANDOFF.md; checkpoints/CURRENT.md; tasks/TASK-PCM-0024-github-authority.md; docs/CONTINUITY_INDEX.md; .continuity/documents.json"],"completed":["Merged PR #56 enforcement was followed by large-repository optimization and a reproducible stress profile; added stale-writer and multi-task worktree regression coverage."],"decisions":["Keep #53 open; local separate-root tests do not claim the issue's required real two-user hosted adoption. Stress guardrails are provisional and one-machine only."],"evidence":["Full suite: 72 passed; Ruff, MyPy, compileall, continuity validation, git diff check, and Python 3.12 wheel/sdist package parity passed. Stress profile: 5000 docs, 2000 checkpoints, lookup p95 77.637 ms, append p95 461.396 ms, pack 6916.171 ms / 1905540 bytes, Python traced peak 31686050 bytes; see docs/benchmarks/PCM-0024-stress-profile.md. Issue #53 is OPEN. Branch protection requires six CI checks and enforce-admins is enabled. This session has only one authenticated GitHub identity."],"next_action":"Open a PR for the committed follow-up and enable auto-merge behind required checks without closing issue #53; then arrange independent issue-53 holdouts and the real two-user, separate-drive adoption.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0024","timestamp":"2026-09-24T04:41:43Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"2d058ee0950f809c0c5f778bd72fc1ad1c759389c098e891093934c513eb2178","request_id":"f16bcb7eeb95455ab5822528d0ab13f0","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0024"} -->

Completed:
- Merged PR #56 enforcement was followed by large-repository optimization and a reproducible stress profile; added stale-writer and multi-task worktree regression coverage.

Evidence:
- Full suite: 72 passed; Ruff, MyPy, compileall, continuity validation, git diff check, and Python 3.12 wheel/sdist package parity passed. Stress profile: 5000 docs, 2000 checkpoints, lookup p95 77.637 ms, append p95 461.396 ms, pack 6916.171 ms / 1905540 bytes, Python traced peak 31686050 bytes; see docs/benchmarks/PCM-0024-stress-profile.md. Issue #53 is OPEN. Branch protection requires six CI checks and enforce-admins is enabled. This session has only one authenticated GitHub identity.

Decisions:
- Keep #53 open; local separate-root tests do not claim the issue's required real two-user hosted adoption. Stress guardrails are provisional and one-machine only.

Changed:
- src/continuity/cli.py; tests/test_checkpoint_retries.py; tests/test_worktrees.py; tests/pcm0024_stress_profile.py; docs/benchmarks/PCM-0024-stress-profile.md; PROJECT.md; HANDOFF.md; checkpoints/CURRENT.md; tasks/TASK-PCM-0024-github-authority.md; docs/CONTINUITY_INDEX.md; .continuity/documents.json

Blocked/uncertain:
- A second independently authenticated collaborator and independent no-history issue-53 holdouts remain outstanding.

Next:
- Open a PR for the committed follow-up and enable auto-merge behind required checks without closing issue #53; then arrange independent issue-53 holdouts and the real two-user, separate-drive adoption.

### 2026-09-24 04:44:14 UTC — Codex

<!-- continuity:checkpoint {"agent":"Codex","blocked":["Hosted rerun of PR #57 is pending; issue #53's real two-user adoption and independent no-history holdouts remain outstanding."],"changed":["tests/test_worktrees.py; .continuity/documents.json; docs/CONTINUITY_INDEX.md"],"completed":["Fixed PR #57's first hosted CI failure: the cross-drive checkout-reuse test now falls back to a writable temporary root on Unix while retaining cross-volume coverage on Windows."],"decisions":["Treat same-volume Unix fallback as root-reuse coverage only; do not describe it as cross-drive proof. Windows local run exercised different volumes."],"evidence":["First PR #57 workflow run 35956749486 failed only in tests.test_worktrees.ManagedWorktreeTests.test_create_reuses_registered_checkout_on_another_drive because the hosted Unix account cannot create a directory under '/'. The corrected targeted test passed on local Windows; Ruff and continuity validation passed."],"next_action":"Confirm the new required CI runs pass for PR #57; keep issue #53 open and auto-merge gated on the complete required check set.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0024","timestamp":"2026-09-24T04:44:14Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"bc5875f7c857525c2f869898d2d63dd2c32fcdf72ab2d72dde3be8e2885bb09c","request_id":"d81cdfea897f4076ba70eeee23b5afb6","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0024"} -->

Completed:
- Fixed PR #57's first hosted CI failure: the cross-drive checkout-reuse test now falls back to a writable temporary root on Unix while retaining cross-volume coverage on Windows.

Evidence:
- First PR #57 workflow run 35956749486 failed only in tests.test_worktrees.ManagedWorktreeTests.test_create_reuses_registered_checkout_on_another_drive because the hosted Unix account cannot create a directory under '/'. The corrected targeted test passed on local Windows; Ruff and continuity validation passed.

Decisions:
- Treat same-volume Unix fallback as root-reuse coverage only; do not describe it as cross-drive proof. Windows local run exercised different volumes.

Changed:
- tests/test_worktrees.py; .continuity/documents.json; docs/CONTINUITY_INDEX.md

Blocked/uncertain:
- Hosted rerun of PR #57 is pending; issue #53's real two-user adoption and independent no-history holdouts remain outstanding.

Next:
- Confirm the new required CI runs pass for PR #57; keep issue #53 open and auto-merge gated on the complete required check set.

### 2026-09-24 04:49:08 UTC — Codex

<!-- continuity:checkpoint {"agent":"Codex","blocked":["Need an independently authenticated collaborator/device on a separate drive for the two-user adoption, plus independent no-history sessions specifically for issue #53."],"changed":["tasks/TASK-PCM-0024-github-authority.md; checkpoints/CURRENT.md; HANDOFF.md"],"completed":["PR #57 auto-merged the large-repository stress profile, context-pack optimization, stale-writer safeguard, and task-specific worktree tests."],"decisions":["PR #57 proves required CI and automatic merge for this slice, but does not satisfy the issue's two-user adoption or independent fresh-session holdouts. Leave #53 open."],"evidence":["PR #57 merged at b9a23f7612b41902e2b5c10c1da086e33888ef22. Latest head checks in workflow 35956947124: quality, test 3.11, test 3.12, package, package parity 3.11, and package parity 3.12 all passed; auto-merge job passed. continuity issue verify PCM-0024 --root . reports issue #53 OPEN. Local full suite 72 passed; wheel/sdist parity passed. The cross-drive checkout test passed on two Windows volumes; Unix hosted fallback uses a separate writable root."],"next_action":"Publish the reconciled post-merge task/current/handoff checkpoint through a PR without closing #53; then arrange the independent issue-53 holdouts and real two-user adoption.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0024","timestamp":"2026-09-24T04:49:08Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"3ca00f63cf3bfe14a7db235d46c8a78ef50be08e6f287a85bfee9623e82c3460","request_id":"50d304f042974f56b5670435a46af79e","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0024"} -->

Completed:
- PR #57 auto-merged the large-repository stress profile, context-pack optimization, stale-writer safeguard, and task-specific worktree tests.

Evidence:
- PR #57 merged at b9a23f7612b41902e2b5c10c1da086e33888ef22. Latest head checks in workflow 35956947124: quality, test 3.11, test 3.12, package, package parity 3.11, and package parity 3.12 all passed; auto-merge job passed. continuity issue verify PCM-0024 --root . reports issue #53 OPEN. Local full suite 72 passed; wheel/sdist parity passed. The cross-drive checkout test passed on two Windows volumes; Unix hosted fallback uses a separate writable root.

Decisions:
- PR #57 proves required CI and automatic merge for this slice, but does not satisfy the issue's two-user adoption or independent fresh-session holdouts. Leave #53 open.

Changed:
- tasks/TASK-PCM-0024-github-authority.md; checkpoints/CURRENT.md; HANDOFF.md

Blocked/uncertain:
- Need an independently authenticated collaborator/device on a separate drive for the two-user adoption, plus independent no-history sessions specifically for issue #53.

Next:
- Publish the reconciled post-merge task/current/handoff checkpoint through a PR without closing #53; then arrange the independent issue-53 holdouts and real two-user adoption.

## Handoff

Read issue #53, PROJECT, CURRENT, this task, and only relevant policy/test records. Confirm current GitHub state; do not rely on prior chat. Issue #33 remains open for cleanup/closeout, but does not block this owner-directed task.
