# Current Handoff

Start from repository state, not prior chat history.

## Read order

1. `PROJECT.md`
2. `AGENTS.md` when present
3. `checkpoints/CURRENT.md`
4. the active task named by CURRENT
5. the minimum relevant specification/design document

## Authority

For GitHub repositories, Issues are authoritative for task scope, priority, ownership, dependencies, acceptance, and lifecycle. The linked task file is a compact working cache. Merged default-branch history owns accepted code, and PR checks/merge evidence own delivery. Verify the live issue with `continuity issue verify <TASK-ID>` before resuming.

## Workspace lifecycle

Keep one permanent main checkout as the project's home base and use it for sequential work. When genuine parallelism or isolation is useful, create one managed linked worktree per independent active task under `<canonical-root>/pcm/worktree/<TASK-ID>`, not one per session or agent; resume it across sessions. Do not create sibling clones or arbitrary worktree paths.

Before creating a tree, PCM checks Git's registered worktrees and its private per-device workspace registry. Register existing checkouts on other drives with `continuity workspace register --root <checkout>`. One clean, unlocked match is reused; a dirty, locked, conflicting, or ambiguous match stops before creation. PCM does not scan drives. Registry paths stay local and must never be copied into shared records.

After required checks pass, the PR is merged, the task record is complete, and the worktree is clean, run `continuity worktree remove <TASK-ID>`. It verifies the GitHub PR, required checks, and merged commit and refuses locked/pinned, dirty, or unproven cleanup; never force-remove unfinished or user-modified work. For a short audit hold, record the reason, expected release date, exact path, and unlock/remove next action in the completed task's checkpoint, then pin the tree with `git worktree lock --reason "<reason; release YYYY-MM-DD>" <path>`. When the audit ends, unlock it and run normal verified cleanup. Other Git hosts remain unsupported for cleanup until PCM has a tested CI/merge verifier for them. `workspace.mode: single-checkout` is available when strict one-checkout behavior is preferred.

Reuse immutable package caches where supported, but keep mutable dependency environments separate when lockfiles or runtimes differ. Track dependency changes in manifests, lockfiles, or patch files.

## Finding earlier project documents

When `.continuity/documents.json` is present, it is the machine-readable inventory and `docs/CONTINUITY_INDEX.md` is its generated human view. Every fresh session or task takeover/resumption must consult the inventory before choosing its next action, not only before writing a document: run `git fetch origin`, then use `continuity docs find "<issue title and task-objective terms>" --task <TASK-ID>` and read matching records and their declared neighbors. The search is deterministic metadata search, not semantic whole-repository search. `continuity validate` checks the generated view; use `continuity docs render` to refresh its freshness labels after source edits. A `NEEDS_REVIEW` result preserves historical evidence but says not to rely on it without checking the current file.

## Degraded continuity

Execution safety and existing authorization outrank continuity bookkeeping. If canonical continuity state is temporarily unavailable, do not stop safe work or repair storage merely to force a write. Use an already-authorized alternate checkout/host and run `continuity checkpoint <TASK-ID> --root <canonical-root> --recovery-root <alternate-root> ...` to write the JSON recovery receipt under `.continuity/recovery/`; do not create an ad-hoc Markdown checkpoint under `checkpoints/` or replace the alternate task file. Reconcile it later with `continuity recovery reconcile --root <canonical-root> --file <receipt>`. The repository/task lineage is authoritative; a physical worktree is not.

Normal checkpointing is a delivery operation, not a local note: commit the product change first, then run `continuity checkpoint`. The command prints a `REQUEST_ID`, commits the canonical checkpoint and synchronously pushes the task branch to `origin`; if interrupted, rerun with the same `--request-id` to avoid a duplicate (changed payload with the same ID is rejected). Open or update a PR after pushing. GitHub CI and auto-merge then run asynchronously, gated by required reviews/checks and any merge queue. Confirm the merge before marking complete or removing the worktree.

Delegated agents are temporary workers. Capture each worker's result and evidence
in the parent task/checkpoint, then explicitly close it immediately. Stop and
close workers that are no longer needed, including completed, interrupted,
failed, cancelled, and timed-out workers. Do not leave completed workers open for
possible future use; see `docs/AGENT_LIFECYCLE.md`.

## Continuity records

<!-- pcm:policy {"id":"continuity-records","policy_version":"1.1.0","protocol_version":"0.1.0-draft"} -->

Write continuity issues, updates, pull requests, and project-state documents so a new reader can understand the problem, human outcome, scope, evidence, and next action without the original chat. Cite external claims and link repository claims to their revision or CI evidence. Include reproduction detail only when it is needed to verify the claim. Keep PR openings skimmable; put long logs in linked artifacts. Preserve project ownership outside continuity. Do not claim automatic tracker sync or chat capture unless implemented and tested. GitHub's issue-closing keywords in PR descriptions and commit messages remain active under negation; use them only when the issue should complete at merge, and verify issue status afterward.

## Verification

Each task names the useful outcome for a person and the smallest checks that can verify it. Prefer deterministic checks. Use a fresh-session holdout only when the promise is about what a new session can discover or do; judge it against visible requirements, not hidden expectations. A passing test does not replace the promised human-visible result.
