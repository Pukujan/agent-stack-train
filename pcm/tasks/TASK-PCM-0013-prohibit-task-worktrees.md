# TASK-PCM-0013 — Prohibit Task Clones and Git Worktrees

<!-- continuity:task {"acceptance":["all new software and minimal projects use the sole single-checkout policy with no workspace-mode selection","the legacy workspace_mode key is rejected with a clear migration instruction and validation never rewrites configuration","linked-worktree configuration, branches, and generated worktree instructions are removed from active schemas, CLI, templates, documentation, and tests while prior task history remains append-only","required repository lint, type, test, compile, build, validation, and CI gates pass before merge"],"depends_on":["PCM-0012"],"goal":"Make single-checkout mandatory across Project Continuity and remove linked task worktrees as a supported configuration.","id":"PCM-0013","next_action":"Remove workspace mode selection and legacy validation compatibility, update all active guidance, and add regression coverage.","owner":"Codex implementation session","priority":"P0","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"The user requires one canonical checkout and explicitly prohibits every task clone, Git worktree, task folder, and extra environment. PCM-0012 made linked worktrees configurable; this additive follow-up must make that policy unconditional without silently rewriting existing project configuration."} -->

- Status: active
- Owner: Codex implementation session
- Priority: P0
- Depends on: PCM-0012

## Goal

Make a single canonical checkout the only supported execution model. Do not
create task clones, linked Git worktrees, task folders, or additional dependency
environments. New projects must receive this policy in every generated profile.

## Migration behavior

Projects whose `.continuity/config.json` contains the legacy `workspace_mode`
key must fail validation with a clear message directing maintainers to remove
that key. Validation must not edit or silently normalize the file. Removing the
key is a user-controlled migration; the remaining config is validated normally.

## Allowed files

- `AGENTS.md`
- `SPEC.md`
- `README.md`
- `docs/HANDOFF_PROTOCOL.md`
- `schemas/v1/config.schema.json`
- `src/continuity/cli.py`
- `templates/v1/software/AGENTS.md`
- `tests/test_cli.py`
- `tasks/TASK-PCM-0013-prohibit-task-worktrees.md`
- `checkpoints/CURRENT.md`

Do not rewrite PCM-0011 or PCM-0012 history. Other archival task records and
blind-test artifacts are outside this task's scope.

## Acceptance criteria

- [x] Remove `workspace_mode` and all linked-worktree choices from config schema, CLI, templates, active docs, and tests.
- [x] Generated projects unconditionally instruct serial work in one canonical checkout with one dependency environment and prohibit clones/worktrees/task folders.
- [x] Validation rejects any config containing `workspace_mode` and reports a clear migration message without changing the config bytes.
- [ ] Tests cover generated defaults, absence of the old CLI option, legacy-key rejection and non-mutation, and successful validation after the user removes the key.
- [ ] Required lint, type checks, tests, compilation, package build, self-validation, and PR CI pass.
- [ ] Commit and push on this branch, open a PR, and merge only after required branch-protection checks pass.

## Checkpoint log

### 2026-09-23 — Task created

Completed:

- Read the canonical checkout's `AGENTS.md`, `PROJECT.md`, `checkpoints/CURRENT.md`, active PCM-0012 task, `SPEC.md`, and `docs/VERSIONING.md`.
- Confirmed the checkout is `D:/claude/projects/project-continuity-modules`, on clean `main`, with `origin` set to the PCM GitHub repository.
- Created this additive follow-up and a task branch in the existing checkout.

Evidence:

- `git status --short --branch` reported clean `main...origin/main` before branch creation.
- `git rev-parse --show-toplevel` returned `D:/claude/projects/project-continuity-modules`.
- `gh auth status` confirmed the GitHub account is available.

Decisions:

- PCM-0012 and PCM-0011 remain unchanged as historical records.
- `workspace_mode` is the legacy key to explicitly detect and reject; validation will instruct the user to remove it, without rewriting the config.

Changed:

- `tasks/TASK-PCM-0013-prohibit-task-worktrees.md`
- `checkpoints/CURRENT.md`

Blocked/uncertain:

- None currently.

Next:

- Implement the strict single-checkout policy in the allowed active files and add regression tests.

### 2026-09-23 — Mandatory single-checkout implementation

Completed:

- Removed `workspace_mode` from the published and built-in config schema, initialization output, CLI arguments, and template branching.
- Updated active protocol, handoff, README, root instructions, and generated software instructions to prohibit task clones, task folders, linked Git worktrees, and additional dependency environments.
- Added an explicit pre-schema legacy-key diagnostic instructing users to remove `workspace_mode` manually; validation does not modify the file.
- Updated tests to cover generated config/guidance, removed CLI option, extra-worktree rejection, legacy-key byte preservation, and validation after manual migration.

Evidence:

- `PYTHONPATH=src python -m unittest discover -s tests -v` — 19 passed.
- `ruff check .` — passed.
- `mypy src` — passed.
- `python -m compileall -q src tests` — passed.
- `PYTHONPATH=src python -m continuity validate --root .` — `VALID`.
- `python -m pip wheel . --no-deps --no-build-isolation --no-cache-dir --wheel-dir .task-tmp\wheelhouse` — wheel built successfully.
- `python -m build` — unavailable locally because the `build` frontend is not installed; the required CI package job remains authoritative for this command.
- `git diff --check` — passed.
- GitHub reports PCM-0012 PR #21 merged; the current branch was created from `main` after that merge.

Decisions:

- Keep the no-secondary-worktree validator check as an unconditional invariant.
- Keep historical PCM-0011/0012 task records untouched; legacy `workspace_mode` remains documented solely for migration and regression coverage.

Changed:

- `AGENTS.md`, `README.md`, `SPEC.md`, `docs/HANDOFF_PROTOCOL.md`, `schemas/v1/config.schema.json`, `src/continuity/cli.py`, `templates/v1/software/AGENTS.md`, `tests/test_cli.py`, `checkpoints/CURRENT.md`, and this task file.

Blocked/uncertain:

- Required branch-protection CI has not run yet. The exact local `python -m build` frontend is unavailable.

Next:

- Review the final diff, commit and push this branch, open its PR, and wait for all required checks before merge.
