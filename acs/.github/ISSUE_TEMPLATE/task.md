---
name: Continuity task
about: Record an actionable continuity outcome with clear evidence
title: "Continuity: [human outcome]"
labels: ""
assignees: ""
---

## Problem and consequence

Who or what is affected, and what becomes harder, unsafe, or impossible?

## Desired result

What observable result would resolve the problem?

## Scope and boundaries

What is included, what is not, and what dependencies or uncertainty matter?

## How we will know

List observable acceptance checks proportionate to the outcome.

## Evidence and sources

Link relevant repository state at a revision. Cite direct sources for external factual claims.

## Reproduction (only when needed)

Record the starting revision, relevant inputs/configuration, runtime, exact command or prompt, observed result, and limitations.

## Continuity links

- Leaf owning issue, parent ancestry and dependencies (or explicitly none):
- Task ID, primary writer, branch and linked repository projection:
- Related issues or PRs:
- Current owner and next action:

This template records context; it does not automatically synchronize this issue with repository tasks, pull requests, or checkpoints.

<!-- pcm:github-progression:start -->
## GitHub-owned progression

GitHub Issues are required for PCM-governed project work and own task scope, acceptance, priority, ownership, dependencies, lifecycle and durable project progression. Merged default-branch history owns accepted code and normative/domain documents; PR checks and merge records own delivery facts. Checked-in PROJECT/CURRENT/TASK/checkpoint/handoff documents are mandatory versioned projections for task state, not a parallel authority. Local files, registries, context packs and chat are ephemeral execution aids. Domain-document ownership stays with the target project.

Every issue progress update MUST link the leaf child issue that owns the work, its parent ancestry and dependencies (or explicitly none). A top-level deliverable identifies itself as the leaf and says parent: none. Create one child per independently deliverable scope, never one per comment. Record task ID, primary writer and branch on the issue before creating its repository projection. Re-read live issues and relevant source revisions before resuming; the issue verifier checks identity/status, not semantic agreement.

Authorized owner/user direction can revise intent: record it on the owning GitHub issue with a correction/supersession link before dependent work. It cannot alter observed CI/merge facts or waive required gates. Stale projections yield to their field's authority. If direction, ownership or evidence conflicts remain unresolved, pause affected work and record uncertainty; continue independent safe work. One primary writer owns each task branch/checkpoint stream. Coordinate shared-document edits through linked issues/PRs, re-read the current base and reconcile concurrent changes; never force-push or overwrite another writer. Issue prose is not an atomic lock.

Label observed results, repository/external evidence, agent reports and inference separately. Preserve contradictory evidence with source/revision and mark conclusions disputed or unknown until resolved. Append correction/supersession evidence; never rewrite checkpoint history. An upstream correction MUST identify affected descendants and assumptions on their issues; pause, re-plan and revalidate dependent work before resuming. Follow explicit parent/dependency links within the affected scope; cycles or unknown lineage block affected claims. No graph database, local canonical ledger or autonomous polling agent is required.

Before every push, synchronize relevant docs and task/checkpoint projections, CURRENT/HANDOFF when affected, and reviewed catalog/generated index. Record leaf/parent/dependency links, source issue/comment revision, as-of status, evidence, blockers and next action. Commit product/docs first; `continuity checkpoint` then commits and synchronously pushes the checkpoint with a stable request ID. Push at every stop, but open the pull request when the work is done or the branch reaches the cadence limit (`.coord/cadence.json`; by default 10 commits, 400 changed lines or 24 hours), not at every stop; never poll GitHub more often than its `min_poll_seconds` (default 60). Publish a leaf issue receipt keyed by request ID and exact pushed SHA, linking changed docs/checkpoint, PR, tests and pending gates, when the pull request opens, at a handoff or block, and once after the merge, not after every push; each receipt names every request ID and pushed SHA since the previous one, so every push stays traceable; add the linked parent progression update with the merge receipt. Put small steps on the leaf issue's checklist; file a sub-issue only for a piece with its own pull request. Retry a missing receipt without another checkpoint/push; inspect for the same key before posting. --receipt-repo and --receipt-issue are opt-in and still require a proven lookup; omit them and the receipt stays manual. Automatic issue-comment synchronization is not implemented. Issue #67 remains open.

Required CI and GitHub auto-merge are mandatory. Where a repository turns GitHub auto-merge off (its `allow_auto_merge` setting), it merges by hand: leave the pull request open, ready and passing, and do not call the work delivered until it merges. Arm auto-merge only on a pull request opened by the owner or a trusted collaborator (the repository's admins, and logins in its `AUTO_MERGE_AUTHORS` variable); anyone else's, a fork's included, waits for the owner's review. Verify protection, required reviews/checks on the exact current-base or merge-queue candidate, and auto-merge; missing, failed, skipped, stale or unverified gates fail closed: no completion or cleanup. After CI/merge, the merge receipt carries the exact check results, PR/merge SHA and live issue status and links the parent update; fetch and verify accepted history. Reconcile material doc/status corrections in a new synchronized increment. Receipt-only transitions need no recursive doc commit: docs retain an explicit as-of/pending state and point to the live issue. Never label local-only or merely pushed work delivered. Preserve unsafe resources and keep incomplete issues open.

On a host other than GitHub (GitLab, Gitea or Forgejo, a plain Git server) or without a signed-in `gh`, issue verification, receipts and verified worktree cleanup do not run: continuity keeps Git-only durability (checkpoint commits pushed to origin), a human records scope and progress on that host by hand, and `continuity preflight --root <root>` prints which duties the host carries. SPEC section 8.3 names the four operations a host adapter must provide; only the GitHub adapter exists.
<!-- pcm:github-progression:end -->

<!-- pcm:issue-log-format:start -->
## Issue log format (issue-log-format 1.2.0)

<!-- pcm:policy {"id":"issue-log-format","policy_version":"1.2.0","protocol_version":"0.1.0-draft"} -->

Write issue logs, progress updates, and pull requests in one plain-language shape a newcomer can follow. Pick the tier by the kind of issue, not by preference. **Core tier (every issue log):** title states the problem and intended direction; a 1-3 paragraph summary naming who/what is affected, the consequence, and what this proposes; identity and lineage (leaf owning issue, parent ancestry or none, task ID, primary writer, branch); observed facts vs interpretation, with inferences labelled *inferred*; acceptance criteria with numeric thresholds marked *(proposed)* when untested; boundaries/non-goals and one next action. **Investigation tier (incidents, failures, research, design issues):** numbered symptoms; hypotheses with Status, confirm/refute, and experiment; evidence with provenance; a **Counter-signal** entry when one exists; honest caveat; problems-vs-gaps; a **Proposal** labelled *(proposal)* stating none of it exists unless named as existing. **Pull requests open reader-first:** problem and consequence, what changes, how to verify, and what stays unchanged; lineage links; evidence and one next action; long logs collapsed or linked; reference issues with "Refs #<number>" and use closing keywords only when closing at merge is intended. **Diagrams (mermaid):** when a record describes a flow with 4+ ordered steps or 2+ branches, add a fenced mermaid diagram *and* keep an adjacent text list or table so the record survives render failure; default to `graph TD` (vertical) because wide `LR` flows shrink to illegible strips on phones — reserve `LR` for 4 or fewer short nodes; cap 8 nodes and 6-word labels; wrap diagrams that may exceed the container width inside `<details>` (GitHub mounts the renderer lazily on expand); preview the rendered diagram before publishing (broken syntax shows a visible parse error) and never cite renderer URLs as standalone sources. **Readability rules:** give every SHA, comment id, flag, file path, or tool name a plain-word meaning in the same sentence before it carries load; write evidence as the claim first, numbers as support (“nothing this change could break failed (263 tests, same six machine-environment failures as before)”), never bare counts; no unexplained acronym or bare identifier on first use in any tier; PR openings and checkpoint Completed/Next lines start with one problem sentence a newcomer can follow; the rule set applies to CURRENT projections and checkpoint entries exactly as to issue logs. No private absolute paths or secrets; link rather than paste long logs. See `docs/ISSUE_LOG_FORMAT.md` for the full format, exemplar, and examples.
<!-- pcm:issue-log-format:end -->
