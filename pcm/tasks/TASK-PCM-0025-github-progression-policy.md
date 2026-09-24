# TASK-PCM-0025 — GitHub-owned progression policy

<!-- continuity:task {"acceptance":["SPEC defines field authority, conflicts, one writer/shared documents, evidence correction and downstream lineage re-planning.","Every issue update links leaf/parent/dependency lineage and every pushed increment synchronizes required docs before finite GitHub receipts.","Generated and adopting-project guidance passes deterministic propagation/contradiction and conflict-preservation tests.","Required local gates and exact protected hosted checks pass; GitHub auto-merge and live issue reconciliation are verified.","Parent issue 53 stays open; second-account verification remains outside acceptance; automation remains separately tracked in issue 67."],"depends_on":[],"goal":"Make GitHub-owned progression, bounded authority and finite publication consistent across policy and generated adopter guidance.","id":"PCM-0025","issue_url":"https://github.com/Pukujan/project-continuity-modules/issues/66","next_action":"Publish the synchronized checkpoint and PR for issue 66, then verify exact required CI and GitHub auto-merge.","owner":"Astra/Codex primary writer; issue 66","priority":"P1","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Fresh sessions need one durable task authority and a finite, auditable delivery protocol."} -->

## Human outcome

Make GitHub-owned progression, bounded authority and finite publication consistent across policy and generated adopter guidance.

## Authority and lineage

This is a mandatory versioned projection, not canonical task state. Leaf [#66](https://github.com/Pukujan/project-continuity-modules/issues/66) owns scope/lifecycle; parent ancestry: [#53 / PCM-0024](https://github.com/Pukujan/project-continuity-modules/issues/53). Source issue observed at revision/update time 2026-09-24T15:32:31Z. Branch: `task/PCM-0025-github-progression-policy`; one primary writer: Astra/Codex. Prerequisites are merged PRs #56/#57/#61/#62/#64/#65; no unresolved prerequisite. Independent automation child [#67 / PCM-0026](https://github.com/Pukujan/project-continuity-modules/issues/67) under #53 depends on this policy. #33 cleanup is independent.

## Scope and boundaries

SPEC, PROJECT, README, AGENTS, handoff/records/adopter guidance, GitHub/profile/generated templates, deterministic policy tests and synchronized task/catalog/index projections. No runtime scheduler, automatic issue-comment claims, new account requirement, unrelated repository changes or parent completion. [Owner correction](https://github.com/Pukujan/project-continuity-modules/issues/53#issuecomment-5816655372) supersedes second-account blockers in historical projections.

## Acceptance criteria

- [ ] SPEC defines field authority, conflicts, one writer/shared documents, evidence correction and downstream lineage re-planning.
- [ ] Every issue update links leaf/parent/dependency lineage and every pushed increment synchronizes required docs before finite GitHub receipts.
- [ ] Generated and adopting-project guidance passes deterministic propagation/contradiction and conflict-preservation tests.
- [ ] Required local gates and exact protected hosted checks pass; GitHub auto-merge and live issue reconciliation are verified.
- [ ] Parent issue 53 stays open; second-account verification remains outside acceptance; automation remains separately tracked in issue 67.

## Evidence and sources

Starting accepted revision: `7762792263779719af03fd13a30b858a05ad120d`. Live #53 was independently read including its latest owner comment. Full-access fetch and owner-authenticated gh work. Main protection observed: six required quality/test/package/parity contexts, strict current-base checks, enforce-admins, no force push. Implementation is candidate work until the live [leaf receipt](https://github.com/Pukujan/project-continuity-modules/issues/66) records exact CI/merge evidence.

## Local verification

Commands observed on Python 3.12:
- `PYTHONPATH=src python -m unittest discover -s tests -v`: 78 passed in 350.921s.
- `python -m unittest discover -s tests -p test_github_progression_policy.py -v`: 5 passed after final normative clarification.
- `python -m ruff check .`, `python -m mypy src`, `python -m compileall -q src tests`: passed.
- `python tests/package_smoke.py --root .`: wheel and source archive builds, isolated installs, generated minimal/software parity and PCM-0018 feature parity passed on Python 3.12.
- `python -m continuity validate --root .`, `python -m continuity docs render --check`, `git diff --check`: passed.
- Historical PCM-0024 checkpoint text compared with starting HEAD: preserved verbatim.

The earlier interrupted full-suite/package attempts had no captured final result and are not counted as passes. Tests verify deterministic policy propagation and existing behavior, not a new fresh-session or cross-account experiment. Resumption evidence: https://github.com/Pukujan/project-continuity-modules/issues/66#issuecomment-5817535817.

## Publication boundary

Local Python 3.12 gates passed: 78 tests in 350.921s; five focused policy tests also passed after the indexed-checkpoint clarification; Ruff, MyPy, compileall, continuity validation, generated-index synchronization and diff checks passed. Wheel and source archive build/install parity passed for minimal/software profiles and PCM-0018 features. Pushed checkpoint, PR, required hosted checks and auto-merge are pending in this snapshot; the live leaf issue owns subsequent events. Every push must include synchronized applicable docs; the subsequent request-ID/SHA receipt and parent update live on GitHub. Receipt-only transitions need no recursive doc commit. Material corrections require another synchronized increment. Do not infer current lifecycle from this snapshot.

## Checkpoint log

No checkpoints yet.

### 2026-09-24 16:02:31 UTC — Astra/Codex via owner-authorized Pukujan

<!-- continuity:checkpoint {"agent":"Astra/Codex via owner-authorized Pukujan","blocked":["Required hosted checks, automatic merge and final issue/document reconciliation are pending; this checkpoint is not merged delivery."],"changed":["SPEC, PROJECT, README, AGENTS, HANDOFF, CURRENT, handoff/records/adoption/version guidance, GitHub/profile templates, cli generators, policy tests, PCM-0024/0025/0026 task projections, catalog and generated index."],"completed":["Implemented bounded GitHub authority, lineage/evidence corrections, finite synchronized publication and mandatory CI/auto-merge policy; propagated generated/adopter guidance and deterministic tests."],"decisions":["Second-account verification is not required per owner comment 5816655372; historical checkpoint text is preserved. Manual issue receipts remain mandatory while automation is separately queued."],"evidence":["Product commit b88ef1e; 78 unittest tests passed in 350.921s on Python 3.12; five focused policy tests passed; Ruff, MyPy, compileall, continuity/index validation, diff checks and wheel/sdist build/install parity passed.","Leaf https://github.com/Pukujan/project-continuity-modules/issues/66 under parent https://github.com/Pukujan/project-continuity-modules/issues/53; automation sibling https://github.com/Pukujan/project-continuity-modules/issues/67 depends on this policy; no unresolved prerequisite."],"next_action":"Open the policy PR for leaf issue 66; verify exact required CI and auto-merge, then reconcile receipts under parent issue 53.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0025","timestamp":"2026-09-24T16:02:31Z"} -->
<!-- continuity:checkpoint-operation {"payload_sha256":"eb8bff97413559a638954cbb081b877aeabf1c5bd1b8adc19abf65fee4019759","request_id":"pcm0025-policy-20260924","schema":"project-continuity.checkpoint-operation.v1","task_id":"PCM-0025"} -->

Completed:
- Implemented bounded GitHub authority, lineage/evidence corrections, finite synchronized publication and mandatory CI/auto-merge policy; propagated generated/adopter guidance and deterministic tests.

Evidence:
- Product commit b88ef1e; 78 unittest tests passed in 350.921s on Python 3.12; five focused policy tests passed; Ruff, MyPy, compileall, continuity/index validation, diff checks and wheel/sdist build/install parity passed.
- Leaf https://github.com/Pukujan/project-continuity-modules/issues/66 under parent https://github.com/Pukujan/project-continuity-modules/issues/53; automation sibling https://github.com/Pukujan/project-continuity-modules/issues/67 depends on this policy; no unresolved prerequisite.

Decisions:
- Second-account verification is not required per owner comment 5816655372; historical checkpoint text is preserved. Manual issue receipts remain mandatory while automation is separately queued.

Changed:
- SPEC, PROJECT, README, AGENTS, HANDOFF, CURRENT, handoff/records/adoption/version guidance, GitHub/profile templates, cli generators, policy tests, PCM-0024/0025/0026 task projections, catalog and generated index.

Blocked/uncertain:
- Required hosted checks, automatic merge and final issue/document reconciliation are pending; this checkpoint is not merged delivery.

Next:
- Open the policy PR for leaf issue 66; verify exact required CI and auto-merge, then reconcile receipts under parent issue 53.

## Handoff

Verify live #66 and #53, then follow the exact next action above. The parent remains OPEN. Follow SPEC section 8; no local ledger is authority.
