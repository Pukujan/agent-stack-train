# Project Continuity Modules

Project Continuity Modules (PCM) is a Git-native continuity system for long-running work with AI agents.

It exists for a simple reason: **a project can last for months, but an agent session does not.**

## The problem PCM is trying to solve

Working with capable agents is easy when the task fits inside one conversation. Long-running projects are different.

Over time, important context gets spread across chat histories, local notes, branches, issue comments, generated summaries, and the memory of whichever person or agent was working last. Eventually the project starts depending on a particular session still being available and correctly remembered.

That creates a few recurring problems.

### Context rot

Long conversations gradually become poor project memory.

Early decisions fall out of the active context window. Summaries compress away details that later turn out to matter. Agents repeat work because they cannot see what was already tried. A new session may infer why something was done instead of reading the evidence that originally justified it.

Even when a conversation is technically still available, the useful project state is mixed together with brainstorming, abandoned ideas, corrections, and incidental discussion.

The longer the project runs, the harder it becomes to answer basic questions reliably:

- What are we actually building?
- What is the current state?
- What task is active right now?
- What has already been completed?
- Which commands and tests were actually run?
- What decisions were made, and why?
- What is blocked?
- What is the exact next action?

### Session dependence

A project should not stop making sense because a chat ended, a context window filled up, a different model takes over, or a human returns two weeks later.

If the only durable record is "the previous agent knew what was going on," the project has no real continuity.

This is especially painful when several agents or people work on the same repository. Each handoff becomes an exercise in reconstructing history instead of continuing from a known state.

### Research numbers become harder to trust

Continuity is also a reproducibility problem.

Suppose one session reports an evaluation score of 71.4% and a later session reports 74.2%. Those numbers are only meaningful if the project can recover the conditions that produced them:

- exact code and commit;
- dataset or source revision;
- split and sample definition;
- model and configuration;
- prompt or rubric version;
- seeds and calibration state;
- commands that were run;
- test and validation results;
- known failures or exclusions.

If those details live only in transient chat context, later sessions can accidentally compare incompatible runs, repeat an old mistake, use a moving dataset revision, or report a result without being able to reproduce how it was obtained.

PCM does not make research correct by itself. It makes the **state and evidence around the work durable enough to inspect, reproduce, and challenge later**.

## The idea

PCM treats continuity as part of the repository instead of part of the conversation.

The Git repository becomes the shared memory that survives sessions, agents, models, and machines.

A participating project keeps a small set of human-readable files that answer different questions:

- **PROJECT** — What is this project, what are its goals, and what should remain stable?
- **CURRENT** — Where is the project right now?
- **TASK** — What bounded unit of work is active?
- **CHECKPOINT** — What was completed, what evidence exists, what changed, what is blocked, and what comes next?
- **Git history** — What exact revisions carried those state changes?
- **CONTEXT PACK** — A disposable convenience view derived from the canonical repository state.

The important distinction is that **PCM is the toolkit and protocol; the target project repository owns the actual project state**.

You do not depend on the PCM repository's own development history to remember your project. You use PCM to initialize and maintain continuity files inside your project.

## What continuity looks like in practice

A long-running project might involve dozens or hundreds of sessions.

A typical cycle is:

1. A fresh human or agent opens the repository.
2. It reads the project's handoff/current state and the one active task.
3. It performs only that bounded work.
4. It runs whatever tests, experiments, or validation the task requires.
5. Before stopping, it writes a checkpoint containing the important evidence, decisions, blockers, changed files, and one concrete next action.
6. It commits and pushes that state to the task branch. A normal checkpoint is not complete while it exists only in a local worktree.
7. The session can disappear completely.
8. A new session resumes from the repository rather than reconstructing the old conversation.

That means the project can continue across:

- context-window limits;
- new ChatGPT sessions;
- different models or agent products;
- different developers or researchers;
- local and cloud execution environments;
- interruptions lasting days or months.

The goal is not to preserve every sentence an agent ever produced. The goal is to preserve the **minimum trustworthy state needed to continue the work correctly**.

### Execution versus bookkeeping

Continuity state is important, but writing it is not an execution gate. If a canonical continuity file or checkout becomes temporarily unavailable while the underlying task remains safe, continue only through an already-authorized alternate environment and record a small recovery receipt with `--recovery-root`. Do not create a clone or worktree as a workaround. Reconcile that receipt into the canonical task when it becomes writable.

The durable identity is the repository/task lineage: project identity, task ID, branch/ref, remote, and Git history. New software projects default to serial task branches in one canonical checkout; projects may explicitly select registered linked worktrees when parallel execution is required. Normal checkpoints must be committed and pushed; an unavailable remote is an emergency degraded-continuity condition that must be recorded and repaired, not a second local canonical state.

## Why Git is the transport

Git already solves several parts of the continuity problem well:

- durable versioned state;
- exact commits;
- branches for bounded work;
- reviewable diffs;
- distributed copies;
- chronological history;
- conflict detection;
- reproducible references to earlier states.

PCM builds on that instead of introducing a separate project-memory service.

Issue trackers, pull requests, task systems, or agent memories can still be useful, but they are treated as coordination layers. The repository remains capable of explaining itself without requiring access to an old chat.

## Human-readable first, machine-checkable second

The continuity files are ordinary Markdown and JSON. A person should be able to open them and understand the project without special software.

PCM also adds small machine-readable metadata markers and versioned schemas so basic continuity invariants can be checked automatically.

For example, validation can detect cases such as:

- the declared current task file does not exist;
- a task ID is malformed or duplicated;
- a completed task is still marked active;
- required continuity files are missing;
- a checkpoint is missing required evidence or next-action fields;
- a generated context pack lacks Git provenance.

The purpose of validation is not bureaucracy. It is to catch the kinds of continuity errors that become expensive several sessions later.

## Core repository layout

A PCM-enabled project typically contains:

```text
PROJECT.md
HANDOFF.md
checkpoints/
  CURRENT.md
tasks/
  TASK-APP-0001-example.md
.continuity/
  config.json
  packs/
schemas/
  v1/
```

The main roles are:

- `PROJECT.md` — stable project contract and scope;
- `checkpoints/CURRENT.md` — present program/repository state;
- `tasks/TASK-*.md` — bounded tasks and their checkpoint history;
- `HANDOFF.md` — simple cold-start entrypoint for a fresh session;
- `.continuity/config.json` — protocol/profile/task-prefix configuration;
- `schemas/v1/` — machine-readable continuity contracts;
- `.continuity/packs/` — generated context bundles that can be discarded and regenerated.

## Using PCM as a helper for another repository

When PCM is supplied to an agent as a helper, **the PCM checkout is not the target project**. Project state belongs in the repository the user is actually working on.

Make the target root explicit and preflight it before relying on continuity state:

```bash
continuity preflight --root /path/to/target
```

A healthy preflight prints `MODE: TARGET_VALID`. `DEGRADED_TARGET` means the target's PCM shape is present but a canonical file is temporarily unavailable; keep the task moving only through the recovery-receipt path and do not claim the target is fully validated until reconciliation. If it reports `HELPER_REPOSITORY`, `NOT_ADOPTED`, or `INVALID_TARGET`, stop treating that root as a continuity-enabled target and correct the integration first.

Do not create a second continuity repository and do not store target PROJECT/CURRENT/TASK state in the PCM source repository.

For an existing repository whose PROJECT, AGENTS, README, or HANDOFF files must be preserved, use the non-destructive overlay procedure in [`docs/TARGET_ADOPTION.md`](docs/TARGET_ADOPTION.md). A target is considered integrated only after:

```bash
continuity validate --root /path/to/target
```

returns `VALID`.

## Using PCM in a new project

Python 3.11+ is currently the only runtime requirement.

From a PCM source checkout:

```bash
python -m pip install -e .
```

Then, inside the project you want to make resumable:

```bash
continuity init --profile software --name "My Project" --task-prefix APP
continuity validate
```

Software initialization defaults to `workspace_mode: single-checkout`: task
branches run sequentially in the canonical folder and reuse its one dependency
environment. Linked task worktrees are available only by explicit opt-in with
`--workspace-mode linked-worktrees`.

Create a bounded task:

```bash
continuity task new \
  --slug first-task \
  --goal "Implement the first bounded piece of work." \
  --why "This is the next dependency in the project."
```

Before a session ends, append a checkpoint:

```bash
continuity checkpoint APP-0001 \
  --agent "agent-or-person-name" \
  --completed "Implemented the bounded change." \
  --evidence "pytest -q -> 42 passed" \
  --next "Open the review PR and verify CI."
```

If the canonical task file cannot be written but safe work can continue, use an authorized alternate checkout:

```bash
continuity checkpoint APP-0001 \
  --root /path/to/canonical-checkout \
  --recovery-root /path/to/authorized-alternate \
  --agent "agent-or-person-name" \
  --evidence "canonical task temporarily unavailable; product check passed" \
  --next "Reconcile the recovery receipt when the canonical checkout is writable."
```

The command exits successfully after writing a recovery receipt under `.continuity/recovery/`. Later, reconcile that receipt into the canonical task with `continuity recovery reconcile`.

Commit the product change first, then run `continuity checkpoint`. The command commits the checkpoint and pushes the task branch. CI runs on the pushed branch and pull-request automation merges it after the required checks pass.

A future session should be able to continue without needing the previous conversation.

## Non-destructive initialization

`continuity init` is intentionally conservative.

It writes continuity-managed files only when they are absent or already byte-identical to what PCM expects. If an existing planned path contains different user content, initialization refuses before writing anything.

The intent is to help an existing project adopt continuity without silently replacing its own project documentation.

## Context packs

A context pack is a generated view for convenience when a fresh session needs a compact bundle of the relevant project state.

It records Git provenance such as repository, ref, and commit and includes the selected canonical source files.

Context packs are **derived**, not authoritative. If a context pack disagrees with the canonical files in the repository, the repository files win.

## What PCM is not

PCM is not:

- a replacement for Git;
- an autonomous project manager;
- a requirement to keep one agent running forever;
- a hosted memory database;
- a substitute for tests or experimental rigor;
- a promise that an agent's written claim is true;
- a reason to preserve every chat transcript;
- a requirement to use GitHub, Beads, Jira, or any particular agent vendor.

It is a small protocol for making project state durable enough that work can cross session boundaries without losing its identity.

## Current status

The continuity protocol is currently `0.1.0-draft`; the CLI package is `0.2.0`.

The implemented core includes:

- versioned continuity schemas;
- minimal and software initialization profiles;
- non-destructive `init`;
- deterministic `validate`;
- explicit target/helper `preflight`;
- task creation;
- append-only checkpointing;
- Git-provenance context-pack generation;
- fixture and end-to-end tests.

Automatic synchronization with external issue/task systems is intentionally separate from the core protocol.

## Development validation

For PCM itself:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m continuity validate --root .
```

The long-term success criterion is straightforward:

> A project should remain understandable and resumable even if every previous agent session disappears.
