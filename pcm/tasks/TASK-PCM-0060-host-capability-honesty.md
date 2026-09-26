# TASK-PCM-0060 — Host Capability Honesty

<!-- continuity:task {"acceptance":["Owner picks scope on #182 (probe-only / probe+SPEC adapter-seam / defer); decision comment cited in the task record.","Chosen slice lands red-first: capability classification of origin host in preflight (or doctor) with a printed matrix, template honesty sentence in all guidance copies + init output, SPEC interface note if approved; full suite at baseline; six contexts + receipt on #182.","GitHub fail-closed behavior unchanged: worktree removal still refuses non-verified hosts."],"depends_on":[],"goal":"Decide and implement non-GitHub host honesty: capability probe (preflight/doctor), template text that states which duties degrade without GitHub, documented 4-operation adapter seam in SPEC, and an install/onboarding page (#182).","id":"PCM-0060","issue_url":"https://github.com/Pukujan/project-continuity-modules/issues/182","next_action":"Owner decision gate on the linked leaf issue first; then implement per # acceptance list.","owner":"owner/Astra planning","priority":"P3","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"Today a GitLab adopter silently loses the issue-authority half while generated guidance promises it (cli.py:2256 github-only parse; nine gh call sites)."} -->

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
