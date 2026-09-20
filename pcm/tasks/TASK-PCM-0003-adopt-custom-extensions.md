# TASK-PCM-0003 — Adopt continuity v1 in custom-extensions

<!-- continuity:task {"acceptance":["custom-extensions adopts protocol v1 without replacing its existing human-readable project/handoff contracts","specs/PDD.md carries valid continuity project metadata and remains the stable product contract","HANDOFF.md carries valid continuity current metadata and remains the mutable checkpoint","a target .continuity/config.json declares protocol/version/software profile/task prefix and canonical paths","target schemas/v1 exactly match the protocol repository v1 schema files","root tasks location is available for future bounded root tasks without duplicating the feature-branch PROV task","the target repository validates with the PCM v1 validator","no extension runtime code, release/current.json, registry status, permissions, or provenance-exporter feature branch is changed","target adoption PR is mergeable and all available CI/status gates are satisfied before merge","exact evidence, decisions, blockers, changed paths, and one next action are checkpointed before stop"],"depends_on":["PCM-0002"],"goal":"Adopt Project Continuity Protocol v1 in Pukujan/custom-extensions as a non-destructive overlay on its existing repository contracts.","id":"PCM-0003","next_action":"Review and merge task/PCM-0003-adopt-custom-extensions; after merge, activate PCM-0004.","owner":"ChatGPT/Sol current implementation session; GitHub assignee Pukujan","priority":"P0","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"PCM-0001 and PCM-0002 proved the protocol in its own repository and a fresh minimal target; the next risk is adopting it into a mature repository without erasing existing continuity semantics."} -->

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

- [x] custom-extensions adopts protocol v1 without replacing its existing human-readable project/handoff contracts;
- [x] `specs/PDD.md` carries valid continuity project metadata and remains the stable product contract;
- [x] `HANDOFF.md` carries valid continuity current metadata and remains the mutable checkpoint;
- [x] a target `.continuity/config.json` declares protocol/version/software profile/task prefix and canonical paths;
- [x] target `schemas/v1` exactly match the protocol repository v1 schema files;
- [x] root tasks location is available for future bounded root tasks without duplicating the feature-branch PROV task;
- [x] the target repository validates with the PCM v1 validator;
- [x] no extension runtime code, `release/current.json`, registry status, permissions, or provenance-exporter feature branch is changed;
- [x] target adoption PR is mergeable and all available CI/status gates are satisfied before merge;
- [x] exact evidence, decisions, blockers, changed paths, and one next action are checkpointed before stop.

## Evidence expectations

Record target branch/ref/commit, exact validator command/result, schema identity evidence, target PR mergeability/status checks, and the fact that the release workflow is not triggered by these paths.

## Checkpoint log

No checkpoints yet.

### 2026-09-20 18:37:00 UTC — ChatGPT/Sol custom-extensions adoption

<!-- continuity:checkpoint {"agent":"ChatGPT/Sol custom-extensions adoption","blocked":[],"changed":["Pukujan/custom-extensions:.continuity/config.json","Pukujan/custom-extensions:schemas/v1/**","Pukujan/custom-extensions:specs/PDD.md","Pukujan/custom-extensions:HANDOFF.md","Pukujan/custom-extensions:tasks/.gitkeep","tasks/TASK-PCM-0003-adopt-custom-extensions.md","checkpoints/CURRENT.md","HANDOFF.md"],"completed":["Adopted continuity v1 in Pukujan/custom-extensions as a non-destructive overlay on its existing PDD/HANDOFF contracts.","Validated the target continuity state and verified exact schema identity.","Merged target PR #8 after mergeability and all available CI/status gates passed."],"decisions":["Use specs/PDD.md as canonical PROJECT and HANDOFF.md as canonical CURRENT instead of replacing mature target documents.","Keep active ChatGPT Provenance Exporter work branch-local; main declares no active root continuity task.","Do not modify extension runtime, release descriptor, registry status, permissions, package scripts, or the provenance feature branch."],"evidence":["Target config: profile=software, task_prefix=CEX, project=specs/PDD.md, current=HANDOFF.md, tasks=tasks.","PCM v1 validator on the adopted continuity state -> VALID.","Target schema blob SHAs exactly match protocol repo: config 8cff4abc2ddbc26a21ce33a7867a924fd2e13b73; project b0fc0d6dfc34975f1167eb32a69a7eb711473b23; current 3eaa0e4c79595ec9bc5f3cf4058cab0f91d235e8; task a6f61c1f8b110687a103775c56c45dc6359e63f1; checkpoint 5162bbaaf01331c0a28b0c9f964cb3c8ed7b63c8; context-pack 97626e34144e20e8feb35ffc3b5351afa154d24f.","Target PR #8 -> mergeable=true; 0 statuses; 0 check runs; 0 workflow runs; release workflow paths not touched.","Target PR #8 merged -> f77979d51302c2af328c7f16037312fefadc784c.","Post-merge target main contains continuity config plus project/current metadata markers."],"next_action":"Review and merge task/PCM-0003-adopt-custom-extensions; after merge, activate PCM-0004.","protocol_version":"0.1.0-draft","schema":"project-continuity.checkpoint.v1","task_id":"PCM-0003","timestamp":"2026-09-20T18:37:00Z"} -->

Completed:
- Adopted continuity v1 in `Pukujan/custom-extensions` as a non-destructive overlay on its existing PDD/HANDOFF contracts.
- Validated the target continuity state and verified exact schema identity.
- Merged target PR #8 after mergeability and all available CI/status gates passed.

Evidence:
- target config: `profile=software`, `task_prefix=CEX`, `project=specs/PDD.md`, `current=HANDOFF.md`, `tasks=tasks`;
- PCM v1 validator on the adopted continuity state -> `VALID`;
- all six target schema blob SHAs exactly match the protocol repository;
- target PR #8 -> `mergeable=true`; 0 statuses; 0 check runs; 0 workflow runs; release workflow paths not touched;
- target PR #8 merged -> `f77979d51302c2af328c7f16037312fefadc784c`;
- post-merge target `main` contains the continuity config and project/current metadata markers.

Decisions:
- Use `specs/PDD.md` as canonical PROJECT and `HANDOFF.md` as canonical CURRENT instead of replacing mature target documents.
- Keep active ChatGPT Provenance Exporter work branch-local; `main` declares no active root continuity task.
- Do not modify extension runtime, release descriptor, registry status, permissions, package scripts, or the provenance feature branch.

Changed:
- `Pukujan/custom-extensions:.continuity/config.json`
- `Pukujan/custom-extensions:schemas/v1/**`
- `Pukujan/custom-extensions:specs/PDD.md`
- `Pukujan/custom-extensions:HANDOFF.md`
- `Pukujan/custom-extensions:tasks/.gitkeep`
- `tasks/TASK-PCM-0003-adopt-custom-extensions.md`
- `checkpoints/CURRENT.md`
- `HANDOFF.md`

Blocked/uncertain:
- none

Next:
- Review and merge `task/PCM-0003-adopt-custom-extensions`; after merge, activate PCM-0004.

## Handoff

Fresh session: read PROJECT -> CURRENT -> this task -> SPEC, then the target repository HANDOFF/AGENTS/read order. Work only PCM-0003.
