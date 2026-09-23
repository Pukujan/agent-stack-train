# Project Continuity Protocol — Draft v1 Specification

Status: executable bootstrap draft (`0.1.0-draft`).

## 1. Purpose

The protocol defines the minimum durable state required for a repository to be resumed by a fresh agent/session without relying on private conversation history.

## 2. Canonical objects

### PROJECT
Stable contract: goal, why, scope/non-goals, principles, phases, success criteria.

### CURRENT
Repository-wide checkpoint: phase, active priority/task, completed/active/queued work, blockers, exact next action.

### TASK
Bounded execution contract: ID, status, owner, priority, dependencies, goal, why, allowed scope, acceptance criteria, commands/evidence expectations, append-only checkpoints, handoff.

### CHECKPOINT
Append-only observation of state transition with:
- time/agent;
- completed;
- evidence;
- decisions;
- changed paths;
- blocked/uncertain;
- next atomic action.

### CONTEXT PACK
Generated view derived from canonical objects and tagged with repository/ref/commit/protocol version/source list.

### TRACKER MIRROR
Optional Issue/Beads/PR representation linked by the same task ID. It is not canonical unless a profile explicitly says otherwise.

## 3. v1 machine-readable shape

The declared protocol remains Git-readable Markdown plus JSON configuration. Canonical Markdown files include one single-line JSON metadata marker:

```text
<!-- continuity:<kind> { ... } -->
```

The v1 JSON Schema draft 2020-12 contracts are:

- `schemas/v1/config.schema.json`
- `schemas/v1/project.schema.json`
- `schemas/v1/current.schema.json`
- `schemas/v1/task.schema.json`
- `schemas/v1/checkpoint.schema.json`
- `schemas/v1/context-pack.schema.json`

Profiles are versioned under `templates/v1/`. `software` extends the `minimal` profile with software-agent/readme conventions; profiles may add requirements but cannot weaken core invariants.

## 4. Required invariants

A continuity-compliant repository must allow deterministic validation of at least:

- protocol version is declared;
- PROJECT exists and has valid project metadata;
- CURRENT exists and has valid current metadata;
- CURRENT names zero or one primary active task;
- named active task exists and its file/reference agree;
- task ID/status/goal/why/acceptance/next-action fields exist;
- task dependencies reference valid task IDs or use an `external:` dependency identifier;
- checkpoint structure is valid; v1 checkpoint metadata is validated when present;
- completed tasks are not marked active;
- context packs identify source repository/ref/commit/protocol version/source files and are treated as derived;
- no secret material is required inside continuity state;
- tracker references are optional and cannot be the only copy of task context.

Pre-v1 checkpoint entries may lack the v1 metadata marker; validators preserve that history and require the legacy human sections rather than rewriting it.

## 5. Session lifecycle

### Start
Read PROJECT → CURRENT → active TASK → minimum relevant spec.

### Work
Operate only within task scope or revise/split task first.

### Checkpoint
Record observed evidence, decisions, changes, uncertainty, next action.

### Stop/handoff
Ensure state is committed or dirty state is explicitly recorded, tests/evidence are captured, blockers are named, and next action is singular/unambiguous.

### Degraded continuity
Execution safety and existing authorization outrank continuity bookkeeping. Failure to read or write canonical continuity state is a degraded condition, not an execution gate, when the underlying task remains safe and recoverable. Continue in an already-authorized alternate checkout or host, write a recovery receipt containing the same repository/task lineage and checkpoint evidence, and reconcile it into canonical state when writable.

The authoritative identity is the repository/task lineage (project identity, task ID, branch/ref, remote, and Git history), not a physical path or machine. All projects use serial task branches in one canonical folder and prohibit task clones, task folders, linked Git worktrees, and additional dependency environments. The configuration key `workspace_mode` is unsupported; validators must reject it with a migration instruction and must not rewrite the user's configuration. A normal checkpoint MUST commit and push the task branch to the configured remote; a local-only checkpoint is not a durable handoff. If the remote is temporarily unavailable, use authorized degraded recovery evidence and restore the pushed handoff as soon as possible rather than inventing a second identity.

## 6. CLI behavior

`continuity init` materializes v1 schemas and profile files. It performs a full conflict preflight and never silently overwrites different existing content.

`continuity validate` is deterministic and requires no LLM. It returns success only when core v1 structural invariants hold.

`continuity task new` allocates the next four-digit task ID from the configured prefix and writes one bounded task file.

`continuity checkpoint` adds a checkpoint entry without deleting or replacing prior checkpoint history, then commits and pushes it to the task branch. It must fail visibly if the normal push cannot be completed.

`continuity checkpoint --recovery-root <alternate>` preserves a minimal recovery receipt in an authorized alternate checkout when canonical checkpoint state is temporarily unavailable. `continuity recovery reconcile` appends that receipt to the canonical task once it is writable.

`continuity pack` creates a derived Markdown view with repository/ref/commit/protocol/task/generation/source metadata.

## 7. Versioning

Projects declare a protocol version in `.continuity/config.json`. Backward-compatible optional additions are minor versions; incompatible required-state changes are major versions. Migrations must preserve historical checkpoint evidence.

## 8. Authority

Canonical repository files are authoritative for project continuity. Generated context packs and chat summaries are derived. External trackers are coordination mirrors.

## 9. Evidence semantics

Continuity records should prefer claims tied to evidence. Validators check structure and references but do not decide whether a human/model semantic claim is true.

## 10. v1 implementation boundary

PCM-0001 covers schemas, minimal/software templates, deterministic validator, init/bootstrap, task creation, checkpoint append, context-pack generation, tests, and self-dogfooding. GitHub/Beads synchronization adapters are deferred to later tasks.
