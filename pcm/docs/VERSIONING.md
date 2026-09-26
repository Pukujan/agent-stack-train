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

PCM-0009 therefore sets the CLI/package source version to **0.2.0** because it adds the backward-compatible `preflight` command and adoption contract. This is version metadata, not evidence that a public package was published. The repository protocol remains **0.1.0-draft** because no required canonical object or schema meaning changes.

PCM-0010 keeps the repository protocol at **0.1.0-draft**. Recovery receipts are optional, backward-compatible evidence outside the required canonical lifecycle; they do not replace or weaken existing PROJECT/CURRENT/TASK/CHECKPOINT schemas. The CLI/package remains on the 0.2.x compatibility line while it adds degraded-continuity handling and recovery reconciliation.

PCM-0018 sets the backward-compatible CLI/package source version to **0.3.0**: checkpoint request IDs are an optional extension marker, and a document catalog is an optional capability. Existing checkpoint history stays readable, repositories need not adopt a catalog, and old validators can ignore the extension marker and unrecognized catalog files. This does not publish a package. The protocol remains **0.1.0-draft** because no new canonical object is required for every repository.

PCM-0024 sets the backward-compatible CLI/package source version to **0.4.0**: it adds read-only GitHub issue verification and private local workspace registration/reuse. `issue_url` is optional task metadata generally, but repositories that enable `trackers.github` require it for active tasks and new task creation. This does not publish a package. The protocol remains **0.1.0-draft** because the authority behavior is opt-in for GitHub repositories and existing non-GitHub repositories remain valid.

PCM-0027 sets the backward-compatible CLI/package source version to **0.5.0**: `continuity validate` gains the issue-log-format marker checks (missing and stale are warnings, contradictory or malformed is an error) and the generated guidance carries the new `issue-log-format` **1.0.0** module block ([`docs/ISSUE_LOG_FORMAT.md`](ISSUE_LOG_FORMAT.md)). Because that normative reference changes the record contract, continuity-records guidance is now policy **1.3.0**. This does not publish a package. The protocol remains **0.1.0-draft** because no required canonical object or schema meaning changes; existing adopters follow the marker-replacement update path in `docs/ISSUE_LOG_FORMAT.md`.

PCM-0039 raises the `issue-log-format` policy module to **1.1.0** (2026-09-25, [#126](https://github.com/Pukujan/project-continuity-modules/issues/126)): the module and generated guidance gain diagram rules (when to draw, `graph TD` default, size caps, mandatory text alternative, collapsed wide diagrams, verify-before-publish, no standalone renderer links) verified against GitHub rendering in the `Pukujan/pcm-mermaid-matrix` evidence set. The CLI/package source version stays **0.5.0** — guidance text only, no new command or behavior contract — and no package is published. The protocol remains **0.1.0-draft**; existing adopters follow the marker-replacement update path in `docs/ISSUE_LOG_FORMAT.md`.

PCM-0057 raises the CLI/package source version to **0.6.0**: `continuity checkpoint` now prints a version-drift NOTE comparing the installed build against the checkout's declared version (owner decision B on [#162](https://github.com/Pukujan/project-continuity-modules/issues/162), observability only — never a refusal), and PCM-0055 changed the receipt POST wire format behind the same 0.5.0 label, so `continuity --version` must distinguish the two behaviors (the #162 stale-binary hazard class). This is a backward-compatible safety capability per the PATCH/MINOR rule above; no package is published. The protocol remains **0.1.0-draft**.

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

## PCM-0025 policy reconciliation

Continuity-record guidance is now policy **1.2.0**, tracked by [#66](https://github.com/Pukujan/project-continuity-modules/issues/66) under [#53](https://github.com/Pukujan/project-continuity-modules/issues/53). This corrects contradictory descriptions of the already-required GitHub authority and delivery contract; it adds no CLI command or schema field. Package source remains **0.4.0**, unpublished; the machine-readable protocol remains **0.1.0-draft**. Earlier opt-in wording above describes historical implementation, not an exemption from current governed-work policy.

Existing projects must reconcile PCM-owned guidance with SPEC section 8, preserving their domain content and historical checkpoints. GitHub issues own task/progression state; checked-in files are mandatory projections. Offline schema fixtures can still validate structurally, but that does not certify GitHub governance, semantic agreement, required CI or auto-merge. Generated guidance changes reach newly initialized projects; existing adopters need a reviewed guidance update. No automatic migration, receipt automation or public release is claimed.
