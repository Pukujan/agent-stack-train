# Project Continuity Modules — Project Contract

<!-- continuity:project {"id":"project-continuity-modules","protocol_version":"0.1.0-draft","schema":"project-continuity.project.v1","title":"Project Continuity Modules"} -->

## Main goal

Build a reusable, versioned project-continuity protocol and toolkit that lets a fresh AI or human session enter any participating repository and recover the project's purpose, current state, bounded task, evidence, blockers, and exact next action without needing prior conversation history.

## Why

Long-running AI-assisted projects accumulate context across many sessions and agents. Relying on a single conversation creates context rot, hidden state, poor handoffs, duplicated work, and unverifiable claims about what previous agents did.

The project should turn continuity into a repository invariant rather than a prompt-writing habit.

## Core model

GitHub owns durable project task/progression state. Repository documents are mandatory versioned projections for task fields; merged history owns accepted code and normative/domain contracts:

1. `PROJECT` — stable purpose, scope, principles, phases.
2. `CURRENT` — repository/program-wide present state and priority.
3. `TASK` — one bounded unit of work for one primary agent/session.
4. `CHECKPOINT` — append-only evidence of completed work, tests, decisions, blockers, and next action.
5. `GITHUB ISSUE` — required authority for scope, acceptance, priority, ownership, dependencies, lifecycle and progression; PR/check/merge records own delivery facts.
6. `CONTEXT PACK` — generated convenience view, never canonical.

## Design principles

- cold-startable from live GitHub issues and synchronized repository projections;
- human- and agent-readable;
- machine-validatable;
- versioned and migratable;
- independent of any one model/vendor;
- Git-native;
- evidence-aware;
- minimal enough for small projects but extensible through profiles;
- context packs derived from canonical state, never replacing it;
- GitHub is authoritative for task lifecycle in PCM-governed GitHub repositories; host-specific adapter tooling remains modular;
- project protocol must be able to manage its own development.

## v1 target capabilities

- normative protocol specification;
- machine-readable schemas;
- templates/profiles;
- `continuity init`;
- `continuity validate`;
- `continuity task new`;
- `continuity checkpoint`;
- `continuity pack`;
- required GitHub issue tracking and manual push/merge receipts; runtime receipt automation remains separate;
- migration/versioning conventions;
- deterministic tests;
- examples/dogfooding.

## Initial profiles

- minimal;
- software;
- research;
- browser-extension.

## Non-goals for v1

- replacing Git;
- becoming a full project-management SaaS;
- requiring a hosted server;
- making LLM-generated summaries canonical;
- making Beads/Jira, a graph database, local canonical ledger or polling agent required; GitHub is required for governed project work;
- encoding every domain's workflow in one universal schema;
- treating previous-agent prose as evidence without supporting results.

## Definition of success for v1

Following the bounded authority and finite publication rules in SPEC section 8, a fresh repository can be initialized with the protocol, validated deterministically, assigned a bounded task, checkpointed by multiple independent sessions, and resumed by another session using PROJECT + CURRENT + TASK + one relevant spec/context pack without reading historical chats.

Every pushed increment synchronizes applicable docs and records leaf/parent/dependency lineage on GitHub. Required CI and GitHub auto-merge are mandatory; failed or unverified gates prohibit completion/cleanup. Local execution state is never delivered state. See [SPEC section 8](SPEC.md#8-authority) for owner-direction conflicts, shared writers, evidence corrections and downstream re-planning.
