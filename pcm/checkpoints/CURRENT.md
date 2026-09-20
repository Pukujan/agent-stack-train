# Current Repository Checkpoint

<!-- continuity:current {"active_task":"PCM-0001","active_task_file":"tasks/TASK-PCM-0001-bootstrap-v1.md","protocol_version":"0.1.0-draft","schema":"project-continuity.current.v1"} -->

## Program state

Phase: bootstrap — define and implement protocol v1.

Current P0 task: `TASK-PCM-0001-bootstrap-v1.md` / GitHub issue #1 / branch `task/PCM-0001-bootstrap-v1`.

## Main objective

Turn the continuity pattern proven in Eval Lab and the ChatGPT provenance-exporter project into a reusable, machine-validatable, versioned protocol/toolkit that another project can adopt without manually recreating the structure.

## Completed

- repository created;
- core project contract defined;
- draft v1 normative concepts written;
- self-hosting AGENTS/read-order established;
- protocol configuration introduced;
- handoff/versioning docs established;
- active bootstrap task prepared;
- PCM-0001 implementation completed on its task branch: v1 schemas/templates/CLI and fixture tests are present and self-validation passes in the tested worktree.

## Active

- PCM-0001: implementation complete on task branch; awaiting review/merge.

## Queued

1. PCM-0002 — dogfood v1 on a minimal fixture repository.
2. PCM-0003 — migrate/adopt in `Pukujan/custom-extensions`.
3. PCM-0004 — migrate/adopt in `Pukujan/Eval-lab`.
4. PCM-0005 — GitHub Issue adapter and bidirectional consistency checks.
5. PCM-0006 — optional Beads adapter.
6. PCM-0007 — protocol v1.0 release/migration contract.

## Blockers

None known.

## Next atomic action

Review and merge `task/PCM-0001-bootstrap-v1`; after merge, activate PCM-0002 without starting adapter work.
