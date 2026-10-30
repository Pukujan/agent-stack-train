# TASK-PCM-0011 — Canonical Checkout Worktree Policy

<!-- continuity:task {"acceptance":["the operating contract defines a canonical checkout by host/path plus normalized remote and forbids duplicate sibling clones","the software profile and generated AGENTS.md require registered linked worktrees below the canonical checkout","tests prove newly initialized software projects inherit this rule","context-pack source paths are stable across Windows and POSIX","all repository tests and continuity validation pass"],"depends_on":[],"goal":"Make continuity-created projects use one canonical checkout and place task isolation in registered linked worktrees nested beneath it.","id":"PCM-0011","next_action":"resolve PR merge state with latest main, then run required CI and merge","owner":"Codex current implementation session","priority":"P0","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Sibling clones and task directories have multiplied under D:\\\\claude and obscured which checkout is authoritative; future project instructions need an explicit, tested default."} -->

- Status: active
- Owner: Codex current implementation session
- Priority: P0
- Depends on: none

## Goal

Make continuity-created projects use one canonical checkout and place task isolation in registered linked worktrees nested beneath it.

## Why

Sibling clones and task directories have multiplied under D:\\claude and obscured which checkout is authoritative; future project instructions need an explicit, tested default.

## Allowed files

- `AGENTS.md`
- `src/continuity/cli.py`
- `templates/v1/software/AGENTS.md`
- `tests/test_cli.py`
- `tasks/TASK-PCM-0011-canonical-checkout-worktree-policy.md`
- `checkpoints/CURRENT.md`

## Acceptance criteria

- [ ] The operating contract defines a canonical checkout by host/path plus normalized remote and forbids duplicate sibling clones.
- [ ] The software profile and generated `AGENTS.md` require registered linked worktrees below the canonical checkout.
- [ ] Tests prove newly initialized software projects inherit the rule.
- [ ] Context-pack source paths are stable across Windows and POSIX.
- [ ] All repository tests and continuity validation pass.

## Checkpoint log

### 2026-09-23 — Canonical checkout rule added

Completed:

- added canonical project-root identity and nested linked-worktree requirements to the operating contract and software profile;
- updated the CLI's generated `AGENTS.md` to match the checked-in profile template;
- normalized context-pack source paths to POSIX separators for stable metadata.

Evidence:

- project-continuity-modules unit suite after merging current `main`: 15 passed;
- `continuity validate --root .`: VALID;
- `git diff --check`: passed.

Decisions:

- branch differences do not justify a second clone of the same normalized remote;
- isolation stays within the canonical checkout through registered linked worktrees.
- incorporated `main` commit `93c0549` without replacing its helper/target or checkpoint-delivery rules.

Changed:

- `AGENTS.md`, `src/continuity/cli.py`, `templates/v1/software/AGENTS.md`, `tests/test_cli.py`, `checkpoints/CURRENT.md`.

Blocked/uncertain:

- none locally; required GitHub CI must validate the refreshed PR before auto-merge.

Next:

- push the merge resolution and verify required CI/auto-merge for PR #19.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
