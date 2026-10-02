# Agent Stack Train

> **One certified version set for the agent stack.** Every adopter pins the train once and reads compatible component versions from here, instead of hand-copying a pin into many files.

The stack is a set of repositories that ship together: a continuity system, a narrative system, an install surface, and an issue-log ticketing system. This repository holds the **certified version set** — the single answer to "which component versions are compatible with each other".

## Why this is its own repository

Two things went wrong when the certified set lived inside one of the components:

1. **A product certified its own siblings.** Every other repository had to trust a peer's file to learn what "compatible" meant.
2. **The pin was copied, so it drifted.** Measured 2026-10-01: one version pin lived in thirteen files across three revisions.

Versions are a different kind of artifact from the products they describe, so they get their own home.

## The two documents

| Document | Lives in | Owns |
| --- | --- | --- |
| [`stack-releases.json`](stack-releases.json) | **this repository** | The certified versions: one entry per component, with version, commit, and role. |
| `stack-manifest.json` | **each adopter** | That adopter's pins: which train it follows and which component versions it consumes. |

The adopter manifest shape is [`stack-manifest.schema.json`](stack-manifest.schema.json).

## Certified components

The current train is `2026-10-01`, status `proposed` — no adopter has been migrated onto it yet.

| Component | Version | Role |
| --- | --- | --- |
| `project-continuity-modules` | 0.6.0 | Execution continuity: tasks, checkpoints, immutable push receipts, required PR gates. |
| `content-generation-modules` | 0.5.12 | Narrative and styling authority: writing routing, human-sounding writing, output naming, visual direction, image generation. |
| `agent-custom-setup` | 0.1.0 (`multi-agent-hotload`) | Install surface: hot-load the full stack plus the coordination runtime. |
| `observational-issue-ops` | 0.1.0 | Issue-log ticketing system: the canonical issue form, the filer stamp, and its triage. |

## How to adopt

1. Add a `stack-manifest.json` to your repository, set `adopter` to your repository name, and point `source` at this repository's `stack-releases.json`.
2. Pin every component the train certifies, using the exact version, commit, and module count from the train.
3. Run the check in CI:

   ```bash
   python scripts/check_manifest.py --manifest stack-manifest.json \
     --train-url https://raw.githubusercontent.com/Pukujan/agent-stack-train/main/stack-releases.json
   ```

The check fails closed: a missing component, a version or commit that disagrees with the train, or a manifest that pins a component the train does not certify all exit non-zero.

## Validate

```bash
python scripts/check_manifest.py --self                 # this repository's train is well-formed
python scripts/check_manifest.py --manifest <path>      # an adopter's pins agree with the train
```

## Boundaries

- This repository owns **versions only** — no product code, no issue governance, no narrative, no execution continuity.
- A certified entry is a compatibility statement, not a release mandate. `status` moves from `proposed` to `certified` when the owner accepts a train.
- Changing a certified version is an owner-gated change.

## Ownership

- **This repository** owns the certified version set.
- **Each adopter** owns its own `stack-manifest.json`.
- No repository owns another repository's pins.
