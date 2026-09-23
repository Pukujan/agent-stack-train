# Versioning and Migration

PCM has two independent version identities:

- **CLI/package version** — the installable `project-continuity` tool in `pyproject.toml`.
- **protocol version** — the repository-state contract declared in `.continuity/config.json`.

A CLI release can add safety commands or fix validation behavior without forcing every target repository to migrate its protocol declaration.


## Protocol version classes

The continuity protocol uses semantic-versioning principles.

### Patch
Clarifications, documentation fixes, validator bugs, or behavior fixes that do not change required repository state.

### Minor
Backward-compatible optional capabilities, new profiles, new optional fields/adapters.

### Major
Incompatible changes to required canonical objects, meanings, or validation invariants.

## CLI/package version classes

The CLI/package also follows semantic versioning:

- PATCH: implementation/documentation fixes with no new public command or behavior contract.
- MINOR: backward-compatible commands or safety capabilities, such as target preflight.
- MAJOR: incompatible CLI/API changes.

PCM-0009 therefore releases as CLI/package **0.2.0** because it adds the backward-compatible `preflight` command and adoption contract. The repository protocol remains **0.1.0-draft** because no required canonical object or schema meaning changes.

PCM-0010 keeps the repository protocol at **0.1.0-draft**. Recovery receipts are optional, backward-compatible evidence outside the required canonical lifecycle; they do not replace or weaken existing PROJECT/CURRENT/TASK/CHECKPOINT schemas. The CLI/package remains on the 0.2.x compatibility line while it adds degraded-continuity handling and recovery reconciliation.

## Project declaration

The Python distribution's version has one source of truth in
`src/continuity/__init__.py`. Setuptools reads that value into build metadata,
and `continuity --version` reports the installed module version. CI installs
both wheel and source archive outside the checkout on each supported Python
version and checks their CLI and generated-project output against the source.
This verifies build/install behavior; it does **not** publish a public package
or prove a PyPI release exists. The repository protocol version remains an
independent value.

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
