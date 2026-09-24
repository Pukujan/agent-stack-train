# Current Handoff

This repository is ready for a fresh PCM development session without prior chat history.

## Current status

- PCM-0017 is complete: PR #49 delivered package/runtime version identity and isolated wheel/sdist generated-output parity on Python 3.11 and 3.12; PR #50 completed canonical closeout, and issue #31 is closed. PCM-0018 / [GitHub issue #33](https://github.com/Pukujan/project-continuity-modules/issues/33) remains active. Its implementation PR #51 merged automatically at `98747fce4d5c805670dc3b00bb572e5c02706237`; all hosted quality, Python 3.11/3.12 test, package, package-parity, and auto-merge checks passed. The permanent checkout is now clean on `main` at that commit. The implementation candidate is version 0.3.0 and has not been published. Independent baseline and candidate fresh-session reports are recorded in the PCM-0018 task; the candidate found the seeded PCM-0015 research/plan and related catalog entries. The candidate trial clone remains and the baseline trial directory retains a hidden `.git` marker; ordinary cleanup was denied and the environment's automatic review blocked follow-up removal. Cleanup and separate merged closeout remain outstanding. Issue #33 stays open.
- PCM-0024 / [GitHub issue #53](https://github.com/Pukujan/project-continuity-modules/issues/53) is active on the existing `task/PCM-0024-github-authority` checkout. Its GitHub task authority and checkout reuse merged in PR #56 at `4033b49`; follow-up stress and writer/worktree safeguards merged automatically in PR #57 at `b9a23f7612b41902e2b5c10c1da086e33888ef22` after all six required checks passed. The local 72-test suite, stress profile, Python 3.12 wheel/sdist parity, and checkout reuse on different Windows volumes passed. Independent no-history issue-53 holdouts and an actual second authorized user on a separate drive remain outstanding. PCM-0018 / #33 remains open for owner cleanup and separate closeout.
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
4. `tasks/TASK-PCM-0024-github-authority.md`
5. `SPEC.md`
6. `docs/HANDOFF_PROTOCOL.md`
7. `docs/TESTING_POLICY.md`
8. `docs/AGENT_LIFECYCLE.md`
9. `docs/VERSIONING.md`

On every task takeover/resumption, use the optional catalog before choosing
the next action: run `git fetch origin`, then `continuity docs find "<issue
title and task-objective terms>" --task PCM-0024` and read matching records and
their declared neighbors. The catalog and generated human index are
`.continuity/documents.json` and `docs/CONTINUITY_INDEX.md`; do not invent
another index when the catalog is present.

## Exact next action

Commit and push the verified follow-up, then publish a PR linked to #53 without closing it. After merge, run independent no-history issue-53 holdouts and arrange a two-user, separate-drive adoption with an independently authenticated collaborator. The task's prior evidence, exact open criteria, and collaboration boundary are in [tasks/TASK-PCM-0024-github-authority.md](tasks/TASK-PCM-0024-github-authority.md). PCM-0018 / #33 remains open for owner cleanup and separate closeout; do not claim it is complete. Leave issues #15 and #42 open for their explicit scope constraints; do not modify excluded target repositories or search/generate the images.

## Authority

PCM owns only its protocol/tooling development state. When PCM is used as a helper for another repository, that target repository owns its PROJECT/CURRENT/TASK/checkpoint state. A target is not integrated until `continuity validate --root <target>` succeeds. The authoritative identity is the repository/task lineage and Git history; alternate worktrees/hosts are execution infrastructure. Normal checkpoints commit and push the task branch; CI and pull-request automation deliver the pushed state. Use and later reconcile a recovery receipt when canonical continuity state is temporarily unavailable.

## Workspace policy

Keep one permanent main checkout as the project home base and use it for sequential work. Create a linked worktree only when parallelism or isolation is useful, under `pcm/worktree/<TASK-ID>`, and reuse that task's worktree across sessions. Do not create one per agent or sibling clones. After required checks pass, the PR is merged, the task is complete, and the worktree is clean, run `continuity worktree remove <TASK-ID>`; it verifies GitHub delivery and refuses locked/pinned or otherwise unsafe cleanup. For a short audit hold, record its reason, expected release date, exact path, and unlock/remove next action in the completed task's checkpoint, then lock the tree with `git worktree lock --reason "<reason; release YYYY-MM-DD>" <path>`. When the audit ends, return to the permanent checkout, unlock the tree, and run the normal verified cleanup. Other Git hosts remain unsupported for cleanup until PCM has a tested CI/merge verifier for them. Shared package caches are encouraged, but mutable dependency environments stay separate when their lockfiles or runtimes differ. Strict `single-checkout` mode remains available.

## Continuity records

<!-- pcm:policy {"id":"continuity-records","policy_version":"1.1.0","protocol_version":"0.1.0-draft"} -->

Issue logs, progress updates, pull requests, and continuity documents should explain the human problem and observable outcome, then scope, evidence, and one next action. Cite external claims and link repository claims to a revision or CI result. Include reproduction detail only when it helps verify a claim; keep PR openings skimmable and link long logs. The CLI does not automatically synchronize arbitrary trackers; reconcile authoritative issue status explicitly. GitHub closing keywords in PR descriptions or commit messages still act under negation; use them only when the referenced issue should complete at merge. Use `Refs #<number>` for progress-only changes and verify issue status after every merge.
