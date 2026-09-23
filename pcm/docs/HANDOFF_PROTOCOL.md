# Handoff Protocol

## Goal

A fresh session should resume from repository state without needing the previous conversation.

## Canonical hierarchy

```text
PROJECT
  ↓
CURRENT
  ↓
TASK
  ↓
CHECKPOINTS
```

Issues/Beads/PRs mirror coordination. Context packs are generated views.

## Start-session procedure

1. read `PROJECT.md`;
2. read `checkpoints/CURRENT.md`;
3. open the active task;
4. read only the minimum relevant spec/design file;
5. confirm branch/scope before edits.

If delegated agents are used, read `docs/AGENT_LIFECYCLE.md` as part of the
relevant handoff contract.

## Checkpoint format

Append, do not rewrite history:

```
### YYYY-MM-DD HH:MM UTC — <agent/session>

Completed:
- ...

Evidence:
- command/artifact -> observed result

Decisions:
- ...

Changed:
- ...

Blocked/uncertain:
- none | ...

Next:
- one atomic action
```

## Stop-session requirements

Before stopping:
- commit meaningful product work before checkpointing;
- run `continuity checkpoint`, which commits the checkpoint and pushes the task branch to `origin`;
- do not call a normal checkpoint complete while it exists only in a local worktree;
- if the remote is unavailable, use the degraded recovery-receipt path and record the exact local state;
- record tests/commands/results;
- record uncertainty rather than guessing;
- set one exact next action;
- update CURRENT only when repository-level state changed;
- link task ID to issue/PR/Beads item when used.

## Degraded continuity

Execution safety and existing authorization outrank checkpoint bookkeeping. A temporary failure to read or write `PROJECT`, `CURRENT`, `TASK`, or `HANDOFF` state is a degraded continuity condition, not an independent reason to stop safe work.

Use an already-authorized alternate checkout or host when needed. Record the same task ID, repository identity, branch/ref, source commit, evidence, and next action in a recovery receipt with `continuity checkpoint --recovery-root <alternate-root>`. Do not repair storage merely to force a write, ask again for permission that already exists, treat a physical path as project identity, or create competing continuity state. Reconcile the receipt after the canonical checkout is writable with `continuity recovery reconcile`.

Each task uses the one canonical checkout, with task branches run sequentially. Do not create task clones, task folders, or linked Git worktrees. The pushed task branch is the required durable shared handoff for normal operation. CI runs on every pushed branch, and pull-request automation merges after the required checks pass.

## Delegated-agent cleanup

Delegated agents are temporary workers. Before the parent session moves on, it
must capture each worker's result in the parent task/checkpoint and explicitly
close the worker. A terminal `completed` status is not enough: an open completed
worker still consumes an agent slot. Stop and close workers that are no longer
needed, including workers that fail, are interrupted, cancelled, or time out.

## Context packs

A context pack may concatenate/transform canonical state for convenience, but must identify:
- repository;
- ref/branch;
- commit;
- protocol version;
- task ID;
- generation time;
- source file list.

Never update a context pack instead of canonical state.
