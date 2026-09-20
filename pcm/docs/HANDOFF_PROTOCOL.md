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
- commit meaningful work or document dirty state;
- record tests/commands/results;
- record uncertainty rather than guessing;
- set one exact next action;
- update CURRENT only when repository-level state changed;
- link task ID to issue/PR/Beads item when used.

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
