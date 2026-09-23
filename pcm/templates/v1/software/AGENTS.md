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

Continuity bookkeeping supports execution but does not gate safe execution. If canonical continuity state is temporarily unavailable, continue safe authorized work in an already-authorized alternate checkout/host and run `continuity checkpoint <TASK-ID> --root <canonical-root> --recovery-root <alternate-root> ...` to write the JSON recovery receipt under `.continuity/recovery/`. Do not write an ad-hoc checkpoint under `checkpoints/`, replace the alternate task file, repair storage merely to write a checkpoint, treat a physical worktree as project identity, create competing continuity state, or request redundant permission. Reconcile later with `continuity recovery reconcile --root <canonical-root> --file <receipt>`.

For a normal checkpoint, commit the product change first and then run `continuity checkpoint`; it commits the checkpoint and pushes the task branch to `origin`. A normal checkpoint is not complete while it exists only in a local worktree. CI runs on every pushed branch and pull-request automation merges after required checks pass.

If the remote is temporarily unavailable, use the degraded recovery-receipt path and record the exact local state. Do not invent a second canonical branch or worktree; publish and reconcile as soon as the shared Git path is available again.
