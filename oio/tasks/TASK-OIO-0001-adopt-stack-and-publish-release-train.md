# TASK-OIO-0001 — Adopt Stack And Publish Release Train

<!-- continuity:task {"acceptance":["continuity validate --root . returns VALID","validate_content_system.py --adapter .content-system --project-root . --check-adopter-readme prints VALID","stack-manifest.json and stack-releases.json exist and name the same four components","the scaffold is pushed through a merged PR on a task branch, not committed to main"],"depends_on":[],"goal":"Make OIO a clean adopter of the PCM + CGM + ACS stack and publish the release train","id":"OIO-0001","issue_url":"https://github.com/Pukujan/observational-issue-ops/issues/1","next_action":"open the PR for the adoption scaffold and confirm required gates before merge","owner":"owner/Pukujan","priority":"P5","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"OIO governs the shared issue protocol but was not itself wired into the stack it governs, risking the same drift the stack exists to remove"} -->

- Status: active
- Owner: owner/Pukujan
- Priority: P5
- Depends on: none

## Goal

Make OIO a clean adopter of the PCM + CGM + ACS stack and publish the release train.

## Why

OIO governs the shared issue protocol but was not itself wired into the stack it governs, risking the same drift the stack exists to remove.

## Allowed files

- `PROJECT.md`, `AGENTS.md`, `HANDOFF.md`, `checkpoints/`, `tasks/`, `.continuity/`, `schemas/`
- `.content-system/`
- `stack-manifest.json`, `stack-releases.json`
- `docs/assets/`
- `README.md`

## Human outcome

A maintainer can open OIO, read one manifest, and know exactly which PCM, CGM, and ACS versions this repository consumes; and any adopter can read one release train to pin the same set. OIO stops being a document outside the stack and becomes a member of it.

## Scope and boundaries

- In scope: the PCM continuity scaffold, the CGM adapter and narrative assets, the stack manifest and release train, and the adopter README.
- Out of scope: migrating any other repository onto the shared source (that is a separate owner-gated step per repository).
- Dependencies/uncertainty: none blocking. The release train names the versions the sibling issues certified; no adopter has consumed it yet.

## Acceptance criteria

- [ ] `continuity validate --root .` returns `VALID`.
- [ ] `python scripts/validate_content_system.py --root "$CGM_ROOT" --adapter .content-system --project-root . --check-adopter-readme` prints `VALID`.
- [ ] `stack-manifest.json` and `stack-releases.json` exist and name the same four components (OIO, PCM, CGM, ACS).
- [ ] The scaffold is pushed through a merged PR on a task branch, not committed straight to `main`.

## Evidence and sources

- PCM CLI 0.6.0 @ `4e2385474b4af9249ca009cbdcb38c4498932475`.
- CGM 0.5.7 @ `c069613ca8b3e02bcf5aba1960160583537f8a3a`.
- ACS module `multi-agent-hotload` @ `0.1.0`.
- Plan of record: [Pukujan/project-continuity-modules#226](https://github.com/Pukujan/project-continuity-modules/issues/226).

## Reproduction details (only when needed)

Run the two validators above from a checkout of the pinned CGM (the content validator defaults its `--root` to the current directory).

## Related records

- Leaf owning issue: [#1](https://github.com/Pukujan/observational-issue-ops/issues/1). Parent ancestry: none. Dependencies: none.
- Primary writer / branch / source issue revision / as-of status: agent session / `task/OIO-0001-adopt-stack` / issue #1 as filed / active.
- Related PR/CI evidence and push receipt (request ID / SHA): pending.

## Checkpoint log

No checkpoints yet.

## Handoff

Read PROJECT → CURRENT → this task → minimum relevant spec. Checkpoint before stopping.
