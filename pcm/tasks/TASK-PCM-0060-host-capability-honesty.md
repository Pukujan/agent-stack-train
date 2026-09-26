# TASK-PCM-0060 — Host Capability Honesty

<!-- continuity:task {"acceptance": ["Owner picks scope on #182 (probe-only / probe+SPEC adapter-seam / defer); decision comment cited in the task record.", "Chosen slice lands red-first: capability classification of origin host in preflight (or doctor) with a printed matrix, template honesty sentence in all guidance copies + init output, SPEC interface note if approved; full suite at baseline; six contexts + receipt on #182."], "depends_on": [], "goal": "Decide and implement non-GitHub host honesty: capability probe (preflight/doctor), template text that states which duties degrade without GitHub, documented 4-operation adapter seam in SPEC, and an install/onboarding page (#182).", "id": "PCM-0060", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/182", "next_action": "Owner scope answer on #182 (probe-only / probe+SPEC adapter-seam / defer); then implement per acceptance.", "owner": "owner/Astra planning", "priority": "P3", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "active", "why": "Today a GitLab adopter silently loses the issue-authority half while generated guidance promises it (cli.py:2256 github-only parse; nine gh call sites)."} -->

- Status: active
- Owner: owner/Astra planning
- Priority: P3
- Depends on: none

## Goal

Decide and implement non-GitHub host honesty: capability probe (preflight/doctor), template text that states which duties degrade without GitHub, documented 4-operation adapter seam in SPEC, and an install/onboarding page (#182).

## Why

Today a GitLab adopter silently loses the issue-authority half while generated guidance promises it (cli.py:2256 github-only parse; nine gh call sites).

## Allowed files

See leaf issue: the scope decision names the exact files; until then this task changes no repository content.

## Human outcome

Adopters on non-GitHub hosts learn, before being surprised, exactly which continuity guarantees (issue authority, receipts, merge-window checks) their host can and cannot provide, so silent loss of the issue-authority half becomes a stated limitation instead of a surprise.

## Scope and boundaries

- In scope: the decision record + any slice the owner approves on the leaf issue.
- Out of scope: everything the leaf issue's boundaries section excludes.
- Dependencies/uncertainty: owner scope answer pending.

## Acceptance criteria

- [ ] Owner picks scope on #182 (probe-only / probe+SPEC adapter-seam / defer); decision comment cited in the task record.
- [ ] Chosen slice lands red-first: capability classification of origin host in preflight (or doctor) with a printed matrix, template honesty sentence in all guidance copies + init output, SPEC interface note if approved; full suite at baseline; six contexts + receipt on #182.

## Evidence and sources

Leaf issue #182 records the current silent-degradation behavior; no host-capability probe exists in the CLI at 0.6.0 (observed: continuity preflight classifies nothing about the origin host).

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none): leaf #182 (PCM-0060); parent: none; depends: none; related #15, #33/#109, #162, #181.
- Primary writer / branch / source issue revision / as-of status: owner/Astra (omp session); branch task/PCM-0063-projections (projection increment only, no code); source: live issue bodies; as-of 2026-09-26T11:35Z.
- Related PR/CI evidence and push receipt (request ID / SHA): none yet (decision gate); arms evidence rides PCM-0046 (PRs #188/#192/#193).

## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
