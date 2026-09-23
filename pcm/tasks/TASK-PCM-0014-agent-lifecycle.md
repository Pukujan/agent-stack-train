# TASK-PCM-0014 — Close completed delegated agents and bound concurrency

<!-- continuity:task {"acceptance":["delegated-agent lifecycle is normative in the PCM specification and operating guidance","completed, interrupted, failed, cancelled, and timed-out workers all require parent capture followed by explicit close","generated minimal and software guidance carries the cleanup rule","deterministic policy tests prevent the close-after-result rule from disappearing","issue #24 and the final evidence are recorded without modifying unrelated repositories","full lint, type, compilation, test, package, and continuity validation pass"],"depends_on":["PCM-0013"],"goal":"Prevent finished delegated agents from remaining open and consuming concurrency slots after their work is complete.","id":"PCM-0014","next_action":"Run the full automated release gate, push, and allow protected CI to merge.","owner":"Codex current PCM policy implementation session; GitHub issue #24","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Open completed agents remain visible and can count toward the concurrency limit. PCM needs an explicit capture, checkpoint, and close lifecycle for every delegated worker."} -->

- Status: active
- Owner: Codex current PCM policy implementation session; GitHub issue #24
- Priority: P1
- Depends on: PCM-0010
- GitHub issue: #24
- Suggested branch: `task/PCM-0014-agent-lifecycle`

## Goal

Prevent finished delegated agents from remaining open and consuming concurrency
slots after their work is complete.

## Allowed files

- `AGENTS.md`
- `README.md`
- `SPEC.md`
- `docs/AGENT_LIFECYCLE.md`
- `docs/HANDOFF_PROTOCOL.md`
- `templates/**`
- `tests/test_agent_lifecycle_policy.py`
- this task and `checkpoints/CURRENT.md`

Do not modify Hades v2, Eval Lab, harness-on-steroids,
inference-recommendation-engine, or any unrelated target repository.

## Acceptance criteria

- [x] delegated-agent lifecycle is normative in the PCM specification and operating guidance;
- [x] completed, interrupted, failed, cancelled, and timed-out workers all require parent capture followed by explicit close;
- [x] generated minimal and software guidance carries the cleanup rule;
- [x] deterministic policy tests prevent the close-after-result rule from disappearing;
- [x] issue #24 and the final evidence are recorded without modifying unrelated repositories;
- [ ] full lint, type, compilation, test, package, and continuity validation pass.

## Checkpoint log

### 2026-09-23 06:00 UTC — Codex PCM-0014 policy implementation

Completed:

- Added the canonical delegated-agent lifecycle policy.
- Added normative references in the specification, operating contract, handoff protocol, README, and generated profiles.
- Added deterministic policy tests for capture-then-close guidance and lifecycle coverage.
- Closed the completed blind-test worker from this PCM session after capturing its result.

Evidence:

- Official ChatGPT guidance states that completed subagents remain available until explicitly closed and documents the close operation.
- GitHub issue #24 records the durable policy and acceptance criteria.

Decisions:

- Agent threads are temporary execution infrastructure; the parent task/checkpoint is canonical.
- No unrelated target repository, including Hades v2, is modified.

Changed:

- `AGENTS.md`
- `README.md`
- `SPEC.md`
- `docs/AGENT_LIFECYCLE.md`
- `docs/HANDOFF_PROTOCOL.md`
- `templates/v1/minimal/HANDOFF.md`
- `templates/v1/software/AGENTS.md`
- `tests/test_agent_lifecycle_policy.py`
- this task

Blocked/uncertain:

- Hosted CI and automatic merge remain to be verified.

Next:

- Run the full automated release gate, push, and allow protected CI to merge.

### 2026-09-23 13:34:48 UTC — Codex PCM-0014 agent lifecycle policy

<!-- continuity:checkpoint {"agent":"Codex PCM-0014 agent lifecycle policy","blocked":[],"changed":["AGENTS.md; HANDOFF.md; README.md; SPEC.md; checkpoints/CURRENT.md; docs/AGENT_LIFECYCLE.md; docs/HANDOFF_PROTOCOL.md; templates/v1/minimal/HANDOFF.md; templates/v1/software/AGENTS.md; tasks/TASK-PCM-0014-agent-lifecycle.md; tests/test_agent_lifecycle_policy.py"],"completed":["Added normative delegated-agent lifecycle policy requiring parent capture followed by explicit close.","Added guidance to AGENTS.md, SPEC.md, README.md, handoff protocol, and generated minimal/software profiles.","Added deterministic policy tests covering capture-then-close and terminal-state cleanup guidance.","Closed the completed blind-test subagent after capturing its result."],"decisions":["Agent threads are temporary execution infrastructure; the parent task/checkpoint and pushed Git branch remain canonical.","Do not modify Hades v2 or any unrelated target repository."],"evidence":["ruff check . -> All checks passed.","mypy src -> Success: no issues found in 3 source files.","python -m compileall -q src tests -> exit 0.","PYTHONPATH=src python -m unittest discover -s tests -q -> 16 tests passed.","PYTHONPATH=src python -m continuity validate --root . -> VALID.","python -m build -> project_continuity-0.2.0 sdist and wheel built successfully.","GitHub issue #24 -> durable policy request and acceptance criteria."],"next_action":"Verify protected CI and allow automatic merge of the pushed task branch.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0014","timestamp":"2026-09-23T13:34:48Z"} -->

Completed:
- Added normative delegated-agent lifecycle policy requiring parent capture followed by explicit close.
- Added guidance to AGENTS.md, SPEC.md, README.md, handoff protocol, and generated minimal/software profiles.
- Added deterministic policy tests covering capture-then-close and terminal-state cleanup guidance.
- Closed the completed blind-test subagent after capturing its result.

Evidence:
- ruff check . -> All checks passed.
- mypy src -> Success: no issues found in 3 source files.
- python -m compileall -q src tests -> exit 0.
- PYTHONPATH=src python -m unittest discover -s tests -q -> 16 tests passed.
- PYTHONPATH=src python -m continuity validate --root . -> VALID.
- python -m build -> project_continuity-0.2.0 sdist and wheel built successfully.
- GitHub issue #24 -> durable policy request and acceptance criteria.

Decisions:
- Agent threads are temporary execution infrastructure; the parent task/checkpoint and pushed Git branch remain canonical.
- Do not modify Hades v2 or any unrelated target repository.

Changed:
- AGENTS.md; HANDOFF.md; README.md; SPEC.md; checkpoints/CURRENT.md; docs/AGENT_LIFECYCLE.md; docs/HANDOFF_PROTOCOL.md; templates/v1/minimal/HANDOFF.md; templates/v1/software/AGENTS.md; tasks/TASK-PCM-0012-agent-lifecycle.md; tests/test_agent_lifecycle_policy.py

Blocked/uncertain:
- none

Next:
- Verify protected CI and allow automatic merge of the pushed task branch.
