# TASK-PCM-0003 — Adopt continuity v1 in custom-extensions

<!-- continuity:task {"acceptance":["custom-extensions adopts protocol v1 without replacing its existing human-readable project/handoff contracts","specs/PDD.md carries valid continuity project metadata and remains the stable product contract","HANDOFF.md carries valid continuity current metadata and remains the mutable checkpoint","a target .continuity/config.json declares protocol/version/software profile/task prefix and canonical paths","target schemas/v1 exactly match the protocol repository v1 schema files","root tasks location is available for future bounded root tasks without duplicating the feature-branch PROV task","the target repository validates with the PCM v1 validator","no extension runtime code, release/current.json, registry status, permissions, or provenance-exporter feature branch is changed","target adoption PR is mergeable and all available CI/status gates are satisfied before merge","exact evidence, decisions, blockers, changed paths, and one next action are checkpointed before stop"],"depends_on":["PCM-0002"],"goal":"Adopt Project Continuity Protocol v1 in Pukujan/custom-extensions as a non-destructive overlay on its existing repository contracts.","id":"PCM-0003","next_action":"Create the target adoption branch, add the non-destructive continuity overlay, validate it with the PCM v1 validator, and open/merge the target PR only if all available gates pass.","owner":"ChatGPT/Sol current implementation session; GitHub assignee Pukujan","priority":"P0","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"PCM-0001 and PCM-0002 proved the protocol in its own repository and a fresh minimal target; the next risk is adopting it into a mature repository without erasing existing continuity semantics."} -->

- Status: active
- Owner: ChatGPT/Sol current implementation session; GitHub assignee Pukujan
- Priority: P0
- Depends on: PCM-0002
- Suggested branch: `task/PCM-0003-adopt-custom-extensions`
- GitHub issue: #5
- Target repository: `Pukujan/custom-extensions`

## Goal

Adopt Project Continuity Protocol v1 in `Pukujan/custom-extensions` as a non-destructive overlay on its existing repository contracts.

## Target repository findings

- existing `AGENTS.md`, `HANDOFF.md`, root PDD/SDD, status/release process, and extension registry are authoritative;
- `specs/PDD.md` already expresses stable product intent/properties and is the best PROJECT equivalent;
- `HANDOFF.md` already serves as the mutable repository checkpoint;
- active ChatGPT Provenance Exporter work is intentionally isolated on `feature/chatgpt-provenance-exporter` and must not be merged or duplicated by this task;
- release workflow runs only for `release/current.json` changes on `main`, so continuity-only adoption does not trigger release CI.

## Allowed files

In `project-continuity-modules`:
- `tasks/TASK-PCM-0002-dogfood-minimal.md` only for final completion checkpoint/status;
- `tasks/TASK-PCM-0003-adopt-custom-extensions.md`;
- `checkpoints/CURRENT.md`;
- `HANDOFF.md`.

In `Pukujan/custom-extensions` on a dedicated adoption branch:
- `.continuity/config.json`;
- `schemas/v1/**`;
- `specs/PDD.md` metadata marker only;
- `HANDOFF.md` metadata marker plus minimal continuity note if needed;
- `tasks/.gitkeep` or equivalent empty root task location if Git requires a tracked path.

Do not modify extension runtime code, manifests, permissions, `extensions/registry.json`, `release/current.json`, release notes, package scripts, root behavioral specs, or the provenance-exporter feature branch.

## Acceptance criteria

- [ ] custom-extensions adopts protocol v1 without replacing its existing human-readable project/handoff contracts;
- [ ] `specs/PDD.md` carries valid continuity project metadata and remains the stable product contract;
- [ ] `HANDOFF.md` carries valid continuity current metadata and remains the mutable checkpoint;
- [ ] a target `.continuity/config.json` declares protocol/version/software profile/task prefix and canonical paths;
- [ ] target `schemas/v1` exactly match the protocol repository v1 schema files;
- [ ] root tasks location is available for future bounded root tasks without duplicating the feature-branch PROV task;
- [ ] the target repository validates with the PCM v1 validator;
- [ ] no extension runtime code, `release/current.json`, registry status, permissions, or provenance-exporter feature branch is changed;
- [ ] target adoption PR is mergeable and all available CI/status gates are satisfied before merge;
- [ ] exact evidence, decisions, blockers, changed paths, and one next action are checkpointed before stop.

## Evidence expectations

Record target branch/ref/commit, exact validator command/result, schema identity evidence, target PR mergeability/status checks, and the fact that the release workflow is not triggered by these paths.

## Checkpoint log

No checkpoints yet.

## Handoff

Fresh session: read PROJECT -> CURRENT -> this task -> SPEC, then the target repository HANDOFF/AGENTS/read order. Work only PCM-0003.
