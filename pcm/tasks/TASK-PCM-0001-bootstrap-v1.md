# TASK-PCM-0001 — Bootstrap Project Continuity Protocol v1

- Status: active
- Owner: next implementation agent
- Priority: P0
- Depends on: none
- Suggested branch: `task/PCM-0001-bootstrap-v1`
- GitHub issue: to be linked after creation

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

- [ ] protocol v1 draft schema locations/names established;
- [ ] schemas cover config/project/current/task/checkpoint/context-pack metadata or an explicitly justified equivalent;
- [ ] versioned templates exist for at least minimal + software profiles;
- [ ] target repository can be initialized without overwriting existing user content silently;
- [ ] deterministic `validate` command identifies missing/invalid canonical state;
- [ ] validator checks active-task references and core required fields;
- [ ] task creation produces stable IDs/files from configured prefix;
- [ ] checkpoint operation appends rather than rewrites history;
- [ ] context-pack generation records repo/ref/commit/protocol version/source files;
- [ ] tests include valid fixtures and intentionally broken repositories;
- [ ] this repository itself passes its own validator;
- [ ] README contains a concise “point a new agent here” workflow;
- [ ] exact commands/results and next action are checkpointed before stop.

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

## Handoff

Fresh session: read PROJECT → CURRENT → this task → SPEC. Implement only PCM-0001. Before stopping, append exact evidence and one atomic next action here.
