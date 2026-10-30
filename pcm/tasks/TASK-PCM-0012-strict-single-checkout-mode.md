# TASK-PCM-0012 — Strict Single-Checkout Mode

<!-- continuity:task {"acceptance":["new software initialization defaults to an explicit single-checkout workspace mode","linked-worktree mode remains available only when explicitly selected","generated AGENTS.md matches the selected workspace mode","validate rejects registered linked worktrees when single-checkout mode is selected","CI covers schema, CLI generation, both modes, and strict-mode validation"],"depends_on":[],"goal":"Add an explicit single-checkout mode to Project Continuity so projects can prohibit task worktrees and use serial branches in one canonical folder.","id":"PCM-0012","next_action":"Implement the workspace-mode config, generated guidance, validation, and tests in the existing canonical checkout.","owner":"Codex current implementation session","priority":"P0","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"PCM-0011 prohibited duplicate sibling clones but recommended nested per-task worktrees; the local D-drive policy requires one working folder and one project environment, so future generated instructions must support that mode without silently changing the choices available to other projects."} -->

- Status: active
- Owner: Codex current implementation session
- Priority: P0
- Depends on: PCM-0011 merged in PR #19; issue #20

## Goal

Add a declared workspace-isolation mode. New software projects default to
`single-checkout`: tasks run serially on branches in the canonical checkout,
reuse its dependency environment, and never create task clones or linked
worktrees. `linked-worktrees` remains available only as an explicit opt-in for
projects that choose parallel isolated directories.

## Why

PCM-0011 correctly prohibited sibling clones but its root contract, software
template, and generated `AGENTS.md` advised agents to create registered task
worktrees. That recommendation can multiply task folders and dependency
installs on a machine that requires one local checkout. The workspace choice
must be explicit, validated, and reflected in generated instructions.

Issue: https://github.com/Pukujan/project-continuity-modules/issues/20

## Allowed files

- `AGENTS.md`
- `SPEC.md`
- `README.md`
- `schemas/v1/config.schema.json`
- `src/continuity/cli.py`
- `templates/v1/software/AGENTS.md`
- `tests/test_cli.py`
- `tasks/TASK-PCM-0012-strict-single-checkout-mode.md`
- `tasks/TASK-PCM-0011-canonical-checkout-worktree-policy.md` (append-only merged-status note)
- `checkpoints/CURRENT.md`

## Acceptance criteria

- [ ] The v1 config schema accepts an optional `workspace_mode` with values `single-checkout` and `linked-worktrees`, preserving old configs.
- [ ] New `continuity init --profile software` runs default to `single-checkout`; linked worktrees require an explicit `--workspace-mode linked-worktrees` selection.
- [ ] Generated software `AGENTS.md` tells single-checkout projects to work serially in the canonical checkout, reuse one dependency environment, and prohibit clones/worktrees; linked mode is generated only when selected.
- [ ] `continuity validate` reports linked Git worktrees when the declared mode is `single-checkout`, without changing or removing them.
- [ ] Deterministic tests cover default mode, explicit linked mode, legacy configs, and strict-mode violation reporting.
- [ ] CI passes and the checkpoint is pushed and merged through a required-check PR.

## Checkpoint log

### 2026-09-23 — Cause confirmed and issue recorded

Completed:

- Read PCM's GitHub `AGENTS.md`, the merged PCM-0011 task, generated software profile, and protocol specification.
- Confirmed the root operating contract, software template, CLI-generated `AGENTS.md`, and specification recommend or permit nested task worktrees.
- Recorded the missing strict single-checkout mode as GitHub issue #20 without disclosing machine-specific paths.
- Fast-forwarded the one canonical local PCM checkout to merged `main` (`9d8deb3`) and created this task branch in place; no second clone or worktree was created.

Evidence:

- PCM-0011 merged as PR #19 at `9d8deb3`; the local recommendation was present in the merged `AGENTS.md`, software template, `SPEC.md`, and `src/continuity/cli.py` generator.
- `main` is protected by a required PR and required `quality`, `test (3.11)`, `test (3.12)`, and `package` checks; administrator enforcement is enabled and force-push/deletion are disabled.

Decisions:

- Keep linked-worktree mode available to other projects, but make it explicit; default new software projects to serial single-checkout behavior.
- Preserve PCM-0011's merged checkpoint and prior task history; append the follow-up rather than rewriting it.
- Do not delete or move any existing task directories as part of this upstream policy change.

Changed:

- GitHub issue #20.
- `checkpoints/CURRENT.md`.
- `tasks/TASK-PCM-0012-strict-single-checkout-mode.md`.

Blocked/uncertain:

- None for implementation. Existing adopted repositories require their local root policy or a later explicit migration; changing their local folders is outside this task.

Next:

- Implement config schema/CLI mode selection, generated guidance, strict-mode validation, and deterministic tests.

### 2026-09-23 — Mode, generator, validation, and tests implemented

Completed:

- Added the optional `workspace_mode` config value and `continuity init --workspace-mode` choice. New projects default to `single-checkout`; `linked-worktrees` requires explicit selection.
- Updated the PCM root contract, protocol, README, software profile, and CLI-generated AGENTS.md so their workspace rules agree.
- Added read-only `continuity validate` enforcement for single-checkout Git projects; it reports linked worktrees and never changes them.
- Added coverage for default strict mode, explicit linked mode, CLI parsing, legacy configs, canonical-only worktree state, and prohibited linked worktrees.

Evidence:

- `python -m unittest discover -s tests -v` — 20 passed.
- `ruff check .` — passed.
- `mypy src` — passed.
- `python -m compileall -q src tests` — passed.
- `python -m continuity validate --root .` — `VALID`.
- `git diff --check` — passed; Git reports only configured LF-to-CRLF conversion notices.
- Local runtime: Python 3.12.10; required PR CI will cover Python 3.11 and 3.12 and package build.

Changed:

- `AGENTS.md`, `SPEC.md`, `README.md`, `schemas/v1/config.schema.json`, `src/continuity/cli.py`, `templates/v1/software/AGENTS.md`, `tests/test_cli.py`, `checkpoints/CURRENT.md`, and this task file.

Decisions:

- Existing configs without `workspace_mode` remain valid and retain their prior semantics; new initialization writes the explicit safe default.
- Strict validation applies only to a Git checkout and reports all violations without deleting or moving anything.

Blocked/uncertain:

- None locally. Required remote CI has not run because the branch has not yet been pushed.

Next:

- Review the final diff, commit and push this branch, open a PR, and wait for all required CI checks before merge.

## Handoff

Read PROJECT → CURRENT → this task → the minimum relevant specification. Preserve
all prior checkpoint and handoff records.
