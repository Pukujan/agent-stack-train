# Observational Issue Ops — Project Contract

<!-- continuity:project {"id":"observational-issue-ops","protocol_version":"0.1.0-draft","schema":"project-continuity.project.v1","title":"Observational Issue Ops"} -->

<!-- pcm:github-progression:start -->
## GitHub-owned progression

GitHub Issues are required for PCM-governed project work and own task scope, acceptance, priority, ownership, dependencies, lifecycle and durable project progression. Merged default-branch history owns accepted code and normative/domain documents; PR checks and merge records own delivery facts. Checked-in PROJECT/CURRENT/TASK/checkpoint/handoff documents are mandatory versioned projections for task state, not a parallel authority. Local files, registries, context packs and chat are ephemeral execution aids. Domain-document ownership stays with the target project.

Every issue progress update MUST link the leaf child issue that owns the work, its parent ancestry and dependencies (or explicitly none). A top-level deliverable identifies itself as the leaf and says parent: none. Create one child per independently deliverable scope, never one per comment. Record task ID, primary writer and branch on the issue before creating its repository projection. Re-read live issues and relevant source revisions before resuming; the issue verifier checks identity/status, not semantic agreement.

Authorized owner/user direction can revise intent: record it on the owning GitHub issue with a correction/supersession link before dependent work. It cannot alter observed CI/merge facts or waive required gates. Stale projections yield to their field's authority. If direction, ownership or evidence conflicts remain unresolved, pause affected work and record uncertainty; continue independent safe work. One primary writer owns each task branch/checkpoint stream. Coordinate shared-document edits through linked issues/PRs, re-read the current base and reconcile concurrent changes; never force-push or overwrite another writer. Issue prose is not an atomic lock.

Label observed results, repository/external evidence, agent reports and inference separately. Preserve contradictory evidence with source/revision and mark conclusions disputed or unknown until resolved. Append correction/supersession evidence; never rewrite checkpoint history. An upstream correction MUST identify affected descendants and assumptions on their issues; pause, re-plan and revalidate dependent work before resuming. Follow explicit parent/dependency links within the affected scope; cycles or unknown lineage block affected claims. No graph database, local canonical ledger or autonomous polling agent is required.

Before every push, synchronize relevant docs and task/checkpoint projections, CURRENT/HANDOFF when affected, and reviewed catalog/generated index. Record leaf/parent/dependency links, source issue/comment revision, as-of status, evidence, blockers and next action. Commit product/docs first; `continuity checkpoint` then commits and synchronously pushes the checkpoint with a stable request ID. After every successful push, manually publish a leaf issue receipt keyed by request ID and exact pushed SHA, linking changed docs/checkpoint, PR, tests and pending gates; add a linked parent progression update. Retry a missing receipt without another checkpoint/push; inspect for the same key before posting. --receipt-repo and --receipt-issue are opt-in and still require a proven lookup; omit them and the receipt stays manual. Automatic issue-comment synchronization is not implemented; issue #67 is CLOSED (owner freeze decision 2026-09-25) and its unmet guaranteed-completion acceptance transferred to #110.

Required CI and GitHub auto-merge are mandatory. Arm auto-merge only after the increment's final push: a later push races the merge window and strands outside accepted history. Verify protection, required reviews/checks on the exact current-base or merge-queue candidate, and auto-merge; missing, failed, skipped, stale or unverified gates fail closed: no completion or cleanup. After CI/merge, append the exact check results, PR/merge SHA and live issue status to the leaf and link the parent update; fetch and verify accepted history. Reconcile material doc/status corrections in a new synchronized increment. Receipt-only transitions need no recursive doc commit: docs retain an explicit as-of/pending state and point to the live issue. Never label local-only or merely pushed work delivered. Preserve unsafe resources and keep incomplete issues open.
<!-- pcm:github-progression:end -->

## Main goal

Hold one shared, versioned protocol for reporting what someone observed — a three-plane, non-binding observational-issue form and the triage that labels it — so every repository in the stack files an observation the same way and can follow it from first sighting to a decision.

## Why

The same issue-governance rule was hand-copied into several repositories, and the same version pins into many files. Copies drift, so a report filed in one repository no longer matches the trail in another, and nobody can tell which copy is authoritative. Measured 2026-10-01: one CGM version pin lived in thirteen files across three revisions. OIO removes the copy — the rule lives in one place and every repository points at it.

## Scope

- The three-plane observational-issue form (`.github/ISSUE_TEMPLATE/observational-issue.yml`).
- The triage automation that reads a filed issue and applies the plane and priority labels (`.github/workflows/issue-triage.yml`).
- The release train: `stack-releases.json`, the single place adopters read the certified versions of OIO, PCM, CGM, and ACS from.

## Non-goals

- Not a tracker, a workflow engine, or a place to store another project's issues. Each repository keeps its own issue history.
- Does not own any adopter's product code, issues, or releases.
- Does not replace PCM (execution continuity), CGM (narrative and style), or ACS (runtime safety and the hotloader). OIO consumes them.
- Does not make any observation binding. Every issue filed under this protocol is a proposal.

## Definition of success

- A maintainer or agent can file one observation and have it labelled by plane and priority without hand-editing a repository's own copy of the rules.
- An adopter reads its stack versions from one manifest and a check fails closed when a projection disagrees.
- The protocol, the triage, and the release train live in exactly one repository, and every other repository points at it.
