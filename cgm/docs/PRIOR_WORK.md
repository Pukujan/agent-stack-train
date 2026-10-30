# Prior work and dogfood evidence

This helper was extracted from repository-specific work. The examples below are the source of the reusable patterns: human situation first, technical detail second, a hero plus a distinct supporting image, exact prompt records, asset manifests, responsive review pages, explicit boundaries, and human review questions.

## Repositories that shaped the contract

| Repository | Human-facing story | Visual and review evidence |
| --- | --- | --- |
| [Eval Lab](https://github.com/Pukujan/Eval-lab) | Opens with the cost of trusting a polished but wrong judgment, then explains evidence, calibration, routing, and the research boundary. | [README](https://github.com/Pukujan/Eval-lab#readme), [content-system preview](https://github.com/Pukujan/Eval-lab/blob/main/docs/content-system-preview.md), [adapter](https://github.com/Pukujan/Eval-lab/tree/main/.content-system) |
| [Harness on steroids](https://github.com/Pukujan/harness-on-steroids) | Starts with the failure around a capable model, then separates shipped evidence, proposed protocol, and unfinished outcome evaluation. | [README](https://github.com/Pukujan/harness-on-steroids#readme), [preview](https://github.com/Pukujan/harness-on-steroids/blob/main/docs/content-system-preview.md), [image prompts](https://github.com/Pukujan/harness-on-steroids/blob/main/docs/content-system-image-prompts.md), [adapter](https://github.com/Pukujan/harness-on-steroids/tree/main/.content-system) |
| [Custom Extensions](https://github.com/Pukujan/custom-extensions) | Starts with the everyday problem of browser tools disappearing into chats and ZIPs, then puts installation, scope, permissions, and evidence before implementation detail. | [README](https://github.com/Pukujan/custom-extensions#readme), [preview](https://github.com/Pukujan/custom-extensions/blob/main/docs/content-system-preview.md), [image prompts](https://github.com/Pukujan/custom-extensions/blob/main/docs/content-system-image-prompts.md), [adapter](https://github.com/Pukujan/custom-extensions/tree/main/.content-system) |
| [Hades Product](https://github.com/Pukujan/hades-product) | Opens with the relationship question, makes privacy and continuity legible, and keeps the product specification separate from the live research instance. | [README](https://github.com/Pukujan/hades-product#readme), [preview](https://github.com/Pukujan/hades-product/blob/main/docs/content-system-preview.md), [image prompts](https://github.com/Pukujan/hades-product/blob/main/docs/content-system-image-prompts.md), [adapter](https://github.com/Pukujan/hades-product/tree/main/.content-system) |

The multi-repository adoption and review history is recorded in [Project Continuity Modules task PCM-0008](https://github.com/Pukujan/project-continuity-modules/blob/main/tasks/TASK-PCM-0008-multi-repo-content-system.md). It records four README promotions, target-specific adapters, generated visual assets, prompt and provenance records, responsive review packets, and the shared title-plus-subtitle rule.

## What was carried forward

- Put the human question or everyday problem before the system diagram.
- State what the repository is and is not before making a promise.
- Use the first image to introduce the story and the second image to explain a different boundary or mechanism.
- Keep the visual copy exact and short, and keep icons/SVGs text-free.
- Record image role, prompt intent, dimensions, text, references, review decision, and limitations.
- Make evidence, status, privacy, risk, and unfinished work visible before the technical appendix.
- Render and inspect the story at desktop, tablet, and mobile widths when an HTML preview is available.
- Leave the final promotion decision with a human.

## What this helper adds after that work

The earlier projects proved the editorial pattern in separate repositories. Version `0.2.0` makes the pattern explicit in this helper itself through:

- a required README contract;
- an expanded README template;
- a README playbook and image guide;
- prior-work links and provenance expectations;
- deterministic checks that reject a technical-only helper README;
- a versioned changelog entry and migration note.
