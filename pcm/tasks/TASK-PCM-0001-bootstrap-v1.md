# TASK-PCM-0001 — Bootstrap Project Continuity Protocol v1

<!-- continuity:task {"acceptance":["protocol v1 draft schema locations/names established","schemas cover config/project/current/task/checkpoint/context-pack metadata","versioned templates exist for minimal and software profiles","target repository can be initialized without silently overwriting existing user content","deterministic validate identifies missing/invalid canonical state","validator checks active-task references and core required fields","task creation produces stable IDs/files from configured prefix","checkpoint operation appends rather than rewrites history","context-pack generation records repo/ref/commit/protocol version/source files","tests include valid fixtures and intentionally broken repositories","this repository itself passes its own validator","README contains a concise point-a-new-agent-here workflow","exact commands/results and next action are checkpointed before stop"],"depends_on":[],"goal":"Create the first executable continuity protocol: versioned schemas + templates + deterministic validation + bootstrap/init for a target repository, while dogfooding the protocol in this repository.","id":"PCM-0001","next_action":"Review and merge task/PCM-0001-bootstrap-v1; after merge, activate PCM-0002 without starting adapter work.","owner":"ChatGPT/Sol (current implementation session; GitHub assignee Pukujan)","priority":"P0","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"The current continuity method works manually but still depends on a user telling each new agent how to recreate PROJECT/CURRENT/TASK/handoff/context-pack structure. PCM-0001 turns that convention into reusable infrastructure."} -->

- Status: active
- Owner: ChatGPT/Sol (current implementation session; GitHub assignee Pukujan)
- Priority: P0
- Depends on: none
- Suggested branch: `task/PCM-0001-bootstrap-v1`
- GitHub issue: #1

## Goal

Create the first executable continuity protocol: versioned schemas + templates + deterministic validation + bootstrap/init for a target repository, while dogfooding the protocol in this repository.

## Why

The current continuity method works manually but still depends on a user telling each new agent how to recreate PROJECT/CURRENT/TASK/handoff/context-pack structure. PCM-0001 turns that convention into reusable infrastructure.

## Allowed files

- `README.md`
- `PROJECT.md`
- `AGENTS.md`
- `SPEC.md`
- `.continuity/**`
- `schemas/**`
- `templates/**`
- `src/**`
- `tests/**`
- `examples/**`
- `docs/**`
- `tasks/TASK-PCM-0001-bootstrap-v1.md`
- `checkpoints/CURRENT.md`
- packaging/config files required for the chosen implementation

Do not add unrelated hosted services or project-management features.

## Acceptance criteria

- [x] protocol v1 draft schema locations/names established;
- [x] schemas cover config/project/current/task/checkpoint/context-pack metadata;
- [x] versioned templates exist for at least minimal + software profiles;
- [x] target repository can be initialized without overwriting existing user content silently;
- [x] deterministic `validate` command identifies missing/invalid canonical state;
- [x] validator checks active-task references and core required fields;
- [x] task creation produces stable IDs/files from configured prefix;
- [x] checkpoint operation appends rather than rewrites history;
- [x] context-pack generation records repo/ref/commit/protocol version/source files;
- [x] tests include valid fixtures and intentionally broken repositories;
- [x] this repository itself passes its own validator;
- [x] README contains a concise “point a new agent here” workflow;
- [x] exact commands/results and next action are checkpointed before stop.

## Design constraints

- canonical project state remains Git-readable text/files;
- machine-readable metadata may accompany Markdown but must not make human inspection impossible;
- generated context packs are derived and disposable;
- GitHub/Beads adapters are optional integrations, not core dependencies;
- no LLM is required for deterministic validation;
- protocol versions/migrations must be explicit.

## Evidence expectations

Record:
- chosen implementation language and rationale;
- schema validation strategy;
- init behavior on existing/non-empty repos;
- validator command/results;
- self-validation result;
- fixture test results.

## Checkpoint log

### 2026-09-20 — ChatGPT/Sol bootstrap

Completed:
- created project contract, draft spec, AGENTS contract, continuity config, current checkpoint, handoff/versioning docs, and this bounded task;
- separated canonical repository state from issue/Beads/context-pack mirrors;
- established self-hosting requirement.

Evidence:
- repository was empty before bootstrap;
- project state now lives on default branch so a fresh session can start from the repository alone.

Decisions:
- build a protocol/toolkit, not merely copy Markdown templates;
- make deterministic validation central;
- defer GitHub/Beads adapters until core schemas/bootstrap/validation exist;
- use the repo itself as the first dogfood target.

Blocked/uncertain:
- implementation language/package layout remains for the next task owner to decide and document.

Next:
- create v1 schema/template layout and smallest validator/init CLI with tests.

### 2026-09-20 17:47:53 UTC — ChatGPT/Sol implementation session

<!-- continuity:checkpoint {"agent":"ChatGPT/Sol implementation session","blocked":[],"changed":[".continuity/config.json; PROJECT.md; README.md; SPEC.md; HANDOFF.md; checkpoints/CURRENT.md; docs/VERSIONING.md; tasks/TASK-PCM-0001-bootstrap-v1.md.","pyproject.toml; src/continuity/**; schemas/v1/**; templates/v1/**; tests/**."],"completed":["Established v1 JSON Schema contracts for config/project/current/task/checkpoint/context-pack metadata.","Added versioned minimal and software profile templates plus a dependency-free Python 3.11+ CLI for init, validate, task new, checkpoint, and pack.","Added valid and intentionally broken fixtures and dogfooded validation on this repository worktree."],"decisions":["Use Python 3.11+ standard library only so bootstrap validation/init has no runtime dependency or LLM requirement.","Use JSON Schema draft 2020-12 as the machine-readable v1 contract and embedded single-line JSON metadata comments in canonical Markdown to preserve direct human readability.","continuity init performs conflict preflight and writes nothing when any planned path contains different existing user content; unrelated non-empty repository content is preserved.","Preserve pre-v1 checkpoint history without rewriting it; validate legacy human sections and validate v1 checkpoint metadata when present."],"evidence":["PYTHONPATH=src python -S -m unittest discover -s tests -v -> 7 tests ran; OK.","PYTHONPATH=src python -S -m continuity validate --root . -> VALID.","PYTHONPATH=src python -S -m continuity validate --root tests/fixtures/valid-minimal -> VALID.","PYTHONPATH=src python -S -m continuity validate --root tests/fixtures/broken-missing-current -> INVALID: 1 error; exit 1; missing canonical CURRENT as expected."],"next_action":"Review and merge task/PCM-0001-bootstrap-v1; after merge, activate PCM-0002 without starting adapter work.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0001","timestamp":"2026-09-20T17:47:53Z"} -->

Completed:
- Established v1 JSON Schema contracts for config/project/current/task/checkpoint/context-pack metadata.
- Added versioned minimal and software profile templates plus a dependency-free Python 3.11+ CLI for init, validate, task new, checkpoint, and pack.
- Added valid and intentionally broken fixtures and dogfooded validation on this repository worktree.

Evidence:
- PYTHONPATH=src python -S -m unittest discover -s tests -v -> 7 tests ran; OK.
- PYTHONPATH=src python -S -m continuity validate --root . -> VALID.
- PYTHONPATH=src python -S -m continuity validate --root tests/fixtures/valid-minimal -> VALID.
- PYTHONPATH=src python -S -m continuity validate --root tests/fixtures/broken-missing-current -> INVALID: 1 error; exit 1; missing canonical CURRENT as expected.

Decisions:
- Use Python 3.11+ standard library only so bootstrap validation/init has no runtime dependency or LLM requirement.
- Use JSON Schema draft 2020-12 as the machine-readable v1 contract and embedded single-line JSON metadata comments in canonical Markdown to preserve direct human readability.
- continuity init performs conflict preflight and writes nothing when any planned path contains different existing user content; unrelated non-empty repository content is preserved.
- Preserve pre-v1 checkpoint history without rewriting it; validate legacy human sections and validate v1 checkpoint metadata when present.

Changed:
- .continuity/config.json; PROJECT.md; README.md; SPEC.md; HANDOFF.md; checkpoints/CURRENT.md; docs/VERSIONING.md; tasks/TASK-PCM-0001-bootstrap-v1.md.
- pyproject.toml; src/continuity/**; schemas/v1/**; templates/v1/**; tests/**.

Blocked/uncertain:
- none

Next:
- Review and merge task/PCM-0001-bootstrap-v1; after merge, activate PCM-0002 without starting adapter work.

## Handoff

Fresh session: read PROJECT → CURRENT → this task → SPEC. Implement only PCM-0001. Before stopping, append exact evidence and one atomic next action here.
