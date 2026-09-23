# Current Repository Checkpoint

<!-- continuity:current {"active_task":"PCM-0012","active_task_file":"tasks/TASK-PCM-0012-strict-single-checkout-mode.md","protocol_version":"0.1.0-draft","schema":"project-continuity.current.v1"} -->

## Program state

Phase: adoption — prove v1 in mature repositories.

Current P0 task: PCM-0012 — strict single-checkout mode for projects that prohibit task worktrees.
PCM-0011's linked-worktree guidance merged in PR #19 and is retained as history; this follow-up makes workspace isolation explicit and defaults new software projects to one checkout.

## Main objective

Adopt the validated continuity protocol in existing repositories without erasing their domain-specific project contracts or handoff semantics.

## Completed

- PCM-0009 — helper/target identity hardening merged to `main` in PR #16 at `93c0549`; required checks passed.
- PCM-0011 — canonical remote identity and no-sibling-clone rules merged in PR #19 at `9d8deb3`; its nested worktree recommendation is superseded by the configurable follow-up, not erased.
- PCM-0001 — executable v1 schemas/templates/CLI/validator/bootstrap merged;
- PCM-0002 — fresh minimal end-to-end dogfood merged; 8-test suite passed and final validation was VALID.
- PCM-0008 — four repository-specific README promotions merged after review; all adapters pin content-generation-modules v0.1.2.

## Active

- PCM-0010 — degraded continuity guidance and recovery receipts, tracked by issue #17 and delivered in PR #18; its historical task record is retained.
- PCM-0012 — explicit single-checkout versus linked-worktree mode, tracked by issue #20.

## Prior completed/adopted work

- PCM-0003 — custom-extensions adoption merged in PR #6; the canonical task state is recorded in the prior checkpoint history.
- PCM-0004 — reusable content-generation system is published at v0.1.2; Eval Lab README promotion PR #30 is merged with green CI.

## Queued

1. PCM-0005 — GitHub Issue adapter and bidirectional consistency checks.
2. PCM-0006 — optional Beads adapter.
3. PCM-0007 — protocol v1.0 release/migration contract.

## Blockers

None known.

## Next atomic action

Review and deliver PCM-0012 through required CI, then reconcile the strict mode with the local D-drive policy.
