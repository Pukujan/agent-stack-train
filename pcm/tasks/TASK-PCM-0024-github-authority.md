# TASK-PCM-0024 — Make GitHub authoritative and prove reliable continuation

<!-- continuity:task {"acceptance":["Amend the normative specification and adopter guidance so GitHub issues are required and authoritative for PCM-governed task scope and lifecycle; keep merged repository history authoritative for accepted code","Deterministic tests verify the authority rule reaches generated guidance and conflict-safe adoption","A disposable GitHub adoption proves pushed checkpoints, required CI, automatic merge, issue closeout, and safe cleanup, including failure behavior","Fresh sessions without parent-chat history reliably find the authoritative issue, repository handoff, actual status, and next action; record observable baseline/candidate evidence and uncertainty","Add a reproducible larger-repository stress profile while keeping differential tests limited to a named trusted reference and tests proportional to the claim","Required local and hosted quality gates pass, changes merge automatically, and final task/checkpoint/handoff state is reconciled before issue #53 closes"],"depends_on":[],"goal":"Make GitHub the required authority for PCM project tracking and prove that a fresh session can continue the GitHub-owned task through tested, merged delivery and safe cleanup.","id":"PCM-0024","issue_url":"https://github.com/Pukujan/project-continuity-modules/issues/53","next_action":"No-history holdouts at baseline 5304bfa and candidate 18e262d and the focused local checkout/checkpoint tests are recorded in child issue #63. Keep #53 open and preserve the explicit boundary that cross-account GitHub permissions and a real second user's hosted adoption remain unverified because this repository has only the owner's account.","owner":"Codex PCM session; GitHub issue #53","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"The current SPEC treats external trackers as optional mirrors, while the owner requires GitHub authority. A fresh agent must be able to recover task scope/status and complete the push, CI, merge, closeout, and cleanup path without chat history or contradictory local state."} -->

- Status: active per owner direction; PCM-0018 / #33 cleanup remains separately blocked
- Owner: Codex PCM session; GitHub issue #53
- Priority: P1
- Prior sequencing dependency on PCM-0018 was explicitly overridden by the owner to proceed; #33 remains open with cleanup follow-up recorded.

## Human outcome

A new session should be able to identify the authorized work from GitHub, resume from the repository’s compact checkpoint, and carry the task through required checks, automatic merge, closeout, and safe cleanup without depending on this chat.

## Scope and boundaries

- Issue [#53](https://github.com/Pukujan/project-continuity-modules/issues/53) owns the full scope and acceptance criteria.
- GitHub authority, private per-device checkout registration, safe existing-checkout reuse, writer serialization, and delivery guidance merged in PR #56 at `4033b49`. Baseline/candidate no-history evidence is recorded; this issue remains open because cross-account hosted multi-user acceptance is unverified.
- PCM-0018 / issue #33 has recorded its pinned baseline/candidate evidence. Its residual disposable-copy cleanup and closeout remain open; do not represent #33 as completed.
- Retain the existing human-first issue policy (#32), fresh-session fairness policy (#39), and bounded worktree lifecycle. Do not create an issue per test type or modify unrelated target repositories.

## Acceptance criteria

- [x] Implement and test the GitHub authority and delivery contract in the normative spec and generated adopter guidance (PR #56, merged at `4033b49`; hosted required checks passed).
- [ ] Verify the policy and end-to-end issue → checkpoint/push → required CI → automatic merge → issue closeout → safe cleanup path in a disposable adoption.
- [x] Record independent no-history fresh-session results for the GitHub-authority promise and a reproducible large-repository stress measurement; label what a single run cannot establish. Baseline/candidate reports are recorded in #63, with approximate timings and unknown runtime identifiers; one run per revision demonstrates discovery, not repeatability. The 5,000-document/2,000-checkpoint synthetic stress profile and its single-machine limits are recorded in the benchmark report.
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

### 2026-09-24 04:52:43 UTC — Codex

<!-- continuity:checkpoint {"agent":"Codex","blocked":["Independent no-history issue-53 holdouts and actual two-user/separate-drive adoption still need an independent session and second authenticated collaborator/device."],"changed":["PR #58 description; issue #53 status and correction comment"],"completed":["PR #58 merged the post-merge task/current/handoff reconciliation. GitHub briefly auto-closed issue #53 because PR prose contained the phrase 'does not close #53'; the issue was reopened immediately and the merged PR description was corrected."],"decisions":["Avoid negated close-keyword phrases around issue references in PR descriptions; use explicit status wording and verify the issue after every merge. Do not claim PCM-0024 complete."],"evidence":["PR #58 merged at dffa814317358870ccba0be7716f511b9b0f5d5a after all six required checks passed. Issue #53 is currently OPEN (verified with gh issue view and continuity issue verify); the correction and reason are documented in issue comment https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5807908634."],"next_action":"Arrange an authorized collaborator on a separate device/drive and authorize independent no-history issue-53 holdouts; then run the remaining proof, reconcile all evidence, and only close #53 after full acceptance.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0024","timestamp":"2026-09-24T04:52:43Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"274ca16095ba14e9fa5ee36d24993217812cd5d5f93d82ba6bbada5c32117215","request_id":"23ed54e496ab4dfa94973e3af1cfa55b","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0024"} -->

Completed:
- PR #58 merged the post-merge task/current/handoff reconciliation. GitHub briefly changed issue #53's state because PR prose contained a negated lifecycle directive; the issue was reopened immediately and the merged PR description was corrected.

Evidence:
- PR #58 merged at dffa814317358870ccba0be7716f511b9b0f5d5a after all six required checks passed. Issue #53 is currently OPEN (verified with gh issue view and continuity issue verify); the correction and reason are documented in issue comment https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5807908634.

Decisions:
- Avoid negated close-keyword phrases around issue references in PR descriptions; use explicit status wording and verify the issue after every merge. Do not claim PCM-0024 complete.

Changed:
- PR #58 description; issue #53 status and correction comment

Blocked/uncertain:
- Independent no-history issue-53 holdouts and actual two-user/separate-drive adoption still need an independent session and second authenticated collaborator/device.

Next:
- Arrange an authorized collaborator on a separate device/drive and authorize independent no-history issue-53 holdouts; then run the remaining proof, reconcile all evidence, and mark issue #53 complete only after full acceptance.

### 2026-09-24 04:57:00 UTC — Codex

<!-- continuity:checkpoint {"agent":"Codex","blocked":["Independent no-history issue-53 holdouts and actual two-user/separate-drive adoption still need an independent session and second authenticated collaborator/device."],"changed":["tasks/TASK-PCM-0024-github-authority.md; issue #53 progress comment"],"completed":["Reopened issue #53 after two consecutive unintended lifecycle transitions tied to merged commit directives; updated the task's exact next action to use neutral completion wording and documented the event on the issue."],"decisions":["Use positive lifecycle wording in checkpoint next actions and verify the live issue state after every merge."],"evidence":["PR #59 merged at 1066cec402ca7fcd76eda16146984ee464726625 with all six required checks and no PR closingIssuesReferences. The close event cites that merge commit; its squash message copied the task checkpoint next_action text 'only close #53 after full acceptance'. Issue #53 is OPEN again after gh issue reopen. Issue comment https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5807908634 records the earlier wording event; this second trigger is now understood."],"next_action":"Ask the owner to designate an independently authenticated collaborator/device and authorize independent no-history holdouts; run the required collaboration and fresh-session proof, then mark the issue complete only after every acceptance criterion passes.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0024","timestamp":"2026-09-24T04:57:00Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"9cea536d9ccf76f3c39356d1968a9f3f486a5bd6253a12f99264acbe726c922c","request_id":"417d831970eb4d858d618296e154a464","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0024"} -->

Completed:
- Reopened issue #53 after two consecutive unintended lifecycle transitions tied to merged commit directives; updated the task's exact next action to use neutral completion wording and documented the event on the issue.

Evidence:
- PR #59 merged at 1066cec402ca7fcd76eda16146984ee464726625 with all six required checks and no PR closingIssuesReferences. The close event cites that merge commit; its squash message copied the task checkpoint next_action text 'only close #53 after full acceptance'. Issue #53 is OPEN again after gh issue reopen. Issue comment https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5807908634 records the earlier wording event; this second trigger is now understood.

Decisions:
- Use positive lifecycle wording in checkpoint next actions and verify the live issue state after every merge.

Changed:
- tasks/TASK-PCM-0024-github-authority.md; issue #53 progress comment

Blocked/uncertain:
- Independent no-history issue-53 holdouts and actual two-user/separate-drive adoption still need an independent session and second authenticated collaborator/device.

Next:
- Ask the owner to designate an independently authenticated collaborator/device and authorize independent no-history holdouts; run the required collaboration and fresh-session proof, then mark the issue complete only after every acceptance criterion passes.

### 2026-09-24 05:07:12 UTC — Codex

<!-- continuity:checkpoint {"agent":"Codex","blocked":["Independent no-history issue-53 holdouts and the real two-user/separate-drive adoption need an independently authenticated collaborator/device."],"changed":["SPEC.md; README.md; docs/CONTINUITY_RECORDS_POLICY.md; generated AGENTS/HANDOFF guidance and templates; src/continuity/cli.py; tests/test_continuity_records_policy.py"],"completed":["Added a normative GitHub issue-transition rule to PCM's policy, generated adopter instructions, and PR template. It explains that negated issue-closing keywords still change issue state and that progress-only PRs should use references."],"decisions":["Progress PRs reference issues without lifecycle keywords; use a completion keyword only when the issue's acceptance is satisfied. Verify live issue state after merges."],"evidence":["python -m unittest discover -s tests -v: 73 passed. Ruff, MyPy, compileall, continuity validation, and Python 3.12 wheel/sdist parity passed. The new regression verifies minimal/software generated guidance and PR templates. GitHub's official linking documentation lists the keywords and says they work in PR descriptions and commit messages: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue. Repo incident is documented in issue #53 comments; #53 is currently OPEN."],"next_action":"Publish the issue-lifecycle wording safeguard PR with auto-merge gated by required checks; then ask the owner to designate an independently authenticated collaborator/device and authorize the remaining holdouts.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0024","timestamp":"2026-09-24T05:07:12Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"e62b991ab2982d13e73b40c842b8a20c3ac05374f7f2ba13f7547c02bf158d96","request_id":"bb3a561593da4713bc80900224371283","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0024"} -->

Completed:
- Added a normative GitHub issue-transition rule to PCM's policy, generated adopter instructions, and PR template. It explains that negated issue-closing keywords still change issue state and that progress-only PRs should use references.

Evidence:
- python -m unittest discover -s tests -v: 73 passed. Ruff, MyPy, compileall, continuity validation, and Python 3.12 wheel/sdist parity passed. The new regression verifies minimal/software generated guidance and PR templates. GitHub's official linking documentation lists the keywords and says they work in PR descriptions and commit messages: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue. Repo incident is documented in issue #53 comments; #53 is currently OPEN.

Decisions:
- Progress PRs reference issues without lifecycle keywords; use a completion keyword only when the issue's acceptance is satisfied. Verify live issue state after merges.

Changed:
- SPEC.md; README.md; docs/CONTINUITY_RECORDS_POLICY.md; generated AGENTS/HANDOFF guidance and templates; src/continuity/cli.py; tests/test_continuity_records_policy.py

Blocked/uncertain:
- Independent no-history issue-53 holdouts and the real two-user/separate-drive adoption need an independently authenticated collaborator/device.

Next:
- Publish the issue-lifecycle wording safeguard PR with auto-merge gated by required checks; then ask the owner to designate an independently authenticated collaborator/device and authorize the remaining holdouts.

### 2026-09-24 05:13:30 UTC — Codex

<!-- continuity:checkpoint {"agent":"Codex","blocked":["Need owner-designated independent GitHub collaborator/device and independent no-history baseline/candidate holdouts."],"changed":["checkpoints/CURRENT.md; HANDOFF.md"],"completed":["PR #61 merged the lifecycle-language guardrail into canonical and generated adopter guidance. Updated CURRENT and HANDOFF with merged state and the remaining acceptance action."],"decisions":["The issue-state safeguard is now normative and generated for adopters; same-user simulations remain distinct from the required two-user proof."],"evidence":["PR #61 merged automatically at 18e262d250634f8297391391ec793ed91c49a5ee after all six required checks and the auto-merge job passed. It has no closingIssuesReferences; continuity issue verify reports #53 OPEN. Local 73-test suite, Ruff, MyPy, compileall, validation, and Python 3.12 wheel/sdist parity passed. The candidate holdout revision is 18e262d; pre-implementation baseline is 5304bfa."],"next_action":"Ask the owner to designate an independently authenticated collaborator on a separate device/drive and authorize no-history holdouts at 5304bfa and 18e262d; then run the remaining two-user and fresh-session acceptance proof.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0024","timestamp":"2026-09-24T05:13:30Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"9b49eaef847881d7ff840f28689a34ef1dd9f90166b97595276a5545f4056ea5","request_id":"1e8f077c6cbb4c6a8b55f211a88a05e4","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0024"} -->

Completed:
- PR #61 merged the lifecycle-language guardrail into canonical and generated adopter guidance. Updated CURRENT and HANDOFF with merged state and the remaining acceptance action.

Evidence:
- PR #61 merged automatically at 18e262d250634f8297391391ec793ed91c49a5ee after all six required checks and the auto-merge job passed. It has no closingIssuesReferences; continuity issue verify reports #53 OPEN. Local 73-test suite, Ruff, MyPy, compileall, validation, and Python 3.12 wheel/sdist parity passed. The candidate holdout revision is 18e262d; pre-implementation baseline is 5304bfa.

Decisions:
- The issue-state safeguard is now normative and generated for adopters; same-user simulations remain distinct from the required two-user proof.

Changed:
- checkpoints/CURRENT.md; HANDOFF.md

Blocked/uncertain:
- Need owner-designated independent GitHub collaborator/device and independent no-history baseline/candidate holdouts.

Next:
- Ask the owner to designate an independently authenticated collaborator on a separate device/drive and authorize no-history holdouts at 5304bfa and 18e262d; then run the remaining two-user and fresh-session acceptance proof.

### 2026-09-24 05:16:50 UTC — Codex

<!-- continuity:checkpoint {"agent":"Codex","blocked":[],"changed":["docs/CONTINUITY_INDEX.md; tasks/TASK-PCM-0024-github-authority.md"],"completed":["Refreshed the generated continuity document index after final handoff reconciliation."],"decisions":["no new decisions"],"evidence":["The prior checkpoint request 1e8f077c6cbb4c6a8b55f211a88a05e4 is recorded and pushed to origin; docs render and continuity validate both pass; issue #53 remains OPEN."],"next_action":"Wait for an owner-designated independently authenticated collaborator on a separate device/drive and authorization for the baseline/candidate no-history holdouts; then complete the remaining multi-user and fresh-session acceptance proof.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0024","timestamp":"2026-09-24T05:16:50Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"5d44841b084ae5bbdc82a9d197d5378f7902964b745b99f423cd453ff1e9949e","request_id":"5db24a81f0d5465c92f1d1c209c0ac79","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0024"} -->

Completed:
- Refreshed the generated continuity document index after final handoff reconciliation.

Evidence:
- The prior checkpoint request 1e8f077c6cbb4c6a8b55f211a88a05e4 is recorded and pushed to origin; docs render and continuity validate both pass; issue #53 remains OPEN.

Decisions:
- no new decisions

Changed:
- docs/CONTINUITY_INDEX.md; tasks/TASK-PCM-0024-github-authority.md

Blocked/uncertain:
- none

Next:
- Wait for an owner-designated independently authenticated collaborator on a separate device/drive and authorization for the baseline/candidate no-history holdouts; then complete the remaining multi-user and fresh-session acceptance proof.

### 2026-09-24 05:27:44 UTC — Codex

<!-- continuity:checkpoint {"agent":"Codex","blocked":["Need an owner-designated independently authenticated collaborator with access to a separate device or drive to perform the issue-53 holdouts and coordinated adoption."],"changed":["HANDOFF.md; checkpoints/CURRENT.md; docs/CONTINUITY_INDEX.md; tasks/TASK-PCM-0024-github-authority.md; issue #53; child issue #63"],"completed":["Created and linked child issue #63 for the independently authenticated collaborator adoption and issue-53 holdouts.","Reconciled issue #53 to acknowledge the recorded PCM-0018 baseline/candidate reports while keeping its issue-53-specific proof separate."],"decisions":["Keep #53 and #33 open; same-account tests do not satisfy the separate-user acceptance."],"evidence":["GitHub issue #63 is open and linked under #53. Issue #53 is OPEN. Issue #33 task/issue records contain independent baseline and candidate reports at 85f1346 and 98747fc, with timings and cleanup status.","GitHub collaborator listing returns only Pukujan with admin/push permissions; a distinct authorized collaborator is not currently available."],"next_action":"Ask the repository owner to designate and authorize a second GitHub collaborator for issue #63; then run independent sessions at baseline 5304bfa and candidate 18e262d plus the real two-user checkout, writer, CI, merge, and cleanup proof.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0024","timestamp":"2026-09-24T05:27:44Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"414ac12cd5f567865d1780a76d48df42f25d92cad5647e5ff434ac4de2a880af","request_id":"7a31a2b0f5e84ef18bc7def81e7bc2c1","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0024"} -->

Completed:
- Created and linked child issue #63 for the independently authenticated collaborator adoption and issue-53 holdouts.
- Reconciled issue #53 to acknowledge the recorded PCM-0018 baseline/candidate reports while keeping its issue-53-specific proof separate.

Evidence:
- GitHub issue #63 is open and linked under #53. Issue #53 is OPEN. Issue #33 task/issue records contain independent baseline and candidate reports at 85f1346 and 98747fc, with timings and cleanup status.
- GitHub collaborator listing returns only Pukujan with admin/push permissions; a distinct authorized collaborator is not currently available.

Decisions:
- Keep #53 and #33 open; same-account tests do not satisfy the separate-user acceptance.

Changed:
- HANDOFF.md; checkpoints/CURRENT.md; docs/CONTINUITY_INDEX.md; tasks/TASK-PCM-0024-github-authority.md; issue #53; child issue #63

Blocked/uncertain:
- Need an owner-designated independently authenticated collaborator with access to a separate device or drive to perform the issue-53 holdouts and coordinated adoption.

Next:
- Ask the repository owner to designate and authorize a second GitHub collaborator for issue #63; then run independent sessions at baseline 5304bfa and candidate 18e262d plus the real two-user checkout, writer, CI, merge, and cleanup proof.

### 2026-09-24 06:30:03 UTC — Codex

<!-- continuity:checkpoint {"agent":"Codex","blocked":[],"changed":["HANDOFF.md; checkpoints/CURRENT.md; docs/CONTINUITY_INDEX.md; tasks/TASK-PCM-0024-github-authority.md; issue #53; issue #63"],"completed":["Ran independent no-history PCM-0024 holdouts at baseline 5304bfa and candidate 18e262d using subagents with no parent-chat history; recorded their reports and limits in child issue #63.","Ran the focused checkout/checkpoint suites: 24 tests passed in 72.740 seconds, covering cross-volume registered checkout reuse, local resolver locking, stale-writer rejection, independent task branches, and cleanup evidence gates."],"decisions":["Use local no-history agents and deterministic tests for the claims they prove; retain the real cross-account hosted-adoption claim as an explicit unverified boundary. Do not require the owner to create a second account."],"evidence":["Baseline holdout recovered the GitHub authority rule, issue #53 OPEN and #33 separate/open state, and detected baseline SPEC/README/task/HANDOFF contradictions; it recommended reconciling #33 status and activating #53. No files or worktrees changed; elapsed time approximate 2 minutes.","Candidate holdout recovered the issue scope and authority boundaries, identified #53/#33 open work and child #63, and recommended verifying current PR state then proceeding with the outstanding issue-53 proof. No files or worktrees changed; elapsed time approximate 3 minutes.","Holdout runtime/model identifiers unavailable; one run per revision does not establish repeatability. Local tests do not prove a distinct GitHub account, cross-account permissions, or a real second users hosted PR/CI path."],"next_action":"Preserve the completed holdout and local-test evidence in the task record. Keep issue #53 open because actual cross-account GitHub permissions and hosted adoption remain unverified; proceed only if the owner supplies an existing independent account or changes that acceptance criterion.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0024","timestamp":"2026-09-24T06:30:03Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"b671d86f5d373a9546731885380edbc2cefb906d55e4898ab69d38025308febb","request_id":"b17d2c197d304ee9a53140a5aa36c6b0","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0024"} -->

Completed:
- Ran independent no-history PCM-0024 holdouts at baseline 5304bfa and candidate 18e262d using subagents with no parent-chat history; recorded their reports and limits in child issue #63.
- Ran the focused checkout/checkpoint suites: 24 tests passed in 72.740 seconds, covering cross-volume registered checkout reuse, local resolver locking, stale-writer rejection, independent task branches, and cleanup evidence gates.

Evidence:
- Baseline holdout recovered the GitHub authority rule, issue #53 OPEN and #33 separate/open state, and detected baseline SPEC/README/task/HANDOFF contradictions; it recommended reconciling #33 status and activating #53. No files or worktrees changed; elapsed time approximate 2 minutes.
- Candidate holdout recovered the issue scope and authority boundaries, identified #53/#33 open work and child #63, and recommended verifying current PR state then proceeding with the outstanding issue-53 proof. No files or worktrees changed; elapsed time approximate 3 minutes.
- Holdout runtime/model identifiers unavailable; one run per revision does not establish repeatability. Local tests do not prove a distinct GitHub account, cross-account permissions, or a real second users hosted PR/CI path.

Decisions:
- Use local no-history agents and deterministic tests for the claims they prove; retain the real cross-account hosted-adoption claim as an explicit unverified boundary. Do not require the owner to create a second account.

Changed:
- HANDOFF.md; checkpoints/CURRENT.md; docs/CONTINUITY_INDEX.md; tasks/TASK-PCM-0024-github-authority.md; issue #53; issue #63

Blocked/uncertain:
- none

Next:
- Preserve the completed holdout and local-test evidence in the task record. Keep issue #53 open because actual cross-account GitHub permissions and hosted adoption remain unverified; proceed only if the owner supplies an existing independent account or changes that acceptance criterion.

## Handoff

Read issue #53, PROJECT, CURRENT, this task, and only relevant policy/test records. Confirm current GitHub state; do not rely on prior chat. Issue #33 remains open for cleanup/closeout, but does not block this owner-directed task.
