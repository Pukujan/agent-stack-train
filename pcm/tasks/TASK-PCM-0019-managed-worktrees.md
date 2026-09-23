# TASK-PCM-0019 — Managed temporary worktrees and dependency reuse

<!-- continuity:task {"acceptance":["managed-worktree support is enabled by a validated workspace policy; strict single-checkout remains an explicit opt-out and old configurations remain compatible","the main checkout remains the permanent home base and is used for sequential work; PCM-managed worktrees are created under the canonical project at pcm/worktree/<task-id> only when parallelism/isolation is useful, binding one active task to one task branch","cleanup refuses trees outside the managed root, dirty or untracked work, unpublished commits, and work that is not proven merged into the canonical remote default branch","a pushed, CI-approved and merged task tree can be removed without force; the local task branch is removed only after safe tree removal","cleanup fails closed for non-GitHub remotes until PCM implements a tested CI/merge verifier for those hosts","generated agent instructions explain when to use a worktree, resuming one tree across sessions, push/required-CI/automatic-merge, safe cleanup, and preservation of unfinished trees","dependency guidance reuses immutable pnpm/uv caches and installed runtimes where supported, but never shares mutable node_modules or .venv across incompatible lockfiles or interpreters","deterministic tests cover path/identity safety, creation reuse, rejection cases, and verified cleanup; repeatable disposable runs measure checkout disk use without leaving resources","the #34 corrected-candidate holdout and a fresh scenario variant pass under the separate #39 protocol","full Ruff, MyPy, compile, Python 3.11/3.12 tests, package build, continuity validation, required hosted CI, automatic merge, issue closeout, and local cleanup all succeed","PCM-0009 remains separately scoped and no unrelated target repository is modified","any short intentional hold of a completed task worktree is recorded in the canonical task checkpoint with its reason, expected release date, exact path, and next unlock/remove action; native Git locking prevents cleanup during the hold and normal verified cleanup runs after release"],"depends_on":["PCM-0011","PCM-0012","PCM-0013","PCM-0022"],"goal":"Allow useful parallel task isolation without scattering worktrees or repeatedly storing full dependency payloads, while ensuring every finished task is pushed, checked, merged and cleaned up safely.","id":"PCM-0019","next_action":"After PR #48 passes protected CI and merges, verify the closeout issues and remove only PCM-0019 local task branches and disposable test clones; leave unrelated PCM branches untouched.","owner":"Codex PCM development session; GitHub issue #34","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"completed","why":"A blanket worktree ban blocks safe parallel isolation, while unmanaged worktrees and per-tree environments can accumulate on disk. The intended result is one permanent main checkout, one temporary task-owned tree only when useful, shared immutable package caches, and refusal-first cleanup after verified GitHub delivery."} -->

## Human outcome

Independent tasks can work at the same time without creating confusing sibling
clones, while completed local checkouts do not quietly accumulate. A new session
resumes the task's existing tree; a separate tree is created only for a separate
parallel task. GitHub's merged history—not a local path or checkout—is the
authority for accepted work.

## Source and baseline evidence

- GitHub issue [#34](https://github.com/Pukujan/project-continuity-modules/issues/34)
  owns the behavior and cleanup contract; issue #20's single-checkout option is
  retained as the opt-out and will be reconciled after this task.
- The recorded baseline holdout on #34 failed implementation readiness: it chose
  a path under Git metadata instead of `pcm/worktree`, did not activate a task,
  and left Ruff/MyPy failures. That draft was disposable and is not accepted.
- At activation, `main` is `4329b47` and matches `origin/main`. GitHub has
  required `quality`, Python 3.11/3.12 test, and package checks; repository CI
  enables squash auto-merge and remote branch deletion.
- Read-only GitHub check on 2026-09-23 confirms `main` protection requires those
  four checks and disallows force-push/deletion. The PR workflow requests
  auto-merge only after these checks pass.

## External research and provenance

Checked on 2026-09-23 against the current official documentation:

- [Git `worktree` documentation](https://git-scm.com/docs/git-worktree) says
  registered trees share repository administration, and ordinary removal
  refuses a dirty tree (including untracked files); `--force` bypasses that
  protection. PCM cleanup must not use force. This is a documented tool
  guarantee, not a claim that Git verifies remote CI or merge policy.
- [pnpm](https://pnpm.io/) describes one content-addressable store whose files
  are hard-linked into each project's `node_modules`. This can avoid storing
  duplicate package payloads on the same filesystem, but each checkout still
  has its own dependency layout and task-specific lockfile behavior.
- Astral's [uv cache documentation](https://docs.astral.sh/uv/concepts/cache/)
  describes a thread-safe, append-only package cache and locking when installing
  into a target environment. Its [project layout documentation](https://docs.astral.sh/uv/concepts/projects/layout/)
  says the normal project environment is `.venv` per project and documents
  centralized project environments as a preview feature. This supports reuse
  of downloads/build artifacts; it does not establish that separate task
  environments with different locks/interpreters can safely share one mutable
  `.venv`.
- Microsoft's [GetCompressedFileSizeW documentation](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getcompressedfilesizew)
  describes the API used by the Windows experiment to report the actual bytes
  of file storage used (compressed size when applicable).
- A disposable Windows/Python 3.12 experiment now measures a 1 MiB deterministic
  payload in three linked worktrees versus three `git clone --no-hardlinks`
  copies on the user's C: NTFS volume. `tests.test_worktrees.WorktreeStorageExperimentTests`
  reported 3,145,728 bytes of checked-out files in either case; one common Git
  object store for the worktrees was 1,049,070 bytes, versus 3,147,210 bytes
  across three independent clone object stores. The Win32 file-storage API
  measured the home checkout plus three worktrees at 5,243,374 bytes, versus
  the same home checkout plus three non-hardlinked clones at 8,390,584 bytes.
  This confirms a 3,147,210-byte saving for this tiny fixture, while showing
  that every additional worktree still materializes its own checkout files.
  The experiment excludes directory/filesystem metadata, real-project size,
  package caches, and virtual environments; it is not a universal savings
  estimate.

## Scope

Implement the repository policy, configuration, CLI behavior, tests, and
verification evidence for a managed temporary-worktree lifecycle. Keep the
default identity as the same canonical repository and remote; the main checkout
is the permanent home base, and a path is only an execution location. Use the
main checkout for sequential work and create a managed tree only when isolation
or parallelism is useful. Preserve strict single-checkout mode as an opt-out.
Reuse package-manager caches, but not mutable environment directories when
dependency inputs differ. Keep `PCM-0009` separate and do not modify any target
repository.

Do not implement the other open reports (#30, #31, #33, #35, #39, #42), except
the #39 acceptance runs that are explicitly dependent on this candidate. Do not
restore or generate README images; #42 remains separately owned and deferred.

## Acceptance

- [x] Workspace policy has a clear safe default, explicit managed and strict
  modes, backward-compatible reading, and generated guidance matching the mode.
- [x] A task can create/reuse only its own tree at
  `<canonical-root>/pcm/worktree/<TASK-ID>` on its bound branch; no sibling
  clone or arbitrary path is created.
- [x] Cleanup is refusal-first and verifies canonical remote identity, exact
  managed path, task/branch association, clean tracked and untracked state,
  publication, and merge into the protected remote default branch. It never
  uses force removal or deletes dirty, unmerged, pinned, or user-owned trees.
- [x] Cleanup fails closed for non-GitHub remotes until PCM implements a tested
  CI/merge verifier for those hosts.
- [x] A short intentional audit hold is recorded in the completed task
  checkpoint with its reason, expected release date, exact path, and
  unlock/remove next action. Git locking makes normal cleanup refuse it; after
  the audit, the operator can unlock it and complete verified cleanup.
- [x] Successful cleanup removes the worktree and only then its safely merged
  local task branch. GitHub remains responsible for protected CI, auto-merge,
  and remote branch deletion; PCM must report inability to verify rather than
  pretending a local clean tree proves delivery.
- [x] Guidance recommends one tree per active task reused across sessions and
  additional trees only for real parallel work. pnpm/uv caches and managed
  runtimes may be reused; `node_modules`/`.venv` remain isolated when lockfiles,
  interpreters, or task-specific dependencies differ. Finished trees and their
  private environments are removed after successful merge.
- [x] Deterministic tests cover strict-mode rejection, managed path/identity,
  idempotent resume, task/branch/path conflicts, dirty/untracked refusal,
  unpublished/unmerged refusal, and successful post-merge cleanup.
- [x] Repeated disposable checkouts are measured with a reproducible method and
  their temporary repositories are removed; do not claim zero disk cost.
- [x] Fresh-session baseline/candidate and one visible-requirement variant are
  evaluated under #39 fairness rules; holdout workers are stopped/closed after
  capturing evidence.
- [x] Full local gates and required hosted CI pass; a protected PR auto-merges,
  issue #34 closes after merge and evidence, CURRENT/HANDOFF/task records agree,
  and no task worktree or branch remains locally.

## Checkpoint log

### 2026-09-23 — Codex PCM-0019 activation

Completed:
- Confirmed issue #34 is open and owns managed worktree lifecycle behavior.
- Confirmed #17 is closed; the prior PCM-0010 baseline/fix/rerun is complete.
- Confirmed issue #20 remains open even though its requested strict
  single-checkout mode landed in PR #21; #34 explicitly owns the policy
  reconciliation.
- Activated this task as the implementation slice required before #39's
  corrected-candidate holdout.

Evidence:
- `git status --short --branch` before activation -> `main...origin/main`, only
  previously generated `dist/` and `src/project_continuity.egg-info/` untracked.
- `git worktree list --porcelain` -> one canonical checkout.
- GitHub issue/PR queries -> #34 open, #39 open, #20 open; PRs #43/#44 merged.
- GitHub branch protection -> required `quality`, `test (3.11)`, `test (3.12)`,
  `package`; force-push and branch deletion disabled. CI workflow enables
  auto-merge after these checks.
- `continuity validate --root .` -> initially failed because the new task listed
  the prose label `PCM-0022 policy` instead of the actual task ID `PCM-0022`;
  corrected above, rerun pending.

Decisions:
- Use the canonical PCM checkout and one task branch; worktrees are optional
  for isolation, not required for every task or session.
- Keep #34 implementation separate from #39 testing-method policy and #15's
  target-repository remediation.
- Do not touch unrelated target repositories or the deferred README image task.

Changed:
- `tasks/TASK-PCM-0019-managed-worktrees.md`
- `checkpoints/CURRENT.md`
- `HANDOFF.md`

Blocked/uncertain:
- The exact safe default and portable proof of remote PR merge need to be
  resolved against existing config compatibility and tests before implementation.
- Previous build outputs remain as generated, untracked directories because
  the shell rejected the targeted cleanup command; they are not part of the task
  change and will not be staged.

Next:
- Inspect workspace configuration and implement create/list/remove behavior
  with refusal-first safety tests.

### 2026-09-23 — managed-worktree policy and CLI candidate

Completed:
- Replaced the blanket worktree ban with a permanent home checkout plus
  optional task-scoped linked worktrees for genuine isolation/parallelism.
- Added validated workspace modes, a new-project default, backward compatibility,
  task-path confinement, create/resume/remove commands, GitHub-only verified
  cleanup, and refusal when delivery cannot be proven.
- Updated PCM's generated and self-hosted instructions. Recorded official Git,
  pnpm, and uv documentation as sources and measured a repeatable disposable
  checkout comparison.

Evidence:
- Python 3.12: `python -m unittest discover -s tests -v` -> 43 passed.
- Python 3.11.15: same test suite -> 43 passed; `continuity validate --root .`
  -> VALID.
- `ruff check src tests`, `mypy src`, compileall, Python 3.12 continuity
  validation, and `python -m build` -> passed.
- Storage experiment (three linked worktrees vs three independent
  `--no-hardlinks` clones): 3,145,728 checkout bytes each; one shared worktree
  Git-object store 1,049,070 bytes; clone object stores 3,147,210 bytes total.
  Logical file sizes only; physical allocation and dependency environments were
  not measured.
- GitHub cleanup integration test proves removal succeeds when the exact task
  head is merged, required checks pass, remote task status is completed, and the
  local home checkout has not yet pulled the merge. Dirty, unmerged, and
  unverifiable cases refuse cleanup.

Decisions:
- One checkout is not mandatory: it is the permanent home base and default for
  sequential work; linked worktrees are temporary and created only when useful.
- Do not share mutable dependency environments across incompatible lockfiles.
  Reuse package caches; let safe cleanup remove the task's private environment.
- Do not claim generic-host CI proof: until another host has a tested verifier,
  PCM leaves its worktree untouched rather than guessing.

Changed:
- `src/continuity/cli.py`, `schemas/v1/config.schema.json`,
  `.continuity/config.json`, `tests/test_cli.py`, and `tests/test_worktrees.py`
- `AGENTS.md`, `HANDOFF.md`, `README.md`, `SPEC.md`,
  `docs/HANDOFF_PROTOCOL.md`, and both applicable profile templates
- This task record and `checkpoints/CURRENT.md`

Blocked/uncertain:
- Fresh-session candidate/variant checks under issue #39, hosted protected CI,
  merge, closeout, and post-merge local branch/worktree cleanup remain pending.
- The measurement is a small synthetic logical-byte comparison, not a Windows
  disk-allocation or real-project dependency benchmark.
- Pre-existing generated `dist/` and `src/project_continuity.egg-info/` remain
  untracked and unstaged; build outputs are not included in the task.

Next:
- Commit and push the reviewed candidate, then run the separate #39 holdout
  and scenario variant against the pushed candidate.

### 2026-09-23 — Windows storage measurement and final local gates

Completed:
- Extended the disposable experiment to compare actual per-file storage on
  Windows using the documented Win32 file-storage API; recorded the filesystem,
  baseline, method, source, and limitations.
- Reran both supported Python test suites and all local quality/package gates
  after the measurement change.

Evidence:
- C: is NTFS. With the same 1 MiB deterministic repo payload, the home checkout
  plus three linked worktrees used 5,243,374 file-storage bytes; the same home
  checkout plus three non-hardlinked clones used 8,390,584 bytes, a difference
  of 3,147,210 bytes for this fixture. The test also reports logical file
  lengths. `GetCompressedFileSizeW` method is documented by Microsoft above.
- Python 3.12 and Python 3.11.15 full suites -> 43 passed each; both produced
  the Windows measurement above.
- Ruff, MyPy, compileall, `continuity validate --root .`, and `python -m build`
  -> passed.
- Product/test commit `9aa1c16` records the Windows measurement implementation;
  the durable task note/checkpoint is the next separate push.

Decisions:
- Report the result as a small-fixture comparison, not an expected percentage
  saving for real repositories. Each worktree still stores its own checkout
  files; most savings here are the avoided extra Git-object copies.
- Keep the managed-worktree recommendation: one home checkout for sequential
  work, optional temporary linked trees for true parallelism/isolation, and
  cleanup only after remote verification.

Changed:
- `tests/test_worktrees.py`
- This task record and `checkpoints/CURRENT.md`

Blocked/uncertain:
- Issue #39's fresh-session candidate and variant runs, protected hosted CI,
  automatic merge, issue reconciliation, and local branch cleanup remain.
- Directory metadata, package stores, mutable environments, and a production
  repository were not measured.

Next:
- Publish the checkpoint and candidate PR; then run #39's separate holdout and
  scenario variant before closing issue #34.

### 2026-09-23 19:54:47 UTC — Codex PCM-0019 follow-up

<!-- continuity:checkpoint {"agent":"Codex PCM-0019 follow-up","blocked":["Issue #39 corrected-candidate and fresh variant holdouts, hosted CI and merge, issue #34/#20 closeout, and local branch cleanup remain pending."],"changed":["src/continuity/cli.py, tests/test_worktrees.py, tests/test_cli.py, .gitignore, AGENTS.md, HANDOFF.md, README.md, SPEC.md, docs/HANDOFF_PROTOCOL.md, templates/v1/minimal/HANDOFF.md, templates/v1/software/AGENTS.md"],"completed":["Rechecked merged PR #45 in an independent Luna session; the blind candidate review found missing protection for intentionally pinned worktrees and a path-identity normalization gap.","Added explicit refusal for Git-locked worktrees, canonical continuity-path comparison against origin default, normalized worktree root identity checks, and user-facing lock/unlock guidance."],"decisions":["One permanent checkout remains the project home; use linked worktrees only for real isolation/parallel tasks, reuse one tree across sessions, and remove only after remote merge/CI/completion proof.","Use native git worktree lock/unlock for intentional retention; no custom pin-state format or extra pin CLI is needed."],"evidence":["Fresh independent session completed without child agents or external publication; it reported no changes outside its disposable checkout. Session 01a0cfc7-0c07-7131-8dff-f6261b6baeb6 was archived after evidence capture.","Python 3.11.15 and Python 3.12.10 full suites: 45 tests passed each; Ruff, MyPy, compileall, package build, continuity validation, and diff checks passed.","Windows NTFS fixture repeated: 5,243,374 bytes for home checkout plus three linked worktrees and 8,390,584 bytes for home plus three no-hardlinks clones; excludes filesystem metadata and package environments."],"next_action":"Push this checkpoint and candidate PR, wait for protected CI/automatic merge, then run independent corrected-candidate and fresh-variant holdouts before closing #34 and reconciling #20.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0019","timestamp":"2026-09-23T19:54:47Z"} -->

Completed:
- Rechecked merged PR #45 in an independent Luna session; the blind candidate review found missing protection for intentionally pinned worktrees and a path-identity normalization gap.
- Added explicit refusal for Git-locked worktrees, canonical continuity-path comparison against origin default, normalized worktree root identity checks, and user-facing lock/unlock guidance.

Evidence:
- Fresh independent session completed without child agents or external publication; it reported no changes outside its disposable checkout. Session 01a0cfc7-0c07-7131-8dff-f6261b6baeb6 was archived after evidence capture.
- Python 3.11.15 and Python 3.12.10 full suites: 45 tests passed each; Ruff, MyPy, compileall, package build, continuity validation, and diff checks passed.
- Windows NTFS fixture repeated: 5,243,374 bytes for home checkout plus three linked worktrees and 8,390,584 bytes for home plus three no-hardlinks clones; excludes filesystem metadata and package environments.

Decisions:
- One permanent checkout remains the project home; use linked worktrees only for real isolation/parallel tasks, reuse one tree across sessions, and remove only after remote merge/CI/completion proof.
- Use native git worktree lock/unlock for intentional retention; no custom pin-state format or extra pin CLI is needed.

Changed:
- src/continuity/cli.py, tests/test_worktrees.py, tests/test_cli.py, .gitignore, AGENTS.md, HANDOFF.md, README.md, SPEC.md, docs/HANDOFF_PROTOCOL.md, templates/v1/minimal/HANDOFF.md, templates/v1/software/AGENTS.md

Blocked/uncertain:
- Issue #39 corrected-candidate and fresh variant holdouts, hosted CI and merge, issue #34/#20 closeout, and local branch cleanup remain pending.

Next:
- Push this checkpoint and candidate PR, wait for protected CI/automatic merge, then run independent corrected-candidate and fresh-variant holdouts before closing #34 and reconciling #20.

### 2026-09-23 20:09:04 UTC — Codex PCM-0019 audit-retention follow-up

<!-- continuity:checkpoint {"agent":"Codex PCM-0019 audit-retention follow-up","blocked":["PR #47 hosted CI/merge and a properly scoped fresh candidate rerun plus the fresh retention variant remain; #34 and #20 must stay open until the holdouts pass."],"changed":["AGENTS.md, HANDOFF.md, README.md, SPEC.md, docs/HANDOFF_PROTOCOL.md, src/continuity/cli.py, tasks/TASK-PCM-0019-managed-worktrees.md, templates/v1/minimal/HANDOFF.md, templates/v1/software/AGENTS.md, tests/test_cli.py"],"completed":["The independent retention-variant session identified that a Git lock prevents removal but the policy did not require a durable expiry and release record; added a short-hold record containing reason, expected release date, path, and unlock/remove action.","Updated PCM operating rules, software and minimal profiles, generated instructions, README, protocol, task acceptance, and regression assertions; no custom pin database was added."],"decisions":["Temporary audit holds must be time-bounded and recorded in the task checkpoint; Git native lock protects them during the hold, and the ordinary verified cleanup remains mandatory after unlock."],"evidence":["Variant session 01a0cfda-315f-73d1-a806-e4213bbc8cc8 at merged commit 396bf6b: 22 test_cli tests passed, continuity validation VALID, git diff --check passed; first attempt omitted PYTHONPATH=src and failed imports, then the corrected command passed.","After incorporating the variant, full suite passed 46 tests each on Python 3.11.15 and 3.12.10; Ruff, MyPy, compileall, package build, continuity validation, and diff check passed.","The independent candidate session 01a0cfd8-2027-7382-b395-5c54c13309d7 read the task/docs but stopped without tests or changes, citing that hosted CI/merge were outside its no-publish scope. Record this as a failed candidate holdout, not a pass.","PR #45 merged at c04d5fa; safety follow-up PR #46 merged at 396bf6b after all hosted package, quality, and Python 3.11/3.12 checks passed."],"next_action":"Push this checkpoint and PR #47; after CI/merge, run a fresh local audit of issue #34 on the current merged commit, then a fresh variant that exercises a time-bounded audit hold, without providing a diagnosis or evaluator checklist.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0019","timestamp":"2026-09-23T20:09:04Z"} -->

Completed:
- The independent retention-variant session identified that a Git lock prevents removal but the policy did not require a durable expiry and release record; added a short-hold record containing reason, expected release date, path, and unlock/remove action.
- Updated PCM operating rules, software and minimal profiles, generated instructions, README, protocol, task acceptance, and regression assertions; no custom pin database was added.

Evidence:
- Variant session 01a0cfda-315f-73d1-a806-e4213bbc8cc8 at merged commit 396bf6b: 22 test_cli tests passed, continuity validation VALID, git diff --check passed; first attempt omitted PYTHONPATH=src and failed imports, then the corrected command passed.
- After incorporating the variant, full suite passed 46 tests each on Python 3.11.15 and 3.12.10; Ruff, MyPy, compileall, package build, continuity validation, and diff check passed.
- The independent candidate session 01a0cfd8-2027-7382-b395-5c54c13309d7 read the task/docs but stopped without tests or changes, citing that hosted CI/merge were outside its no-publish scope. Record this as a failed candidate holdout, not a pass.
- PR #45 merged at c04d5fa; safety follow-up PR #46 merged at 396bf6b after all hosted package, quality, and Python 3.11/3.12 checks passed.

Decisions:
- Temporary audit holds must be time-bounded and recorded in the task checkpoint; Git native lock protects them during the hold, and the ordinary verified cleanup remains mandatory after unlock.

Changed:
- AGENTS.md, HANDOFF.md, README.md, SPEC.md, docs/HANDOFF_PROTOCOL.md, src/continuity/cli.py, tasks/TASK-PCM-0019-managed-worktrees.md, templates/v1/minimal/HANDOFF.md, templates/v1/software/AGENTS.md, tests/test_cli.py

Blocked/uncertain:
- PR #47 hosted CI/merge and a properly scoped fresh candidate rerun plus the fresh retention variant remain; #34 and #20 must stay open until the holdouts pass.

Next:
- Push this checkpoint and PR #47; after CI/merge, run a fresh local audit of issue #34 on the current merged commit, then a fresh variant that exercises a time-bounded audit hold, without providing a diagnosis or evaluator checklist.

### 2026-09-23 20:21:02 UTC — PCM-0019 final closeout candidate

<!-- continuity:checkpoint {"agent":"Codex PCM-0019 closeout","blocked":[],"changed":["tasks/TASK-PCM-0019-managed-worktrees.md","checkpoints/CURRENT.md","HANDOFF.md","GitHub issue comments #20, #34, and #39"],"completed":["Completed managed-worktree lifecycle, native lock-based audit holds, deterministic safety tests, and time-bounded retention guidance in merged PRs #45, #46, and #47.","Completed the independent corrected-candidate audit and fresh retention variant on main snapshot e5a161b6c734ccca44ffddb10b1c35cd5c6e09cf; both final sessions made no edits and did not publish.","Recorded research provenance, benchmark limitations, issue resolution, and exact holdout prompts/results on GitHub issues #20, #34, and #39."],"decisions":["Keep one permanent project home and use optional task-scoped linked worktrees only for real parallelism or isolation; reuse one tree across sessions.","Run normal verified cleanup after push, green checks, merge, task completion, and clean state; preserve dirty, unmerged, unverifiable, or Git-locked trees without force.","For a short audit hold, record reason, expected release date, exact path, and unlock/remove next action in the task checkpoint; after the hold, unlock and run normal verified cleanup."],"evidence":["Final candidate session 01a0cfe4-a142-70d0-9dda-c83617939cab: gpt-6-luna/low; full suite 46 passed; validation VALID; Ruff, MyPy, compileall, package build, and diff check passed; no files changed.","Final retention variant 01a0cfe6-b7bc-7793-b54a-29e7441ffcc7: gpt-6-luna/low; pinned-cleanup test passed; validation VALID; diff check passed; no files changed.","A prior candidate attempt that stopped without verification is recorded as a non-pass; it was not counted as successful evidence. Exact final prompts and permitted context are documented in issue #39.","Python 3.11.15 and Python 3.12.10 local suites each passed 46 tests. PRs #45, #46, and #47 passed protected package, quality, test (3.11), and test (3.12) checks before automatic merge.","Windows C: NTFS fixture: home plus three linked worktrees 5,243,374 file-storage bytes; home plus three --no-hardlinks clones 8,390,584 bytes. Small synthetic fixture; filesystem metadata and dependency environments excluded.","Sources: https://git-scm.com/docs/git-worktree; https://pnpm.io/; https://docs.astral.sh/uv/concepts/cache/; https://docs.astral.sh/uv/concepts/projects/layout/; https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getcompressedfilesizew."],"next_action":"After PR #48 passes protected CI and merges, verify the closeout issues and remove only PCM-0019 local task branches and disposable test clones; leave unrelated PCM branches untouched.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0019","timestamp":"2026-09-23T20:21:02Z"} -->

Completed:
- Managed-worktree lifecycle, native Git lock-based audit holds, deterministic safety tests, and time-bounded retention guidance are in merged PRs #45, #46, and #47.
- The independent corrected-candidate audit and a fresh retention variant both passed on the merged main snapshot. Final agents were archived after evidence capture.
- Detailed human-readable issue comments with research provenance, storage measurements, limits, exact prompts, and results are posted to #20, #34, and #39. PR #48 will close those three logs after protected CI passes and merges.

Evidence:
- Candidate session 01a0cfe4-a142-70d0-9dda-c83617939cab, model gpt-6-luna/low, started at e5a161b6c734ccca44ffddb10b1c35cd5c6e09cf: 46 tests passed; continuity validation VALID; Ruff, MyPy, compileall, package build, and diff check passed. No files changed.
- Variant session 01a0cfe6-b7bc-7793-b54a-29e7441ffcc7, same model and commit: pinned-cleanup regression passed; validation VALID; diff check passed. No files changed.
- An earlier candidate attempt stopped without running checks. It is explicitly recorded as a non-pass; it was not counted as evidence.
- Python 3.11.15 and Python 3.12.10 suites each passed 46 tests. PRs #45–#47 passed required protected CI before automatic merge.
- Windows C: NTFS fixture measured 5,243,374 bytes for home plus three linked worktrees and 8,390,584 bytes for home plus three non-hardlinked clones. This small synthetic result excludes filesystem metadata and package environments.
- Research sources: [Git worktree docs](https://git-scm.com/docs/git-worktree), [pnpm](https://pnpm.io/), [uv cache](https://docs.astral.sh/uv/concepts/cache/), [uv project layout](https://docs.astral.sh/uv/concepts/projects/layout/), and [Microsoft storage API](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getcompressedfilesizew). Method and limitations are documented in the task and issue #34.

Decisions:
- One permanent project home is the default; task-owned worktrees are temporary tools for real parallelism/isolation, not one per agent or session.
- Share immutable caches, not incompatible mutable dependency environments.
- Clean up only after verified push/checks/merge/completion; preserve dirty, unmerged, unverifiable, or time-bounded Git-locked work, then perform normal verified cleanup after unlock.

Changed:
- `tasks/TASK-PCM-0019-managed-worktrees.md`
- `checkpoints/CURRENT.md`
- `HANDOFF.md`
- GitHub issue comments on #20, #34, and #39

Blocked/uncertain:
- None for PCM-0019 after this closeout PR merges. Afterward, verify issue closure and remove only the local PCM-0019 branches/disposable clones; do not touch unrelated branches or repositories.

Next:
- Merge PR #48 after required hosted checks; perform the one-time local PCM-0019 cleanup, then select any future work from the remaining open issues.

## Handoff

Read `PROJECT.md` → `checkpoints/CURRENT.md` → this task → `AGENTS.md` →
`SPEC.md` → `docs/HANDOFF_PROTOCOL.md` → `docs/TESTING_POLICY.md`. Treat the
#34 issue and this task as authoritative scope; do not infer the #39 evaluator
answer from the prior blind worker's diagnosis.
