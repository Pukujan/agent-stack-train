# Agent Operating Contract

## Start

Read PROJECT → CURRENT → active TASK → minimum relevant spec before editing.

## Scope

Work only inside the active bounded task. Split or revise the task before materially expanding scope.

## Canonical checkout and worktree

- Identify the single canonical checkout by host/path and normalized Git remote, then reuse it.
- Do not create another clone or sibling project folder for a task.
- When isolation is needed, reuse a registered linked worktree or create one under `<canonical-root>/.worktrees/<task-slug>`; ensure `.worktrees/` is ignored.
- Record the canonical root separately from the task worktree. If the root is ambiguous or unavailable, resolve it before creating a directory.

## Checkpoint

Before stopping after meaningful work, append completed work, exact evidence, decisions, changed paths, blockers, and one next atomic action.
