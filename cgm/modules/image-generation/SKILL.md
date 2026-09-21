---
name: image-generation
description: Turn a project brief and visual style into reproducible, reviewable image-generation briefs and asset records for product documentation and marketing.
---

# Image generation

## Prompt recipe

Compose the brief in this order:

1. communication goal;
2. subject and relationship;
3. setting and camera/composition;
4. visual treatment and palette;
5. aspect ratio and dimensions;
6. text policy;
7. negative constraints;
8. reference asset and continuity requirements.

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
