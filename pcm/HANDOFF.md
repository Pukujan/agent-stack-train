# Current Handoff

This repository is ready for a fresh session without prior chat history.

## Active work

- Task: `PCM-0003 — Adopt continuity v1 in custom-extensions`
- GitHub issue: #5
- Suggested task branch: `task/PCM-0003-adopt-custom-extensions`
- Canonical task file: `tasks/TASK-PCM-0003-adopt-custom-extensions.md`
- Target repository: `Pukujan/custom-extensions`

## Read exactly this first

1. `PROJECT.md`
2. `AGENTS.md`
3. `checkpoints/CURRENT.md`
4. `tasks/TASK-PCM-0003-adopt-custom-extensions.md`
5. `SPEC.md`
6. target repository `HANDOFF.md` and its prescribed read order

Then implement only the bounded adoption task. Do not reconstruct project state from prior conversations.

## Exact next action

Create the target adoption branch, add the non-destructive continuity overlay, validate it with the PCM v1 validator, and merge the target PR only if all available gates pass.

## Authority

PCM task state is canonical in this repository. Existing target-repository contracts remain authoritative for target semantics; PCM-0003 must overlay rather than replace them.
