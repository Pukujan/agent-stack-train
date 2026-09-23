# Agent Operating Contract

This repository dogfoods the continuity protocol it is building.

## Read order

Before doing work:

1. `PROJECT.md`
2. `checkpoints/CURRENT.md`
3. the active `tasks/TASK-*.md`
4. the minimum relevant document:
   - normative design: `SPEC.md`
   - handoffs: `docs/HANDOFF_PROTOCOL.md`
   - versioning/migrations: `docs/VERSIONING.md`

Do not scan historical chats for context by default.

## One task, one primary branch/session

Task IDs use `PCM-XXXX`.

Recommended branch format:

```text
task/PCM-0001-bootstrap-v1
```

One primary agent/session owns the writable task state at a time.

## Canonical checkout and task worktrees

- Before writing, identify the single canonical checkout by host/path and normalized Git remote; continue in that checkout.
- Do not create another clone or sibling project folder to isolate a task. A different task or branch does not justify a duplicate checkout.
- If a separate working directory is necessary, reuse an existing registered linked worktree or create one at `<canonical-root>/.worktrees/<task-slug>`.
- Keep `.worktrees/` ignored by the canonical repository, and record the canonical root separately from the task worktree in the handoff/checkpoint.
- If the canonical checkout is unavailable or ambiguous, stop and resolve ownership/path before creating anything.

## Checkpoint rule

Before stopping after meaningful work, append to the active task:

- completed work;
- evidence/commands/results;
- files changed;
- decisions;
- blockers/uncertainty;
- one exact next action.

Update `checkpoints/CURRENT.md` only when program-wide state or priority changes.

## Evidence rule

Distinguish:
- observed command/test result;
- repository state;
- external artifact;
- agent/model claim;
- inference/assumption.

Never promote an unsupported previous-session statement into project fact.

## Scope rule

If the task expands materially, update/split the task before doing the expanded work.

## Self-hosting rule

Changes to the continuity protocol must be managed using the continuity protocol itself whenever practical. Protocol defects discovered while dogfooding should become explicit tasks/issues rather than silent conventions.
