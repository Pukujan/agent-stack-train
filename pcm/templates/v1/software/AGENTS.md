# Agent Operating Contract

## Start

Read PROJECT → CURRENT → active TASK → minimum relevant spec before editing.

## Scope

Work only inside the active bounded task. Split or revise the task before materially expanding scope.

## Canonical checkout

- Identify the single canonical checkout by host/path and normalized Git remote, then reuse it.
- Do not create another clone or sibling project folder for a task.
- Work sequentially on task branches in the one canonical checkout and reuse its one root dependency environment.
- Never create task clones, Git worktrees, task folders, or additional dependency environments.
- If the canonical checkout is unavailable or ambiguous, resolve policy and ownership before creating a directory.

## Checkpoint

Before stopping after meaningful work, append completed work, exact evidence, decisions, changed paths, blockers, and one next atomic action.

Continuity bookkeeping supports execution but does not gate safe execution. If canonical continuity state is temporarily unavailable, continue safe authorized work only in an already-authorized alternate environment; do not create a clone or worktree to work around it. When authorized, run `continuity checkpoint <TASK-ID> --root <canonical-root> --recovery-root <alternate-root> ...` to write the JSON recovery receipt under `.continuity/recovery/`. Do not write an ad-hoc checkpoint under `checkpoints/`, replace the alternate task file, repair storage merely to write a checkpoint, create competing continuity state, or request redundant permission. Reconcile later with `continuity recovery reconcile --root <canonical-root> --file <receipt>`.

For a normal checkpoint, commit the product change first and then run `continuity checkpoint`; it commits the checkpoint and pushes the task branch to `origin`. A normal checkpoint is not complete while it exists only in a local worktree. CI runs on every pushed branch and pull-request automation merges after required checks pass.

If the remote is temporarily unavailable, use the degraded recovery-receipt path and record the exact local state. Do not invent a second canonical branch or worktree; publish and reconcile as soon as the shared Git path is available again.

## Continuity records

<!-- pcm:policy {"id":"continuity-records","policy_version":"1.0.0","protocol_version":"0.1.0-draft"} -->

For continuity issues, progress updates, pull requests, and PCM-owned project-state documents, explain the human problem and outcome first, then scope, status, linked evidence, and one next action. Cite external factual claims and tie repository claims to a revision, issue, PR, or CI result. Record reproduction details only when needed to verify the claim. Keep PR openings skimmable; link or collapse long logs. Preserve the project's existing ownership outside PCM continuity.

## Verification

Each task names its human-visible outcome and proportionate checks. Use deterministic regression tests by default. Add a fresh-session holdout only when the task promises that a new agent can discover or follow repository guidance; its checks must come from visible requirements, and ambiguous criteria are inconclusive. Do not create separate PDD/SDD/TDD paperwork or a sub-issue for every test type.

Delegated agents are temporary workers. Give each worker one bounded task, record
its result and evidence in the parent task/checkpoint, and explicitly close it
immediately after the result is captured. This applies to completed, interrupted,
failed, cancelled, and timed-out workers. Stop and close workers that are no
longer needed; do not leave completed workers open for possible future use. Use
the smallest useful number of workers. See `docs/AGENT_LIFECYCLE.md`.
