# Handoff Protocol

## Goal

A fresh session should resume from repository state without needing the previous conversation.

## Canonical hierarchy

```text
PROJECT
  ↓
CURRENT
  ↓
TASK
  ↓
CHECKPOINTS
```

Issues/Beads/PRs mirror coordination. Context packs are generated views.

## Start-session procedure

1. read `PROJECT.md`;
2. read `checkpoints/CURRENT.md`;
3. open the active task;
4. read only the minimum relevant spec/design file;
5. confirm branch/scope before edits.

If delegated agents are used, read `docs/AGENT_LIFECYCLE.md` as part of the
relevant handoff contract.

## Checkpoint format

Append, do not rewrite history:

```
### YYYY-MM-DD HH:MM UTC — <agent/session>

Completed:
- ...

Evidence:
- command/artifact -> observed result

Decisions:
- ...

Changed:
- ...

Blocked/uncertain:
- none | ...

Next:
- one atomic action
```

## Stop-session requirements

Before stopping:
- commit meaningful product work before checkpointing;
- run `continuity checkpoint`, which commits the checkpoint and pushes the task branch to `origin`;
- do not call a normal checkpoint complete while it exists only in a local worktree;
- if the remote is unavailable, use the degraded recovery-receipt path and record the exact local state;
- record tests/commands/results;
- record uncertainty rather than guessing;
- set one exact next action;
- update CURRENT only when repository-level state changed;
- link task ID to issue/PR/Beads item when used.

If an operation may be retried, preserve its printed checkpoint `REQUEST_ID`
and reuse it with the identical payload. PCM treats the same ID and content as
one event, rejects changed content under that ID, and preserves the first
timestamp.

## Degraded continuity

Execution safety and existing authorization outrank checkpoint bookkeeping. A temporary failure to read or write `PROJECT`, `CURRENT`, `TASK`, or `HANDOFF` state is a degraded continuity condition, not an independent reason to stop safe work.

Use an already-authorized alternate checkout or host when needed. Record the same task ID, repository identity, branch/ref, source commit, evidence, and next action in a recovery receipt with `continuity checkpoint --recovery-root <alternate-root>`. Do not repair storage merely to force a write, ask again for permission that already exists, treat a physical path as project identity, or create competing continuity state. Reconcile the receipt after the canonical checkout is writable with `continuity recovery reconcile`.

The Git repository, remote, task ID, branch/ref, and commit history define task identity; a local path does not. Keep one permanent main checkout as the project home base. Use it for sequential work. When isolation or parallel work is genuinely useful, create one managed linked worktree per independent active task under `<canonical-root>/pcm/worktree/<TASK-ID>`; do not create one per session/agent or create sibling clones. Reuse the same task worktree across sessions.

After the task's commits/checkpoints are pushed, required CI passes, its PR is merged, its task record is complete, and the worktree is clean, run `continuity worktree remove <TASK-ID>`. The command verifies the GitHub PR, required checks, and merged commit, and refuses locked/pinned, dirty, or unproven cleanup; never force-remove unfinished or user-modified work. For a short audit hold, record the reason, expected release date, exact path, and unlock/remove next action in the completed task's checkpoint, then lock the tree with `git worktree lock --reason "<reason; release YYYY-MM-DD>" <path>`. A lock causes normal cleanup to refuse the tree; it does not replace the cleanup record. When the audit ends, return to the permanent checkout, run `git worktree unlock <path>`, then `continuity worktree remove <TASK-ID>` to finish normal verified cleanup ([Git documentation](https://git-scm.com/docs/git-worktree)). Until another host has a tested CI/merge verifier, cleanup for non-GitHub remotes fails closed and leaves the worktree intact. A worktree shares Git repository data, but mutable dependencies are not automatically shared: reuse safe package download/build caches, and keep environments separate when lockfiles or runtimes differ. Projects that require stricter disk minimization may select `workspace.mode: single-checkout`.

Normal checkpoints still need to be pushed; worktrees do not create a second project identity. If checkpoint storage is unavailable, use only an already-authorized alternate environment and the recovery-receipt path above, not a newly created worktree as a workaround.

When `.continuity/documents.json` exists, it owns the document catalog;
`docs/CONTINUITY_INDEX.md` is a generated human view. On every fresh session or
task takeover/resumption, before deciding the next action, fetch `origin` and
run `continuity docs find "<issue title and task-objective terms>" --task
<TASK-ID>`. Read the matching records and their declared neighbors before
concluding that prior work is missing or creating/recreating documentation.
The command reads cached remote-tracking state and does not fetch. Treat
`NEEDS_REVIEW` as targeted staleness and `REMOTE_UNKNOWN` as unverified, not
current. After inspecting a source change, refresh its explicit review hash and
regenerate the human view. Context packs include task-associated records and
declared neighbors only; their Git commit/blob/hash provenance identifies
exactly what was read.

## Delegated-agent cleanup

Delegated agents are temporary workers. Before the parent session moves on, it
must capture each worker's result in the parent task/checkpoint and explicitly
close the worker. A terminal `completed` status is not enough: an open completed
worker still consumes an agent slot. Stop and close workers that are no longer
needed, including workers that fail, are interrupted, cancelled, or time out.

## Context packs

A context pack may concatenate/transform canonical state for convenience, but must identify:
- repository;
- ref/branch;
- commit;
- protocol version;
- task ID;
- generation time;
- source file list.

Never update a context pack instead of canonical state.
