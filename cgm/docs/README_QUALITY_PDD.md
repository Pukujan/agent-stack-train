# Product definition: readable, evidence-led project stories

Status: contract proposal for Content Generation Modules `0.4.0`.

## Problem

A repository can follow a README outline and still leave its reader unsure why the project matters. Section presence does not guarantee an explanation: an agent may state a category, list modules, and link a source without showing the situation that led to the work, what went wrong, what changes for a person, or what the evidence actually supports.

The same gap affects trust. A short `claim`, `source`, and `status` record does not explain what a source establishes, what it leaves unproven, or which repository revision was inspected. The prose can sound polished while its evidence trail is difficult to reproduce.

Operational claims also change over time. A durable record needs to distinguish when a fact applied from when the project recorded or corrected it, while keeping the owning request in the repository's issue history.

## Users and jobs

| Reader | Job to be done |
| --- | --- |
| First-time user or researcher | Understand the situation, useful outcome, and limits before deciding whether to continue. |
| Developer or maintainer | See how the project works, what is implemented, how to try it, and where to verify claims. |
| Fresh ChatGPT agent | Rebuild the story from the target repository and supplied context without relying on prior chat or inventing product facts. |
| Reviewer or project owner | Correct the audience, story, source classification, claim status, visual direction, and next action. |

## Product hypothesis

If a fresh agent develops the reader's problem through concrete consequences and records, for each material claim, what its evidence supports and does not support, readers will understand the project and verify its claims more reliably than when the agent only fills a section template.

This is a testable hypothesis, not a promise of a fixed usability or conversion increase.

## Goals

1. Make the reader's situation, friction, consequence, and desired outcome concrete before explaining architecture, using CGM's existing narrative order.
2. Preserve the project's distinctive brand, market position, and human voice without copying another project's story.
3. Tie material factual claims to traceable evidence, explain each source's support and limits, and distinguish observation, experiment, plan, inference, and unknowns.
4. Give both human readers and technical readers a clear route through the page.
5. Make a new ChatGPT session able to reproduce the process from the pinned CGM contract and target-repository context.
6. Keep CGM's existing narrative image generation, brand, prompt, copy, accessibility, crop, review, and provenance requirements intact.
7. Use the tracked GitHub issue as the change owner and PR/commit history as the operational record; distinguish valid time from record time when a claim is time-bound.

## Non-goals

- Making every README use PCM's topic, wording, length, headings, or visual identity.
- Treating citations as proof that a source is correct.
- Forcing every project into one emotional story when its audience or task calls for another form.
- Replacing a target repository's brand, evidence, or owner decisions with CGM defaults.
- Using an automated prose score as final acceptance.
- Claiming a hidden-holdout result without a sealed fixture and an independently recorded run.

## Success measures

On a blinded reader task, a first-time reader should be able to identify the project's primary reader, problem, useful outcome, current status, main evidence boundary, and next action. A reviewer should be able to resolve each required citation to its recorded source revision and locator. Unsupported claims, stale evidence, or mismatched status must be visible rather than polished away.

The release decision uses deterministic contract checks, reader-task results, independent editorial review, and a separate visual/image non-regression review. No single model score decides success. The reference repositories shape the development contract and are not holdouts.
