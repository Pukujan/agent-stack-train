# Content Generation Modules

![Editorial illustration of scattered repository evidence becoming a clear README for a human reader](assets/marketing/hero-content-truth.png)

**Your product already has a story. It is just scattered across code, notes, tests, screenshots, and half-finished drafts.**

When an agent turns that material directly into a README, visual brief, or HTML demo, the result can look polished and still leave a reader asking: what is this, who is it for, and which claims can I trust?

Content Generation Modules gives the work a usable shape. It turns a target repository's facts and evidence into human-ready brand language, project context, README content, visual direction, image briefs, and responsive HTML demos—while keeping a human in the review loop.

## Make the product easier to understand

The hard part is rarely producing more words or more pixels. The hard part is keeping the story connected to the product.

This system helps an agent:

- **Start with a real situation.** Name what the reader is trying to do and what becomes difficult.
- **Separate facts from guesses.** Point important claims to code, tests, data, or committed artifacts.
- **Give every output a job.** Shape the README, visual, image, or demo around one clear message.
- **Leave the final judgment to people.** Use deterministic checks for structure and human review for meaning and quality.

![Editorial workflow showing six modules around one evidence brief](assets/marketing/six-modules-one-story.png)

## Six modules. One story.

| Module | What it helps an agent do | Typical output |
| --- | --- | --- |
| [`brand-foundation`](modules/brand-foundation/SKILL.md) | define the audience, promise, voice, and claim boundaries | `brand-language.json` |
| [`content-context`](modules/content-context/SKILL.md) | map the repository's user, problem, mechanism, evidence, and limits | `project-brief.json` |
| [`writing-direction`](modules/writing-direction/SKILL.md) | put the reader's situation before the architecture | README, post, landing-page copy |
| [`visual-direction`](modules/visual-direction/SKILL.md) | give every visual one role, composition, palette, and crop plan | `visual-style.json` |
| [`image-generation`](modules/image-generation/SKILL.md) | create reviewable prompts and asset records | images plus manifest entries |
| [`html-demo`](modules/html-demo/SKILL.md) | turn the story into an accessible, responsive demonstration | HTML/CSS demo and screenshots |

Load only the modules needed for the requested output. Each entry point is short so the target repository can carry the product facts and examples that make the work specific.

## From evidence to output

```text
facts in the target repository
              |
              v
small adapter with an evidence boundary
              |
              v
brief -> direction -> draft -> review
              |
              v
README, visual, image, or HTML output
```

The adapter keeps the source of truth close to the product. The brief records what is shipped, experimentally supported, planned, or unknown. The directions shape the output for a human reader. The validator checks the structure. A person decides whether the result deserves to ship.

## Start with a target repository

Add this small adapter to the project that owns the product story:

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
2. Add an `AGENTS.md` pointer telling agents to load the adapter before README, marketing, image, or HTML work.
3. Copy the relevant starters from [`templates/`](templates/) and replace empty fields with facts from the target repository.
4. Build or update `project-brief.json` before drafting.
5. Validate the helper and adapter before review:

   ```powershell
   python scripts/validate_content_system.py `
     --root path/to/content-generation-modules `
     --adapter path/to/target-repository/.content-system `
     --project-root path/to/target-repository
   ```

The adapter's `system-version.json` must declare `schema_version: content-generation.adapter.v1` and record `helper_repository`, `helper_version`, `helper_commit`, and the six module names. The pin prevents a target project from silently changing when this helper's `main` branch moves.

## Trust is part of the output

This repository is a helper contract, not a universal brand or a product database. The target repository supplies the product facts, audience, evidence, visual identity, and asset files.

The validator checks the contract, module entry points, schemas, templates, adapter fields, version pins, and—when a project root is supplied—asset paths. It does not decide whether copy is persuasive, an image is beautiful, or a model-assisted score is right. Human review remains authoritative for subjective quality.

For visual work, keep one dominant idea, keep the main human and product subjects visible, declare the aspect ratio and crop behavior, and reject visuals that imply unsupported capabilities. For narrative raster assets, record a short exact title and subtitle when the asset needs to orient a first-time reader. Keep icons, SVGs, logos, and tiny helper graphics text-free unless lettering is explicitly required.

## Repository map

- [`templates/`](templates/) contains starter JSON files and a README outline.
- [`schemas/`](schemas/) defines the project brief, asset manifest, and review rubric shapes.
- [`assets/marketing/`](assets/marketing/) contains the generated README visuals and their safe prompt notes.
- [`scripts/validate_content_system.py`](scripts/validate_content_system.py) runs dependency-free structural checks.
- [`CHATGPT_SETUP.md`](CHATGPT_SETUP.md) explains how to use the helper as durable context for a ChatGPT Project or custom GPT.
- [`tests/`](tests/) covers the validator's helper and adapter checks.

From the repository root:

```powershell
python scripts/validate_content_system.py --root .
python -m unittest discover -s tests -v
```

The current draft contract is `0.1.2` (`v0.1.2`). It is intentionally small and will be promoted after being used in more than one repository.
