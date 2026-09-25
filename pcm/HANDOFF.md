# Current Handoff

This repository is ready for a fresh PCM development session without prior chat history.

## Current projection — policy increment pending delivery

Leaf [#66 / PCM-0025](https://github.com/Pukujan/project-continuity-modules/issues/66) owns this bounded policy work under parent [#53 / PCM-0024](https://github.com/Pukujan/project-continuity-modules/issues/53). Branch: `task/PCM-0025-github-progression-policy`; primary writer: Astra/Codex. Source issue update observed: 2026-09-24T15:32:31Z. Prerequisite authority/checkpoint slices are merged; no unresolved prerequisite. Automation sibling [#67 / PCM-0026](https://github.com/Pukujan/project-continuity-modules/issues/67) depends on #66 and is queued; #33 cleanup remains independent.

Candidate work defines GitHub-owned progression, mandatory synchronized docs, finite receipts, bounded conflicts/lineage corrections and deterministic generated/adopter guidance tests. Local Python 3.12 gates passed: 78 tests in 350.921s; five focused policy tests also passed after the indexed-checkpoint clarification; Ruff, MyPy, compileall, continuity validation, generated-index synchronization and diff checks passed. Wheel and source archive build/install parity passed for minimal/software profiles and PCM-0018 features. Pushed checkpoint, PR, required hosted checks and auto-merge are pending in this snapshot; the live leaf issue owns subsequent events.

The [owner decision](https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5816655372) supersedes all historical second-account blockers below: the accepted #63 holdouts/local tests suffice for their stated claims; cross-account permissions remain untested but are not required. #53 remains OPEN for its broader acceptance. Historical prose below is preserved as as-of evidence, not current instructions.

## Next atomic action

Publish the synchronized #66 checkpoint/PR, then verify exact required CI and auto-merge and reconcile GitHub receipts. Receipt-only transitions need no recursive doc commit; material corrections require another synchronized increment.

## Historical status (superseded by projection above)

- PCM-0017 is complete: PR #49 delivered package/runtime version identity and isolated wheel/sdist generated-output parity on Python 3.11 and 3.12; PR #50 completed canonical closeout, and issue #31 is closed. PCM-0018 / [GitHub issue #33](https://github.com/Pukujan/project-continuity-modules/issues/33) remains active. Its implementation PR #51 merged automatically at `98747fce4d5c805670dc3b00bb572e5c02706237`; all hosted quality, Python 3.11/3.12 test, package, package-parity, and auto-merge checks passed. The permanent checkout is now clean on `main` at that commit. The implementation candidate is version 0.3.0 and has not been published. Independent baseline and candidate fresh-session reports are recorded in the PCM-0018 task; the candidate found the seeded PCM-0015 research/plan and related catalog entries. The candidate trial clone remains and the baseline trial directory retains a hidden `.git` marker; ordinary cleanup was denied and the environment's automatic review blocked follow-up removal. Cleanup and separate merged closeout remain outstanding. Issue #33 stays open.
- PCM-0024 / [GitHub issue #53](https://github.com/Pukujan/project-continuity-modules/issues/53) is active on the existing `task/PCM-0024-github-authority` checkout. Its GitHub task authority and checkout reuse merged in PR #56 at `4033b49`; stress and writer/worktree safeguards merged in PR #57 at `b9a23f7612b41902e2b5c10c1da086e33888ef22`; lifecycle-language safeguards merged in PR #61 at `18e262d250634f8297391391ec793ed91c49a5ee`; checkpoint/index reconciliation merged in PR #62 at `3ce80b4a4ef85c5ca02c9622697b5a4422cdbf45`; and independent holdout/evidence-boundary reconciliation merged in PR #64 at `fbd52fec989a6b05a6d8bfa733ef4ca314e213d3`. The 73-test suite, stress profile, Python 3.12 wheel/sdist parity, and checkout reuse tests passed. No-history subagents independently inspected baseline `5304bfa` and candidate `18e262d`; the focused checkout/checkpoint suite passed 24 tests. Those results cover agent recovery and local writer/reuse behavior, but not permissions or hosted delivery by a second GitHub identity. Issue #53 remains open for that explicit hosted multi-user criterion. The independent PCM-0018 / #33 reports are recorded, but #33 remains open for its own trial-copy cleanup and separate closeout.
- PCM-0019's managed-worktree implementation, cleanup safeguards, and time-bounded audit holds are in merged PRs #45–#47; final task/checkpoint/handoff closeout is PR #48. Issues #20, #34, and #39 are closed after protected CI; the PCM-0019 task branches are removed and the permanent main checkout is the only registered worktree. Five disposable holdout clone folders remain outside the repository because the local recursive-deletion operation was blocked; they are not registered worktrees.
- The final independent candidate and retention-variant audits passed on the merged snapshot; full suites passed 46 tests each on Python 3.11 and 3.12. Detailed evidence, exact prompts, research citations, and measurement limits are in `tasks/TASK-PCM-0019-managed-worktrees.md` and GitHub issue comments #34/#39.
- #42 README image recovery remains deferred; do not search for or generate images until the user provides the promised plan.
- PCM-0023 / issue #32 completed in PR #43 at `867e5ae`; closeout PR #44 updated the canonical task status and closed #32.
- PCM-0015 is complete as a planning-only task. Its plan merged in PR #29 at `b379ba3`; issue #28 is closed. The plan does not mean the proposed capabilities have been implemented.
- PCM-0014 is complete and merged automatically in PR #26 at `b9e0f7c`; issue #24 is closed.
- Issue #17's baseline failure, fix, and blind rerun are recorded; it closed after status correction in PR #37. Issue #15 remains open because it includes an unperformed target-repository remediation outside current scope. Issue #42 remains deferred until the user provides the promised image plan; do not search for or generate images.
- PCM-0012 and PCM-0013 remain separately recorded workspace-policy histories.
- Other reports stay separately scoped; consult GitHub for the current open list before selecting new work.
- The active PCM-0024 source candidate is `0.4.0`, sourced from `continuity.__version__`; it has not been published. The protocol remains independently declared as `0.1.0-draft`.
- Protocol version remains: `0.1.0-draft`

## Read exactly this first

1. `PROJECT.md`
2. `AGENTS.md`
3. `checkpoints/CURRENT.md`
4. `tasks/TASK-PCM-0025-github-progression-policy.md`
5. `SPEC.md`
6. `docs/HANDOFF_PROTOCOL.md`
7. `docs/TESTING_POLICY.md`
8. `docs/AGENT_LIFECYCLE.md`
9. `docs/VERSIONING.md`

On every task takeover/resumption, use the optional catalog before choosing
the next action: run `git fetch origin`, then `continuity docs find "<issue
title and task-objective terms>" --task PCM-0025` and read matching records and
their declared neighbors. The catalog and generated human index are
`.continuity/documents.json` and `docs/CONTINUITY_INDEX.md`; do not invent
another index when the catalog is present.

## Historical next action (superseded)

The baseline/candidate no-history holdouts and focused local tests are recorded in child issue [#63](https://github.com/Pukujan/project-continuity-modules/issues/63) and [the PCM-0024 task](tasks/TASK-PCM-0024-github-authority.md). They verify fresh-session recovery and local checkout/writer behavior. This session has only the repository owner's GitHub identity, so cross-account permissions and an actual second user's hosted push/PR/CI path remain unverified. Keep #53 open unless its owner changes that acceptance criterion; keep #33 open for its separate cleanup/closeout. Leave issues #15 and #42 open for their explicit scope constraints; do not modify excluded target repositories or search/generate the images.

## Authority

PCM owns only its protocol/tooling development state. When PCM is used as a helper for another repository, that target repository owns its PROJECT/CURRENT/TASK/checkpoint state. A target is not integrated until `continuity validate --root <target>` succeeds. The authoritative identity is the repository/task lineage and Git history; alternate worktrees/hosts are execution infrastructure. Normal checkpoints commit and push the task branch; CI and pull-request automation deliver the pushed state. Use and later reconcile a recovery receipt when canonical continuity state is temporarily unavailable.

## Workspace policy

Keep one permanent main checkout as the project home base and use it for sequential work. Create a linked worktree only when parallelism or isolation is useful, under `pcm/worktree/<TASK-ID>`, and reuse that task's worktree across sessions. Do not create one per agent or sibling clones. After required checks pass, the PR is merged, the task is complete, and the worktree is clean, run `continuity worktree remove <TASK-ID>`; it verifies GitHub delivery and refuses locked/pinned or otherwise unsafe cleanup. For a short audit hold, record its reason, expected release date, private workspace ID, and unlock/remove next action in the completed task's checkpoint, then lock the tree with `git worktree lock --reason "<reason; release YYYY-MM-DD>" <path>`. When the audit ends, return to the permanent checkout, unlock the tree, and run the normal verified cleanup. Other Git hosts remain unsupported for cleanup until PCM has a tested CI/merge verifier for them. Shared package caches are encouraged, but mutable dependency environments stay separate when their lockfiles or runtimes differ. Strict `single-checkout` mode remains available.

## Continuity records

<!-- pcm:policy {"id":"continuity-records","policy_version":"1.3.0","protocol_version":"0.1.0-draft"} -->

Issue logs, progress updates, pull requests, and continuity documents should explain the human problem and observable outcome, then scope, evidence, and one next action. Cite external claims and link repository claims to a revision or CI result. Include reproduction detail only when it helps verify a claim; keep PR openings skimmable and link long logs. The CLI does not automatically synchronize arbitrary trackers; reconcile authoritative issue status explicitly. GitHub closing keywords in PR descriptions or commit messages still act under negation; use them only when the referenced issue should complete at merge. Use `Refs #<number>` for progress-only changes and verify issue status after every merge.

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
## Issue log format (issue-log-format 1.1.0)

<!-- pcm:policy {"id":"issue-log-format","policy_version":"1.1.0","protocol_version":"0.1.0-draft"} -->

Write issue logs, progress updates, and pull requests in one plain-language shape a newcomer can follow. Pick the tier by the kind of issue, not by preference. **Core tier (every issue log):** title states the problem and intended direction; a 1-3 paragraph summary naming who/what is affected, the consequence, and what this proposes; identity and lineage (leaf owning issue, parent ancestry or none, task ID, primary writer, branch); observed facts vs interpretation, with inferences labelled *inferred*; acceptance criteria with numeric thresholds marked *(proposed)* when untested; boundaries/non-goals and one next action. **Investigation tier (incidents, failures, research, design issues):** numbered symptoms; hypotheses with Status, confirm/refute, and experiment; evidence with provenance; a **Counter-signal** entry when one exists; honest caveat; problems-vs-gaps; a **Proposal** labelled *(proposal)* stating none of it exists unless named as existing. **Pull requests open reader-first:** problem and consequence, what changes, how to verify, and what stays unchanged; lineage links; evidence and one next action; long logs collapsed or linked; reference issues with "Refs #<number>" and use closing keywords only when closing at merge is intended. **Diagrams (mermaid):** when a record describes a flow with 4+ ordered steps or 2+ branches, add a fenced mermaid diagram *and* keep an adjacent text list or table so the record survives render failure; default to `graph TD` (vertical) because wide `LR` flows shrink to illegible strips on phones — reserve `LR` for 4 or fewer short nodes; cap 8 nodes and 6-word labels; wrap diagrams that may exceed the container width inside `<details>` (GitHub mounts the renderer lazily on expand); preview the rendered diagram before publishing (broken syntax shows a visible parse error) and never cite renderer URLs as standalone sources. No private absolute paths or secrets; link rather than paste long logs. See `docs/ISSUE_LOG_FORMAT.md` for the full format, exemplar, and examples.
<!-- pcm:issue-log-format:end -->
