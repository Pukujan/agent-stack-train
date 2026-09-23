# Current Repository Checkpoint

<!-- continuity:current {"active_task":"PCM-0015","active_task_file":"tasks/TASK-PCM-0015-versioned-project-memory.md","protocol_version":"0.1.0-draft","schema":"project-continuity.current.v1"} -->

## Program state

Phase: adoption — prove v1 in mature repositories.

PCM-0015 — plan versioned, verifiable project memory — is active as a planning-only task linked to issue #28. Its discussion and PROV-O provenance graph are recorded; Astra's proposal now has a parent-reviewed, explicitly limited proof path. No implementation is authorized by this planning task. PCM-0014 — close completed delegated agents and bound concurrency — merged automatically in PR #26 at `b9e0f7c` after protected CI passed.
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
- PCM-0010 — degraded continuity bookkeeping, recovery receipts, mandatory checkpoint pushes, and protected CI merge flow merged in PR #18 and the protected main delivery.
- PCM-0014 — delegated-agent lifecycle policy and deterministic cleanup guidance merged automatically in PR #26 at `b9e0f7c`; protected CI passed.

## Active

- PCM-0015 — planning-only design for versioned adoption, safe checkpoint retries, scoped document discovery, and a measured fresh-session trial. Assertions, ownership automation, Node packaging, publication, and host integrations remain optional/separate; do not implement them from this plan.

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

Run PCM-0015 documentation/repository checks and deliver the planning-only result through required CI and automatic merge. Afterward, decide separately whether to open only the first bounded proof slice; keep queued PCM-0005 distinct.
