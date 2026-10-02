# Agent Stack Train — Project Contract

## Main goal

Own the **one certified version set** for the agent stack — a single, versioned record of which component versions are compatible with each other — so that every repository in the stack reads compatible versions from one place instead of hand-copying a pin into many files.

## Why

The same version pin was hand-copied across many files and drifted: measured 2026-10-01, one pin lived in thirteen files across three revisions. Worse, the pin lived inside one of the product repositories, so that repository certified its own siblings and every other repository had to trust a peer's file to learn what "compatible" meant. Versions are a different kind of artifact from the products they describe, so they get their own home.

## Scope

- `stack-releases.json` — the certified version set: one entry per component, with version, commit, and role.
- `stack-manifest.schema.json` — the shape of an adopter's own pin file.
- `scripts/check_manifest.py` — the reusable check an adopter runs in CI to prove its manifest agrees with the train.
- The rule for reading the train: pin once, reference by version, never hand-copy.

## Non-goals

- **Does not own any adopter's product code, issues, or releases.** It describes them.
- **Does not own the components' own development.** Each component repository owns its code, its issues, and its release.
- **Does not replace** PCM (execution continuity), CGM (narrative and style), ACS (the install surface), or OIO (the issue log).
- **Does not certify a version it has not been asked to.** `status: proposed` until the owner accepts a train.

## Who owns which pins

- **This repository** owns the certified version set — the answer to "which versions are compatible".
- **Each adopter** owns its own `stack-manifest.json` — the answer to "which train and components this repository consumes".
- No repository owns another repository's pins.

## Definition of success

- An adopter reads every compatible version from one train, and a check fails closed when its manifest disagrees.
- A version pin appears in exactly one place — the train — and every adopter points at it rather than restating it.
- No product repository certifies its own siblings.
