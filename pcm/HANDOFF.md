# Current Handoff

This repository is ready for a fresh PCM development session without prior chat history.

## Active work

- PCM-0019 / issue #34 is active: implement temporary task-owned worktrees under `pcm/worktree/<TASK-ID>`, safe push/CI/merge/removal, and immutable package-cache reuse. Start with `tasks/TASK-PCM-0019-managed-worktrees.md`.
- Preserve strict single-checkout as an explicit opt-out. Issue #20's feature landed in PR #21 but remains open; reconcile it only after #34's final policy and tests pass.
- PCM-0022 / issue #39 remains a separate test-method task. Run its corrected-candidate fresh-session checks only after #34 has a candidate; do not fold its policy/harness work into #34.
- #42 README image recovery is deferred; do not search for or generate images until the user provides the promised plan.
- PCM-0023 / issue #32 completed in PR #43 at `867e5ae`; closeout PR #44 updates the canonical task status/current pointer and closes #32.
- PCM-0022 / issue #39 remains open: its policy merged in PR #40, but its corrected-candidate fresh-session rerun depends on the separate issue #34. Read its task file only when resuming that follow-up.
- PCM-0019 / issue #34 remains open and separate. The #39 corrected-candidate holdout depends on its future implementation; do not implement managed worktrees under PCM-0022.

- PCM-0015 is complete as a planning-only task. Its plan merged in PR #29 at `b379ba3`; issue #28 is closed. Read `tasks/TASK-PCM-0015-versioned-project-memory.md` and `docs/plans/PCM-0015-implementation-plan.md` only when working on those follow-ups. The plan does not mean the proposed capabilities have been implemented.
- PCM-0014 is complete and merged automatically in PR #26 at `b9e0f7c`.
- GitHub issue #24 is closed by PR #26.
- Open reports are tracked separately: #30-35. Issue #17's baseline failure, fix, and blind rerun are recorded; it closed after status correction in PR #37. Issue #15 remains open because it includes an unperformed target-repository remediation outside current scope.
- PCM-0012 and PCM-0013 remain separately recorded workspace-policy histories.
- Candidate CLI/package version remains: `0.2.0`
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

Finish PCM-0019/#34: align the generated and repository guidance with the managed-worktree lifecycle, complete deterministic safety and disk-footprint tests, run all local gates and continuity validation, then push for required CI and automatic merge. Keep the #39 fresh-session holdout separate and dependent on this candidate.

## Authority

PCM owns only its protocol/tooling development state. When PCM is used as a helper for another repository, that target repository owns its PROJECT/CURRENT/TASK/checkpoint state. A target is not integrated until `continuity validate --root <target>` succeeds. The authoritative identity is the repository/task lineage and Git history; alternate worktrees/hosts are execution infrastructure. Normal checkpoints commit and push the task branch; CI and pull-request automation deliver the pushed state. Use and later reconcile a recovery receipt when canonical continuity state is temporarily unavailable.

## Workspace policy

Keep one permanent main checkout as the project home base and use it for sequential work. Create a linked worktree only when parallelism or isolation is useful, under `pcm/worktree/<TASK-ID>`, and reuse that task's worktree across sessions. Do not create one per agent or sibling clones. After required checks pass, the PR is merged, the task is complete, and the worktree is clean, run `continuity worktree remove <TASK-ID>`; it verifies GitHub delivery and refuses locked/pinned or otherwise unsafe cleanup. For a short audit hold, record its reason, expected release date, exact path, and unlock/remove next action in the completed task's checkpoint, then lock the tree with `git worktree lock --reason "<reason; release YYYY-MM-DD>" <path>`. When the audit ends, return to the permanent checkout, unlock the tree, and run the normal verified cleanup. Other Git hosts remain unsupported for cleanup until PCM has a tested CI/merge verifier for them. Shared package caches are encouraged, but mutable dependency environments stay separate when their lockfiles or runtimes differ. Strict `single-checkout` mode remains available.

## Continuity records

<!-- pcm:policy {"id":"continuity-records","policy_version":"1.0.0","protocol_version":"0.1.0-draft"} -->

Issue logs, progress updates, pull requests, and continuity documents should explain the human problem and observable outcome, then scope, evidence, and one next action. Cite external claims and link repository claims to a revision or CI result. Include reproduction detail only when it helps verify a claim; keep PR openings skimmable and link long logs. These records do not automatically synchronize trackers.
