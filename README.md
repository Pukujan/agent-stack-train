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

The live train is `current`. Versions are not copied into this README, because a copied table is how the 2026-10-01 snapshot stayed on PCM 0.6.0 after 0.7.0 had shipped. The versions are [`stack-releases.json`](stack-releases.json). `scripts/refresh_train.py` rewrites that file from the default branch of each component listed in [`components.json`](components.json). [Refresh the release train](.github/workflows/refresh-train.yml) runs that script every hour and on demand.

## How to adopt

1. Add a `stack-manifest.json` to your repository, set `adopter` to your repository name, set `release_train` to `current`, and point `source` at this repository's `stack-releases.json`.
2. Name every component the train certifies. Leave each pin empty to follow the train. Copy a version or commit only when that repository is deliberately frozen.
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
- A certified entry is the default-branch head of that component, refreshed by `scripts/refresh_train.py`. The owner accepted this channel on 2026-10-05 after the frozen `2026-10-01` snapshot held PCM at 0.6.0.
- A hand edit of a version in `stack-releases.json` is overwritten on the next refresh. Change `components.json` to change where a version is read from.

## Ownership

- **This repository** owns the certified version set.
- **Each adopter** owns its own `stack-manifest.json`.
- No repository owns another repository's pins.
