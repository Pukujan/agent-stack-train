# Content Generation Modules

<p align="center">
  <img src="assets/marketing/hero-content-truth.png" alt="Scattered repository notes and files become a clear README that a human reader can understand." width="100%">
</p>

> A versioned contract for turning repository evidence into welcoming product stories, useful visuals, and reviewable human-facing output.

**A project can be technically complete and still be difficult to understand.** Its facts live in code, tests, screenshots, research notes, prompts, and half-finished drafts. When an agent jumps from that material straight to a README, the result can sound polished while leaving a new reader unsure what the project is, why it matters, or which claims are safe to trust.

Content Generation Modules exists to close that gap. It gives agents and maintainers a shared way to build the human explanation first, connect it to evidence, and let technical detail arrive when it helps the reader make a decision.

## Why this exists

The reader should not have to reverse-engineer the product from its folder tree.

This helper was created for the moment when a team needs a README, product page, visual brief, generated image, or HTML demo and the project already has more truth than a blank prompt can hold. The work is not only “write better copy.” It is to find the recognizable human situation, name the consequence, show what the project changes, prove the important claims, and state where the work stops.

That requires a small contract between the target repository and the agent:

- the project repository owns its facts, audience, evidence, visual identity, and boundaries;
- the helper supplies the reusable method and module instructions;
- the output starts with a human reason to care and moves toward architecture;
- images carry one clear idea and a recorded path from generation to use;
- deterministic checks catch missing structure, while human review decides whether the story is honest and welcoming.

The first screen should feel like an invitation into the project. Technical details come second because they are more useful after the reader knows what they are helping explain.

## What this project is

This repository is a **versioned, agent-readable content and visual contract**. It is for maintainers, agents, designers, researchers, and engineers who need public-facing project information to stay specific, evidence-bounded, and reusable.

It is not a universal brand, product database, hosted image service, or substitute for the target repository's own research. The target project supplies the source of truth through a small `.content-system/` adapter; this helper supplies the working method, templates, schemas, visual rules, guides, and review gates.

## What you can make or use

With the six modules and a target repository adapter, you can create:

- a **brand foundation** that names the audience, promise, personality, preferred language, and claim boundaries;
- a **project brief** that maps the user, problem, solution, mechanism, evidence, terminology, and limitations;
- a **story-first README or product document** that welcomes a reader before explaining the architecture;
- a **visual direction** with palette, composition, responsive roles, text policy, and rejection conditions;
- **generated image briefs and asset records** that explain how to create, review, place, and reuse visuals;
- an **accessible responsive HTML demo** that lets a person inspect the story at desktop, tablet, and mobile widths.

<p align="center">
  <img src="assets/marketing/six-modules-one-story.png" alt="Six content modules surround one evidence brief while a person marks the result ready for review." width="520">
</p>

## How it works

```text
target repository situation and evidence
                    |
                    v
          pinned .content-system adapter
                    |
                    v
brief -> brand -> writing / visual / image / HTML direction
                    |
                    v
        draft -> deterministic checks -> human review
                    |
                    v
             useful, versioned output
```

1. **Start with the reader.** Use the target repository to identify the human situation, cost, audience, and job to be done.
2. **Build the source map.** Record supported claims, status, terminology, and boundaries in the project brief and related adapter files.
3. **Choose the right modules.** Load only the brand, context, writing, visual, image, or HTML guidance the requested output needs.
4. **Give every output one job.** A README explains the project; a hero introduces the promise; a supporting image explains a different mechanism or boundary.
5. **Check and review.** The validator checks structure and file contracts. A human checks whether the story is useful, accurate, accessible, and ready to share.

## Image generation and use

The images in this README are committed examples of the visual contract. The [hero asset](assets/marketing/hero-content-truth.png) introduces the problem: scattered evidence becoming a clear README. The [supporting asset](assets/marketing/six-modules-one-story.png) explains the system: six modules gathered around one evidence brief.

The full workflow is in [`docs/IMAGE_GUIDE.md`](docs/IMAGE_GUIDE.md). It explains how to choose an image role, write a prompt, supply exact title and subtitle copy, generate candidates, inspect them at use size, reject weak directions, add alt text, place the asset in Markdown or HTML, and record the final decision.

The committed records in [`assets/marketing/IMAGE_NOTES.md`](assets/marketing/IMAGE_NOTES.md) and [`assets/marketing/asset-manifest.json`](assets/marketing/asset-manifest.json) show the expected level of detail: role, dimensions, exact text, prompt intent, alt text, README placement, crop behavior, rejection conditions, and review decision.

For narrative raster assets, use one exact title of roughly 2–6 words and one exact subtitle of roughly 6–16 words. Keep them in quiet space, keep the human and product subjects visible, and keep icons, SVGs, logos, and tiny helper graphics text-free unless lettering is part of their function.

## Templates and guides

Start from the [README template](templates/README.template.md) and its [machine-readable contract](templates/readme-contract.json). The template puts the human situation, promise, usefulness, mechanism, evidence, images, prior work, and next action in a deliberate order.

Use the guides according to the output:

- [`docs/README_PLAYBOOK.md`](docs/README_PLAYBOOK.md) explains the twenty-second test, welcoming language, evidence status, section order, visual placement, and human review.
- [`docs/IMAGE_GUIDE.md`](docs/IMAGE_GUIDE.md) explains image roles, prompt structure, exact in-image copy, responsive crops, alt text, manifest fields, and rejection rules.
- [`docs/MIGRATING_TO_0.2.md`](docs/MIGRATING_TO_0.2.md) explains how existing `0.1.x` target repositories adopt the stronger human-facing contract.
- [`CHATGPT_SETUP.md`](CHATGPT_SETUP.md) gives project instructions and source-selection guidance for a ChatGPT Project or custom GPT.
- [`templates/`](templates/) contains starter project, brand, visual, image, asset, review, and README files.
- [`schemas/`](schemas/) defines the project brief, asset manifest, review rubric, and README contract shapes.

## Prior work and references

This helper is extracted from real repository-specific work, not invented as an isolated documentation exercise. Four public repositories received separate content-system previews and README promotions:

| Repository | What the work taught the helper |
| --- | --- |
| [Eval Lab](https://github.com/Pukujan/Eval-lab) | Start with the cost of trusting a polished but wrong judgment, then explain evidence, confidence, routing, and the research boundary. |
| [Harness on steroids](https://github.com/Pukujan/harness-on-steroids) | Start with the failure around a capable model, separate shipped evidence from proposals, and keep outcome evaluation honest. |
| [Custom Extensions](https://github.com/Pukujan/custom-extensions) | Start with the everyday problem of tools disappearing into chats and ZIPs, then put installation, permissions, risk, and evidence before implementation. |
| [Hades Product](https://github.com/Pukujan/hades-product) | Start with the relationship question, make privacy and continuity legible, and separate product specification from the live research instance. |

Each of those repositories retains a target-specific adapter, reviewed images, prompt records, asset manifests, responsive preview materials, and human review questions. The full evidence map, with links to the previews and adapters, is [`docs/PRIOR_WORK.md`](docs/PRIOR_WORK.md). The cross-repository adoption record is [Project Continuity Modules task PCM-0008](https://github.com/Pukujan/project-continuity-modules/blob/main/tasks/TASK-PCM-0008-multi-repo-content-system.md).

## Evidence and boundaries

The adapter is a source map, not marketing copy. Important claims should point to a file, test, data artifact, or reviewed output and be labeled `shipped`, `experimentally_supported`, `planned`, or `unknown`.

The validator checks the helper contract, README sections, required guides, local images, module entry points, schemas, templates, adapter fields, version pins, and—when a project root is supplied—asset paths. It does not decide whether copy is persuasive, an image is beautiful, or a model-assisted score is right. Human review remains authoritative for subjective quality.

The helper does not invent capabilities, audience research, metrics, integrations, or guarantees. If the evidence is missing, the output should say so.

## Start with a target repository

Add this adapter to the project that owns the product story:

```text
.content-system/
├── system-version.json
├── project-brief.json
├── brand-language.json
├── visual-style.json
├── asset-manifest.json
└── review-rubric.json
```

Then:

1. Pin the helper release or commit in `.content-system/system-version.json`.
2. Add an `AGENTS.md` pointer telling agents to load the adapter, README playbook, and image guide before human-facing work.
3. Copy the relevant starters from [`templates/`](templates/) and replace empty fields with facts from the target repository.
4. Inspect prior reviewed outputs before choosing a new story or visual direction.
5. Build or update `project-brief.json` before drafting.
6. Validate the helper and adapter before review:

   ```powershell
   python scripts/validate_content_system.py `
     --root path/to/content-generation-modules `
     --adapter path/to/target-repository/.content-system `
     --project-root path/to/target-repository
   ```

The adapter's `system-version.json` must declare `schema_version: content-generation.adapter.v1` and record `helper_repository`, `helper_version`, `helper_commit`, and the six module names. The pin prevents a target project from silently changing when this helper's `main` branch moves.

## Try it

To validate this helper from its repository root:

```powershell
python scripts/validate_content_system.py --root .
python -m unittest discover -s tests -v
```

To use the writing workflow, read [`docs/README_PLAYBOOK.md`](docs/README_PLAYBOOK.md), fill [`templates/README.template.md`](templates/README.template.md) from the target repository's evidence, and review the result against [`templates/readme-contract.json`](templates/readme-contract.json) before opening a PR.

## Current version

The current draft contract is `0.2.0` (`v0.2.0`). Existing target repositories pinned to `v0.1.2` remain on that earlier contract until they deliberately migrate; new human-facing work should use the `0.2.0` README and image gates.
