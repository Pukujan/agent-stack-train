# Current Handoff

This repository is ready for a fresh PCM development session without prior chat history.

## Current status

- No active continuity task after the PCM-0017 implementation merged. PR #49 delivered package/runtime version identity and isolated wheel/sdist generated-output parity on Python 3.11 and 3.12. This closeout PR updates the canonical task/checkpoint state and closes issue #31 only after its six required checks pass and it merges.
- PCM-0019's managed-worktree implementation, cleanup safeguards, and time-bounded audit holds are in merged PRs #45–#47; final task/checkpoint/handoff closeout is PR #48. Issues #20, #34, and #39 are closed after protected CI; the PCM-0019 task branches are removed and the permanent main checkout is the only registered worktree. Five disposable holdout clone folders remain outside the repository because the local recursive-deletion operation was blocked; they are not registered worktrees.
- The final independent candidate and retention-variant audits passed on the merged snapshot; full suites passed 46 tests each on Python 3.11 and 3.12. Detailed evidence, exact prompts, research citations, and measurement limits are in `tasks/TASK-PCM-0019-managed-worktrees.md` and GitHub issue comments #34/#39.
- #42 README image recovery remains deferred; do not search for or generate images until the user provides the promised plan.
- PCM-0023 / issue #32 completed in PR #43 at `867e5ae`; closeout PR #44 updated the canonical task status and closed #32.
- PCM-0015 is complete as a planning-only task. Its plan merged in PR #29 at `b379ba3`; issue #28 is closed. The plan does not mean the proposed capabilities have been implemented.
- PCM-0014 is complete and merged automatically in PR #26 at `b9e0f7c`; issue #24 is closed.
- Issue #17's baseline failure, fix, and blind rerun are recorded; it closed after status correction in PR #37. Issue #15 remains open because it includes an unperformed target-repository remediation outside current scope. Issue #42 remains deferred until the user provides the promised image plan; do not search for or generate images.
- PCM-0012 and PCM-0013 remain separately recorded workspace-policy histories.
- Other reports stay separately scoped; consult GitHub for the current open list before selecting new work.
- Candidate CLI/package version and runtime diagnostic now both report `0.2.0`, sourced from `continuity.__version__`. Protocol version remains independent at `0.1.0-draft`. Artifact verification does not publish to PyPI.
- Protocol version remains: `0.1.0-draft`

## Read exactly this first

1. `PROJECT.md`
2. `AGENTS.md`
3. `checkpoints/CURRENT.md`
4. `SPEC.md`
5. `docs/HANDOFF_PROTOCOL.md`
6. `docs/AGENT_LIFECYCLE.md`
7. `docs/VERSIONING.md`

## Exact next action

After this closeout PR passes the six protected checks and merges, verify issue #31 is closed; then start PCM-0018 / issue #33 as the next separately scoped task. Issues #15 and #42 stay open for the out-of-scope target repair and deferred image plan; do not alter those repositories or search/generate the images.

## Authority

PCM owns only its protocol/tooling development state. When PCM is used as a helper for another repository, that target repository owns its PROJECT/CURRENT/TASK/checkpoint state. A target is not integrated until `continuity validate --root <target>` succeeds. The authoritative identity is the repository/task lineage and Git history; alternate worktrees/hosts are execution infrastructure. Normal checkpoints commit and push the task branch; CI and pull-request automation deliver the pushed state. Use and later reconcile a recovery receipt when canonical continuity state is temporarily unavailable.

## Workspace policy

Keep one permanent main checkout as the project home base and use it for sequential work. Create a linked worktree only when parallelism or isolation is useful, under `pcm/worktree/<TASK-ID>`, and reuse that task's worktree across sessions. Do not create one per agent or sibling clones. After required checks pass, the PR is merged, the task is complete, and the worktree is clean, run `continuity worktree remove <TASK-ID>`; it verifies GitHub delivery and refuses locked/pinned or otherwise unsafe cleanup. For a short audit hold, record its reason, expected release date, exact path, and unlock/remove next action in the completed task's checkpoint, then lock the tree with `git worktree lock --reason "<reason; release YYYY-MM-DD>" <path>`. When the audit ends, return to the permanent checkout, unlock the tree, and run the normal verified cleanup. Other Git hosts remain unsupported for cleanup until PCM has a tested CI/merge verifier for them. Shared package caches are encouraged, but mutable dependency environments stay separate when their lockfiles or runtimes differ. Strict `single-checkout` mode remains available.

## Continuity records

<!-- pcm:policy {"id":"continuity-records","policy_version":"1.0.0","protocol_version":"0.1.0-draft"} -->

Issue logs, progress updates, pull requests, and continuity documents should explain the human problem and observable outcome, then scope, evidence, and one next action. Cite external claims and link repository claims to a revision or CI result. Include reproduction detail only when it helps verify a claim; keep PR openings skimmable and link long logs. These records do not automatically synchronize trackers.
