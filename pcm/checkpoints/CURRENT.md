# Current Repository Checkpoint

<!-- continuity:current {"active_task":null,"active_task_file":null,"protocol_version":"0.1.0-draft","schema":"project-continuity.current.v1"} -->

## Program state

Phase: adoption — prove v1 in mature repositories.

PCM-0019 / issue #34 is complete in PRs #45–#47, with closeout PR #48 carrying the final task/checkpoint/handoff state and closing issues #20, #34, and #39 after protected CI. The rule is one permanent home checkout for sequential work plus optional task-owned linked worktrees for real parallelism/isolation; verified cleanup follows green required checks, merge, and task completion. A short audit hold must be time-bounded in the task checkpoint and protected with Git's native worktree lock; it is unlocked and normally cleaned up afterward. Final local suites passed 46 tests each on Python 3.11 and 3.12. The Windows C: NTFS fixture used 5,243,374 file-storage bytes for home plus three linked worktrees versus 8,390,584 bytes for home plus three non-hardlinked clones; details and limits are in the task and issue comments. PR #48 is merged, issues #20/#34/#39 are closed, PCM-0019 task branches are removed, and the permanent main checkout is the only registered worktree. Five disposable holdout clone folders remain outside the repository because the local recursive-deletion operation was blocked; they are not registered worktrees. PCM-0017 / issue #31's implementation is merged in PR #49. Package version metadata and runtime now both derive from `continuity.__version__` (`0.2.0`); the protocol remains `0.1.0-draft`. CI verifies wheel/sdist installs and generated-file parity on Python 3.11/3.12; main requires all six quality/test/package/parity checks. This PR updates the canonical task status before closing #31. There is no active continuity task. No unrelated target repository is in scope.

PCM-0015 — plan versioned, verifiable project memory — completed as a planning-only task in PR #29 at `b379ba3`; issue #28 is closed. The plan did not implement the proposed capabilities. Follow-up issues #30-35 now track separate work for report-to-issue closeout, package/install parity, memory/discovery proof, managed worktrees/dependency caches, Codex session rotation, and archiving finished helper conversations. PCM-0010's baseline failure, fix, and post-fix blind rerun were already recorded and merged; stale issue #17 status was corrected and it closed through PR #37 at `cf76827`. PCM-0009's protocol/tooling work is on `main`, but issue #15 remains open because its broader description includes a target-repository remediation not performed here. PCM-0014 — close completed delegated agents and bound concurrency — merged automatically in PR #26 at `b9e0f7c` after protected CI passed.
PCM-0012 and PCM-0013 are merged workspace-policy deliveries and remain separately recorded in their own task histories.

## Main objective

Adopt the validated continuity protocol in existing repositories without erasing their domain-specific project contracts or handoff semantics.

## Completed

- PCM-0009 — helper/target identity hardening merged to `main` in PR #16 at `93c0549`; required checks passed.
- PCM-0011 — canonical remote identity and no-sibling-clone rules merged in PR #19 at `9d8deb3`; its nested worktree recommendation is superseded by the configurable follow-up, not erased.
- PCM-0012 — explicit single-checkout mode merged in PR #21; its linked-worktree opt-in is superseded by PCM-0013, with its task history retained.
- PCM-0013 — mandatory single-checkout policy and non-mutating legacy-config migration merged in PR #22 at `368273a`; required CI passed.
- PCM-0010 — degraded continuity guidance and recovery receipts merged in PR #18; its historical task record is retained.
- PCM-0001 — executable v1 schemas/templates/CLI/validator/bootstrap merged;
- PCM-0002 — fresh minimal end-to-end dogfood merged; 8-test suite passed and final validation was VALID.
- PCM-0008 — four repository-specific README promotions merged after review; all adapters pin content-generation-modules v0.1.2.
- PCM-0009 — helper/target identity hardening and cold-start blind acceptance merged in PR #16.
- PCM-0010 — degraded continuity bookkeeping, recovery receipts, mandatory checkpoint pushes, and protected CI merge flow merged through PR #18 and PR #16; its release gate and issue #17 closeout are complete.
- PCM-0014 — delegated-agent lifecycle policy and deterministic cleanup guidance merged automatically in PR #26 at `b9e0f7c`; protected CI passed.
- PCM-0015 — planning-only versioned memory/adoption proposal merged in PR #29 at `b379ba3`; required CI passed and issue #28 was closed after follow-ups were linked.
- PCM-0023 — human-first auditable continuity records merged in PR #43 at `867e5ae`; quality, Python 3.11/3.12 tests, package build, and automatic-merge checks passed.
- PCM-0019 — managed temporary worktrees, verified cleanup, native lock-based audit holds, measured storage, and independent candidate/variant checks completed through PRs #45–#48; final local suites passed 46 tests on Python 3.11 and 3.12.
- PCM-0017 — package/runtime version identity and isolated wheel/sdist generated-output parity merged in PR #49; six required hosted checks and local Python 3.11/3.12 suites passed. This closeout PR updates its task status before closing issue #31.

## Open and separately tracked

- Issue #15 remains open for its required target-repository remediation, which is outside current scope.
- Issue #42 remains deferred until the user provides the promised image plan; do not search for or generate images.

## Prior completed/adopted work

- PCM-0003 — custom-extensions adoption merged in PR #6; the canonical task state is recorded in the prior checkpoint history.
- PCM-0004 — reusable content-generation system is published at v0.1.2; Eval Lab README promotion PR #30 is merged with green CI.

## Queued

1. PCM-0005 — GitHub Issue adapter and bidirectional consistency checks.
2. PCM-0006 — optional Beads adapter.
3. PCM-0007 — protocol v1.0 release/migration contract.

## Other open reports

- PCM-0018 / issue #33 — idempotent checkpoints and blind fresh-session document discovery.
- PCM-0020 / issue #35 — safe Codex main-session rotation.
- PCM-0021 / issue #30 — archive helper conversations while preserving main-session history.
- Issue #15 remains open for its required target-repository remediation; that repository is explicitly outside the active scope.
- Issue #42 README image recovery remains deferred until the user provides the promised plan; do not search for or generate images before then.

## Blockers

None known.

## Next atomic action

After this closeout PR passes the six protected checks and merges, verify issue #31 is closed; then begin PCM-0018 / issue #33 with a bounded baseline of checkpoint idempotence, document discovery, and context-pack behavior. Leave #15 and #42 open for their explicit scope constraints.
