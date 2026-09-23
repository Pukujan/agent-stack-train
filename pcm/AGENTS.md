# Agent Operating Contract

This repository dogfoods the continuity protocol it is building.

## Operating mode gate

Before reading task state, determine whether this repository is the **thing being developed** or only a **helper for another repository**.

- If the user points at PCM to help work on another repository, PCM is helper/tooling only. The other repository is the target and owns PROJECT, CURRENT, TASK, checkpoints, and project-specific operational state.
- Identify the target repository/root explicitly and run `continuity preflight --root <target>` before treating continuity as active.
- Do not create a new continuity repository for the target, do not write the target project's state into this repository, and do not use PCM's own CURRENT/TASK as the target's task state.
- A target is not PCM-integrated merely because it contains similarly named files. Integration is established only when the target passes `continuity validate --root <target>`.
- If a mature target already owns PROJECT/AGENTS/HANDOFF documentation, preserve those semantics and follow `docs/TARGET_ADOPTION.md` rather than replacing them.

Only when the task is to change Project Continuity Modules itself should the PCM read order below be used.

## Read order

Before doing work:

1. `PROJECT.md`
2. `checkpoints/CURRENT.md`
3. the active `tasks/TASK-*.md`
4. the minimum relevant document:
   - normative design: `SPEC.md`
   - handoffs: `docs/HANDOFF_PROTOCOL.md`
   - versioning/migrations: `docs/VERSIONING.md`

Do not scan historical chats for context by default.

## One task, one primary branch/session

Task IDs use `PCM-XXXX`.

Recommended branch format:

```text
task/PCM-0001-bootstrap-v1
```

One primary agent/session owns the writable task state at a time.

This is a lineage rule, not a permanent physical-worktree rule. A repository/task branch may be checked out in an authorized alternate worktree or host when execution needs to move. The Git repository, task ID, branch/ref, and commit history identify the work; a filesystem path does not.

## Checkpoint rule

Before stopping after meaningful work, append to the active task:

- completed work;
- evidence/commands/results;
- files changed;
- decisions;
- blockers/uncertainty;
- one exact next action.

Update `checkpoints/CURRENT.md` only when program-wide state or priority changes.

Continuity bookkeeping supports execution but does not gate safe execution. If a canonical task, CURRENT, or HANDOFF file is temporarily unavailable, do not repair storage merely to force a write, stop otherwise-safe authorized work, or ask again for an already-authorized host/worktree. Continue in the authorized alternate checkout and run `continuity checkpoint ... --recovery-root <alternate-root>` to leave a recovery receipt. Reconcile it later with `continuity recovery reconcile --root <canonical-root> --file <receipt>`. Recovery receipts are temporary evidence, not a competing project identity.

Normal checkpoint delivery is mandatory: commit the product change first, then run `continuity checkpoint`. The command commits the canonical checkpoint and pushes the task branch to `origin`; a normal checkpoint is not complete while it exists only in a local worktree. CI runs on every pushed branch, and pull-request automation merges after the required checks pass. Do not create a second branch or worktree identity to avoid publishing.

If the remote itself is unavailable, use the degraded recovery-receipt path. That is an emergency continuity condition, not a successful normal handoff: record the exact local state, continue only when the task remains safe, and publish/reconcile as soon as the shared Git path is available again.

## Evidence rule

Distinguish:
- observed command/test result;
- repository state;
- external artifact;
- agent/model claim;
- inference/assumption.

Never promote an unsupported previous-session statement into project fact.

## Scope rule

If the task expands materially, update/split the task before doing the expanded work.

## Self-hosting rule

Changes to the continuity protocol must be managed using the continuity protocol itself whenever practical. Protocol defects discovered while dogfooding should become explicit tasks/issues rather than silent conventions.
