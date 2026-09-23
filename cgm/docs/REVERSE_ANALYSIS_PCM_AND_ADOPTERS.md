# Reverse analysis: PCM readability with CGM branding and visuals

Reviewed 2026-09-23 against the revisions linked below. This is a source-grounded design analysis, not a controlled usability study.

## The intended combination

Project Continuity Modules (PCM) is the reference for explaining a human problem, developing the consequences, guiding different readers, and keeping claims tied to evidence and provenance. Content Generation Modules (CGM) supplies the brand and market framing, reusable writing and visual direction, and its existing generated-image system.

The goal is to let a fresh ChatGPT agent reproduce that combination when given CGM, a pinned CGM version, and sufficient context and evidence from a target repository. **Transfer the method, not PCM's story, headings, language, or visual identity.** The target repository remains authoritative for its facts, audience, and brand.

## What the PCM README does well

At the reviewed revision, PCM opens with a recognizable mismatch: projects outlast individual agent sessions. It then connects that situation to lost decisions, repeated work, and uncertainty about what is current before introducing its mechanism. A research example distinguishes preserving reproducible state from proving that the research conclusion is correct. The subsequent sections give readers a mental model, a practical work cycle, explicit boundaries, and technical ways to continue. [PCM README, lines 3–60](https://github.com/Pukujan/project-continuity-modules/blob/4329b47a7c4d28c073f881d2b32ef0faeb3300ff/README.md#L3-L60)

This sequence is stronger than merely adding a “Why” heading. It develops a causal story: the reader's situation, the friction, the consequence, the project's response, and the evidence boundary. The explanation uses concrete questions and examples before asking the reader to learn internal vocabulary. Readers who need depth can keep going into the model and operations.

PCM also makes writing and evidence practices operational. Its continuity-records policy calls for an understandable human explanation, explicit status and boundaries, source lineage, and reproduction detail where useful. It recommends revision-pinned repository links, direct external sources, and plain treatment of missing evidence. [PCM continuity-records policy, lines 18–27, 31–55, 63–70](https://github.com/Pukujan/project-continuity-modules/blob/4329b47a7c4d28c073f881d2b32ef0faeb3300ff/docs/CONTINUITY_RECORDS_POLICY.md#L18-L27)

Its holdout guidance is proportional: use deterministic checks for ordinary requirements, and fresh-session holdouts when making claims about what a new agent can discover or do. It gives observable evidence priority over LLM-only judgment. [PCM-0022, lines 12–36](https://github.com/Pukujan/project-continuity-modules/blob/4329b47a7c4d28c073f881d2b32ef0faeb3300ff/tasks/TASK-PCM-0022-agent-facing-holdouts.md#L12-L36)

## What CGM already contributes

CGM's reviewed `0.3.1` README already starts with the reader, states what the helper does and does not claim, and explains why a polished output can still hide a weak story. Its playbook says to develop a concrete example, preserve evidence boundaries, and write in welcoming language. [CGM README, lines 3–36 and 71–84](https://github.com/Pukujan/content-generation-modules/blob/8d4f041e8b82f007000b3a1b83d08c39616cc8c7/README.md#L3-L36), [README playbook, lines 27–51 and 76–99](https://github.com/Pukujan/content-generation-modules/blob/8d4f041e8b82f007000b3a1b83d08c39616cc8c7/docs/README_PLAYBOOK.md#L27-L51)

CGM also already has detailed brand, visual, image-generation, exact title/subtitle, prompt-record, crop, accessibility, and review requirements. Its current validator rejects narrative SVG substitutions and checks generated-image provenance and hashes. **That image system is a protected strength of this update.** This work adds readable claim explanation and source lineage without changing the current visual direction, image workflow, required image count, or asset records.

The narrower gap is in the project brief: the old evidence object identifies a claim and source, with status, but does not require a plain-language explanation of what that source establishes or leaves unproven, or an exact source revision. [CGM project-brief schema at the reviewed revision, lines 13–26](https://github.com/Pukujan/content-generation-modules/blob/8d4f041e8b82f007000b3a1b83d08c39616cc8c7/schemas/project-brief.schema.json#L13-L26)

## Useful patterns from the other reviewed repositories

| Reference | Observed pattern | What CGM adopts |
| --- | --- | --- |
| [Eval Lab README](https://github.com/Pukujan/Eval-lab/blob/bc777271e58de01d16197208b1bcfb40c9d98da7/README.md#L7-L27) and [PDD](https://github.com/Pukujan/Eval-lab/blob/bc777271e58de01d16197208b1bcfb40c9d98da7/docs/PDD.md#L29-L53) | Begins from the trust problem behind grading many plausible answers, then explains a middle path and separates model explanation from objective evidence. | Start with the reader's concern, then connect each promise to an evidence boundary. |
| [Harness on Steroids README](https://github.com/Pukujan/harness-on-steroids/blob/14df2f7ed278bc0c2deebbd7a80fafc4daa6fe42/README.md#L3-L34) | Describes recognizable developer friction, observable behavior, and limits without treating a small corpus as universal evidence. | Use concrete consequences and testable outcomes; avoid turning examples into universal claims. |
| [Harness metamorphic tests](https://github.com/Pukujan/harness-on-steroids/blob/14df2f7ed278bc0c2deebbd7a80fafc4daa6fe42/tests/test_metamorphic.py#L11-L36) and [hash-only hidden tests](https://github.com/Pukujan/harness-on-steroids/blob/14df2f7ed278bc0c2deebbd7a80/tests/test_hidden_holdout.py#L7-L42) | Checks relations across transformed inputs and protects expected hidden content behind hashes. | Test invariants and keep actual holdout cases and answer keys outside the agent's checkout. |
| [EFAH provenance oracle](https://github.com/Pukujan/efah-harness/blob/8468999833cab64f70e8a7cee61c52a9e0a4e5e0/project-pack/acceptance/oracle-definitions/ORACLE-003-provenance-binding.yaml#L18-L45) | Binds a result to a contract, commits, named evidence, and recomputed content hash; separates deterministic verdicts from model judgment. | Make source identity mechanically checkable while leaving meaning and tone to human review. |
| [Project Assurance Modules PDD](https://github.com/Pukujan/project-assurance-modules/blob/72872c31c606f4783d1012f2d4dc842d747f5788/specs/PDD.md#L52-L73) | Separates owner decisions, proposals, machine-checkable evidence, and human judgment; warns against evidence circularity. | Keep deterministic structure checks from being mistaken for truth or reader-quality judgments. |

Private owner-supplied repositories were also reviewed read-only as development context. Their identifying details and private content are not reproduced here, and they are not used as public examples or as hidden holdouts.

## The versioned change

The `0.4.0` candidate keeps the existing story order and introduces project-brief v2. Each material claim retains `claim`, `source`, and `status`, and adds:

- `supports`: what the cited evidence establishes, stated plainly;
- `limits`: what that evidence does not establish;
- `source_revision`: a source kind, stable reference, and exact identity and locator;
- `recorded_at`: when that version of the evidence record was entered, with optional `valid_time` bounds for time-bound claims.

Repository evidence records a full commit, repository-relative path, locator, and immutable permalink. External sources record a direct URI and access date. Unknown-search records cannot substantiate a shipped claim. Requested README citations must appear in the README and point to the recorded source.

This adds source resolution and bounded explanations to CGM's current human-facing method; it does not claim that fields alone can determine whether prose is accurate or welcoming. The validator enforces structure and source identity. Independent readers and maintainers review interpretation and tone. See [`PROVENANCE_AND_CITATION.md`](PROVENANCE_AND_CITATION.md) and [`MIGRATING_TO_0.4.md`](MIGRATING_TO_0.4.md).

## Acceptance and limitations

The PDD, SDD, and TDD define reader jobs, the story spine, evidence records, deterministic gates, metamorphic checks, and an independent holdout protocol. The automated suite currently checks bounded v2 evidence, immutable repository citations, adapter compatibility, evidence-order invariance, and the existing image rules. **The sealed hidden holdout has not been run.** The reference repositories were development evidence, so they cannot also count as unseen test targets.

The README comparisons are affected by topic, author, length, examples, and other edits. Pukujan's review motivates the work but is not a reader study. The hypothesis that this contract improves understanding and claim traceability needs blinded reader tasks and fresh, unseen target repositories. Until those runs exist, CGM claims only that the structure is specified and its visible deterministic checks pass.

## Inspected revisions

| Repository | Inspected revision |
| --- | --- |
| `project-continuity-modules` | `4329b47a7c4d28c073f881d2b32ef0faeb3300ff` |
| `content-generation-modules` | `8d4f041e8b82f007000b3a1b83d08c39616cc8c7` |
| `Eval-lab` | `bc777271e58de01d16197208b1bcfb40c9d98da7` |
| `harness-on-steroids` | `14df2f7ed278bc0c2deebbd7a80fafc4daa6fe42` |
| `efah-harness` | `8468999833cab64f70e8a7cee61c52a9e0a4e5e0` |
| `project-assurance-modules` | `72872c31c606f4783d1012f2d4dc842d747f5788` |
