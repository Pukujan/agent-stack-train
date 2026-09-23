# TASK-PCM-0019 — Managed temporary worktrees and dependency reuse

<!-- continuity:task {"acceptance":["managed-worktree support is enabled by a validated workspace policy; strict single-checkout remains an explicit opt-out and old configurations remain compatible","the main checkout remains the permanent home base and is used for sequential work; PCM-managed worktrees are created under the canonical project at pcm/worktree/<task-id> only when parallelism/isolation is useful, binding one active task to one task branch","cleanup refuses trees outside the managed root, dirty or untracked work, unpublished commits, and work that is not proven merged into the canonical remote default branch","a pushed, CI-approved and merged task tree can be removed without force; the local task branch is removed only after safe tree removal","cleanup fails closed for non-GitHub remotes until PCM implements a tested CI/merge verifier for those hosts","generated agent instructions explain when to use a worktree, resuming one tree across sessions, push/required-CI/automatic-merge, safe cleanup, and preservation of unfinished trees","dependency guidance reuses immutable pnpm/uv caches and installed runtimes where supported, but never shares mutable node_modules or .venv across incompatible lockfiles or interpreters","deterministic tests cover path/identity safety, creation reuse, rejection cases, and verified cleanup; repeatable disposable runs measure checkout disk use without leaving resources","the #34 corrected-candidate holdout and a fresh scenario variant pass under the separate #39 protocol","full Ruff, MyPy, compile, Python 3.11/3.12 tests, package build, continuity validation, required hosted CI, automatic merge, issue closeout, and local cleanup all succeed","PCM-0009 remains separately scoped and no unrelated target repository is modified"],"depends_on":["PCM-0011","PCM-0012","PCM-0013","PCM-0022"],"goal":"Allow useful parallel task isolation without scattering worktrees or repeatedly storing full dependency payloads, while ensuring every finished task is pushed, checked, merged and cleaned up safely.","id":"PCM-0019","next_action":"Publish the managed-worktree candidate for protected CI, then run the separate #39 corrected-candidate holdout and scenario variant.","owner":"Codex PCM development session; GitHub issue #34","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"A blanket worktree ban blocks safe parallel isolation, while unmanaged worktrees and per-tree environments can accumulate on disk. The intended result is one permanent main checkout, one temporary task-owned tree only when useful, shared immutable package caches, and refusal-first cleanup after verified GitHub delivery."} -->

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

- [ ] Workspace policy has a clear safe default, explicit managed and strict
  modes, backward-compatible reading, and generated guidance matching the mode.
- [ ] A task can create/reuse only its own tree at
  `<canonical-root>/pcm/worktree/<TASK-ID>` on its bound branch; no sibling
  clone or arbitrary path is created.
- [ ] Cleanup is refusal-first and verifies canonical remote identity, exact
  managed path, task/branch association, clean tracked and untracked state,
  publication, and merge into the protected remote default branch. It never
  uses force removal or deletes dirty, unmerged, pinned, or user-owned trees.
- [ ] Cleanup fails closed for non-GitHub remotes until PCM implements a tested
  CI/merge verifier for those hosts.
- [ ] Successful cleanup removes the worktree and only then its safely merged
  local task branch. GitHub remains responsible for protected CI, auto-merge,
  and remote branch deletion; PCM must report inability to verify rather than
  pretending a local clean tree proves delivery.
- [ ] Guidance recommends one tree per active task reused across sessions and
  additional trees only for real parallel work. pnpm/uv caches and managed
  runtimes may be reused; `node_modules`/`.venv` remain isolated when lockfiles,
  interpreters, or task-specific dependencies differ. Finished trees and their
  private environments are removed after successful merge.
- [ ] Deterministic tests cover strict-mode rejection, managed path/identity,
  idempotent resume, task/branch/path conflicts, dirty/untracked refusal,
  unpublished/unmerged refusal, and successful post-merge cleanup.
- [ ] Repeated disposable checkouts are measured with a reproducible method and
  their temporary repositories are removed; do not claim zero disk cost.
- [ ] Fresh-session baseline/candidate and one visible-requirement variant are
  evaluated under #39 fairness rules; holdout workers are stopped/closed after
  capturing evidence.
- [ ] Full local gates and required hosted CI pass; a protected PR auto-merges,
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

## Handoff

Read `PROJECT.md` → `checkpoints/CURRENT.md` → this task → `AGENTS.md` →
`SPEC.md` → `docs/HANDOFF_PROTOCOL.md` → `docs/TESTING_POLICY.md`. Treat the
#34 issue and this task as authoritative scope; do not infer the #39 evaluator
answer from the prior blind worker's diagnosis.
