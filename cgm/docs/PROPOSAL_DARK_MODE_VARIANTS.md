# Dark-mode variants derived by palette substitution

Status: proposal, not shipped. The transform below is a specification. CGM does
not implement it, and no generated dark asset is claimed here. Tracker issue:
[#42](https://github.com/Pukujan/content-generation-modules/issues/42).

## The problem, measured in an adopter

The narrative illustrations generated under the current image contract are flat
vector-style renders with a small, fixed palette. Measured on the
`Pukujan/stylish-profile` committed assets (2026-10-01), the palette is nine
colours:

| Token | Hex | Use |
| --- | --- | --- |
| cream | `#FFF9F0` | background |
| ink | `#1A1A1A` | linework and text areas |
| royal blue | `#4169E1` | primary accent |
| warm yellow | `#FFD93D` | accent |
| orange | `#FF8C42` | accent |
| pink | `#FF6B9D` | accent |
| lime | `#A8CC00` | accent |
| purple | `#9B6DD6` | accent |
| red | `#E63946` | accent |

GitHub serves READMEs in the reader's theme. On the dark theme, a
cream-background illustration sits inside a near-black page and reads as a
glaring bright rectangle. We observed this on the committed light assets;
nothing about the current contract prevents it.

## Derive, do not regenerate

A dark variant should be a deterministic palette transform of the committed
light asset, not a fresh generation, for two reasons. A regeneration is not
reproducible: the provider is the same built-in image generation workflow the
narrative contract already pins, and nothing in the record guarantees the new
frames match the old geometry, palette, or copy. And each regenerated asset
costs a model call; the frame-sequence proposal
([`PROPOSAL_FRAME_SEQUENCE_ASSETS.md`](PROPOSAL_FRAME_SEQUENCE_ASSETS.md)) means
one motion asset is already five or more calls.

## The transform, as a specification

The rule is a colour substitution over exact palette entries, so the result
depends only on the source file and the mapping table.

1. Swap the two neutrals: background `#FFF9F0` becomes the dark canvas, and
   linework `#1A1A1A` becomes `#FFF9F0`. For GitHub placement the proposed dark
   canvas value is `#0D1117`, the standard dark page background, so the asset
   disappears into the page the way the cream asset disappears into the light
   page.
2. Keep the seven accents (`#4169E1`, `#FFD93D`, `#FF8C42`, `#FF6B9D`,
   `#A8CC00`, `#9B6DD6`, `#E63946`) unchanged in version one. They were chosen
   against a light background, so each derived variant still needs the normal
   contrast review; if a review fails, the fix is a recorded per-token override
   in the mapping, never a hand-edited pixel.
3. Apply the mapping by exact-colour replacement (the assets are flat
   vector-style renders with a fixed palette, so there are no gradients to
   interpolate). Anti-aliased edge pixels blend the two neutrals and must be
   re-mapped as the same pair so outlines do not keep bright halos.
4. Same mapping, same source, same bytes out. The derivation is re-runnable,
   which is what makes it reviewable.

## Markdown pairing, measured and proposed

Two mechanisms, one measured, one to verify on first adoption.

GitHub's Markdown supports theme fragments on the image src: the same image
element with `#gh-dark-mode-only` or `#gh-light-mode-only` appended to the URL
selects per reader theme. That is the pairing mechanism this proposal adopts
for narrative assets.

The `<picture>` fallback was measured on GitHub on 2026-10-01: a
`<picture>` element with a `<source media="(max-width: 640px)" srcset="...">`
and a fallback `<img>` survives the sanitizer; GitHub wraps it in a
`<themed-picture data-catalyst-inline="true">` element and the browser still
performs the media swap. That makes `<picture>` usable as the pairing container
when a fragment-based pair is not available (for example inside HTML demos),
with the measured caveat that the swap is a viewport rule, not a theme rule;
the fragment mechanism stays the primary path for README Markdown.

## What the manifest must record

A reviewer must be able to tell a derived variant from a generated asset
without opening pixels. Proposed fields on the dark entry:

- `derivation` with `derived_from` (the committed light asset path), `method`
  (for example `palette-substitution`), and the `mapping` table (the exact
  token-to-hex pairs applied, including any per-token overrides);
- `source_hash`: the SHA-256 of the light asset the mapping was applied to;
- `hash` of the derived file;
- `provider` and prompt fields carry `derived`, not a model name, and there is
  deliberately no `prompt_record`, because none exists.

A derived entry that records a prompt is a contract violation: it claims a
generation that did not happen.

## Proposed validator rules

1. An asset whose `derivation.method` is set MUST have `derived_from`,
   `mapping`, and `source_hash`, and the referenced light asset MUST exist in
   the manifest with a hash.
2. Re-applying the recorded mapping to the source bytes MUST equal the derived
   file byte for byte (fail closed when the record and the artifact disagree).
3. A derived asset MUST NOT record `prompt_record` or a provider that implies
   generation.
4. Both members of a `#gh-dark-mode-only` / `#gh-light-mode-only` pair MUST be
   in the manifest, and the light member's path MUST appear in both src
   fragments.

## Boundaries

- The nine-colour palette, the glare observation, the fragment pairing, and the
  `<picture>` sanitizer behaviour are the measured parts. The `#0D1117` canvas
  value, accent retention policy, and edge-pixel rule are proposed defaults,
  adjustable per adopter palette.
- An adopter with a different fixed palette substitutes its own neutrals; the
  contract is the swap-and-keep-accents shape plus the recording rules, not
  these nine hexes.
- Derived GIF sequences swap palette per frame before assembly, reusing the
  shared-palette rule from the frame-sequence proposal so the dark loop cannot
  flicker.

## Acceptance criteria for the eventual implementation

1. `schemas/asset-manifest.schema.json` gains the `derivation` shape, and a
   validator enforces rules 1 through 4 fail-closed.
2. A worked example derives one dark variant of a CGM-internal marketing asset
   with the recorded mapping and passes the re-apply check.
3. `docs/IMAGE_GUIDE.md` documents the pairing mechanisms, marks which are
   measured on GitHub and which need first-adoption verification, and links
   this specification.
