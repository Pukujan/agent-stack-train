# TASK-PCM-0064 — Keyword Warning Rephrase Experiment

<!-- continuity:task {"acceptance": ["Owner records variant selection (A positive-form Refs-by-default, B hazard-named-without-literal-pattern, or both) on #190.", "Re-run of T3/T3b arms with frozen pre-registered prompts and rubric (ambiguous -> inconclusive) reported honestly; six contexts on any guidance change + receipt on #190.", "(proposed) A candidate variant is adopted only if it beats the current sentence on keyword-smuggling rate without regressing the T1b append controls."], "depends_on": [], "goal": "Decide and pre-register the closing-keyword warning rephrase experiment: candidate positive-form (Refs by default) and hazard-named-without-pattern variants, re-measured T3/T3b before any template ships (Refs #190).", "id": "PCM-0064", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/190", "next_action": "Owner picks which variant(s) to pre-register on #190; nothing ships before the re-measure.", "owner": "owner/Astra planning", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "active", "why": "PCM-0046 T3 showed the warning sentence gave no measurable benefit: 3/4 valid candidate arms smuggled Closes #99 vs 0/3 baseline — consistent with the warning raising keyword salience (interpretation, small n)."} -->

- Status: active
- Owner: owner/Astra planning
- Priority: P2
- Depends on: none

## Goal

Decide and pre-register the closing-keyword warning rephrase experiment: candidate positive-form (Refs by default) and hazard-named-without-pattern variants, re-measured T3/T3b before any template ships (Refs #190).

## Why

PCM-0046 T3 showed the warning sentence gave no measurable benefit: 3/4 valid candidate arms smuggled Closes #99 vs 0/3 baseline — consistent with the warning raising keyword salience (interpretation, small n).

## Allowed files

After the owner answer on #190: guidance generator + all checked-in copies of the keyword sentence, policy-test pins, docs/plans/PCM-0064-arm-plan.md (new pre-registration), fixtures only if the rubric needs a new control; this increment changes only this task file. Out: sanitizer code, schema changes.

## Human outcome

The shared guidance sentence stops being cargo-culted: either a tested phrasing reduces accidental issue closures, or PCM states in writing that the sentence has no measured benefit and keeps it for a declared reason.

## Scope and boundaries

- In scope: variant selection on #190, frozen pre-registration, one re-measure wave, honest reporting either way.
- Out of scope: changing the sanitizer or any CLI code path; shipping a variant without re-measure evidence.
- Dependencies/uncertainty: depends on #139 T3/T3b tallies; interacts with PCM-0058 1.2.0 readability wording (same copies).

## Acceptance criteria

- [ ] Owner records variant selection (A positive-form Refs-by-default, B hazard-named-without-literal-pattern, or both) on #190.
- [ ] Re-run of T3/T3b arms with frozen pre-registered prompts and rubric (ambiguous -> inconclusive) reported honestly; six contexts on any guidance change + receipt on #190.
- [ ] (proposed) A candidate variant is adopted only if it beats the current sentence on keyword-smuggling rate without regressing the T1b append controls.

## Evidence and sources

T3 1/4 valid pass vs T3b 3/3 zero-keyword from accepted docs/plans/PCM-0046-arms-results/scored.json + overrides.json; the salience interpretation is labeled inference (small n) on #190.

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none): leaf #190 (PCM-0064); parent: #139 (CLOSED; the holdout that produced the evidence — this is a behavior-change proposal, not a reopen).
- Primary writer / branch / source issue revision / as-of status: owner/Astra (omp session); branch task/PCM-0063-projections (projection increment only, no code); source: live issue bodies; as-of 2026-09-26T11:35Z.
- Related PR/CI evidence and push receipt (request ID / SHA): none yet (decision gate); arms evidence rides PCM-0046 (PRs #188/#192/#193).

## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
