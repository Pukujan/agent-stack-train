## Checkpoint rule

Before stopping after meaningful work, update the active task (rewrite sections as needed):

- completed work;
- evidence/commands/results;
- files changed;
- decisions;
- blockers/uncertainty;
- one exact next action.

Update `checkpoints/CURRENT.md` only when program-wide state or priority changes.

Continuity bookkeeping supports execution but does not gate safe execution. If a canonical task, CURRENT, or HANDOFF file is temporarily unavailable, do not repair storage merely to force a write or stop otherwise-safe authorized work. Use only an already-authorized alternate environment; never create a clone or worktree merely to bypass unavailable checkpoint state. Run `continuity checkpoint ... --recovery-root <alternate-root>` only when that alternate environment is authorized, then reconcile with `continuity recovery reconcile --root <canonical-root> --file <receipt>`. Recovery receipts are temporary evidence, not a competing project identity.

Normal checkpoint delivery is mandatory: commit the product change first, then run `continuity checkpoint`. The command commits the checkpoint and synchronously pushes the task branch to `origin`; a normal checkpoint is not complete while it exists only locally. Open/update a PR after pushing. GitHub CI and auto-merge then run asynchronously; auto-merge must wait for required reviews/checks and any merge queue. Do not mark the task complete or remove its worktree until the merged PR and required checks are confirmed. Work only on the task's own branch; never force-push or push directly to the protected default branch. A managed worktree uses the same task/repository identity and is never a substitute for publishing.

The checkpoint command prints a `REQUEST_ID` before it writes. If the command is interrupted, retry the identical payload with the same `--request-id`; the recorded event and push are idempotent. A changed payload under that ID is a conflict and must use a new ID only if it is genuinely a new checkpoint.

If `.continuity/documents.json` exists, every fresh session or task takeover/resumption must consult it before deciding the next action, not only before writing documentation. Run `git fetch origin`, then `continuity docs find "<issue title and task-objective terms>" --task <TASK-ID>`; read the returned matches and declared neighbors before deciding that prior work is missing or creating/replacing a document. The command compares indexed content with the cached `origin/HEAD` when that comparison is provable and labels changed records `NEEDS_REVIEW`. `REMOTE_UNKNOWN` is not proof of freshness. The inventory is canonical and `docs/CONTINUITY_INDEX.md` is generated; run `continuity docs render` after source changes, and use `continuity docs refresh <ID>` only after reviewing the changed source. This lookup is deterministic metadata search, not a semantic crawler.

If the remote itself is unavailable, use the degraded recovery-receipt path. That is an emergency continuity condition, not a successful normal handoff: record the exact local state, continue only when the task remains safe, and publish/reconcile as soon as the shared Git path is available again.

Delegated agents are temporary workers. Give each one a bounded task, capture its
result and evidence in the parent task, and close it immediately after the result
is captured. Completed, interrupted, failed, cancelled, or timed-out workers must
not be left open; stop and close workers that are no longer needed. Use the
smallest useful number of workers and do not treat an agent thread as canonical
project or task state. See `docs/AGENT_LIFECYCLE.md`.

Mention issue numbers where useful.