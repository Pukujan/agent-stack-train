# Project Continuity Protocol — Draft v1 Specification

Status: executable bootstrap draft (`0.1.0-draft`).

## 1. Purpose

The protocol defines the minimum durable state required for a repository to be resumed by a fresh agent/session without relying on private conversation history.

## 2. Records and their bounded authority

GitHub owns durable project task/progression state for PCM-governed work. The following repository records are mandatory versioned projections and evidence; their schema path names (`canonical.*`) locate files, not a second task authority. The checkout is transient editing/execution space. Section 8 defines which source settles each field.

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
Complete the finite publication protocol in section 8.2: synchronized docs and checkpoint push, linked issue receipts, required CI and auto-merge, then verified reconciliation. An interrupted/degraded session MUST record its exact unpublished or pushed-but-unreconciled state on GitHub when available; it MUST NOT call that delivery complete. Local recovery evidence is temporary, never canonical progression.

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

The authoritative identity is the repository/task lineage (project identity, task ID, branch/ref, remote, and Git history), not a physical path or machine. Keep one permanent main checkout as the project home base; use it for sequential work. A linked worktree MAY be used for genuine parallelism or isolation, but MUST be placed under `<canonical-root>/pcm/worktree/<TASK-ID>`, tied to the existing task/branch, and reused across sessions rather than created per agent. Do not create sibling clones. After changes are pushed, required checks pass, the PR is merged, the task is marked complete, and the worktree is clean, `continuity worktree remove` verifies the GitHub PR, required checks, and merged commit before removing it. It MUST refuse locked/pinned, dirty, unmerged, unpublished, or unverifiable work and MUST NOT force-remove it. A short audit hold MUST record its reason, expected release date, private workspace ID, and unlock/remove next action in the completed task's checkpoint, and MUST use Git locking; after the hold, the tree MUST be unlocked and removed through normal verified cleanup. Until another host has a tested CI/merge verifier, cleanup for non-GitHub remotes MUST fail closed and leave the worktree intact. `workspace.mode: single-checkout` remains available for repositories choosing a stricter mode.

Use immutable package download/build caches where supported, but do not share a mutable dependency environment across worktrees with different lockfiles or runtimes. Record intentional dependency changes in tracked manifests, lockfiles, or patch files. The legacy configuration key `workspace_mode` is unsupported; validators must reject it with a migration instruction and must not rewrite the user's configuration. A normal checkpoint MUST commit and push the task branch to the configured remote; a local-only checkpoint is not a durable handoff. If the remote is temporarily unavailable, use authorized degraded recovery evidence and restore the pushed handoff as soon as possible rather than inventing a second identity.

## 6. CLI behavior

`continuity init` materializes v1 schemas and profile files. It performs a full conflict preflight and never silently overwrites different existing content.

`continuity validate` is deterministic and requires no LLM. It returns success only when core v1 structural invariants hold.

`continuity task new` allocates the next four-digit task ID from the configured prefix and writes one bounded task file. The primary writer MUST first reserve the ID and branch on the live owning issue, check existing issue/task allocations, and verify the generated ID agrees. The command's local allocation is not a distributed reservation.

`continuity checkpoint` adds a checkpoint entry without deleting or replacing prior checkpoint history, then commits and pushes it to the task branch. It prints a request ID before mutation. Repeating an identical request with the same ID is a no-op; reusing that ID with different content fails before a write. The first event timestamp is preserved. The publisher can retry both a local commit whose push failed and a push accepted remotely whose response was lost, without creating another event or commit. Older checkpoint entries without operation IDs remain valid.

`continuity checkpoint --recovery-root <alternate>` preserves a minimal recovery receipt in an authorized alternate checkout when canonical checkpoint state is temporarily unavailable. `continuity recovery reconcile` appends that receipt to the canonical task once it is writable.

`continuity worktree create <TASK-ID>` creates or resumes the task's managed linked worktree from the pushed default/task branch. `continuity worktree remove <TASK-ID>` removes only the registered task worktree after checking that the task is complete, the tree is unlocked and clean, and remote merge/CI evidence is sufficient for the configured remote.

`continuity docs init` opts a repository into the optional document catalog. `.continuity/documents.json` is the sole machine-readable source for stable document IDs, paths, human summaries, search terms, declared neighboring records, task associations, and the content/commit last reviewed. `docs/CONTINUITY_INDEX.md` is generated from that inventory and deterministic freshness checks; CI validation rejects a manually or accidentally divergent view. `continuity docs add`, `find`, `refresh`, and `render` register/update records, search metadata deterministically, explicitly acknowledge reviewed content, and regenerate/check the human view. Search is not semantic whole-repository search and does not infer document truth.

Before freshness-sensitive retrieval, a session fetches `origin`. `continuity docs find` compares the indexed file's content hash with the local checkout and, when `origin/HEAD` exists, that cached remote-tracking tree. The content comparison is independent of commit ancestry, so a squash merge does not make unchanged documents appear unknown; the recorded review commit remains provenance. The command does not fetch or make network requests itself. If relevant bytes changed, the record is `NEEDS_REVIEW`; if remote comparison cannot be proven, it is `REMOTE_UNKNOWN`; an unrelated file change does not invalidate the record. Hashes are over UTF-8 text normalized to LF, so Windows line endings do not create false drift. Freshness is provenance, not truth: old checkpoints remain historical evidence and are never rewritten.

`continuity pack` creates a derived Markdown view with repository/ref/commit/protocol/task/generation/source metadata and the exact next action. For a repository with a document inventory it contains PROJECT, CURRENT, TASK, and only documents explicitly associated with the task plus their declared one-hop neighbors. For a repository without the optional catalog, existing SPEC/AGENTS inclusion remains for compatibility. Each included source is read from a clean committed Git snapshot and records its Git blob and content SHA-256; packs do not label dirty working-tree content as HEAD. Selected evidence is marked when it needs review or cannot be compared to the cached remote.

## 7. Versioning

Projects declare a protocol version in `.continuity/config.json`. Backward-compatible optional additions are minor versions; incompatible required-state changes are major versions. The checkpoint request marker and document catalog are optional capabilities, so they do not change the required core objects or the `0.1.0-draft` declaration. Migrations must preserve historical checkpoint evidence.

## 8. Authority

| Record | Authority and limit |
| --- | --- |
| GitHub Issues and their activity | Required authority for task scope, acceptance, priority, ownership, dependencies, lifecycle and durable project progression. Each update identifies the leaf owning work, parent ancestry and dependency lineage. |
| Protected merged default-branch history | Accepted implementation and normative/domain document content at a revision. It does not override newer issue scope/lifecycle. |
| GitHub PR, required check and merge records | Delivery facts for the exact candidate. A successful local test, push or model claim cannot establish merge. |
| Checked-in PROJECT, CURRENT, TASK, checkpoints and HANDOFF | Mandatory versioned documentation: stable/domain contracts retain their content authority, while task/progression fields are as-of projections of linked issues. Checkpoints preserve observations and corrections, not a second lifecycle ledger. |
| Document catalog and generated index | Catalog owns document IDs, paths and review provenance; index is derived. Neither decides truth or task lifecycle. |
| Local checkout, private registry, recovery receipt, context pack, chat | Ephemeral execution/provenance aids. None is canonical task state or proof of delivery. A recovery receipt must later be published/reconciled. |

### 8.1 Conflict, ownership and lineage

Before edits, read the live owning issue and latest relevant comments, parent/dependency links, current PR state and source revisions. A verifier returning OPEN only checks identity/status; it does not prove prose agrees. Resolve stale projections using the authority for the disputed field and append correction/supersession evidence. Do not rewrite checkpoint history or silently convert a prior agent claim into fact.

Authorized human/owner direction can change task intent. Record that direction and its effect on the owning GitHub issue before dependent implementation; link the superseded decision and update acceptance/lineage when needed. GitHub's older intent does not overrule an authorized correction, but chat alone is not a durable amendment. Human direction cannot make failed tests pass, unmerged work delivered, or waive mandatory gates. Unknown authority, contradictory direction or ambiguous ownership pauses only the affected work pending recorded resolution; independent safe work may continue.

Every issue progress update MUST link the leaf child issue owning its work, all parent ancestors and direct prerequisites/dependents relevant to the update (or explicitly none). A top-level deliverable identifies itself as leaf with parent: none. A parent-level aggregate links the relevant leaves. Create one child per independently deliverable scope, never per comment or test type. Record task ID, primary writer, branch and issue links before creating the repository task projection. Keep one primary writer per task branch/checkpoint stream; reviewers and separately scoped tasks do not become competing writers. For shared documents, record the overlap and editing responsibility in linked issues/PRs, re-read current base/source versions, and reconcile concurrent edits before publishing. Issue prose and local locks are not distributed mutual exclusion. Stale/non-fast-forward writes MUST fail; never force-push or overwrite another writer's changes.

An upstream scope, dependency or evidence correction MUST name affected descendants, assumptions and evidence on the owning issues, with a correction link and one next action. Follow explicit parent/dependency links within the affected scope, using a visited set rather than an unbounded scan. Cycles, missing links or unknown impact remain explicit blockers for dependent claims. Pause affected downstream work, revise its acceptance/plan and revalidate invalidated evidence before resuming; preserve unaffected results and history. A merged descendant may need a bounded repair issue, not a rewritten past. No graph database, parallel local ledger, broad scheduler or autonomous issue-polling agent is required.

### 8.2 Finite publication and reconciliation

1. **Before every push:** verify issue/parent/dependency scope and writer; synchronize relevant normative/domain docs, task/checkpoint projections, CURRENT/HANDOFF when affected, and reviewed catalog/generated index. Record the source issue/comment URL and observed revision/time, leaf/parent/dependency links, as-of status, evidence/limits, changed paths, blockers and exact next action. Docs MUST distinguish accepted work from candidate work and pending publication/CI/merge. An unchanged document needs no ceremonial edit. Run proportionate checks. Commit product/docs first, then use `continuity checkpoint` to commit and synchronously push the checkpoint, retaining its request ID for identical retries.
2. **After each successful push:** publish a leaf issue receipt keyed by repository/task/request ID and exact pushed SHA. Link the checkpoint/docs at that SHA, changed-doc inventory, PR (or explicitly pending), tests, pending required gates, blockers and next action. Add a concise parent progression update linking that receipt and ancestry/dependencies. Cover every push, including corrective pushes; group multiple checkpoint references only if every request/SHA remains traceable. An interrupted push or comment is pushed-but-unreconciled until verified: inspect the remote ref and existing receipt key before retrying. A missing receipt requires a comment retry, not another checkpoint or push. Changed facts require an appended correction; never silently edit historical evidence. Until automation exists, the primary writer MUST do this manually.
3. **PR and gates:** open/update the PR, enable GitHub auto-merge, and verify protected required checks/reviews on the exact current-base or merge-queue candidate. Required CI and auto-merge are mandatory. Missing, failed, skipped, stale or unverified required gates, unavailable protection/permissions, or disabled auto-merge fail closed: no completion, merge bypass or cleanup. Record the failure on the leaf with lineage; retain unsafe resources and keep incomplete issues open.
4. **After CI/merge:** append authoritative check results/run links, candidate and merge SHA, PR state, live leaf/parent status, remaining scope and next action; link the parent progression update. Fetch and verify merged history before completing the delivered scope or cleaning resources. A leaf's delivery does not complete its parent. Material doc/task corrections require a new synchronized increment through the same gates. A closeout projection may record the already-verified delivery and identify its own publication as pending.
5. **Stop the receipt loop:** GitHub receipt-only transitions (push/CI/merge acknowledgments and resulting issue lifecycle) do not require another documentation commit solely to copy their own SHA or merge result. Docs retain a truthful explicit as-of/pending statement and link the live issue for subsequent events. At the next substantive increment, refresh affected projections from that issue. This is bounded eventual projection reconciliation, not permission to omit docs before a push or leave materially false current guidance uncorrected.

An indexed task's checkpoint changes its indexed bytes. The current CLI does not automatically render that index during publication. Before publishing such a checkpoint, commit product work, prepare the exact request-keyed entry using the existing `continuity.cli.checkpoint_task` API, review/refresh the affected catalog record and render the index, then commit the synchronized evidence. Invoke `continuity checkpoint` with the identical request ID and payload to publish it idempotently. Do not push a knowingly stale index and call a later repair synchronization. This preparation uses the existing task projection, not another ledger; non-indexed tasks use the ordinary command directly.

A local path registry may contain absolute paths only on that device; shared issues, commits, PRs and handoffs contain repository/task/ref/commit identity, never secrets or machine-specific paths.

Issue lifecycle language in PR descriptions and commit messages is operational: GitHub recognizes supported closing keywords followed by an issue reference and may close the issue when the commit or PR merges to the default branch. Negation does not cancel the keyword. Use such a keyword only when the issue is ready to complete; for progress-only PRs, use `Refs #<number>` or a manual sidebar link. Verify the live issue after each merge before marking its task complete. See [GitHub's linking rules](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue).

## 9. Evidence semantics

Label observed command/test results, repository state, external artifacts, agent/model reports and inference separately. Claims MUST identify source/revision and relevant conditions; confidence is bounded by that evidence, not the fluency or repetition of prose. Contradictory evidence remains preserved and the affected conclusion is disputed or unknown until compared or reproduced. Record which claim a correction supersedes and why; invalidate dependent conclusions under section 8.1. An unknown result blocks only a dependent claim or gate. Validators check structure and references, not semantic truth; a valid schema, green local suite or unsupported numeric confidence cannot resolve factual contradictions.

## 10. v1 implementation boundary

GitHub issue verification is read-only; PCM does not synchronize issue text or status. Checkpoint commits are pushed synchronously through the task branch; required CI and GitHub auto-merge run asynchronously. Section 8's manual issue receipts are mandatory; runtime automation is separately tracked in [PCM-0026 / #67](https://github.com/Pukujan/project-continuity-modules/issues/67), dependent on [PCM-0025 / #66](https://github.com/Pukujan/project-continuity-modules/issues/66), both under [#53](https://github.com/Pukujan/project-continuity-modules/issues/53). Policy and propagation tests do not enforce arbitrary clients or configure repository protection. Jira may report GitHub development links but must not become a second task-status authority. Supporting schemas and offline local fixtures remain usable without network access; such use is not compliant delivered PCM project work without the GitHub gates.

## 11. Continuity record writing and evidence

Continuity records MUST orient a fresh human or agent to the problem, consequence, intended observable outcome, scope, current status, evidence, and next action. Their level of detail should fit the risk and reader need: detailed enough to continue and audit without copying full logs or repeating canonical state in every issue, update, or pull request.

External factual claims SHOULD link directly to authoritative sources. Repository claims SHOULD identify a stable commit/revision and relevant file, issue, PR, or CI run. Experimental, research, failure-reproduction, and agent-behavior claims MUST record enough of the starting revision, inputs/configuration, runtime, commands/prompts, results, and limitations to reproduce the claim; omit fields irrelevant to routine work.

Keep machine-readable IDs and versions aligned across task/checkpoint, tracker, PR, and evidence links. Human-readable and machine-readable records SHOULD share one declared source or have deterministic checks for shared identifiers and status. A valid schema, citation, link, or agent report is not proof of semantic truth.

PCM owns the continuation-record contract and its propagation to adopting projects. It does not standardize unrelated domain/product writing. GitHub issue and PR templates are optional writing aids, not synchronization adapters; installing them MUST preserve conflicting project files. PCM MUST NOT claim automatic conversation capture or issue synchronization. The full policy is in docs/CONTINUITY_RECORDS_POLICY.md.

The readable structure for issue logs, progress updates and pull requests is the separately versioned `issue-log-format` module (policy 1.1.0): docs/ISSUE_LOG_FORMAT.md.
