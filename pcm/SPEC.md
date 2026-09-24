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

### GITHUB ISSUE
For GitHub-governed repositories, the GitHub issue is authoritative for task scope, priority, owner, dependencies, acceptance, and lifecycle. The task file is a compact, committed working cache linked with `issue_url`; conflicts are resolved from the live issue. Merged default-branch history is authoritative for accepted code. Pull request checks and merge evidence are authoritative for delivery. Other trackers, chat, and context packs are secondary views.

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
- checkpoint-operation extension markers, when present, identify one request key per task and match the checkpoint payload digest;
- completed tasks are not marked active;
- context packs identify source repository/ref/commit/protocol version/source files and are treated as derived;
- an optional `.continuity/documents.json` inventory validates and its generated human index matches the canonical inventory and current local source state;
- no secret material is required inside continuity state;
- GitHub-governed repositories link every active task to one issue in the same repository; the live issue is checked before resuming work.
- a local task copy never overrides a changed or closed authoritative issue.

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

### Delegated agents
Delegated agents are temporary execution workers, not canonical project or task
state. The parent MUST give each worker a bounded task, capture its result and
evidence in the parent task/checkpoint, and explicitly close it immediately after
the result is captured. This close requirement applies to completed, interrupted,
failed, cancelled, and timed-out workers. A worker may be reused only for an
explicit follow-up before it is closed. The parent MUST use the smallest useful
number of workers and MUST NOT leave completed workers open for possible future
use. See `docs/AGENT_LIFECYCLE.md`.

### Degraded continuity
Execution safety and existing authorization outrank continuity bookkeeping. Failure to read or write canonical continuity state is a degraded condition, not an execution gate, when the underlying task remains safe and recoverable. Continue in an already-authorized alternate checkout or host, write a recovery receipt containing the same repository/task lineage and checkpoint evidence, and reconcile it into canonical state when writable.

The authoritative identity is the repository/task lineage (project identity, task ID, branch/ref, remote, and Git history), not a physical path or machine. Keep one permanent main checkout as the project home base; use it for sequential work. A linked worktree MAY be used for genuine parallelism or isolation, but MUST be placed under `<canonical-root>/pcm/worktree/<TASK-ID>`, tied to the existing task/branch, and reused across sessions rather than created per agent. Do not create sibling clones. After changes are pushed, required checks pass, the PR is merged, the task is marked complete, and the worktree is clean, `continuity worktree remove` verifies the GitHub PR, required checks, and merged commit before removing it. It MUST refuse locked/pinned, dirty, unmerged, unpublished, or unverifiable work and MUST NOT force-remove it. A short audit hold MUST record its reason, expected release date, exact path, and unlock/remove next action in the completed task's checkpoint, and MUST use Git locking; after the hold, the tree MUST be unlocked and removed through normal verified cleanup. Until another host has a tested CI/merge verifier, cleanup for non-GitHub remotes MUST fail closed and leave the worktree intact. `workspace.mode: single-checkout` remains available for repositories choosing a stricter mode.

Use immutable package download/build caches where supported, but do not share a mutable dependency environment across worktrees with different lockfiles or runtimes. Record intentional dependency changes in tracked manifests, lockfiles, or patch files. The legacy configuration key `workspace_mode` is unsupported; validators must reject it with a migration instruction and must not rewrite the user's configuration. A normal checkpoint MUST commit and push the task branch to the configured remote; a local-only checkpoint is not a durable handoff. If the remote is temporarily unavailable, use authorized degraded recovery evidence and restore the pushed handoff as soon as possible rather than inventing a second identity.

## 6. CLI behavior

`continuity init` materializes v1 schemas and profile files. It performs a full conflict preflight and never silently overwrites different existing content.

`continuity validate` is deterministic and requires no LLM. It returns success only when core v1 structural invariants hold.

`continuity task new` allocates the next four-digit task ID from the configured prefix and writes one bounded task file.

`continuity checkpoint` adds a checkpoint entry without deleting or replacing prior checkpoint history, then commits and pushes it to the task branch. It prints a request ID before mutation. Repeating an identical request with the same ID is a no-op; reusing that ID with different content fails before a write. The first event timestamp is preserved. The publisher can retry both a local commit whose push failed and a push accepted remotely whose response was lost, without creating another event or commit. Older checkpoint entries without operation IDs remain valid.

`continuity checkpoint --recovery-root <alternate>` preserves a minimal recovery receipt in an authorized alternate checkout when canonical checkpoint state is temporarily unavailable. `continuity recovery reconcile` appends that receipt to the canonical task once it is writable.

`continuity worktree create <TASK-ID>` creates or resumes the task's managed linked worktree from the pushed default/task branch. `continuity worktree remove <TASK-ID>` removes only the registered task worktree after checking that the task is complete, the tree is unlocked and clean, and remote merge/CI evidence is sufficient for the configured remote.

`continuity docs init` opts a repository into the optional document catalog. `.continuity/documents.json` is the sole machine-readable source for stable document IDs, paths, human summaries, search terms, declared neighboring records, task associations, and the content/commit last reviewed. `docs/CONTINUITY_INDEX.md` is generated from that inventory and deterministic freshness checks; CI validation rejects a manually or accidentally divergent view. `continuity docs add`, `find`, `refresh`, and `render` register/update records, search metadata deterministically, explicitly acknowledge reviewed content, and regenerate/check the human view. Search is not semantic whole-repository search and does not infer document truth.

Before freshness-sensitive retrieval, a session fetches `origin`. `continuity docs find` compares the indexed file's content hash with the local checkout and, when `origin/HEAD` exists, that cached remote-tracking tree. The content comparison is independent of commit ancestry, so a squash merge does not make unchanged documents appear unknown; the recorded review commit remains provenance. The command does not fetch or make network requests itself. If relevant bytes changed, the record is `NEEDS_REVIEW`; if remote comparison cannot be proven, it is `REMOTE_UNKNOWN`; an unrelated file change does not invalidate the record. Hashes are over UTF-8 text normalized to LF, so Windows line endings do not create false drift. Freshness is provenance, not truth: old checkpoints remain historical evidence and are never rewritten.

`continuity pack` creates a derived Markdown view with repository/ref/commit/protocol/task/generation/source metadata and the exact next action. For a repository with a document inventory it contains PROJECT, CURRENT, TASK, and only documents explicitly associated with the task plus their declared one-hop neighbors. For a repository without the optional catalog, existing SPEC/AGENTS inclusion remains for compatibility. Each included source is read from a clean committed Git snapshot and records its Git blob and content SHA-256; packs do not label dirty working-tree content as HEAD. Selected evidence is marked when it needs review or cannot be compared to the cached remote.

## 7. Versioning

Projects declare a protocol version in `.continuity/config.json`. Backward-compatible optional additions are minor versions; incompatible required-state changes are major versions. The checkpoint request marker and document catalog are optional capabilities, so they do not change the required core objects or the `0.1.0-draft` declaration. Migrations must preserve historical checkpoint evidence.

## 8. Authority

For GitHub-governed repositories, GitHub Issues own task intent and lifecycle; task files are committed working caches. Merged default-branch history owns accepted code, and PR checks/merge records own delivery evidence. Context packs and chat summaries are derived. If task metadata and GitHub disagree, stop and resolve from the issue before editing. A local path registry may contain absolute paths only on that device; shared issues, commits, PRs, and handoffs contain repository/task/ref/commit identity, never machine-specific paths.

## 9. Evidence semantics

Continuity records should prefer claims tied to evidence. Validators check structure and references but do not decide whether a human/model semantic claim is true.

## 10. v1 implementation boundary

GitHub issue verification is read-only; PCM does not synchronize issue text or status. Checkpoint commits are pushed asynchronously through the task branch. Pull requests merge only after branch protection's required reviews/checks; use a merge queue when branch contention warrants it. Each task/checkpoint stream has one primary writer; collaborators work on distinct issue/task branches and submit changes through PRs. Non-fast-forward or stale checkpoint writes fail closed, and force pushes are prohibited. Multiple authorized auto-mergers can request merge; protected branch rules and required checks remain the merge gate. Jira may report GitHub development links but must not become a second task-status authority.

## 11. Continuity record writing and evidence

Continuity records MUST orient a fresh human or agent to the problem, consequence, intended observable outcome, scope, current status, evidence, and next action. Their level of detail should fit the risk and reader need: detailed enough to continue and audit without copying full logs or repeating canonical state in every issue, update, or pull request.

External factual claims SHOULD link directly to authoritative sources. Repository claims SHOULD identify a stable commit/revision and relevant file, issue, PR, or CI run. Experimental, research, failure-reproduction, and agent-behavior claims MUST record enough of the starting revision, inputs/configuration, runtime, commands/prompts, results, and limitations to reproduce the claim; omit fields irrelevant to routine work.

Keep machine-readable IDs and versions aligned across task/checkpoint, tracker, PR, and evidence links. Human-readable and machine-readable records SHOULD share one declared source or have deterministic checks for shared identifiers and status. A valid schema, citation, link, or agent report is not proof of semantic truth.

PCM owns the continuation-record contract and its propagation to adopting projects. It does not standardize unrelated domain/product writing. GitHub issue and PR templates are optional writing aids, not synchronization adapters; installing them MUST preserve conflicting project files. PCM MUST NOT claim automatic conversation capture or issue synchronization. The full policy is in docs/CONTINUITY_RECORDS_POLICY.md.
