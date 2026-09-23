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

## Degraded continuity

Execution safety and existing authorization outrank continuity bookkeeping. If canonical continuity state is temporarily unavailable, do not stop safe work or repair storage merely to force a write. Use an already-authorized alternate checkout/host and run `continuity checkpoint <TASK-ID> --root <canonical-root> --recovery-root <alternate-root> ...` to write the JSON recovery receipt under `.continuity/recovery/`; do not create an ad-hoc Markdown checkpoint under `checkpoints/` or replace the alternate task file. Reconcile it later with `continuity recovery reconcile --root <canonical-root> --file <receipt>`. The repository/task lineage is authoritative; a physical worktree is not. Normal checkpoints must be committed and pushed to the task branch; a local-only checkpoint is not a durable handoff. If the remote is temporarily unavailable, use degraded recovery evidence and publish/reconcile as soon as possible.

Delegated agents are temporary workers. Capture each worker's result and evidence
in the parent task/checkpoint, then explicitly close it immediately. Stop and
close workers that are no longer needed, including completed, interrupted,
failed, cancelled, and timed-out workers. Do not leave completed workers open for
possible future use; see `docs/AGENT_LIFECYCLE.md`.

## Verification

Each task names the useful outcome for a person and the smallest checks that can verify it. Prefer deterministic checks. Use a fresh-session holdout only when the promise is about what a new session can discover or do; judge it against visible requirements, not hidden expectations. A passing test does not replace the promised human-visible result.
