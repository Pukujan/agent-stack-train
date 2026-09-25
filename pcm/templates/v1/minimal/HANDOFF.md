# Current Handoff

Start from repository state, not prior chat history.

## Read order

1. `PROJECT.md`
2. `AGENTS.md` when present
3. `checkpoints/CURRENT.md`
4. the active task named by CURRENT
5. the minimum relevant specification/design document

## Authority

For GitHub repositories, Issues are authoritative for task scope, priority, ownership, dependencies, acceptance, and lifecycle. The linked task file is a compact working cache. Merged default-branch history owns accepted code, and PR checks/merge evidence own delivery. Verify the live issue with `continuity issue verify <TASK-ID>` before resuming.

## Workspace lifecycle

Keep one permanent main checkout as the project's home base and use it for sequential work. When genuine parallelism or isolation is useful, create one managed linked worktree per independent active task under `<canonical-root>/pcm/worktree/<TASK-ID>`, not one per session or agent; resume it across sessions. Do not create sibling clones or arbitrary worktree paths.

Before creating a tree, PCM checks Git's registered worktrees and its private per-device workspace registry. Register existing checkouts on other drives with `continuity workspace register --root <checkout>`. One clean, unlocked match is reused; a dirty, locked, conflicting, or ambiguous match stops before creation. PCM does not scan drives. Registry paths stay local and must never be copied into shared records.

After required checks pass, the PR is merged, the task record is complete, and the worktree is clean, run `continuity worktree remove <TASK-ID>`. It verifies the GitHub PR, required checks, and merged commit and refuses locked/pinned, dirty, or unproven cleanup; never force-remove unfinished or user-modified work. For a short audit hold, record the reason, expected release date, private workspace ID, and unlock/remove next action in the completed task's checkpoint, then pin the tree with `git worktree lock --reason "<reason; release YYYY-MM-DD>" <path>`. When the audit ends, unlock it and run normal verified cleanup. Other Git hosts remain unsupported for cleanup until PCM has a tested CI/merge verifier for them. `workspace.mode: single-checkout` is available when strict one-checkout behavior is preferred.

Reuse immutable package caches where supported, but keep mutable dependency environments separate when lockfiles or runtimes differ. Track dependency changes in manifests, lockfiles, or patch files.

## Finding earlier project documents

When `.continuity/documents.json` is present, it is the machine-readable inventory and `docs/CONTINUITY_INDEX.md` is its generated human view. Every fresh session or task takeover/resumption must consult the inventory before choosing its next action, not only before writing a document: run `git fetch origin`, then use `continuity docs find "<issue title and task-objective terms>" --task <TASK-ID>` and read matching records and their declared neighbors. The search is deterministic metadata search, not semantic whole-repository search. `continuity validate` checks the generated view; use `continuity docs render` to refresh its freshness labels after source edits. A `NEEDS_REVIEW` result preserves historical evidence but says not to rely on it without checking the current file.

## Degraded continuity

Execution safety and existing authorization outrank continuity bookkeeping. If canonical continuity state is temporarily unavailable, do not stop safe work or repair storage merely to force a write. Use an already-authorized alternate checkout/host and run `continuity checkpoint <TASK-ID> --root <canonical-root> --recovery-root <alternate-root> ...` to write the JSON recovery receipt under `.continuity/recovery/`; do not create an ad-hoc Markdown checkpoint under `checkpoints/` or replace the alternate task file. Reconcile it later with `continuity recovery reconcile --root <canonical-root> --file <receipt>`. The repository/task lineage is authoritative; a physical worktree is not.

Normal checkpointing is a delivery operation, not a local note: commit the product change first, then run `continuity checkpoint`. The command prints a `REQUEST_ID`, commits the canonical checkpoint and synchronously pushes the task branch to `origin`; if interrupted, rerun with the same `--request-id` to avoid a duplicate (changed payload with the same ID is rejected). Open or update a PR after pushing. GitHub CI and auto-merge then run asynchronously, gated by required reviews/checks and any merge queue. Confirm the merge before marking complete or removing the worktree.

Delegated agents are temporary workers. Capture each worker's result and evidence
in the parent task/checkpoint, then explicitly close it immediately. Stop and
close workers that are no longer needed, including completed, interrupted,
failed, cancelled, and timed-out workers. Do not leave completed workers open for
possible future use; see `docs/AGENT_LIFECYCLE.md`.

## Continuity records

<!-- pcm:policy {"id":"continuity-records","policy_version":"1.3.0","protocol_version":"0.1.0-draft"} -->

Write continuity issues, updates, pull requests, and project-state documents so a new reader can understand the problem, human outcome, scope, evidence, and next action without the original chat. Cite external claims and link repository claims to their revision or CI evidence. Include reproduction detail only when it is needed to verify the claim. Keep PR openings skimmable; put long logs in linked artifacts. Preserve project ownership outside continuity. Do not claim automatic tracker sync or chat capture unless implemented and tested. GitHub's issue-closing keywords in PR descriptions and commit messages remain active under negation; use them only when the issue should complete at merge, and verify issue status afterward.

## Verification

Each task names the useful outcome for a person and the smallest checks that can verify it. Prefer deterministic checks. Use a fresh-session holdout only when the promise is about what a new session can discover or do; judge it against visible requirements, not hidden expectations. A passing test does not replace the promised human-visible result.

<!-- pcm:github-progression:start -->
## GitHub-owned progression

GitHub Issues are required for PCM-governed project work and own task scope, acceptance, priority, ownership, dependencies, lifecycle and durable project progression. Merged default-branch history owns accepted code and normative/domain documents; PR checks and merge records own delivery facts. Checked-in PROJECT/CURRENT/TASK/checkpoint/handoff documents are mandatory versioned projections for task state, not a parallel authority. Local files, registries, context packs and chat are ephemeral execution aids. Domain-document ownership stays with the target project.

Every issue progress update MUST link the leaf child issue that owns the work, its parent ancestry and dependencies (or explicitly none). A top-level deliverable identifies itself as the leaf and says parent: none. Create one child per independently deliverable scope, never one per comment. Record task ID, primary writer and branch on the issue before creating its repository projection. Re-read live issues and relevant source revisions before resuming; the issue verifier checks identity/status, not semantic agreement.

Authorized owner/user direction can revise intent: record it on the owning GitHub issue with a correction/supersession link before dependent work. It cannot alter observed CI/merge facts or waive required gates. Stale projections yield to their field's authority. If direction, ownership or evidence conflicts remain unresolved, pause affected work and record uncertainty; continue independent safe work. One primary writer owns each task branch/checkpoint stream. Coordinate shared-document edits through linked issues/PRs, re-read the current base and reconcile concurrent changes; never force-push or overwrite another writer. Issue prose is not an atomic lock.

Label observed results, repository/external evidence, agent reports and inference separately. Preserve contradictory evidence with source/revision and mark conclusions disputed or unknown until resolved. Append correction/supersession evidence; never rewrite checkpoint history. An upstream correction MUST identify affected descendants and assumptions on their issues; pause, re-plan and revalidate dependent work before resuming. Follow explicit parent/dependency links within the affected scope; cycles or unknown lineage block affected claims. No graph database, local canonical ledger or autonomous polling agent is required.

Before every push, synchronize relevant docs and task/checkpoint projections, CURRENT/HANDOFF when affected, and reviewed catalog/generated index. Record leaf/parent/dependency links, source issue/comment revision, as-of status, evidence, blockers and next action. Commit product/docs first; `continuity checkpoint` then commits and synchronously pushes the checkpoint with a stable request ID. After every successful push, manually publish a leaf issue receipt keyed by request ID and exact pushed SHA, linking changed docs/checkpoint, PR, tests and pending gates; add a linked parent progression update. Retry a missing receipt without another checkpoint/push; inspect for the same key before posting. --receipt-repo and --receipt-issue are opt-in and still require a proven lookup; omit them and the receipt stays manual. Automatic issue-comment synchronization is not implemented. Issue #67 remains open.

Required CI and GitHub auto-merge are mandatory. Verify protection, required reviews/checks on the exact current-base or merge-queue candidate, and auto-merge; missing, failed, skipped, stale or unverified gates fail closed: no completion or cleanup. After CI/merge, append the exact check results, PR/merge SHA and live issue status to the leaf and link the parent update; fetch and verify accepted history. Reconcile material doc/status corrections in a new synchronized increment. Receipt-only transitions need no recursive doc commit: docs retain an explicit as-of/pending state and point to the live issue. Never label local-only or merely pushed work delivered. Preserve unsafe resources and keep incomplete issues open.
<!-- pcm:github-progression:end -->

<!-- pcm:issue-log-format:start -->
## Issue log format (issue-log-format 1.0.0)

<!-- pcm:policy {"id":"issue-log-format","policy_version":"1.0.0","protocol_version":"0.1.0-draft"} -->

Write issue logs, progress updates, and pull requests in one plain-language shape a newcomer can follow. Pick the tier by the kind of issue, not by preference. **Core tier (every issue log):** title states the problem and intended direction; a 1-3 paragraph summary naming who/what is affected, the consequence, and what this proposes; identity and lineage (leaf owning issue, parent ancestry or none, task ID, primary writer, branch); observed facts vs interpretation, with inferences labelled *inferred*; acceptance criteria with numeric thresholds marked *(proposed)* when untested; boundaries/non-goals and one next action. **Investigation tier (incidents, failures, research, design issues):** numbered symptoms; hypotheses with Status, confirm/refute, and experiment; evidence with provenance; a **Counter-signal** entry when one exists; honest caveat; problems-vs-gaps; a **Proposal** labelled *(proposal)* stating none of it exists unless named as existing. **Pull requests open reader-first:** problem and consequence, what changes, how to verify, and what stays unchanged; lineage links; evidence and one next action; long logs collapsed or linked; reference issues with "Refs #<number>" and use closing keywords only when closing at merge is intended. No private absolute paths or secrets; link rather than paste long logs. See `docs/ISSUE_LOG_FORMAT.md` for the full format, exemplar, and examples.
<!-- pcm:issue-log-format:end -->
