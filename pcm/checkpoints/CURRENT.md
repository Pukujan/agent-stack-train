# Current Repository Checkpoint

## Program state

Phase: bootstrap — define and implement protocol v1.

Current P0 task: `TASK-PCM-0001-bootstrap-v1.md`.

## Main objective

Turn the continuity pattern proven in Eval Lab and the ChatGPT provenance-exporter project into a reusable, machine-validatable, versioned protocol/toolkit that another project can adopt without manually recreating the structure.

## Completed

- repository created;
- core project contract defined;
- draft v1 normative concepts written;
- self-hosting AGENTS/read-order established;
- protocol configuration introduced;
- handoff/versioning docs established;
- active bootstrap task prepared.

## Active

- PCM-0001: v1 schemas/templates/CLI/validator/bootstrap design and implementation.

## Queued

1. PCM-0002 — dogfood v1 on a minimal fixture repository.
2. PCM-0003 — migrate/adopt in `Pukujan/custom-extensions`.
3. PCM-0004 — migrate/adopt in `Pukujan/Eval-lab`.
4. PCM-0005 — GitHub Issue adapter and bidirectional consistency checks.
5. PCM-0006 — optional Beads adapter.
6. PCM-0007 — protocol v1.0 release/migration contract.

## Blockers

None known at bootstrap. Tooling language/package choice remains an implementation decision for PCM-0001 and should be justified in-task.

## Next atomic action

Implement PCM-0001 from its task contract: define v1 machine-readable schemas and templates first, then the smallest validator/bootstrap CLI needed to initialize and validate a fixture repository.
