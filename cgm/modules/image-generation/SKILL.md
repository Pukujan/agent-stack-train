---
name: image-generation
description: Turn a project brief and visual style into reproducible, reviewable image-generation briefs and asset records for product documentation and marketing.
---

# Image generation

## Workflow

1. Start from the reader's question and the single idea the asset must make easier to understand.
2. Choose the asset role: hero, problem, system, evidence, story, social preview, icon, or helper graphic.
3. Declare the audience, message, subject relationship, responsive role, and text policy before writing the prompt.
4. Compose the prompt in the recipe below and supply exact title/subtitle copy when the role is a narrative raster asset.
5. Generate candidates, inspect the actual files at their intended README or HTML sizes, and reject candidates against the visual contract.
6. Move the accepted asset into the target repository, add alt text, and reference it from the README or HTML where it does useful explanatory work.
7. Record the prompt recipe, exact copy, role, dimensions, references, settings, review decision, and final hash in the asset manifest or a linked prompt record.
8. Link the image guide and prompt record from the human-facing document so another person can regenerate, replace, or reuse the asset safely.

## Prompt recipe

Compose the brief in this order:

1. communication goal;
2. subject and relationship;
3. setting and camera/composition;
4. visual treatment and palette;
5. aspect ratio and dimensions;
6. text policy;
7. negative constraints;
8. reference asset and continuity requirements;
9. intended README/HTML placement, alt text, crop behavior, and reuse rule.

Do not ask the image model to explain the whole product in one picture. Choose one scene or visual metaphor.

## Text-bearing raster rule

Narrative raster assets should carry a small amount of orientation text by default:

- a short title, normally 2–6 words;
- a short subtitle, normally 6–16 words;
- exact copy supplied in the brief, with the title and subtitle kept in a quiet panel or clear negative space;
- no extra labels, fake metrics, dense UI copy, or decorative pseudo-text.

This applies to hero, problem, system, evidence, story, and social-preview images. The image should still communicate through the scene, but the title and subtitle give a first-time reader an immediate foothold. Detailed explanation belongs in Markdown or HTML.

Icons, logos, SVGs, tiny helper graphics, and transparent UI elements stay text-free unless the brief explicitly asks for lettering. If generated text is garbled, crowded, or changes the meaning, reject the candidate and regenerate with shorter exact copy; do not silently remove the orientation text.

## Candidate review

Reject candidates that:

- cover the main subject;
- introduce competing focal points;
- use excessive contrast or unreadable text;
- omit the required title/subtitle from a narrative raster asset;
- add more copy than the declared title and subtitle;
- make the human/product relationship ambiguous;
- fail the declared crop or aspect-ratio role;
- imply an unsupported product capability.

## Asset record

For every accepted asset, record role, dimensions, model/provider, prompt recipe, reference assets, seed/settings when available, review decision, and final hash. Record rejected candidates when their failure changes the direction.

## Use in a human-facing document

An image is part of the explanation, not decoration. Put it next to the paragraph it clarifies, give it useful alt text, preserve its declared crop role, and keep detailed explanation in Markdown or HTML. The repository's [image guide](../../docs/IMAGE_GUIDE.md) contains the full generation, placement, responsive, accessibility, and review workflow.
