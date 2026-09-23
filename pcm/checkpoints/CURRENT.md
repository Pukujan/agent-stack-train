# Current Repository Checkpoint

<!-- continuity:current {"active_task":"PCM-0022","active_task_file":"tasks/TASK-PCM-0022-agent-facing-holdouts.md","protocol_version":"0.1.0-draft","schema":"project-continuity.current.v1"} -->

## Program state

Phase: adoption — prove v1 in mature repositories.

On 2026-09-23, the user selected PCM-0022 / issue #39 as the active bounded slice before the previously queued PCM-0019 / issue #34. This is a priority change, not a claim that #34 is complete; its managed-worktree implementation remains separate.

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

## Active

- PCM-0022 / issue #39 — the risk-based testing policy merged in PR #40 after all required CI passed. Keep #39 open for its remaining corrected-candidate holdout, which depends on issue #34. The historical PCM-0010 holdout is unrelated and must not be repeated or mislabeled as this task's evidence.
- Issue #15 remains open only for its target-repository remediation, which is outside current scope.

## Prior completed/adopted work

- PCM-0003 — custom-extensions adoption merged in PR #6; the canonical task state is recorded in the prior checkpoint history.
- PCM-0004 — reusable content-generation system is published at v0.1.2; Eval Lab README promotion PR #30 is merged with green CI.

## Queued

1. PCM-0005 — GitHub Issue adapter and bidirectional consistency checks.
2. PCM-0006 — optional Beads adapter.
3. PCM-0007 — protocol v1.0 release/migration contract.

## Reported follow-ups (not yet implemented)

- PCM-0016 / issue #32 — durable issue intake and evidence-backed closeout.
- PCM-0017 / issue #31 — version identity and installed-package parity.
- PCM-0018 / issue #33 — idempotent checkpoints and blind fresh-session document discovery.
- PCM-0019 / issue #34 — managed worktrees, push/merge/cleanup, and safe dependency-cache reuse.
- PCM-0020 / issue #35 — safe Codex main-session rotation.
- PCM-0021 / issue #30 — archive helper conversations while preserving main-session history.
- PCM-0022 / issue #39 — agent-facing behavior testing and holdout fairness (active).

## Blockers

None known.

## Next atomic action

After issue #34 is implemented, run and record the corrected-candidate fresh-session holdout required by #39 before closing it. PR #40 already merged the policy slice with all required checks passing. Keep issue #34 implementation and strict-checkout issue #20 separately scoped.
