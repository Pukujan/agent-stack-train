# TASK-OIO-0002 — Route the template to its source and fail closed on stack drift

<!-- continuity:task {"acceptance":["scripts/check_stack_consistency.py exits 0 when the manifest and the release train agree and non-zero when a pinned version, commit, train name, or the component set disagrees","the gates job runs the consistency check before the YAML parse step","the observational-issue template names Pukujan/observational-issue-ops as its source and still parses as YAML","continuity validate --root . returns VALID","the increment is pushed through a merged PR on a task branch"],"depends_on":["OIO-0001"],"goal":"Make the observational-issue template name OIO as its source, and make the required gates fail closed when stack-manifest.json disagrees with stack-releases.json","id":"OIO-0002","issue_url":"https://github.com/Pukujan/observational-issue-ops/issues/4","next_action":"open the PR, confirm the gates job passes, then merge","owner":"owner/Pukujan","priority":"P6","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"OIO publishes a release train and pins itself with a manifest, but nothing checked that the two agree, so one edit could silently desynchronise them; and its issue template never named the repository that publishes it"} -->

- Status: active
- Owner: owner/Pukujan
- Priority: P6
- Depends on: OIO-0001 (the adoption scaffold and release train, merged)

## Goal

Make the observational-issue template name OIO as its source, and make the required `gates` check fail closed when `stack-manifest.json` disagrees with `stack-releases.json`.

## Why

OIO publishes a release train and pins itself with a manifest, but nothing checked that the two agree, so a single edit could silently desynchronise them — the exact drift the stack exists to remove. Separately, the issue template never named the repository that publishes it, so a filer had no signal that this form is the canonical one.

## Allowed files

- `.github/ISSUE_TEMPLATE/observational-issue.yml`
- `.github/workflows/ci.yml`
- `scripts/check_stack_consistency.py`
- `checkpoints/`, `tasks/`, `HANDOFF.md`

## Human outcome

An adopter can trust that OIO's own pins match the train OIO certifies, because the required check fails closed otherwise; and a filer reading the form can see which repository is the source of truth.

## Scope and boundaries

- In scope: the source note on the template, the consistency check, and its CI wiring.
- Out of scope: changing any template field, changing the certified versions, or migrating another repository.
- Dependencies/uncertainty: none blocking.

## Acceptance criteria

- [ ] `python scripts/check_stack_consistency.py` exits 0 when the two files agree and non-zero when a pinned version, commit, train name, or the component set disagrees.
- [ ] The `gates` job runs the consistency check.
- [ ] The template names `Pukujan/observational-issue-ops` as its source and still parses as YAML.
- [ ] `continuity validate --root .` returns `VALID`.
- [ ] The increment is pushed through a merged PR on a task branch.

## Evidence and sources

- Leaf owning issue: [#4](https://github.com/Pukujan/observational-issue-ops/issues/4).
- Parent tracking issue: [#1](https://github.com/Pukujan/observational-issue-ops/issues/1).
- Plan of record: [Pukujan/project-continuity-modules#226](https://github.com/Pukujan/project-continuity-modules/issues/226).

## Related records

- Leaf owning issue: [#4](https://github.com/Pukujan/observational-issue-ops/issues/4). Parent ancestry: [#1](https://github.com/Pukujan/observational-issue-ops/issues/1). Dependencies: OIO-0001 (merged).
- Primary writer / branch / source issue revision / as-of status: agent session / `task/OIO-0002-template-routing-and-consistency` / issue #4 as filed / active.

## Checkpoint log
