# TASK-OIO-0003 — Redefine OIO as the issue-log ticketing system and move the train out

<!-- continuity:task {"acceptance":["PROJECT.md defines OIO as a repeatable issue-log ticketing system covering observational issues, operational issues, and proposals, with a required filer stamp and an explicit boundary against ACS, CGM, PCM, and the train repository","the canonical form requires an issue-type field (observational | operational | proposal | incident) and a filer stamp (filer_origin + filer_identity) and still parses as YAML","the triage labels by issue type and filer origin and fails closed with needs-filer-stamp when the stamp is missing or identity-less","stack-releases.json no longer exists in OIO and stack-manifest.json points at Pukujan/agent-stack-train","continuity validate --root . returns VALID and the pinned CGM validator returns VALID","the increment is pushed through a merged PR on a task branch"],"depends_on":["OIO-0002"],"goal":"Rewrite OIO's definition to the issue-log ticketing system the owner specified, add the issue-type and filer-stamp fields, and move the release train to its own repository","id":"OIO-0003","issue_url":"https://github.com/Pukujan/observational-issue-ops/issues/9","next_action":"none; delivered in PR #11 (squash 2a836a5)","owner":"owner/Pukujan","priority":"P3","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"completed","why":"OIO's checked-in definition was narrower than its purpose (observational-only, no filer stamp) and it published the stack's release train, which made a product repository certify its own siblings"} -->

- Status: completed
- Owner: owner/Pukujan
- Priority: P3
- Depends on: OIO-0002 (the template source note and the fail-closed consistency check, merged)

## Goal

Rewrite OIO's definition to the issue-log ticketing system the owner specified, add the issue-type and filer-stamp fields to the canonical form and its triage, and move the release train out of OIO into its own repository.

## Why

OIO's `PROJECT.md` described the repository as "a three-plane, non-binding **observational**-issue form and the triage that labels it". That is narrower than the job the repository exists to do: it omitted operational issues and agent-written proposals, and it never recorded *who or what filed an issue*, so a human's direct report and an agent's own proposal looked identical on the record. Separately, OIO published the stack's certified version set, which made a product repository certify its own siblings; the certified set is a different concern and belongs in its own repository.

## Allowed files

- `PROJECT.md`, `README.md`, `AGENTS.md`
- `.github/ISSUE_TEMPLATE/observational-issue.yml`
- `.github/workflows/issue-triage.yml`, `.github/workflows/ci.yml`
- `stack-manifest.json`, `stack-releases.json` (delete), `scripts/check_stack_consistency.py` (delete)
- `checkpoints/`, `tasks/`, `HANDOFF.md`

## Human outcome

A human filing directly, a human filing through an agent, and an agent proposing an issue on its own initiative all produce the same shape of record, distinguishable by the filer stamp, and an observational issue and an operational issue both route through the same triage. The certified version set lives in one place that no product repository owns.

## Scope and boundaries

- In scope: OIO's definition, the form's type and filer-stamp fields, the triage that labels them, and removing the release train from OIO.
- Out of scope: changing the certified versions, migrating another repository onto the train, and any change to CGM, PCM, or ACS.
- Dependencies/uncertainty: the new train repository is `Pukujan/agent-stack-train`; its train is still `status: proposed`.

## Acceptance criteria

- [x] `PROJECT.md` defines OIO as a repeatable issue-log ticketing system covering observational issues, operational issues, and proposals, with a required filer stamp and an explicit boundary against ACS, CGM, PCM, and the train repository.
- [x] The canonical form requires an issue-type field (observational | operational | proposal | incident) and a filer stamp (filer_origin + filer_identity) and still parses as YAML.
- [x] The triage labels by issue type and filer origin and fails closed with `needs-filer-stamp` when the stamp is missing or identity-less.
- [x] `stack-releases.json` no longer exists in OIO and `stack-manifest.json` points at `Pukujan/agent-stack-train`.
- [x] `continuity validate --root .` returns `VALID` and the pinned CGM validator returns `VALID`.
- [x] The increment is pushed through a merged PR on a task branch (PR #11).

## Evidence and sources

- Leaf owning issue: [#9](https://github.com/Pukujan/observational-issue-ops/issues/9).
- Train repository: [Pukujan/agent-stack-train](https://github.com/Pukujan/agent-stack-train) — bootstrap issue [#1](https://github.com/Pukujan/agent-stack-train/issues/1).
- Plan of record: [Pukujan/project-continuity-modules#226](https://github.com/Pukujan/project-continuity-modules/issues/226).

## Related records

- Leaf owning issue: [#9](https://github.com/Pukujan/observational-issue-ops/issues/9). Parent ancestry: none (top-level deliverable). Dependencies: OIO-0002 (merged).
- Primary writer / branch / source issue revision / as-of status: agent session / `task/OIO-0003-issue-log-definition` / issue #9 as filed / completed.

## Checkpoint log

- 2026-10-01: definition rewritten; form and triage extended with the issue type and filer stamp; `stack-releases.json` and the local consistency checker removed and the manifest repointed at `Pukujan/agent-stack-train`; both validators pass.
- 2026-10-01: merged via PR #11 (squash `2a836a5`); the required `gates` check passed; the receipt is on issue #9.
