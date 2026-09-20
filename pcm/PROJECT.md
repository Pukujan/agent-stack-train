# Project Continuity Modules — Project Contract

## Main goal

Build a reusable, versioned project-continuity protocol and toolkit that lets a fresh AI or human session enter any participating repository and recover the project's purpose, current state, bounded task, evidence, blockers, and exact next action without needing prior conversation history.

## Why

Long-running AI-assisted projects accumulate context across many sessions and agents. Relying on a single conversation creates context rot, hidden state, poor handoffs, duplicated work, and unverifiable claims about what previous agents did.

The project should turn continuity into a repository invariant rather than a prompt-writing habit.

## Core model

Canonical continuity state is layered:

1. `PROJECT` — stable purpose, scope, principles, phases.
2. `CURRENT` — repository/program-wide present state and priority.
3. `TASK` — one bounded unit of work for one primary agent/session.
4. `CHECKPOINT` — append-only evidence of completed work, tests, decisions, blockers, and next action.
5. `ISSUE/BEADS/PR` — coordination mirrors, not sole authority.
6. `CONTEXT PACK` — generated convenience view, never canonical.

## Design principles

- cold-startable from repository state;
- human- and agent-readable;
- machine-validatable;
- versioned and migratable;
- independent of any one model/vendor;
- Git-native;
- evidence-aware;
- minimal enough for small projects but extensible through profiles;
- context packs derived from canonical state, never replacing it;
- issue trackers/adapters optional;
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
- optional GitHub Issue adapter;
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
- forcing GitHub/Beads/Jira as a dependency;
- encoding every domain's workflow in one universal schema;
- treating previous-agent prose as evidence without supporting results.

## Definition of success for v1

A fresh repository can be initialized with the protocol, validated deterministically, assigned a bounded task, checkpointed by multiple independent sessions, and resumed by another session using PROJECT + CURRENT + TASK + one relevant spec/context pack without reading historical chats.
