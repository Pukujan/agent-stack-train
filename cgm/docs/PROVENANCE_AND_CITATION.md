# Claim evidence, citations, and provenance

Use this guide when a README, product page, research summary, or marketing claim needs a reader to verify where it came from.

## Start with the claim, then find its source

For each material factual claim, write down:

| Field | Meaning |
| --- | --- |
| Claim | The smallest factual statement a reader may rely on. |
| Status | `shipped`, `experimentally_supported`, `planned`, or `unknown`. |
| Source | The record and revision that supports or qualifies it. |
| Supports | What the source actually establishes, in plain language. |
| Limits | What the source leaves unproven, in plain language. |
| Public citation | The direct link a README reader can follow, when disclosure is appropriate. |

Do not cite the claim's own generated paragraph as evidence for the product behavior described by that paragraph. A source link establishes traceability; it does not establish that the source's conclusion is correct.

## Classify before writing

Keep these epistemic classes distinct:

- user observation — what the owner or user reported or preferred;
- repository fact — what a pinned file, test, commit, or run directly shows;
- external source — a paper, standard, official document, or other cited publication;
- experiment result — a result with its target, method, run, and limitations;
- inference — a reasoned conclusion from identified sources;
- hypothesis — a proposition that still needs a test;
- unknown — not established by available evidence.

Do not turn an observation into a universal finding, an inference into an observed fact, or a plan into a shipped feature. Preserve contradictions and unsupported mappings.

## Cite where readers need verification

Place direct links near the claim they support. Use commit-pinned repository permalinks rather than a moving `main` link when the exact revision matters. Give external sources a descriptive title and link; include author/date when it helps identify a publication. For a mutable web page, record when it was accessed in the claim's `source_revision`. Keep the README readable by putting implementation-level provenance in the evidence section or linked record, not by attaching dense metadata to every sentence.

## Provenance and temporal records

For each v2 evidence item, `recorded_at` is the timezone-aware transaction time when this version of the record was entered. It is distinct from source dates such as `observed_at`, `published_at`, and `accessed_at`. If the claim only applies during a known period, use optional `valid_time.start` and `valid_time.end` bounds to say when it applied. Do not invent an endpoint when the evidence does not establish one.

This is a small bitemporal convention: valid time describes when a fact applies; transaction time describes when the repository recorded that version. Keep source-event dates separate from both. For a correction, retain the prior evidence in the issue/PR/commit history and record the corrected claim as a later change. The linked GitHub issue owns the change, while the PR and commits provide the operational record; CGM does not create a duplicate issue database or claim to offer a bitemporal query service.

The v0.4 validator checks timestamp shape, timezone presence, and interval ordering. CI also requires a PR to reference an open issue with written acceptance or delivery criteria. Main-branch protection requires the contract checks before merge. These controls establish workflow traceability; they do not prove the claim is true.

For a simple generation event, record its inputs (target revision, approved brief/brand/visual files, external research), the activity (generation/review), the responsible agent or person where known, and the output revision. This follows the interoperable entity/activity/agent and derivation model in [W3C PROV-O](https://www.w3.org/TR/prov-o/) and its [primer](https://www.w3.org/TR/prov-primer/), without requiring a target to deploy an RDF store.

## Evidence-informed house examples

The [PCM README at its reviewed revision](https://github.com/Pukujan/project-continuity-modules/blob/4329b47a7c4d28c073f881d2b32ef0faeb3300ff/README.md) provides a narrative pattern: concrete project situation and consequence, then a mental model, practical cycle, boundaries, and setup. [Eval Lab's content system](https://github.com/Pukujan/Eval-lab/blob/bc777271e58de01d16197208b1bcfb40c9d98da7/docs/README_CONTENT_VISUAL_SYSTEM.md) defines a parallel recipe for concrete human moments, problem-to-question framing, evidence boundaries, and visual roles. [Project Assurance Modules' PDD](https://github.com/Pukujan/project-assurance-modules/blob/72872c31c606f4783d1012f2d4dc842d747f5788/specs/PDD.md) separates agent proposals from mechanically checkable evidence and owner judgment. [The EFAH source record](https://github.com/Pukujan/efah-harness/blob/8468999833cab64f70e8a7cee61c52a9e0a4e5e0/project-pack/evidence/owner-documents/SOURCES.md) demonstrates hashes, derivation notes, and explicit missing-source reporting.

These are examples and methods, not proof that one README structure works for every audience. Test comprehension on the target reader and cite the evidence that belongs to that target.
