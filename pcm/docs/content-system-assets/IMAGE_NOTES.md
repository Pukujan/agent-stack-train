# README image notes

Prompt and review record for the narrative images in [`README.md`](../../README.md). It follows the Content Generation Modules image guide pinned at [`f85e88b`](https://github.com/Pukujan/content-generation-modules/blob/f85e88bc00362c53061d95ac7811bd9c6ada8e32/docs/IMAGE_GUIDE.md) and its default [brand direction](https://github.com/Pukujan/content-generation-modules/blob/f85e88bc00362c53061d95ac7811bd9c6ada8e32/docs/BRAND_DIRECTION.md), because PCM has no visual contract of its own. Owning issue: [#101 / PCM-0029](https://github.com/Pukujan/project-continuity-modules/issues/101).

**Status: all three images generated, reviewed and accepted on 2026-09-24.** The generator returned 1280x720 PNGs regardless of the requested ratio, so each image was cropped to its declared ratio and upscaled with Lanczos to the exact size (about 1.42x). A sharper native-resolution regeneration is a reasonable later improvement. Image providers usually expose no stable seed or model version, so these notes record reproducible intent rather than pixel-identical settings.

## Shared direction

- **Characters (original to PCM, no real people):** an adult developer/researcher in a soft hoodie with short dark hair, and a small, friendly, lantern-shaped companion robot with a warm glowing core. The robot carries or projects a notebook, which stands for the repository's continuity record. Keep both recognisable across all three images.
- **Style:** anime-inspired editorial illustration, clean line art, soft cel shading, blue-violet evening studio light with warm desk-lamp accents.
- **Palette** (CGM default): night ink `#111B4D`, violet `#8F7CFF`, cyan `#63D9FF`, coral `#FF8A70`, warm cream `#F4F1FF` for title panels, mint `#94E3CB`, gold `#FFD28A`.
- **Text policy:** exactly one title and one subtitle per image, in a quiet cream panel or clear negative space. No other lettering: no fake UI labels, code, metrics, logos or pseudo-text.
- **Format:** PNG, sRGB. Convert or resize to the exact declared size before committing.
- **Avoid:** real people or likenesses, brand logos, dark cyberpunk, dense dashboards, fake numbers, extra slogans, and garbled or misspelled text.

## `pcm-hero-continuity.png`

- Role: hero (wide README introduction to the problem and promise).
- Dimensions: 1536x1024, landscape 3:2.
- Exact text: `Projects outlast sessions` / `Keep the state in Git so any fresh session can continue.`
- Prompt: "Anime-inspired editorial illustration, landscape 3:2. An original adult developer in a soft hoodie sits at an evening desk beside a small friendly lantern-shaped companion robot with a warm glowing core. Between them floats an open notebook whose four glowing pages show simple icons only: a house (project), a map pin (current state), a single checkbox (active task), and a bookmark (last checkpoint). Behind them, faded chat bubbles drift away and dissolve, while the notebook stays bright and solid. Blue-violet evening light, warm desk lamp, palette night ink #111B4D, violet #8F7CFF, cyan #63D9FF, coral #FF8A70, cream #F4F1FF. Upper-left quiet cream panel with the title text exactly "Projects outlast sessions" and the subtitle exactly "Keep the state in Git so any fresh session can continue." No other text, no logos, no real people, no fake UI, no numbers."
- Alt text: "An anime-inspired developer and a small lantern-shaped companion robot open a repository notebook whose pages show the project, the current state, the active task, and the last checkpoint, so a new session can continue the work."
- Placement: directly below the README title and lead promise, at `width="100%"`.
- Crop behavior: keep the title panel, both characters and the notebook inside the central 80%. They must stay readable when stacked at 390px wide.
- Rejection conditions: changed or misspelled title/subtitle; extra lettering on the notebook pages; either character missing or ambiguous; dissolving chats compete with the notebook as the focal point; resembles a real person; cyberpunk or dashboard look.
- Review decision: accepted. Title and subtitle exact, no other lettering, notebook pages are icons only, notebook is the focal point. The robot reads as a round companion with a glowing core rather than a literal lantern. Post-processing: right 200 px of the 1280x720 output cropped (lamp and books), then resized to 1536x1024.
- Provider: Grok Bot built-in image generation tool (text-to-image, with the hero image as the character reference for the other two); no seed or model version exposed.
- SHA-256: `e56d4b95721e51e266ee29b20d0f63e2ff26fb285048ddd0e76b0ca7e28a3647`

## `pcm-problem-lost-context.png`

- Role: problem (make the reader's tension visible).
- Dimensions: 1536x1024, landscape 3:2.
- Exact text: `The session ended. Now what?` / `Decisions, evidence, and next steps are scattered across old chats.`
- Prompt: "Anime-inspired editorial illustration, landscape 3:2. The same original developer, looking tired and puzzled, stands at a cluttered desk covered with overlapping blank chat windows, loose sticky notes, and scattered printed charts with no readable text. The small lantern-shaped companion robot holds up a single glowing question-mark card toward the viewer. On the right, a clean but empty notebook waits under a soft spotlight, suggesting what is missing. Blue-violet evening light, cooler and dimmer than the hero, with a warm coral accent on the question mark. Upper-left quiet cream panel with the title text exactly "The session ended. Now what?" and the subtitle exactly "Decisions, evidence, and next steps are scattered across old chats." No other text, no numbers on the charts, no logos, no real people."
- Alt text: "An anime-inspired developer faces a desk scattered with old chat windows, sticky notes, and loose test results, while a small lantern-shaped companion robot holds up a single question: what is the current state?"
- Placement: in "Why this exists", after the research-numbers example, at `width="100%"`.
- Crop behavior: keep the clutter, both characters and the question-mark card visible when stacked at 390px. The empty notebook on the right may crop at narrow widths.
- Rejection conditions: readable fake text or numbers in the clutter; the problem isn't recognisable at a glance; characters covered; changed title/subtitle; despairing or alarming tone instead of puzzled.
- Review decision: accepted. Title and subtitle exact; chat windows, notes and charts show placeholder lines only, with no readable text or numbers; puzzled rather than alarming tone. Post-processing: right 200 px cropped, then resized to 1536x1024. The empty notebook is only partly visible after the crop, which the crop rule allows.
- Provider: Grok Bot built-in image generation tool (text-to-image, with the hero image as the character reference for the other two); no seed or model version exposed.
- SHA-256: `8d6d054c488443abb87d00c2f537706cad037c112f611cde362b93fd97ee96cd`

## `pcm-cycle-square.png`

- Role: supporting (system/mechanism: the per-session cycle).
- Dimensions: 1024x1024, square.
- Exact text: `Read, work, checkpoint, resume` / `Every session leaves the next one a known state.`
- Prompt: "Anime-inspired editorial illustration, square 1:1. The same original developer and the small lantern-shaped companion robot face each other across a circular loop of four glowing icon cards: an open book (read the state), a wrench (do one bounded task), a bookmark with a check mark (write a checkpoint), and a sunrise over a door (the next session resumes). Soft cyan connector lines join the cards into a loop, and a glowing notebook passes from hand to hand. Calm blue-violet evening studio, warm accents, palette night ink #111B4D, violet #8F7CFF, cyan #63D9FF, mint #94E3CB, gold #FFD28A. Top quiet cream band with the title text exactly "Read, work, checkpoint, resume" and the subtitle exactly "Every session leaves the next one a known state." Icon cards carry no words. No other text, no logos, no real people."
- Alt text: "An anime-inspired developer and a lantern-shaped companion robot pass a glowing notebook around a four-step loop: read the state, do one bounded task, write a checkpoint, and let the next session resume."
- Placement: at the start of "How it works", at `width="520"`.
- Crop behavior: keep the title band, both characters and all four cards legible at 520px and at 390px.
- Rejection conditions: fewer or more than four steps; words on the cards; loop order unclear; characters don't match the hero; changed title/subtitle; reads as a second hero with no mechanism.
- Review decision: accepted on the second attempt. The first attempt was rejected because its loop order read read, work, resume, checkpoint. Accepted image: clockwise book, wrench, checked bookmark, sunrise door; no words on cards; title and subtitle exact. Post-processing: the centred 720x720 square cut from the 1280x720 output, resized to 1024x1024.
- Provider: Grok Bot built-in image generation tool (text-to-image, with the hero image as the character reference for the other two); no seed or model version exposed.
- SHA-256: `79ed4d1ce30a9e501add57265ec8db4cd0998a3a88f965c200807bd59e3b5833`

## Reuse rule

Reuse these images only for PCM. To replace one, regenerate it from its prompt, keep its role, size and exact copy (or record a copy change here), inspect it at its README width, then update the review decision and SHA-256 in this file.
