# TASK-PCM-0059 — Distributed Runtime Promotion

<!-- continuity:task {"acceptance":["Owner records scope answer on #181: adopt promotion-as-record + provenance-feedback contract, defer parts, or reject; PCM-0059 closes as decision record either way.","If adopted: guidance/docs slice (PROJECT Operating-environment convention extension from #142 + TARGET_ADOPTION promotion section), no schema/CLI change; merged under six contexts + receipt on #181.","No new hosted service, no auto-deployer, and no unsupervised runtime writes to canonical files appear anywhere in the result."],"depends_on":[],"goal":"Decide PCM's distributed-runtime model: environment roles (work/accepted/staged/live), promotion-as-continuity-record, and the runtime-feedback contract (issue updates with provenance, never unsupervised repo writes) per the GitOps research cited on #181.","id":"PCM-0059","issue_url":"https://github.com/Pukujan/project-continuity-modules/issues/181","next_action":"Owner decision gate on the linked leaf issue first; then implement per # acceptance list.","owner":"owner/Astra planning","priority":"P2","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Owner asked how production vs test branches, explicit-go promotion, and scheduled pulls fit PCM; today the protocol names none of it (#181 records the gap with sources)."} -->

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

Describe what becomes easier, safer, clearer, or possible when this task is complete.

## Scope and boundaries

- In scope: the decision record + any slice the owner approves on the leaf issue.
- Out of scope: everything the leaf issue's boundaries section excludes.
- Dependencies/uncertainty: owner scope answer pending.

## Acceptance criteria

- [ ] state observable, task-specific outcomes.

## Evidence and sources

Link repository state at a revision and cite external factual claims directly. Record commands and results for claims that need verification.

## Reproduction details (only when needed)

Starting revision, material inputs/configuration, runtime, exact command or prompt, observed result, and limitations.

## Related records

- Required leaf owning issue, parent ancestry and dependencies (or explicitly none):
- Primary writer / branch / source issue revision / as-of status:
- Related PR/CI evidence and push receipt (request ID / SHA):

## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
