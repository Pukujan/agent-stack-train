# Agent Operating Contract

## Start

Read PROJECT → CURRENT → active TASK → minimum relevant spec before editing.

## Scope

Work only inside the active bounded task. Split or revise the task before materially expanding scope.

## Canonical checkout and workspace mode

- Identify the single canonical checkout by host/path and normalized Git remote, then reuse it.
- Do not create another clone or sibling project folder for a task.
- New software projects default to `workspace_mode: single-checkout`: work sequentially on task branches in the canonical checkout, reuse its one root dependency environment, and do not create task folders or linked Git worktrees anywhere.
- A project may use `workspace_mode: linked-worktrees` only when that value is explicitly selected in `.continuity/config.json`. Only then may tasks use registered linked worktrees under `<canonical-root>/.worktrees/<task-slug>`; ensure `.worktrees/` is ignored and record the canonical checkout separately.
- If the workspace mode is missing or the canonical checkout is unavailable or ambiguous, do not create a worktree. Resolve policy and ownership first.

## Checkpoint

Before stopping after meaningful work, append completed work, exact evidence, decisions, changed paths, blockers, and one next atomic action.

Continuity bookkeeping supports execution but does not gate safe execution. If canonical continuity state is temporarily unavailable, continue safe authorized work only in an already-authorized alternate environment; do not create a clone or worktree to work around it. When authorized, run `continuity checkpoint <TASK-ID> --root <canonical-root> --recovery-root <alternate-root> ...` to write the JSON recovery receipt under `.continuity/recovery/`. Do not write an ad-hoc checkpoint under `checkpoints/`, replace the alternate task file, repair storage merely to write a checkpoint, create competing continuity state, or request redundant permission. Reconcile later with `continuity recovery reconcile --root <canonical-root> --file <receipt>`.

For a normal checkpoint, commit the product change first and then run `continuity checkpoint`; it commits the checkpoint and pushes the task branch to `origin`. A normal checkpoint is not complete while it exists only in a local worktree. CI runs on every pushed branch and pull-request automation merges after required checks pass.

If the remote is temporarily unavailable, use the degraded recovery-receipt path and record the exact local state. Do not invent a second canonical branch or worktree; publish and reconcile as soon as the shared Git path is available again.
