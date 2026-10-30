# Migrating to Content Generation Modules 0.4

Version `0.4.0` strengthens how a README explains its claims and source trail. It keeps the existing human-first story order, brand ownership, visual direction, and image-generation requirements from `0.3.x`.

## What changes

For each material claim, project-brief v2 records:

- `claim`, `source`, and `status`, as before;
- `supports`: what the cited evidence establishes, in plain language;
- `limits`: what that evidence does not establish;
- `source_revision`: the kind of source, a stable reference, and enough identity to find the exact evidence again;
- `recorded_at`: when this version of the evidence record was entered, as a timezone-aware timestamp.

For claims that apply only during a known interval, add optional `valid_time.start` and `valid_time.end` bounds. These are separate from `recorded_at`: valid time says when the claim applies; record time says when the repository knew or recorded this version. Use the tracking issue for ownership and PR/commit history for append-only operational changes rather than maintaining a second log.

Repository evidence requires an owner/repository, full commit ID, repository-relative path, locator, and immutable permalink. External sources require a direct URL and access date. Owner observations, decisions, and searches that did not establish a fact carry an observation date. An unsuccessful search can support an `unknown` record; it cannot be the sole support for a shipped claim.

The validator checks the record structure and that requested citations appear in the target README. A human still checks whether the source is credible and actually supports the wording. A citation provides traceability, not proof of truth.

## Upgrade a target adapter

1. Keep the helper pinned to the intended `0.4.x` release and commit in `.content-system/system-version.json`.
2. Change `.content-system/project-brief.json` to schema version `content-generation.project-brief.v2`.
3. For every material evidence item, write what the source supports and leaves open, classify its source, and record a stable revision and locator.
4. Add direct citations beside important README claims. Set `cite_in_readme` to `true` for evidence that must appear in the README; the validator checks that link.
5. Revisit any claim whose source is missing, stale, private, or weaker than its wording. Qualify it or mark it `unknown`.
6. Run the pinned helper's validator and the target's reader, evidence, and human review checks.

The starter shape is in [`templates/project-brief.json`](../templates/project-brief.json); the machine-readable contract is [`schemas/project-brief.v2.schema.json`](../schemas/project-brief.v2.schema.json). See [`PROVENANCE_AND_CITATION.md`](PROVENANCE_AND_CITATION.md) for source-kind guidance and [`README_QUALITY_TDD.md`](README_QUALITY_TDD.md) for acceptance and metamorphic tests.

## Visual and image rules continue unchanged

Do not replace the target's visual identity with CGM's default brand. Continue following the target adapter and the existing [`IMAGE_GUIDE.md`](IMAGE_GUIDE.md): narrative images use the required image-generation workflow, exact title and subtitle context, raster outputs, prompt records, hashes, crop and accessibility guidance, and a recorded review decision. The v0.4 story and evidence changes do not waive or weaken those requirements.

## Compatibility

Targets pinned to `0.3.x` may keep project-brief v1 and their existing checks. A target that pins helper `0.4.0` or later must use project-brief v2. Do not change a target adapter's version pin until its brief, README citations, and review are ready together.
