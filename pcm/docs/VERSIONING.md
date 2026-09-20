# Protocol Versioning and Migration

## Version classes

The continuity protocol uses semantic-versioning principles.

### Patch
Clarifications, documentation fixes, validator bugs, or behavior fixes that do not change required repository state.

### Minor
Backward-compatible optional capabilities, new profiles, new optional fields/adapters.

### Major
Incompatible changes to required canonical objects, meanings, or validation invariants.

## Project declaration

A participating repository declares the protocol version in `.continuity/config.json`. The PCM-0001 executable draft uses config schema `project-continuity.config.v1`, protocol version `0.1.0-draft`, and JSON Schema contracts under `schemas/v1/`.

## Migration rule

A migration must:
- state source and target protocol versions;
- list required file/schema changes;
- preserve append-only historical checkpoints;
- never silently discard unknown project/task fields;
- generate a migration report;
- require explicit confirmation before destructive transformations.

## Draft phase

`0.1.0-draft` establishes the concrete v1 schema/tooling shape. A stable `1.0.0` release remains a later explicit task after dogfooding and migrations are demonstrated.
