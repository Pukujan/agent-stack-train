# Agent Operating Contract

This repository dogfoods the continuity protocol it is building.

## Operating mode gate

Before reading task state, determine whether this repository is the **thing being developed** or only a **helper for another repository**.

- If the user points at PCM to help work on another repository, PCM is helper/tooling only. The other repository is the target and owns PROJECT, CURRENT, TASK, checkpoints, and project-specific operational state.
- Identify the target repository/root explicitly and run `continuity preflight --root <target>` before treating continuity as active.
- Do not create a new continuity repository for the target, do not write the target project's state into this repository, and do not use PCM's own CURRENT/TASK as the target's task state.
- A target is not PCM-integrated merely because it contains similarly named files. Integration is established only when the target passes `continuity validate --root <target>`.
- If a mature target already owns PROJECT/AGENTS/HANDOFF documentation, preserve those semantics and follow `docs/TARGET_ADOPTION.md` rather than replacing them.

Only when the task is to change Project Continuity Modules itself should the PCM read order below be used.

## Read order

Before doing work:

1. `PROJECT.md`
2. `checkpoints/CURRENT.md`
3. the active `tasks/TASK-*.md`
4. the minimum relevant document:
   - normative design: `SPEC.md`
   - handoffs: `docs/HANDOFF_PROTOCOL.md`
   - delegated-agent lifecycle: `docs/AGENT_LIFECYCLE.md`
   - versioning/migrations: `docs/VERSIONING.md`

Do not scan historical chats for context by default.

## One task, one primary branch/session

Task IDs use `PCM-XXXX`.

Recommended branch format:

```text
task/PCM-0001-bootstrap-v1
```

One primary agent/session owns the writable task state at a time.

## Canonical checkout

- The Git repository, remote, task ID, branch/ref, and commit history identify the work; a physical path does not. Keep one permanent main checkout as the project's home base.
- For GitHub-governed projects, the linked GitHub issue owns task scope, priority, owner, dependencies, acceptance, and lifecycle; merged default-branch history owns accepted code. Verify the live issue before resuming with `continuity issue verify <TASK-ID>`. Resolve task-file conflicts from the issue before editing.
- Store local checkout roots only in the per-device private registry (`continuity workspace register --root <checkout>`). Before making a worktree, PCM checks registered roots and `git worktree list`; reuse one clean, unlocked matching task branch. Stop if any match is dirty, locked, conflicting, or ambiguous. Never scan all drives or put absolute local paths in shared issues, commits, PRs, or handoffs.
- Use the main checkout for sequential work. Do not create clones or sibling project folders.
- When parallel work or isolation is genuinely useful, use one managed linked worktree per independent active task under `<canonical-root>/pcm/worktree/<TASK-ID>`. Do not make one per session or agent; later sessions resume the same task tree. Do not create arbitrary worktree paths.
- Before stopping, complete the task's pushed checkpoint/PR workflow. Once required checks pass, GitHub merges the PR, the task record is complete, and the worktree is clean, run `continuity worktree remove <TASK-ID>`. It verifies delivery and refuses locked/pinned or otherwise unsafe removal; never force-remove unfinished or user-modified work. For a short audit hold, record its reason, expected release date, private workspace ID, and unlock/remove next action in the completed task's checkpoint, then lock the tree with `git worktree lock --reason "<reason; release YYYY-MM-DD>" <path>`. The lock blocks ordinary cleanup; it does not waive eventual removal. When the audit ends, return to the permanent checkout, unlock the tree, and run the normal verified cleanup. Other Git hosts remain unsupported for cleanup until PCM has a tested CI/merge verifier for them.
- Linked worktrees share Git repository data, but dependency environments may still take space. Reuse immutable download/build caches where supported; do not share a mutable `node_modules` or `.venv` across tasks whose lockfiles or runtimes differ. Track dependency changes in manifests, lockfiles, or patch files.
- `workspace.mode: single-checkout` is available for projects that explicitly want to prohibit linked worktrees.

If the canonical checkout is unavailable or ambiguous, resolve policy and ownership before creating any directory. A worktree is for task isolation/parallelism, not a workaround for unavailable continuity state; degraded continuity uses an already-authorized alternate environment and a recovery receipt.

## Checkpoint rule

Before stopping after meaningful work, append to the active task:

- completed work;
- evidence/commands/results;
- files changed;
- decisions;
- blockers/uncertainty;
- one exact next action.

Update `checkpoints/CURRENT.md` only when program-wide state or priority changes.

Continuity bookkeeping supports execution but does not gate safe execution. If a canonical task, CURRENT, or HANDOFF file is temporarily unavailable, do not repair storage merely to force a write or stop otherwise-safe authorized work. Use only an already-authorized alternate environment; never create a clone or worktree merely to bypass unavailable checkpoint state. Run `continuity checkpoint ... --recovery-root <alternate-root>` only when that alternate environment is authorized, then reconcile with `continuity recovery reconcile --root <canonical-root> --file <receipt>`. Recovery receipts are temporary evidence, not a competing project identity.

Normal checkpoint delivery is mandatory: commit the product change first, then run `continuity checkpoint`. The command commits the checkpoint and synchronously pushes the task branch to `origin`; a normal checkpoint is not complete while it exists only locally. Open/update a PR after pushing. GitHub CI and auto-merge then run asynchronously; auto-merge must wait for required reviews/checks and any merge queue. Do not mark the task complete or remove its worktree until the merged PR and required checks are confirmed. Work only on the task's own branch; never force-push or push directly to the protected default branch. A managed worktree uses the same task/repository identity and is never a substitute for publishing.

The checkpoint command prints a `REQUEST_ID` before it writes. If the command is interrupted, retry the identical payload with the same `--request-id`; the recorded event and push are idempotent. A changed payload under that ID is a conflict and must use a new ID only if it is genuinely a new checkpoint.

If `.continuity/documents.json` exists, every fresh session or task takeover/resumption must consult it before deciding the next action, not only before writing documentation. Run `git fetch origin`, then `continuity docs find "<issue title and task-objective terms>" --task <TASK-ID>`; read the returned matches and declared neighbors before deciding that prior work is missing or creating/replacing a document. The command compares indexed content with the cached `origin/HEAD` when that comparison is provable and labels changed records `NEEDS_REVIEW`. `REMOTE_UNKNOWN` is not proof of freshness. The inventory is canonical and `docs/CONTINUITY_INDEX.md` is generated; run `continuity docs render` after source changes, and use `continuity docs refresh <ID>` only after reviewing the changed source. This lookup is deterministic metadata search, not a semantic crawler.

If the remote itself is unavailable, use the degraded recovery-receipt path. That is an emergency continuity condition, not a successful normal handoff: record the exact local state, continue only when the task remains safe, and publish/reconcile as soon as the shared Git path is available again.

Delegated agents are temporary workers. Give each one a bounded task, capture its
result and evidence in the parent task, and close it immediately after the result
is captured. Completed, interrupted, failed, cancelled, or timed-out workers must
not be left open; stop and close workers that are no longer needed. Use the
smallest useful number of workers and do not treat an agent thread as canonical
project or task state. See `docs/AGENT_LIFECYCLE.md`.

## Evidence rule

Distinguish:
- observed command/test result;
- repository state;
- external artifact;
- agent/model claim;
- inference/assumption.

Never promote an unsupported previous-session statement into project fact.

## Continuity record writing

<!-- pcm:policy {"id":"continuity-records","policy_version":"1.3.0","protocol_version":"0.1.0-draft"} -->

For continuity issues, progress updates, pull requests, and PCM-owned project-state documents, orient the reader to the human problem and consequence, observable outcome, scope, status, evidence, and next action. Link external claims to direct sources and repository claims to a commit/revision, issue, PR, CI run, or artifact. Record enough inputs and commands to reproduce a result only when the claim depends on an experiment, research, or failure reproduction. Keep PR openings skimmable; link or collapse long logs and technical detail. Preserve the target project's ownership of unrelated writing and documents. GitHub's issue-closing keywords in PR descriptions and commit messages remain active under negation; use them only when the issue should complete at merge, and verify issue status afterward. See docs/CONTINUITY_RECORDS_POLICY.md.

## Verification rule

Name the human-visible outcome and choose checks in proportion to the promise being changed. Deterministic regression tests are the default; fresh-session holdouts are reserved for agent-facing workflow promises and must use the visible-contract fairness rules. Do not add process documents or test-type sub-issues by default. See `docs/TESTING_POLICY.md`.

## Scope rule

If the task expands materially, update/split the task before doing the expanded work.

## Self-hosting rule

Changes to the continuity protocol must be managed using the continuity protocol itself whenever practical. Protocol defects discovered while dogfooding should become explicit tasks/issues rather than silent conventions.

<!-- pcm:github-progression:start -->
## GitHub-owned progression

GitHub Issues are required for PCM-governed project work and own task scope, acceptance, priority, ownership, dependencies, lifecycle and durable project progression. Merged default-branch history owns accepted code and normative/domain documents; PR checks and merge records own delivery facts. Checked-in PROJECT/CURRENT/TASK/checkpoint/handoff documents are mandatory versioned projections for task state, not a parallel authority. Local files, registries, context packs and chat are ephemeral execution aids. Domain-document ownership stays with the target project.

Every issue progress update MUST link the leaf child issue that owns the work, its parent ancestry and dependencies (or explicitly none). A top-level deliverable identifies itself as the leaf and says parent: none. Create one child per independently deliverable scope, never one per comment. Record task ID, primary writer and branch on the issue before creating its repository projection. Re-read live issues and relevant source revisions before resuming; the issue verifier checks identity/status, not semantic agreement.

Authorized owner/user direction can revise intent: record it on the owning GitHub issue with a correction/supersession link before dependent work. It cannot alter observed CI/merge facts or waive required gates. Stale projections yield to their field's authority. If direction, ownership or evidence conflicts remain unresolved, pause affected work and record uncertainty; continue independent safe work. One primary writer owns each task branch/checkpoint stream. Coordinate shared-document edits through linked issues/PRs, re-read the current base and reconcile concurrent changes; never force-push or overwrite another writer. Issue prose is not an atomic lock.

Label observed results, repository/external evidence, agent reports and inference separately. Preserve contradictory evidence with source/revision and mark conclusions disputed or unknown until resolved. Append correction/supersession evidence; never rewrite checkpoint history. An upstream correction MUST identify affected descendants and assumptions on their issues; pause, re-plan and revalidate dependent work before resuming. Follow explicit parent/dependency links within the affected scope; cycles or unknown lineage block affected claims. No graph database, local canonical ledger or autonomous polling agent is required.

Before every push, synchronize relevant docs and task/checkpoint projections, CURRENT/HANDOFF when affected, and reviewed catalog/generated index. Record leaf/parent/dependency links, source issue/comment revision, as-of status, evidence, blockers and next action. Commit product/docs first; `continuity checkpoint` then commits and synchronously pushes the checkpoint with a stable request ID. After every successful push, publish a leaf issue receipt keyed by request ID and exact pushed SHA, linking changed docs/checkpoint, PR, tests and pending gates; add a linked parent progression update. Retry a missing receipt without another checkpoint/push; inspect for the same key before posting. `--receipt-repo` and `--receipt-issue` are opt-in and still require a proven lookup; omit them and the receipt stays manual. Automatic issue-comment synchronization is not implemented; issue #67 is CLOSED (owner freeze decision 2026-09-25) and its unmet guaranteed-completion acceptance transferred to #110.

Required CI and GitHub auto-merge are mandatory. Arm auto-merge only after the increment's final push: a later push races the merge window and strands outside accepted history. Verify protection, required reviews/checks on the exact current-base or merge-queue candidate, and auto-merge; missing, failed, skipped, stale or unverified gates fail closed: no completion or cleanup. After CI/merge, append the exact check results, PR/merge SHA and live issue status to the leaf and link the parent update; fetch and verify accepted history. Reconcile material doc/status corrections in a new synchronized increment. Receipt-only transitions need no recursive doc commit: docs retain an explicit as-of/pending state and point to the live issue. Never label local-only or merely pushed work delivered. Preserve unsafe resources and keep incomplete issues open.
<!-- pcm:github-progression:end -->

<!-- pcm:issue-log-format:start -->
## Issue log format (issue-log-format 1.1.0)

<!-- pcm:policy {"id":"issue-log-format","policy_version":"1.1.0","protocol_version":"0.1.0-draft"} -->

Write issue logs, progress updates, and pull requests in one plain-language shape a newcomer can follow. Pick the tier by the kind of issue, not by preference. **Core tier (every issue log):** title states the problem and intended direction; a 1-3 paragraph summary naming who/what is affected, the consequence, and what this proposes; identity and lineage (leaf owning issue, parent ancestry or none, task ID, primary writer, branch); observed facts vs interpretation, with inferences labelled *inferred*; acceptance criteria with numeric thresholds marked *(proposed)* when untested; boundaries/non-goals and one next action. **Investigation tier (incidents, failures, research, design issues):** numbered symptoms; hypotheses with Status, confirm/refute, and experiment; evidence with provenance; a **Counter-signal** entry when one exists; honest caveat; problems-vs-gaps; a **Proposal** labelled *(proposal)* stating none of it exists unless named as existing. **Pull requests open reader-first:** problem and consequence, what changes, how to verify, and what stays unchanged; lineage links; evidence and one next action; long logs collapsed or linked; reference issues with "Refs #<number>" and use closing keywords only when closing at merge is intended. **Diagrams (mermaid):** when a record describes a flow with 4+ ordered steps or 2+ branches, add a fenced mermaid diagram *and* keep an adjacent text list or table so the record survives render failure; default to `graph TD` (vertical) because wide `LR` flows shrink to illegible strips on phones — reserve `LR` for 4 or fewer short nodes; cap 8 nodes and 6-word labels; wrap diagrams that may exceed the container width inside `<details>` (GitHub mounts the renderer lazily on expand); preview the rendered diagram before publishing (broken syntax shows a visible parse error) and never cite renderer URLs as standalone sources. No private absolute paths or secrets; link rather than paste long logs. See `docs/ISSUE_LOG_FORMAT.md` for the full format, exemplar, and examples.
<!-- pcm:issue-log-format:end -->
