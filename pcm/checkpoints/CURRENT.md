# Current Repository Checkpoint

<!-- continuity:current {"active_task":"PCM-0003","active_task_file":"tasks/TASK-PCM-0003-adopt-custom-extensions.md","protocol_version":"0.1.0-draft","schema":"project-continuity.current.v1"} -->

## Program state

Phase: adoption — prove v1 in mature repositories.

Current P0 task: `TASK-PCM-0003-adopt-custom-extensions.md` / GitHub issue #5 / branch `task/PCM-0003-adopt-custom-extensions`.

## Main objective

Adopt the validated continuity protocol in existing repositories without erasing their domain-specific project contracts or handoff semantics.

## Completed

- PCM-0001 — executable v1 schemas/templates/CLI/validator/bootstrap merged;
- PCM-0002 — fresh minimal end-to-end dogfood merged; 8-test suite passed and final validation was VALID.

## Active

- PCM-0003 — adopt continuity v1 in `Pukujan/custom-extensions`.

## Queued

1. PCM-0004 — migrate/adopt in `Pukujan/Eval-lab`.
2. PCM-0005 — GitHub Issue adapter and bidirectional consistency checks.
3. PCM-0006 — optional Beads adapter.
4. PCM-0007 — protocol v1.0 release/migration contract.

## Blockers

None known.

## Next atomic action

Create a dedicated adoption branch in `Pukujan/custom-extensions`, add the non-destructive continuity overlay, validate it with the PCM v1 validator, and merge only after all available target-repository gates pass.
