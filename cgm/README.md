# Content Generation Modules

A versioned, agent-readable system for producing **human-oriented brand language, project context, README content, visual direction, generated images, and responsive HTML demos**.

This repository is a **helper contract**, not a universal brand. It tells an agent how to work. Each product repository supplies its own facts, audience, evidence, visual identity, and asset manifest.

## The operating model

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

The system exists to prevent two common failures:

- copy that sounds polished but says little a person can understand;
- visuals that are attractive in isolation but bury the product story under noise.

## Modules

| Module | Responsibility | Typical output |
| --- | --- | --- |
| `brand-foundation` | identity, positioning, audience, promises, boundaries | `brand-language.json` |
| `content-context` | repository facts, evidence, terminology, claims | `project-brief.json` |
| `writing-direction` | story order, plain language, skimmability, marketing formats | README, post, landing-page copy |
| `visual-direction` | palette, composition, hierarchy, responsive roles | `visual-style.json` |
| `image-generation` | prompt recipes, references, settings, rejection records | images plus asset manifest entries |
| `html-demo` | semantic structure, responsive behavior, accessibility, rendered QA | HTML/CSS demo and screenshots |

Each module has a `SKILL.md` entry point and may be loaded independently. Keep the always-loaded entry point short; place large examples and project facts in the target repository.

## Target repository adapter

Add this small adapter to a project repository:

```text
.content-system/
├── system-version.json
├── project-brief.json
├── brand-language.json
├── visual-style.json
├── asset-manifest.json
└── review-rubric.json
```

The adapter must record the helper repository and exact version/commit. A target repository should also add an `AGENTS.md` pointer telling agents to load the adapter before README, marketing, image, or HTML work.

## The human-first writing contract

Every important section should answer, in this order:

1. **What is happening for the reader?** Start with a recognizable situation.
2. **Why does it matter?** Name the cost, risk, or frustration plainly.
3. **What does this project do?** Use concrete verbs and nouns.
4. **How does it work?** Explain the mechanism at the reader's altitude.
5. **What proves it?** Link to code, tests, data, or a committed artifact.
6. **Where does it stop?** State limitations instead of overselling.

Use bold for the sentence's important anchor, not every other phrase. Use italics for a short qualification or contrast. A reader should be able to skim headings, bold phrases, and the first sentence of each paragraph and still understand the story.

Avoid unsupported superlatives, abstract adjective stacks, fake certainty, generic “AI-powered” claims, and repeated “it enables / it provides / it ensures” sentence cadence.

## The visual contract

Every image has one role and one dominant idea. The visual system should preserve:

- the main human and AI/product subjects;
- calm contrast and a restrained palette;
- enough negative space for the layout where the image will be used;
- minimal or no in-image text except for a deliberate hero title;
- a declared aspect ratio and mobile/tablet crop strategy.

The hero establishes the reference pattern. Supporting images should feel related without becoming alternate hero banners.

## Reproducibility contract

Record, when available:

- helper version and commit;
- model/provider and model version;
- prompt recipe and negative constraints;
- reference asset paths and hashes;
- dimensions, aspect ratio, seed, sampler, and other settings;
- accepted/rejected candidates and the reason for each decision;
- final file hash.

If a hosted generator does not expose a seed or stable model version, record **reproducible intent** rather than claiming pixel-identical reproduction.

## Validation

Run:

```powershell
python scripts/validate_content_system.py --root .
python -m unittest discover -s tests -v
```

For a target repository, run the same validator against the helper root and target adapter when the integration supplies a project root.

The validator checks the contract, module entry points, schema presence, version pins, and required adapter fields. It does not decide whether copy or an image is beautiful; that remains a rubric and human-review question.

## ChatGPT setup

See [`CHATGPT_SETUP.md`](CHATGPT_SETUP.md) for a reusable ChatGPT Project/custom-GPT setup. Use project instructions for behavior and uploaded knowledge for reference material. Use GitHub context for repository facts, and use Codex for branches, commits, PRs, and rendered artifacts.

## Current version

The initial contract is `0.1.0`. It is intentionally small and will be promoted only after being dogfooded in more than one repository.
