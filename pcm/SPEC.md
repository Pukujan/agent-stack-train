# Project Continuity Protocol — Draft v1 Specification

Status: bootstrap draft.

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

## 3. Required invariants

A continuity-compliant repository must allow deterministic validation of at least:

- protocol version is declared;
- PROJECT exists;
- CURRENT exists;
- CURRENT names zero or one primary active task;
- named active task exists;
- task ID/status/goal/why/acceptance/next-action fields exist;
- task dependencies reference valid task IDs or documented externals;
- append-only checkpoint structure is valid;
- completed tasks are not marked active;
- context packs identify their source commit/ref and are treated as derived;
- no secret material is required inside continuity state;
- tracker references are optional and cannot be the only copy of task context.

## 4. Session lifecycle

### Start
Read PROJECT → CURRENT → active TASK → minimum relevant spec.

### Work
Operate only within task scope or revise/split task first.

### Checkpoint
Record observed evidence, decisions, changes, uncertainty, next action.

### Stop/handoff
Ensure state is committed or dirty state is explicitly recorded, tests/evidence are captured, blockers are named, and next action is singular/unambiguous.

## 5. Versioning

Projects declare a protocol version. Backward-compatible optional additions are minor versions; incompatible required-state changes are major versions. Migration tooling is planned.

## 6. Profiles

Profiles may add requirements but cannot weaken core invariants.

Planned profiles:
- minimal;
- software;
- research;
- browser-extension.

## 7. Authority

Canonical repository files are authoritative for project continuity. Generated context packs and chat summaries are derived. External trackers are coordination mirrors.

## 8. Evidence semantics

Continuity records should prefer claims tied to evidence. Validators may check structure but do not decide whether a model's semantic claim is true.

## 9. v1 implementation target

The first implementation should provide:
- schemas;
- templates;
- validator;
- init/bootstrap;
- task creation;
- checkpoint append;
- context-pack generation;
- GitHub adapter;
- tests/examples.
