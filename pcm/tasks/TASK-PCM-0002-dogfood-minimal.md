# TASK-PCM-0002 — Dogfood v1 on a minimal repository

<!-- continuity:task {"acceptance":["a fresh minimal target repository can be initialized end-to-end with the PCM-0001 CLI","initialized minimal state validates deterministically","task creation allocates the configured prefix/id and produces a valid task file","checkpoint operation preserves existing task history and resulting state validates","context-pack generation records repository/ref/commit/protocol version/task/source files","deterministic end-to-end test coverage exercises init -> validate -> task new -> checkpoint -> pack -> validate","any core defect found while dogfooding is fixed only when required for this flow and is covered by a regression test","no GitHub/Beads adapter or external repository migration work is started","exact commands/results, decisions, blockers, changed paths, and one next action are checkpointed before stop"],"depends_on":["PCM-0001"],"goal":"Exercise Project Continuity Protocol v1 end-to-end on a freshly initialized minimal repository and capture/fix only core defects required for that flow.","id":"PCM-0002","next_action":"Review and merge task/PCM-0002-dogfood-minimal; after merge, activate PCM-0003.","owner":"ChatGPT/Sol current implementation session; GitHub assignee Pukujan","priority":"P0","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"PCM-0001 established the executable protocol; the next risk is whether the commands compose correctly in a fresh minimal repository rather than only in isolated fixtures/tests."} -->

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

- [x] a fresh minimal target repository can be initialized end-to-end with the PCM-0001 CLI;
- [x] initialized minimal state validates deterministically;
- [x] task creation allocates the configured prefix/id and produces a valid task file;
- [x] checkpoint operation preserves existing task history and resulting state validates;
- [x] context-pack generation records repository/ref/commit/protocol version/task/source files;
- [x] deterministic end-to-end test coverage exercises `init -> validate -> task new -> checkpoint -> pack -> validate`;
- [x] any core defect found while dogfooding is fixed only when required for this flow and is covered by a regression test;
- [x] no GitHub/Beads adapter or external repository migration work is started;
- [x] exact commands/results, decisions, blockers, changed paths, and one next action are checkpointed before stop.

## Evidence expectations

Record the exact end-to-end commands and observed exit/results. Distinguish an observed CLI/test result from an inference. If a command exposes a core defect, record the failing command first, then the smallest fix and regression result.

## Checkpoint log

No checkpoints yet.

### 2026-09-20 18:31:00 UTC — ChatGPT/Sol PCM-0002 dogfood

<!-- continuity:checkpoint {"agent":"ChatGPT/Sol PCM-0002 dogfood","blocked":[],"changed":["tasks/TASK-PCM-0001-bootstrap-v1.md","tasks/TASK-PCM-0002-dogfood-minimal.md","checkpoints/CURRENT.md","HANDOFF.md","tests/test_cli.py","examples/minimal-dogfood/README.md"],"completed":["Activated PCM-0002 after PCM-0001 merge and closed PCM-0001 canonically.","Ran the v1 minimal lifecycle end to end on a fresh target repository.","Added deterministic end-to-end regression coverage and durable dogfood documentation."],"decisions":["No core CLI/schema/template defect was observed, so PCM-0002 makes no runtime/schema/template change.","Use the byte-identical merged PCM-0001 source as the local executable harness while GitHub remains canonical for project/task state.","Do not start adapters or external repository migrations in PCM-0002."],"evidence":["git hash-object local harness src/continuity/cli.py -> 3ed02d41bf71be2651e35e86151254573353ffa4, matching the merged repository blob.","continuity init --profile minimal --task-prefix DOG -> created config, PROJECT, CURRENT, HANDOFF, and six v1 schemas.","continuity validate after init -> VALID; after task new -> VALID; after checkpoint -> VALID; after pack -> VALID.","continuity task new -> tasks/TASK-DOG-0001-first-dogfood-task.md.","checkpoint preservation probe -> prior-history-preserved=True; checkpoint-marker-count=1.","dogfood Git source commit -> 636f39cd2380f0cf035a97bb92f3b0a57b569890; context-pack marker recorded repository/ref/commit/protocol/task/sources.","PYTHONPATH=src python -S -m unittest discover -s tests -v -> 8 tests ran; OK.","PCM-0002 branch-state mirror: PYTHONPATH=src python -S -m continuity validate --root . -> VALID."],"next_action":"Review and merge task/PCM-0002-dogfood-minimal; after merge, activate PCM-0003.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0002","timestamp":"2026-09-20T18:31:00Z"} -->

Completed:
- Activated PCM-0002 after PCM-0001 merge and closed PCM-0001 canonically.
- Ran the v1 minimal lifecycle end to end on a fresh target repository.
- Added deterministic end-to-end regression coverage and durable dogfood documentation.

Evidence:
- `git hash-object src/continuity/cli.py` on the executable harness -> `3ed02d41bf71be2651e35e86151254573353ffa4`, matching the merged repository blob.
- `continuity init --profile minimal --task-prefix DOG` -> created config, PROJECT, CURRENT, HANDOFF, and six v1 schemas.
- `continuity validate` after init -> `VALID`; after task new -> `VALID`; after checkpoint -> `VALID`; after pack -> `VALID`.
- `continuity task new` -> `tasks/TASK-DOG-0001-first-dogfood-task.md`.
- checkpoint preservation probe -> `prior-history-preserved=True`; `checkpoint-marker-count=1`.
- dogfood Git source commit -> `636f39cd2380f0cf035a97bb92f3b0a57b569890`; context-pack marker recorded repository/ref/commit/protocol/task/sources.
- `PYTHONPATH=src python -S -m unittest discover -s tests -v` -> 8 tests ran; `OK`.
- PCM-0002 branch-state mirror: `PYTHONPATH=src python -S -m continuity validate --root .` -> `VALID`.

Decisions:
- No core CLI/schema/template defect was observed, so PCM-0002 makes no runtime/schema/template change.
- Use the byte-identical merged PCM-0001 source as the local executable harness while GitHub remains canonical for project/task state.
- Do not start adapters or external repository migrations in PCM-0002.

Changed:
- tasks/TASK-PCM-0001-bootstrap-v1.md
- tasks/TASK-PCM-0002-dogfood-minimal.md
- checkpoints/CURRENT.md
- HANDOFF.md
- tests/test_cli.py
- examples/minimal-dogfood/README.md

Blocked/uncertain:
- none

Next:
- Review and merge `task/PCM-0002-dogfood-minimal`; after merge, activate PCM-0003.

## Handoff

Fresh session: read PROJECT -> CURRENT -> this task -> SPEC. Work only PCM-0002. Before stopping, append exact evidence and one atomic next action here.
