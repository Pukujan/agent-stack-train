# TASK-PCM-0027 — Issue Log Format

<!-- continuity:task {"acceptance": ["Module doc docs/ISSUE_LOG_FORMAT.md carries the issue-log-format 1.0.0 marker, spec, exemplar and short-form example; registered in the document catalog and rendered index.", "CLI constant and guidance block propagated to the minimal and software generated guidance, the GitHub issue template, the static template copies, and PCM's own guidance; continuity-records references the module without duplicating it (version bumped to 1.3.0).", "continuity validate reports missing (warning), contradictory (error) and stale (warning) markers; deterministic tests cover each case, plus parity with generated output and preservation of existing adopter files during init.", "The existing-adopter update path is documented and the VERSIONING entry added; package source is 0.5.0.", "Normal checkpoint/PR flow with required checks, auto-merge, and verified reconciliation; the PR uses Refs #99."], "depends_on": [], "goal": "Ship the issue-log-format 1.0.0 module: one human-readable shape for issue logs, updates and PRs that any PCM adopter can apply mechanically", "id": "PCM-0027", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/99", "next_action": "None for PCM-0027: #99 CLOSED (PR #113 at 79337a6; receipt 5829746872; ledger corrections 5830303826). Evaluation-gate transfer recorded on #100 (5830322199).", "owner": "Astra/Codex planning; subagent implementation", "priority": "P1", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "completed", "why": "Agents write issue records of uneven quality; the owner rates human-readable project records as one of the most valuable modules to solve"} -->

- Status: completed 2026-09-25 (#99 CLOSED)
- Owner: Astra/Codex planning; subagent implementation
- Priority: P1
- Depends on: none

## Goal

Ship the issue-log-format 1.0.0 module: one human-readable shape for issue logs, updates and PRs that any PCM adopter can apply mechanically

## Why

Agents write issue records of uneven quality; the owner rates human-readable project records as one of the most valuable modules to solve

## Scope and lineage

Leaf [#99](https://github.com/Pukujan/project-continuity-modules/issues/99), parent: none (top-level deliverable). Branch: `task/PCM-0027-issue-log-format`. The module ships the format spec from #99 under the owner direction in comment 5828143593 (severity contract: missing marker warns, contradictory versions error, stale markers warn with the mechanical update step).

## Allowed files

- `docs/ISSUE_LOG_FORMAT.md` (new module doc), `docs/CONTINUITY_RECORDS_POLICY.md`, `docs/VERSIONING.md`, `docs/CONTINUITY_INDEX.md` (generated), `.continuity/documents.json`
- `src/continuity/cli.py` (constants, generators, validator), `src/continuity/__init__.py` (version), `tests/test_issue_log_format.py` (new), `tests/test_continuity_records_policy.py` (pins only)
- Static guidance copies: `AGENTS.md`, `HANDOFF.md`, `templates/v1/software/AGENTS.md`, `templates/v1/software/README.md`, `templates/v1/minimal/HANDOFF.md`, `.github/ISSUE_TEMPLATE/task.md`, `.github/pull_request_template.md`
- `README.md`, `SPEC.md` (one-line pointers), `tasks/TASK-PCM-0027-issue-log-format.md`

## Human outcome

A fresh agent or person writing an issue log, progress update, or PR in a PCM adopter follows one plain-language shape — core tier for every log, investigation tier for unproven causes — so records read like the IRE-40 exemplar instead of uneven ad-hoc prose, and a stale adopted copy is detectable and mechanically repairable via `continuity validate`.

## Scope and boundaries

- In scope: module doc + marker, CLI constants and guidance block, generator/template/static-copy propagation, validator severity contract with deterministic tests, continuity-records 1.3.0 reference, catalog registration, existing-adopter update path, VERSIONING/README/SPEC bookkeeping.
- Out of scope: the blind evaluation run from #99 (results stay open on the issue until posted), an automated upgrade command, a structural checker as a public command, and any edits to IRE or other target repositories.
- Dependencies/uncertainty: none blocking; the evaluation matrix in #99 proceeds independently under owner direction.

## Acceptance criteria

- [x] Module doc `docs/ISSUE_LOG_FORMAT.md` with the `issue-log-format` 1.0.0 marker, spec, exemplar and short-form example; registered in the document catalog and index.
- [x] CLI constant and guidance block propagated to the minimal and software generated guidance, the GitHub issue template, the static template copies, and PCM's own guidance; continuity-records references the module without duplicating it (version bumped to 1.3.0).
- [x] `continuity validate` reports missing (warning), contradictory (error) and stale (warning) markers; deterministic tests cover each case, plus parity with generated output and preservation of existing adopter files during `init`.
- [x] The existing-adopter update path is documented, and the VERSIONING entry added (package 0.5.0, policy 1.3.0, module 1.0.0).
- [ ] Evaluation run per the #99 design: results posted on the issue with per-cell counts and each success criterion marked pass/fail/inconclusive (remains open on #99; not deliverable from this branch).
- [ ] Normal checkpoint/PR flow: PR with `Refs #99`, required checks, auto-merge, and verified reconciliation.

## Evidence and sources

- Deterministic tests: `tests/test_issue_log_format.py` (module/doc/validator/init/rollout suites) and `tests/test_continuity_records_policy.py` (parity pins), run with `PYTHONPATH=src python3.12 -m unittest`.
- `continuity validate --root .` prints `VALID` with no issue-log-format warnings; `continuity docs render --check` prints `SYNCHRONIZED`.
- Format provenance: #99 "Format spec: issue-log-format 1.0.0 (proposal)"; exemplar [IRE-40](https://github.com/Pukujan/inference-recommendation-engine/issues/40).

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none): leaf #99, parent none, dependencies none.
- Primary writer / branch / source issue revision / as-of status: owner/Astra planning with subagent execution on `task/PCM-0027-issue-log-format`; delivered as of 2026-09-25T08:51:58Z merge; the evaluation-run acceptance transferred to #100 (5830322199).
- Related PR/CI evidence and push receipt (request ID / SHA): [PR #113](https://github.com/Pukujan/project-continuity-modules/pull/113) at `79337a600bf282e98188bbb9ed37ff35468db39f`, closeout #114 at `84fd300`; request pcm0027-module-publish-20260925 pushed `f37c513`; run 36115136343; receipt 5829746872; corrections 5830303826.

## Checkpoint log

No checkpoints yet.

### 2026-09-25 08:50:11 UTC — owner/Astra planning; subagent execution

<!-- continuity:checkpoint {"agent":"owner/Astra planning; subagent execution","blocked":["None."],"changed":["src/continuity/cli.py; src/continuity/__init__.py; docs/ISSUE_LOG_FORMAT.md; .continuity/documents.json; docs/CONTINUITY_INDEX.md; README.md; SPEC.md; docs/VERSIONING.md; docs/CONTINUITY_RECORDS_POLICY.md; AGENTS.md; HANDOFF.md; templates/v1/*; .github/ISSUE_TEMPLATE/task.md; .github/pull_request_template.md; tests/test_issue_log_format.py; tasks/TASK-PCM-0027-issue-log-format.md; checkpoints/CURRENT.md."],"completed":["Implemented and locally verified the issue-log-format 1.0.0 module: CLI constants + mechanically replaceable guidance block, generator propagation (handoff/agents/issue/PR/readme), static-copy + PCM dogfood propagation, severity validator (missing warn / contradictory error / stale warn with update step), module doc + catalog/index, records-policy 1.3.0 reference, package 0.5.0, task projection, CURRENT synchronization."],"decisions":["Owner direction 5828143593: PRs share the core-tier shape; missing stays warning for all adopters in 1.0.0; #99 closes at merge with evaluation adjudication moved to #100."],"evidence":["Focused suites: tests.test_issue_log_format 22 OK; records+progression+cli combined green; full discover 182 with exactly the six known macOS-environmental test_worktrees/test_cli failures (identical names at base); ruff 0.16.9 + mypy 1.18.1 clean; continuity validate VALID; docs render SYNCHRONIZED; cold-start adopter init smoke: all five generated files carry exactly one block, findings ([], []), stale-then-contradictory severity path observed live."],"next_action":"Open PR to main (Refs #99), verify six required contexts + auto-merge on the exact candidate, publish leaf/parent receipts keyed to the merged SHA, then the closeout increment marks PCM-0027 completed and removes the worktree.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0027","timestamp":"2026-09-25T08:50:11Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"c5dbb4f504864619bc599ce524ec8091360086a1adfb7fcb57de676297c9c918","request_id":"pcm0027-module-publish-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0027"} -->

Completed:
- Implemented and locally verified the issue-log-format 1.0.0 module: CLI constants + mechanically replaceable guidance block, generator propagation (handoff/agents/issue/PR/readme), static-copy + PCM dogfood propagation, severity validator (missing warn / contradictory error / stale warn with update step), module doc + catalog/index, records-policy 1.3.0 reference, package 0.5.0, task projection, CURRENT synchronization.

Evidence:
- Focused suites: tests.test_issue_log_format 22 OK; records+progression+cli combined green; full discover 182 with exactly the six known macOS-environmental test_worktrees/test_cli failures (identical names at base); ruff 0.16.9 + mypy 1.18.1 clean; continuity validate VALID; docs render SYNCHRONIZED; cold-start adopter init smoke: all five generated files carry exactly one block, findings ([], []), stale-then-contradictory severity path observed live.

Decisions:
- Owner direction 5828143593: PRs share the core-tier shape; missing stays warning for all adopters in 1.0.0; #99 closes at merge with evaluation adjudication moved to #100.

Changed:
- src/continuity/cli.py; src/continuity/__init__.py; docs/ISSUE_LOG_FORMAT.md; .continuity/documents.json; docs/CONTINUITY_INDEX.md; README.md; SPEC.md; docs/VERSIONING.md; docs/CONTINUITY_RECORDS_POLICY.md; AGENTS.md; HANDOFF.md; templates/v1/*; .github/ISSUE_TEMPLATE/task.md; .github/pull_request_template.md; tests/test_issue_log_format.py; tasks/TASK-PCM-0027-issue-log-format.md; checkpoints/CURRENT.md.

Blocked/uncertain:
- None.

Next:
- Open PR to main (Refs #99), verify six required contexts + auto-merge on the exact candidate, publish leaf/parent receipts keyed to the merged SHA, then the closeout increment marks PCM-0027 completed and removes the worktree.

### 2026-09-25 09:09:30 UTC — owner/Astra planning

<!-- continuity:checkpoint {"agent":"owner/Astra planning","blocked":["None."],"changed":["tasks/TASK-PCM-0027-issue-log-format.md; checkpoints/CURRENT.md."],"completed":["Recorded task completion + parent close-out: [leaf receipt 5829746872](https://github.com/Pukujan/project-continuity-modules/issues/99#issuecomment-5829746872) posted on #99; [#53 parent progression comment posted](https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5828384182) remains the live aggregate link; issue #99 CLOSED."],"decisions":["Status flips to completed only after merge (active-task invariant); evaluation adjudication moved to #100 per owner close plan; worktree removal follows this merge."],"evidence":["PR #113 merged at 79337a600bf282e98188bbb9ed37ff35468db39f; six required contexts + auto-merge green on the exact candidate (run 36115136343); local suite state documented in the task file."],"next_action":"Merge the closeout PR, verify accepted history, then run continuity worktree remove PCM-0027.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0027","timestamp":"2026-09-25T09:09:30Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"2ea7b28fc554c05d7298fb23406c0105c5eae807032e06de20a5a611bd56947e","request_id":"pcm0027-closeout-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0027"} -->

Completed:
- Recorded task completion + parent close-out: [leaf receipt 5829746872](https://github.com/Pukujan/project-continuity-modules/issues/99#issuecomment-5829746872) posted on #99; [#53 parent progression comment posted](https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5828384182) remains the live aggregate link; issue #99 CLOSED.

Evidence:
- PR #113 merged at 79337a600bf282e98188bbb9ed37ff35468db39f; six required contexts + auto-merge green on the exact candidate (run 36115136343); local suite state documented in the task file.

Decisions:
- Status flips to completed only after merge (active-task invariant); evaluation adjudication moved to #100 per owner close plan; worktree removal follows this merge.

Changed:
- tasks/TASK-PCM-0027-issue-log-format.md; checkpoints/CURRENT.md.

Blocked/uncertain:
- None.

Next:
- Merge the closeout PR, verify accepted history, then run continuity worktree remove PCM-0027.

### 2026-09-25 09:09:51 UTC — owner/Astra planning

<!-- continuity:checkpoint {"agent":"owner/Astra planning","blocked":["None."],"changed":["tasks/TASK-PCM-0027-issue-log-format.md (appended checkpoint)."],"completed":["Corrected wording only: [#99](https://github.com/Pukujan/project-continuity-modules/issues/99) is a top-level deliverable (parent: none), so its leaf receipt needs no parent progression post; the prior entry's \"parent close-out\" label referred to [#53 comment 5828384182](https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5828384182), which is the PCM-0026 child close-out that points at #99 as the then-next slice. No facts change."],"decisions":["no new decisions"],"evidence":["Append-only correction preserved under the records policy; both comments verified live."],"next_action":"Merge the closeout PR, verify accepted history, then run continuity worktree remove PCM-0027.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0027","timestamp":"2026-09-25T09:09:51Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"1e8945840b7ae307f90d03ac045d22656353982720d0cad267b5ae4402ed3875","request_id":"pcm0027-closeout-correction-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0027"} -->

Completed:
- Corrected wording only: [#99](https://github.com/Pukujan/project-continuity-modules/issues/99) is a top-level deliverable (parent: none), so its leaf receipt needs no parent progression post; the prior entry's "parent close-out" label referred to [#53 comment 5828384182](https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5828384182), which is the PCM-0026 child close-out that points at #99 as the then-next slice. No facts change.

Evidence:
- Append-only correction preserved under the records policy; both comments verified live.

Decisions:
- no new decisions

Changed:
- tasks/TASK-PCM-0027-issue-log-format.md (appended checkpoint).

Blocked/uncertain:
- None.

Next:
- Merge the closeout PR, verify accepted history, then run continuity worktree remove PCM-0027.

### 2026-09-25 12:18:59 UTC — owner/Astra planning

<!-- continuity:checkpoint {"agent":"owner/Astra planning","blocked":["None."],"changed":["tasks/TASK-PCM-0027-issue-log-format.md; docs/CONTINUITY_INDEX.md."],"completed":["Restored the two verbatim checkpoint Next lines rewritten by PR #119 (01a12e9) in this file's 09:09 entries; post-merge state now lives only in the meta next_action and this appended entry."],"decisions":["Append-only correction per the records policy; no posted comment rewritten for this."],"evidence":["git diff 84562ef 01a12e9 showed the in-entry Next lines edited; restore commit reverts exactly those two lines; validate VALID; docs render SYNCHRONIZED after the append."],"next_action":"Merge the restore PR (Refs #99), then continue the audit follow-ups: #53 dated correction, #99 item-3 grep fix, #110 no-release addendum, checkpoint-index defect issue.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0027","timestamp":"2026-09-25T12:18:59Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"4d57c2d87e764596ad2a38d3f7f9b0c1509385edfc175dbe1b9cf72e76862596","request_id":"pcm0027-append-only-restore-20260925","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0027"} -->

Completed:
- Restored the two verbatim checkpoint Next lines rewritten by PR #119 (01a12e9) in this file's 09:09 entries; post-merge state now lives only in the meta next_action and this appended entry.

Evidence:
- git diff 84562ef 01a12e9 showed the in-entry Next lines edited; restore commit reverts exactly those two lines; validate VALID; docs render SYNCHRONIZED after the append.

Decisions:
- Append-only correction per the records policy; no posted comment rewritten for this.

Changed:
- tasks/TASK-PCM-0027-issue-log-format.md; docs/CONTINUITY_INDEX.md.

Blocked/uncertain:
- None.

Next:
- Merge the restore PR (Refs #99), then continue the audit follow-ups: #53 dated correction, #99 item-3 grep fix, #110 no-release addendum, checkpoint-index defect issue.

## Handoff

Read PROJECT → CURRENT → this task → `docs/ISSUE_LOG_FORMAT.md`. The module shipped on main (`79337a6` + closeout `84fd300`); evaluation adjudication continues under #100 (recorded there via 5830322199).
