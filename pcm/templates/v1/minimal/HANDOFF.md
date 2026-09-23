# Current Handoff

Start from repository state, not prior chat history.

## Read order

1. `PROJECT.md`
2. `AGENTS.md` when present
3. `checkpoints/CURRENT.md`
4. the active task named by CURRENT
5. the minimum relevant specification/design document

## Authority

Canonical repository files are authoritative. Tracker items and context packs are mirrors/derived views.

## Workspace lifecycle

Keep one permanent main checkout as the project's home base and use it for sequential work. When genuine parallelism or isolation is useful, create one managed linked worktree per independent active task under `<canonical-root>/pcm/worktree/<TASK-ID>`, not one per session or agent; resume it across sessions. Do not create sibling clones or arbitrary worktree paths.

After required checks pass, the PR is merged, the task record is complete, and the worktree is clean, run `continuity worktree remove <TASK-ID>`. It verifies the GitHub PR, required checks, and merged commit and refuses locked/pinned, dirty, or unproven cleanup; never force-remove unfinished or user-modified work. Intentionally retained trees can be protected with `git worktree lock --reason "<reason>" <path>` and released later with `git worktree unlock <path>`. Other Git hosts remain unsupported for cleanup until PCM has a tested CI/merge verifier for them. `workspace.mode: single-checkout` is available when strict one-checkout behavior is preferred.

Reuse immutable package caches where supported, but keep mutable dependency environments separate when lockfiles or runtimes differ. Track dependency changes in manifests, lockfiles, or patch files.

## Degraded continuity

Execution safety and existing authorization outrank continuity bookkeeping. If canonical continuity state is temporarily unavailable, do not stop safe work or repair storage merely to force a write. Use an already-authorized alternate checkout/host and run `continuity checkpoint <TASK-ID> --root <canonical-root> --recovery-root <alternate-root> ...` to write the JSON recovery receipt under `.continuity/recovery/`; do not create an ad-hoc Markdown checkpoint under `checkpoints/` or replace the alternate task file. Reconcile it later with `continuity recovery reconcile --root <canonical-root> --file <receipt>`. The repository/task lineage is authoritative; a physical worktree is not. Normal checkpoints must be committed and pushed to the task branch; a local-only checkpoint is not a durable handoff. If the remote is temporarily unavailable, use degraded recovery evidence and publish/reconcile as soon as possible.

Delegated agents are temporary workers. Capture each worker's result and evidence
in the parent task/checkpoint, then explicitly close it immediately. Stop and
close workers that are no longer needed, including completed, interrupted,
failed, cancelled, and timed-out workers. Do not leave completed workers open for
possible future use; see `docs/AGENT_LIFECYCLE.md`.

## Continuity records

<!-- pcm:policy {"id":"continuity-records","policy_version":"1.0.0","protocol_version":"0.1.0-draft"} -->

Write continuity issues, updates, pull requests, and project-state documents so a new reader can understand the problem, human outcome, scope, evidence, and next action without the original chat. Cite external claims and link repository claims to their revision or CI evidence. Include reproduction detail only when it is needed to verify the claim. Keep PR openings skimmable; put long logs in linked artifacts. Preserve project ownership outside continuity. Do not claim automatic tracker sync or chat capture unless implemented and tested.

## Verification

Each task names the useful outcome for a person and the smallest checks that can verify it. Prefer deterministic checks. Use a fresh-session holdout only when the promise is about what a new session can discover or do; judge it against visible requirements, not hidden expectations. A passing test does not replace the promised human-visible result.
