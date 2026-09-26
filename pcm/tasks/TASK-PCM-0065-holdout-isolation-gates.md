# TASK-PCM-0065 — Holdout Isolation Gates

<!-- continuity:task {"acceptance": ["Owner records the gate decision on #191.", "Approved gates land as plan-template + launcher changes with a dry-run fixture proving an out-of-bundle read is detected before arms count; the override-durability pattern (overrides.json) documented in the plan template.", "No already-frozen PCM-0046 artifacts are modified; corrections stay append-only."], "depends_on": [], "goal": "Decide holdout isolation gates (bundle-only visibility, pre-launch out-of-bundle read check, durable override inputs) so future hidden arms cannot reach the answer key (Refs #191).", "id": "PCM-0065", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/191", "next_action": "Owner picks the A/B/C gate set on #191; harness work proceeds only on its own branch with no retroactive edits to PCM-0046 artifacts.", "owner": "owner/Astra planning", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "active", "why": "PCM-0046 found its own harness defect: 7/30 arms enumerated the shared bundle parent; 4/5 T4 arms read or ran the grader's source, voiding those verdicts to inconclusive after the fact."} -->

- Status: active
- Owner: owner/Astra planning
- Priority: P2
- Depends on: none

## Goal

Decide holdout isolation gates (bundle-only visibility, pre-launch out-of-bundle read check, durable override inputs) so future hidden arms cannot reach the answer key (Refs #191).

## Why

PCM-0046 found its own harness defect: 7/30 arms enumerated the shared bundle parent; 4/5 T4 arms read or ran the grader's source, voiding those verdicts to inconclusive after the fact.

## Allowed files

After the owner answer on #191: docs/plans/ templates (launcher/bundles/scorer guidance for future holdouts), a new tests/test_holdout_isolation.py-style dry-run fixture, docs/TESTING_POLICY.md pointer; this increment changes only this task file. Out: the frozen PCM-0046 artifacts (docs/plans/PCM-0046-arms-results/**), already-merged history.

## Human outcome

Every future hidden-arm result means what it says: participants cannot enumerate each other's bundles or reach the grader's own repository, and post-run verdict overrides survive re-scoring as durable inputs.

## Scope and boundaries

- In scope: gate selection on #191 and harness-template changes for FUTURE holdouts.
- Out of scope: any edit to the frozen PCM-0046 artifacts; retroactive rescoring of accepted verdicts.
- Dependencies/uncertainty: depends on isolation-audit.json (accepted); owner gate on #191.

## Acceptance criteria

- [ ] Owner records the gate decision on #191.
- [ ] Approved gates land as plan-template + launcher changes with a dry-run fixture proving an out-of-bundle read is detected before arms count; the override-durability pattern (overrides.json) documented in the plan template.
- [ ] No already-frozen PCM-0046 artifacts are modified; corrections stay append-only.

## Evidence and sources

7/30 arms enumerated the shared parent; 4/5 T4 arms read or executed src/continuity/cli.py + tests/traversal_scorer.py (isolation-audit.json); the re-score-clobbers-overrides near-miss is recorded in REPORT.md.

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none): leaf #191 (PCM-0065); parent: none; defect recorded in accepted docs/plans/PCM-0046-arms-results/isolation-audit.json.
- Primary writer / branch / source issue revision / as-of status: owner/Astra (omp session); branch task/PCM-0063-projections (projection increment only, no code); source: live issue bodies; as-of 2026-09-26T11:35Z.
- Related PR/CI evidence and push receipt (request ID / SHA): none yet (decision gate); arms evidence rides PCM-0046 (PRs #188/#192/#193).

## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
