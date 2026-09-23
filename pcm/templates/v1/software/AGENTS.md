# Agent Operating Contract

## Start

Read PROJECT → CURRENT → active TASK → minimum relevant spec before editing.

## Scope

Work only inside the active bounded task. Split or revise the task before materially expanding scope.

## Canonical checkout

The Git repository, remote, task ID, branch/ref, and commit history identify the work; the physical path does not. Keep one permanent main checkout as the project home base and use it for sequential work. When isolation or parallel work is genuinely useful, create one managed linked worktree per independent active task at `<canonical-root>/pcm/worktree/<TASK-ID>`. Do not create one per session/agent, sibling clones, or arbitrary worktree paths; resume the same worktree across sessions.

After required checks pass, the PR is merged, the task record is complete, and the worktree is clean, run `continuity worktree remove <TASK-ID>`. It verifies the GitHub PR, required checks, and merged commit and refuses locked/pinned or otherwise unsafe cleanup; never force-remove unfinished or user-modified work. Intentionally retained trees can be protected with `git worktree lock --reason "<reason>" <path>` and released later with `git worktree unlock <path>`. Other Git hosts remain unsupported for cleanup until PCM has a tested CI/merge verifier for them. `workspace.mode: single-checkout` is available when a project explicitly wants to prohibit linked worktrees.

Reuse immutable package download/build caches where supported, but keep mutable `node_modules` and `.venv` separate when lockfiles or runtimes differ. Track dependency changes in manifests, lockfiles, or patch files rather than hidden edits to installed packages.

## Checkpoint

Before stopping after meaningful work, append completed work, exact evidence, decisions, changed paths, blockers, and one next atomic action.

Continuity bookkeeping supports execution but does not gate safe execution. If canonical continuity state is temporarily unavailable, continue safe authorized work only in an already-authorized alternate environment; do not create a clone or a new worktree merely to work around it. When authorized, run `continuity checkpoint <TASK-ID> --root <canonical-root> --recovery-root <alternate-root> ...` to write the JSON recovery receipt under `.continuity/recovery/`. Do not write an ad-hoc checkpoint under `checkpoints/`, replace the alternate task file, repair storage merely to write a checkpoint, create competing continuity state, or request redundant permission. Reconcile later with `continuity recovery reconcile --root <canonical-root> --file <receipt>`.

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
