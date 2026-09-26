# TASK-PCM-0059 — Distributed Runtime Promotion

<!-- continuity:task {"acceptance": ["Owner records scope answer on #181: adopt promotion-as-record + provenance-feedback contract, defer parts, or reject; PCM-0059 closes as decision record either way.", "If adopted: guidance/docs slice (PROJECT Operating-environment convention extension from #142 + TARGET_ADOPTION promotion section), no schema/CLI change; merged under six contexts + receipt on #181.", "No new hosted service, no auto-deployer, and no unsupervised runtime writes to canonical files appear anywhere in the result."], "depends_on": [], "goal": "Decide PCM's distributed-runtime model: environment roles (work/accepted/staged/live), promotion-as-continuity-record, and the runtime-feedback contract (issue updates with provenance, never unsupervised repo writes) per the GitOps research cited on #181.", "id": "PCM-0059", "issue_url": "https://github.com/Pukujan/project-continuity-modules/issues/181", "next_action": "Owner scope answer on #181 (adopt promotion-as-record + provenance-feedback contract, defer parts, or reject); PCM-0059 closes as a decision record either way.", "owner": "owner/Astra planning", "priority": "P2", "protocol_version": "0.1.0-draft", "schema": "project-continuity.task.v1", "status": "active", "why": "Owner asked how production vs test branches, explicit-go promotion, and scheduled pulls fit PCM; today the protocol names none of it (#181 records the gap with sources)."} -->

- Status: active
- Owner: owner/Astra planning
- Priority: P2
- Depends on: none

## Goal

Decide PCM's distributed-runtime model: environment roles (work/accepted/staged/live), promotion-as-continuity-record, and the runtime-feedback contract (issue updates with provenance, never unsupervised repo writes) per the GitOps research cited on #181.

## Why

Owner asked how production vs test branches, explicit-go promotion, and scheduled pulls fit PCM; today the protocol names none of it (#181 records the gap with sources).

## Allowed files

See leaf issue: the scope decision names the exact files; until then this task changes no repository content.

## Human outcome

A fresh adopter session reading accepted history learns which environment a fact was observed in and how work is promoted (work -> accepted -> staged/live as continuity records with provenance), without PCM acquiring a deployer or any runtime writing to repositories unsupervised.

## Scope and boundaries

- In scope: the decision record + any slice the owner approves on the leaf issue.
- Out of scope: everything the leaf issue's boundaries section excludes.
- Dependencies/uncertainty: owner scope answer pending.

## Acceptance criteria

- [ ] Owner records scope answer on #181: adopt promotion-as-record + provenance-feedback contract, defer parts, or reject; PCM-0059 closes as decision record either way.
- [ ] If adopted: guidance/docs slice (PROJECT Operating-environment convention extension from #142 + TARGET_ADOPTION promotion section), no schema/CLI change; merged under six contexts + receipt on #181.
- [ ] No new hosted service, no auto-deployer, and no unsupervised runtime writes to canonical files appear anywhere in the result.

## Evidence and sources

Leaf issue #181 records the gap with GitOps sources (Argo/Flux pull models cited there); this task changes no repository content until the owner answers.

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none): leaf #181 (PCM-0059); parent: #142 (decision 5842123846); depends: #142 docs slice; related #162/#166/#169, #137, #180.
- Primary writer / branch / source issue revision / as-of status: owner/Astra (omp session); branch task/PCM-0063-projections (projection increment only, no code); source: live issue bodies; as-of 2026-09-26T11:35Z.
- Related PR/CI evidence and push receipt (request ID / SHA): none yet (decision gate); arms evidence rides PCM-0046 (PRs #188/#192/#193).

## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
