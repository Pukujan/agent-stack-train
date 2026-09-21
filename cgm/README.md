# Content Generation Modules

When an agent starts from a blank prompt, a README or visual brief can sound polished while mixing product facts with guesses. The next person then has to untangle what is true, what is planned, and which project files are authoritative.

This repository is a **versioned, agent-readable contract** for turning a target repository's facts and evidence into reviewable brand language, project context, README content, visual direction, generated-image briefs, and responsive HTML demos. It gives an agent a bounded way to work; it does not contain a product, brand, model, or universal set of claims.

## Start here

Use this helper when a project needs public-facing content or visuals that remain connected to its shipped behavior.

1. Add a `.content-system/` adapter to the target project.
2. Pin the helper's release or commit in `.content-system/system-version.json`.
3. Add an `AGENTS.md` pointer that tells agents to load the adapter before README, marketing, image, or HTML work.
4. Copy the relevant files from [`templates/`](templates/) and replace their empty fields with facts from the target repository. Update template version fields to match the pinned helper.
5. Ask the agent to read the adapter, inspect the cited evidence, and build or update `project-brief.json` before drafting.
6. Validate the helper and adapter before review:

   ```powershell
   python scripts/validate_content_system.py `
     --root path/to/content-generation-modules `
     --adapter path/to/target-repository/.content-system `
     --project-root path/to/target-repository
   ```

The smallest useful adapter contains these files:

```text
.content-system/
├── system-version.json
├── project-brief.json
├── brand-language.json
├── visual-style.json
├── asset-manifest.json
└── review-rubric.json
```

`system-version.json` must declare `schema_version: content-generation.adapter.v1` and record `helper_repository`, `helper_version`, `helper_commit`, and the six module names. The commit or release pin keeps a target project from silently changing behavior when this helper's `main` branch moves.

## The workflow

```text
target repository facts
        |
        v
project adapter + evidence boundary
        |
        v
content / visual / image / HTML module
        |
        v
draft -> deterministic checks -> model rubric -> human review
        |
        v
versioned output + metadata + checkpoint
```

The workflow starts with the reader's situation, names the problem and consequence, explains the project and its mechanism, links claims to evidence, and states the boundaries. That order helps a first-time reader understand the product before encountering its architecture.

## Modules

| Module | Responsibility | Typical output |
| --- | --- | --- |
| [`brand-foundation`](modules/brand-foundation/SKILL.md) | audience, positioning, promise, personality, language boundaries, supported claims | `brand-language.json` |
| [`content-context`](modules/content-context/SKILL.md) | repository facts, evidence, terminology, claims, and limitations | `project-brief.json` |
| [`writing-direction`](modules/writing-direction/SKILL.md) | story order, plain language, skimmability, and marketing formats | README, post, landing-page copy |
| [`visual-direction`](modules/visual-direction/SKILL.md) | palette, composition, hierarchy, responsive roles, and rejection conditions | `visual-style.json` |
| [`image-generation`](modules/image-generation/SKILL.md) | prompt recipes, references, settings, and review records | images plus asset-manifest entries |
| [`html-demo`](modules/html-demo/SKILL.md) | semantic structure, responsive behavior, accessibility, and rendered QA | HTML/CSS demo and screenshots |

Load only the modules needed for the requested output. The entry points are intentionally short; project facts and large examples belong in the target repository.

## Evidence and trust boundaries

The adapter is a source map, not marketing copy. Each important claim should be marked as shipped, experimentally supported, planned, or unknown and should point to a file, test, data set, or committed artifact.

The validator checks the structure of the contract, module entry points, schemas, templates, version pins, required adapter fields, and—when a project root is supplied—asset paths. It does not decide whether copy is persuasive, an image is beautiful, or a model-assisted score is correct. Human review remains the final decision for subjective quality.

This helper does not promise product capabilities, invent audience research, run a hosted generation service, or replace the target repository's own facts. If the evidence is missing, the output should say so.

## Visual and reproducibility rules

Every image has one role and one dominant idea. Keep the human and product subjects visible, preserve calm contrast and negative space, declare the aspect ratio and crop behavior, and reject visuals that imply unsupported capabilities.

For narrative raster assets, record one short exact title and one short exact subtitle when the asset needs to orient a first-time reader. Keep icons, SVGs, logos, and tiny helper graphics text-free unless lettering is explicitly required. Record the helper version, model or provider when available, prompt recipe, references, dimensions, settings, review decision, and final hash. When a hosted generator does not expose a stable seed or model version, record reproducible intent instead of claiming pixel-identical reproduction.

## Repository files

- [`templates/`](templates/) contains starter JSON files and a README outline.
- [`schemas/`](schemas/) defines the project brief, asset manifest, and review rubric shapes.
- [`scripts/validate_content_system.py`](scripts/validate_content_system.py) runs dependency-free structural checks.
- [`CHATGPT_SETUP.md`](CHATGPT_SETUP.md) explains how to use the helper as durable context for a ChatGPT Project or custom GPT.
- [`tests/`](tests/) covers the validator's helper and adapter checks.

## Validate this repository

From the repository root:

```powershell
python scripts/validate_content_system.py --root .
python -m unittest discover -s tests -v
```

For a target repository, pass its adapter and project root as shown in [Start here](#start-here). Keep the helper version in the target adapter aligned with the files used to produce the output.

## Current version

The current draft contract is `0.1.2` (`v0.1.2`). It is intentionally small and will be promoted only after being dogfooded in more than one repository.
