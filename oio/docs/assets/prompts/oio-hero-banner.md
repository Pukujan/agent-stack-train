# Prompt record — oio-hero-banner.png

- **Role:** hero
- **Path:** `docs/assets/oio-hero-banner.png`
- **Dimensions:** 1264x848 (wide 3:2)
- **Provider / model:** `built-in image_gen` (image endpoint, `google/gemini-3-pro-image`)
- **Exact title:** Observational Issue Ops
- **Exact subtitle:** One issue protocol, every repository, one traceable trail
- **SHA-256:** `4aac70dde995d77c576bda4afadc74b6e4f080d2536379d2cb47d1dd531b53cd`
- **Review decision:** accepted after inspection at repository image size (title and subtitle legible and correctly spelled; no added text; characters match the supporting visuals)

## Prompt intent

Show loose note cards gathered from several project folders onto one shared ledger — the movement from scattered reports to a single traceable trail.

## Prompt (verbatim)

```text
Use case: illustration-story
Asset type: hero
Reader question: Why should I care about observational-issue-ops?
Dominant message: One shared issue protocol turns scattered reports from every repository into one traceable, non-binding proposal.
Audience: maintainers and agents across a multi-repository stack
Scene/backdrop: a warm blue-violet evening editorial workspace; a desk with three or four open project folders arranged around one glowing shared ledger page
Subject and relationship: a content designer (a woman with shoulder-length auburn-purple hair, wearing a soft lavender shirt) works at the desk beside a small friendly story-guide companion (a rounded pale-green sprout-like creature with a leaf on its head and a small blue neckerchief); together they gather loose note cards out of the folders and place them onto one open shared ledger. Keep this exact pair of characters so the hero matches the other illustrations in the set.
Style/medium: anime-inspired editorial illustration, soft painterly rendering, rounded content cards, paper and glass panels, soft neon connector lines
Composition/framing: wide 3:2 frame, desk scene centered, a quiet translucent panel in the upper area holds the title and subtitle, subject and ledger stay inside a center-safe crop
Lighting/mood: warm desk light against deep blue-violet evening, calm and orderly
Color palette: night ink #111B4D background, violet #8F7CFF emphasis, cyan #63D9FF connection lines, coral #FF8A70 small warmth, warm cream #F4F1FF title panel, mint #94E3CB confirmation, gold #FFD28A small highlights
Dimensions/aspect ratio: 1536x1024, wide 3:2
Text (verbatim): "Observational Issue Ops" / "One issue protocol, every repository, one traceable trail"
Alt text: A designer and a companion gather loose notes from several project folders onto a single shared ledger.
Constraints: keep the title and subtitle legible and exactly spelled; keep the designer, companion, folders, and ledger visible; clean negative space around the title panel
Avoid: garbled or misspelled text, extra labels, box names or captions on the folders, any text besides the title and subtitle, fake metrics, dense fake UI, dark cyber imagery, sterile dashboards, decorative pseudo-text, clutter
Use in README/HTML: directly below the title and lead sentence
```

## Negative constraints

No garbled or misspelled text, no extra labels, no box names or captions on the folders, no text besides the title and subtitle, no fake metrics, no dense fake UI, no dark cyber imagery, no sterile dashboards, no decorative pseudo-text, no clutter.

## Reuse rule

Wide hero only. Do not crop the title panel or the ledger. Reuse as the social preview at the same crop.

## Revision note

Replaces the prior JPG hero (SHA-256 `fa6165cd…`). CGM's adopter-README contract requires the hero banner to be a PNG; the JPG could not be reused. The character pair was pinned in this revision so the hero matches `oio-problem-scattered.jpg` and `oio-loop-square.jpg`.
