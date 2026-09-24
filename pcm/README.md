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

The durable identity is the repository/task lineage: project identity, task ID, branch/ref, remote, and Git history. Keep one permanent project folder as the home base and use it for sequential tasks. When simultaneous work or isolation genuinely helps, create a temporary managed worktree for that task under `pcm/worktree/<TASK-ID>`; reuse it across sessions rather than making one per agent. Do not create sibling clones. Git worktrees share repository data, so they are lighter than separate clones, though each still has its own checked-out files and may have its own dependency environment. After changes are pushed, required checks pass, GitHub merges the PR, and the task is complete, run `continuity worktree remove <TASK-ID>`; PCM verifies the result before removing the clean worktree. Other Git hosts stay untouched until PCM has a tested CI/merge verifier for them. Unfinished or dirty work is kept, never force-deleted. For a short audit hold, record the reason, expected release date, exact path, and unlock/remove next action in the completed task's checkpoint, then pin the tree with `git worktree lock --reason "<reason; release YYYY-MM-DD>" <path>`. This blocks ordinary cleanup while keeping the hold visible in durable task state. When the audit ends, return to the permanent checkout, run `git worktree unlock <path>`, and run `continuity worktree remove <TASK-ID>` for normal verified cleanup. See [Git's worktree lock/unlock rules](https://git-scm.com/docs/git-worktree).

Dependency downloads/build artifacts should use the package manager's shared cache where supported. pnpm documents a shared content store whose package files are linked into each `node_modules` ([pnpm storage model](https://pnpm.io/)); uv documents a reusable, thread-safe cache ([uv cache](https://docs.astral.sh/uv/concepts/cache/)), while normally keeping a project-specific `.venv` ([uv project layout](https://docs.astral.sh/uv/concepts/projects/layout/)). The goal is to avoid downloading/building the same dependencies repeatedly without allowing one task's dependency edits to disrupt another. Normal checkpoints must be committed and pushed; an unavailable remote is an emergency degraded-continuity condition that must be recorded and repaired, not a second local canonical state.

Delegated agents are also temporary execution views. After a worker returns, the
parent records its result and evidence in the task checkpoint and explicitly
closes the worker. Completed workers are not left open, because a terminal
completed status can still consume an available agent slot. See
[`docs/AGENT_LIFECYCLE.md`](docs/AGENT_LIFECYCLE.md).

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

For GitHub-governed repositories, GitHub Issues own task scope and lifecycle, merged default-branch history owns accepted code, and PR checks/merge evidence own delivery. PCM task files cache a concise working view linked to the authoritative issue. Before resuming, verify current issue state. Local absolute checkout paths belong in a private per-device registry, never shared handoffs.

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
  documents.json   # optional; canonical document inventory
  packs/
docs/
  CONTINUITY_INDEX.md  # optional generated human view
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

Software initialization defaults to managed temporary task worktrees. Use the
main checkout for sequential work; create a worktree only when isolation or
parallelism helps, then run `continuity worktree remove <TASK-ID>` after the
task is merged, complete, and clean. For a short audit hold, record the reason,
release date, exact path, and cleanup action in the task checkpoint, then pin it
with `git worktree lock --reason "<reason; release YYYY-MM-DD>" <path>`; after
the audit, unlock it explicitly before verified cleanup. Choose
`--workspace-mode single-checkout`
to prohibit worktrees. The old scalar `workspace_mode` config key is not
supported; replace it with a `workspace` object such as
`"workspace": {"mode": "managed-worktrees"}` or
`"workspace": {"mode": "single-checkout"}`. Validation explains this
migration and does not modify existing configuration.

Create a bounded task:

```bash
continuity task new \
  --slug first-task \
  --goal "Implement the first bounded piece of work." \
  --why "This is the next dependency in the project." \
  --issue https://github.com/OWNER/REPO/issues/123
```

GitHub repositories use Issues as the required task authority. Verify the live issue before resuming with `continuity issue verify APP-0001`. Register checkouts on additional drives with `continuity workspace register --root <checkout>`; `continuity workspace list` and `unregister` manage this private device-only registry. Worktree creation checks registered roots and reuses a single clean, unlocked matching task branch. It stops before creating a duplicate when a match is dirty, locked, conflicting, or ambiguous. PCM does not scan drives, and registry paths do not enter shared handoffs.

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

The command prints a `REQUEST_ID` before writing. If it is interrupted, reuse
that ID with the identical payload; PCM recognizes the existing event and
retries delivery without adding another checkpoint or commit. Reusing the ID
with different content is rejected.

A future session should be able to continue without needing the previous conversation.

## Non-destructive initialization

`continuity init` is intentionally conservative.

It writes continuity-managed files only when they are absent or already byte-identical to what PCM expects. If an existing planned path contains different user content, initialization refuses before writing anything.

The intent is to help an existing project adopt continuity without silently replacing its own project documentation.

## Context packs

A context pack is a generated view for convenience when a fresh session needs a compact bundle of the relevant project state.

It records Git provenance such as repository, ref, and commit and includes the selected canonical source files.

Context packs are **derived**, not authoritative. If a context pack disagrees with the canonical files in the repository, the repository files win.

## Finding earlier documents

Projects that want an explicit document directory can opt in with
`continuity docs init`. The machine-readable source is
`.continuity/documents.json`; `docs/CONTINUITY_INDEX.md` is generated from it
and checked by `continuity validate`. Register stable IDs and concise search
terms with `continuity docs add`, then find prior work with:

```bash
git fetch origin
continuity docs find "checkpoint retries document discovery" --task APP-0004
continuity pack APP-0004
```

When a catalog exists, each fresh session or task takeover should do this
lookup before choosing its next action—not only before writing a document.
Read the matching records and their declared neighbors before concluding that
prior work is missing or creating another copy.

Search uses declared titles, summaries, keywords, paths, and neighboring-record
links; it does not crawl or semantically understand every repository file.
Freshness checks compare the reviewed file hash with the local checkout and
the locally cached `origin/HEAD`; the content comparison remains useful after
squash merges, while the recorded commit remains provenance. The lookup does
not fetch on its own, so fetch first. `NEEDS_REVIEW` means the local or remote
file bytes changed; `REMOTE_UNKNOWN` means no current comparison could be
proved. Neither changes or erases old evidence. After reviewing a changed source, run
`continuity docs refresh <DOCUMENT-ID>` and `continuity docs render`.
Task-specific packs include only associated records and their declared
neighbors, and identify each committed source by Git blob and SHA-256.

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

The continuity protocol is currently `0.1.0-draft`; the active CLI source candidate is `0.4.0` and has not been published.
Run `continuity --version` to see the package version installed in the active environment. Building or testing the package does not publish a public release.

The implemented core includes:

- versioned continuity schemas;
- minimal and software initialization profiles;
- non-destructive `init`;
- deterministic `validate`;
- explicit target/helper `preflight`;
- task creation;
- append-only checkpointing;
- request-keyed idempotent checkpoint retries;
- optional machine-readable document catalog with generated human index, deterministic lookup, freshness warnings, and task-scoped packs;
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
