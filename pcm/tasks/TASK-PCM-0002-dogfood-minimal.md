# TASK-PCM-0002 — Dogfood v1 on a minimal repository

<!-- continuity:task {"acceptance":["a fresh minimal target repository can be initialized end-to-end with the PCM-0001 CLI","initialized minimal state validates deterministically","task creation allocates the configured prefix/id and produces a valid task file","checkpoint operation preserves existing task history and resulting state validates","context-pack generation records repository/ref/commit/protocol version/task/source files","deterministic end-to-end test coverage exercises init -> validate -> task new -> checkpoint -> pack -> validate","any core defect found while dogfooding is fixed only when required for this flow and is covered by a regression test","no GitHub/Beads adapter or external repository migration work is started","exact commands/results, decisions, blockers, changed paths, and one next action are checkpointed before stop"],"depends_on":["PCM-0001"],"goal":"Exercise Project Continuity Protocol v1 end-to-end on a freshly initialized minimal repository and capture/fix only core defects required for that flow.","id":"PCM-0002","next_action":"Run the minimal end-to-end dogfood flow: init -> validate -> task new -> checkpoint -> pack -> validate, then add deterministic regression coverage for any defect found.","owner":"ChatGPT/Sol current implementation session; GitHub assignee Pukujan","priority":"P0","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"PCM-0001 established the executable protocol; the next risk is whether the commands compose correctly in a fresh minimal repository rather than only in isolated fixtures/tests."} -->

- Status: active
- Owner: ChatGPT/Sol current implementation session; GitHub assignee Pukujan
- Priority: P0
- Depends on: PCM-0001
- Suggested branch: `task/PCM-0002-dogfood-minimal`
- GitHub issue: #3

## Goal

Exercise Project Continuity Protocol v1 end-to-end on a freshly initialized minimal repository and capture/fix only core defects required for that flow.

## Why

PCM-0001 established the executable protocol; the next risk is whether the commands compose correctly in a fresh minimal repository rather than only in isolated fixtures/tests.

## Allowed files

- `examples/minimal-dogfood/**`
- `tests/**`
- `src/continuity/**` only for defects demonstrated by the dogfood flow
- `schemas/v1/**` or `templates/v1/**` only if a demonstrated core invariant requires correction
- `README.md` / `SPEC.md` only if observed behavior requires documentation correction
- `tasks/TASK-PCM-0002-dogfood-minimal.md`
- `tasks/TASK-PCM-0001-bootstrap-v1.md` only for its final completion checkpoint/status
- `checkpoints/CURRENT.md`
- `HANDOFF.md`

Do not start GitHub/Beads adapters, external repository migrations, hosted services, or unrelated feature work.

## Acceptance criteria

- [ ] a fresh minimal target repository can be initialized end-to-end with the PCM-0001 CLI;
- [ ] initialized minimal state validates deterministically;
- [ ] task creation allocates the configured prefix/id and produces a valid task file;
- [ ] checkpoint operation preserves existing task history and resulting state validates;
- [ ] context-pack generation records repository/ref/commit/protocol version/task/source files;
- [ ] deterministic end-to-end test coverage exercises `init -> validate -> task new -> checkpoint -> pack -> validate`;
- [ ] any core defect found while dogfooding is fixed only when required for this flow and is covered by a regression test;
- [ ] no GitHub/Beads adapter or external repository migration work is started;
- [ ] exact commands/results, decisions, blockers, changed paths, and one next action are checkpointed before stop.

## Evidence expectations

Record the exact end-to-end commands and observed exit/results. Distinguish an observed CLI/test result from an inference. If a command exposes a core defect, record the failing command first, then the smallest fix and regression result.

## Checkpoint log

No checkpoints yet.

## Handoff

Fresh session: read PROJECT -> CURRENT -> this task -> SPEC. Work only PCM-0002. Before stopping, append exact evidence and one atomic next action here.
