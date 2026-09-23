# TASK-PCM-0009 — Canonical Checkout Worktree Policy

<!-- continuity:task {"acceptance":["the module's operating contract forbids duplicate sibling clones and defines a canonical checkout by host/path plus normalized remote","the software profile emits canonical-root and nested linked-worktree rules","a test verifies newly initialized software projects receive the rule and remain valid","all repository tests and continuity validation pass"],"depends_on":[],"goal":"Make continuity-created projects use one canonical checkout and place required task isolation in registered linked worktrees nested beneath that checkout.","id":"PCM-0009","next_action":"implement the canonical checkout policy in the operating contract and software profile template, then test generated projects","owner":"Codex current implementation session","priority":"P0","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Sibling clones and task directories have multiplied across D:\\\\claude and obscured which checkout is authoritative; future project instructions need an explicit, testable default."} -->

- Status: active
- Owner: Codex current implementation session
- Priority: P0
- Depends on: none

## Goal

Make continuity-created projects use one canonical checkout and place required task isolation in registered linked worktrees nested beneath that checkout.

## Why

Sibling clones and task directories have multiplied across D:\\claude and obscured which checkout is authoritative; future project instructions need an explicit, testable default.

## Allowed files

- `AGENTS.md`
- `src/continuity/cli.py`
- `templates/v1/software/AGENTS.md`
- `tests/test_cli.py`
- `tasks/TASK-PCM-0009-canonical-checkout-worktree-policy.md`
- `checkpoints/CURRENT.md`

## Acceptance criteria

- [ ] The operating contract forbids duplicate sibling clones and defines a canonical checkout by host/path plus normalized remote.
- [ ] The software profile emits canonical-root and nested linked-worktree rules.
- [ ] A test verifies a newly initialized software project receives the rule and remains valid.
- [ ] All repository tests and continuity validation pass.

## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
