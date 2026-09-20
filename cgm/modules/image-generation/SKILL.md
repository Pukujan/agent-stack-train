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

## Candidate review

Reject candidates that:

- cover the main subject;
- introduce competing focal points;
- use excessive contrast or unreadable text;
- make the human/product relationship ambiguous;
- fail the declared crop or aspect-ratio role;
- imply an unsupported product capability.

## Asset record

For every accepted asset, record role, dimensions, model/provider, prompt recipe, reference assets, seed/settings when available, review decision, and final hash. Record rejected candidates when their failure changes the direction.
