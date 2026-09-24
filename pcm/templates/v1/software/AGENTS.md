# Agent Operating Contract

## Start

Read PROJECT → CURRENT → active TASK → minimum relevant spec before editing.

For GitHub repositories, verify the live linked issue with `continuity issue verify <TASK-ID>` before resuming; the issue owns task scope/lifecycle, merged default-branch history owns accepted code, and PR checks/merge records own delivery. Resolve discrepancies from the issue before editing.

## Scope

Work only inside the active bounded task. Split or revise the task before materially expanding scope.

## Canonical checkout

The Git repository, remote, task ID, branch/ref, and commit history identify the work; the physical path does not. Keep one permanent main checkout as the project home base and use it for sequential work. When isolation or parallel work is genuinely useful, create one managed linked worktree per independent active task at `<canonical-root>/pcm/worktree/<TASK-ID>`. Do not create one per session/agent, sibling clones, or arbitrary worktree paths; resume the same worktree across sessions. Register other existing checkouts with `continuity workspace register --root <checkout>`; PCM checks the private per-device registry and Git's worktree list, reuses one clean unlocked task match, and stops on dirty, locked, conflicting, or ambiguous matches. It never scans drives. Keep absolute paths out of shared handoffs.

After required checks pass, the PR is merged, the task record is complete, and the worktree is clean, run `continuity worktree remove <TASK-ID>`. It verifies the GitHub PR, required checks, and merged commit and refuses locked/pinned or otherwise unsafe cleanup; never force-remove unfinished or user-modified work. For a short audit hold, record the reason, expected release date, exact path, and unlock/remove next action in the completed task's checkpoint, then pin the tree with `git worktree lock --reason "<reason; release YYYY-MM-DD>" <path>`. When the audit ends, return to the permanent checkout, unlock the tree, and run normal verified cleanup. Other Git hosts remain unsupported for cleanup until PCM has a tested CI/merge verifier for them. `workspace.mode: single-checkout` is available when a project explicitly wants to prohibit linked worktrees.

Reuse immutable package download/build caches where supported, but keep mutable `node_modules` and `.venv` separate when lockfiles or runtimes differ. Track dependency changes in manifests, lockfiles, or patch files rather than hidden edits to installed packages.

## Checkpoint

Before stopping after meaningful work, append completed work, exact evidence, decisions, changed paths, blockers, and one next atomic action.

Continuity bookkeeping supports execution but does not gate safe execution. If canonical continuity state is temporarily unavailable, continue safe authorized work only in an already-authorized alternate environment; do not create a clone or a new worktree merely to work around it. When authorized, run `continuity checkpoint <TASK-ID> --root <canonical-root> --recovery-root <alternate-root> ...` to write the JSON recovery receipt under `.continuity/recovery/`. Do not write an ad-hoc checkpoint under `checkpoints/`, replace the alternate task file, repair storage merely to write a checkpoint, create competing continuity state, or request redundant permission. Reconcile later with `continuity recovery reconcile --root <canonical-root> --file <receipt>`.

For a normal checkpoint, commit the product change first and then run `continuity checkpoint`; it prints a stable `REQUEST_ID`, commits, and synchronously pushes the checkpoint to the task branch. If interrupted, retry with the same `--request-id`; the same payload is a no-op and a different payload is rejected. Open or update a PR after pushing. CI and auto-merge run asynchronously after required reviews/checks pass; confirm the merge before marking complete or removing a worktree.

If `.continuity/documents.json` exists, every fresh session or task takeover/resumption must consult it before deciding the next action, not only before writing documentation. Run `git fetch origin`, then `continuity docs find "<issue title and task-objective terms>" --task <TASK-ID>`; read the returned matches and declared neighbors before deciding that prior work is missing or creating/replacing a document. Investigate `NEEDS_REVIEW`/`REMOTE_UNKNOWN` before relying on old evidence. The generated human view is checked by `continuity validate`.

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
