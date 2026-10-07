# Agent Stack Train — Project Contract

## Main goal

Own the **one certified version set** for the agent stack — a single, versioned record of which component versions are compatible with each other — so that every repository in the stack reads compatible versions from one place instead of hand-copying a pin into many files.

## Why

The same version pin was hand-copied across many files and drifted: measured 2026-10-01, one pin lived in thirteen files across three revisions. Worse, the pin lived inside one of the product repositories, so that repository certified its own siblings and every other repository had to trust a peer's file to learn what "compatible" meant. Versions are a different kind of artifact from the products they describe, so they get their own home.

## Scope

- `stack-releases.json` — the certified version set: one entry per component, with version, commit, and role. It records each component's default-branch head.
- `components.json` — where each version is read from (repository, version file, and role).
- `stack-manifest.schema.json` — the shape of an adopter's own pin file. An empty pin follows the train.
- `scripts/check_manifest.py` — the reusable check an adopter runs in CI to prove its manifest agrees with the train.
- `scripts/refresh_train.py` — rewrites the certified set from those default branches, skipping a head that changed only the mesh. The refresh workflow runs it on a schedule.
- The rule for reading the train: pin once, read the version from the train, never hand-copy.

## Non-goals

- **Does not own any adopter's product code, issues, or releases.** It describes them.
- **Does not own the components' own development.** Each component repository owns its code, its issues, and its release.
- **Does not replace** PCM (execution continuity), CGM (narrative and style), ACS (the install surface), or OIO (the issue log).
- **Does not invent a version.** It records the version each component's default branch declares. The owner asked for that channel on 2026-10-05, when the frozen `2026-10-01` snapshot was still certifying PCM 0.6.0 after 0.7.0 had shipped.

## Who owns which pins

- **This repository** owns the certified version set — the answer to "which versions are compatible".
- **Each adopter** owns its own `stack-manifest.json` — the answer to "which train and components this repository consumes".
- No repository owns another repository's pins.

## Definition of success

- An adopter reads every compatible version from one train, and a check fails closed when a copied pin disagrees.
- A version pin appears in exactly one place — the train — and every adopter points at it rather than restating it.
- The train moves when a component's default branch moves, so a newer commit is the certified commit without a separate re-certification.
- No product repository certifies its own siblings.
