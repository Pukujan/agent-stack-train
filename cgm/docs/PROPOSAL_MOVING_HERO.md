# A moving hero built from chained frames

Status: proposal, not shipped. Tracker issue:
[#41](https://github.com/Pukujan/content-generation-modules/issues/41). This
document changes no module, no schema, and no validator today. It extends
[`PROPOSAL_FRAME_SEQUENCE_ASSETS.md`](PROPOSAL_FRAME_SEQUENCE_ASSETS.md) to the
one asset every reader sees first.

## Why the hero specifically

The hero is the largest asset on the page and the visual a reader meets before
they read anything. The frame-chaining method (previous frame as `input[]`,
same `subject`, `scene`, `composition`, `lighting`, `style`, `text`, exactly one
`changes[]` entry per step) was proven on two 720x720 five-frame GIFs in
`Pukujan/stylish-profile` (commit `e2af2da2d3ff1641d0aa169255dc83ace998fa0e`,
2026-10-01). Applying it to the hero is the same mechanism pointed at the
highest-value placement. One honesty note: no animated hero pair has been
produced yet. The square narrative GIFs prove the chaining and assembly; the
wide/portrait hero pair below is the proposed shape, and its first build is
part of the acceptance criteria.

## Framing as a pair, not a crop

`modules/visual-direction/SKILL.md` already says to declare separate roles for
wide hero and portrait assets and not to force every asset into one set of
dimensions. A moving hero inherits that rule with a harder edge: each framing
is its own frame sequence. The wide sequence and the portrait sequence share the
`subject`, `changes`, palette, and durations, but each keeps its own
composition, and chaining happens inside a framing. Cropping the wide frames to
portrait sizes would cut the moving element out of frame at some point in the
sequence, which is exactly what the pair avoids.

Manifest shape for the pair: two sequence entries (same `sequence.id`,
different `orientation`) each carrying the fields from the frame-sequence
proposal, plus one shared `concept` block that names the moving element so a
reviewer can confirm the two framings tell the same story.

## Loop construction: ping-pong, so the loop does not jump

A five-frame sequence `1,2,3,4,5` played forward then cut back to frame 1 makes
the reader see the change twice in one direction and then snap backwards. The
proposed assembly records a ping-pong frame order: forward frames, then the
reverse of the inner frames, for example `1,2,3,4,5,4,3,2` with `loop=0`.
The reverse pass reuses the same committed frame files in the assembly step, so
no extra generation is needed and the shared palette stays valid. The sequence
manifest records both the generated frame count and the delivered
`frame_order`, because the two numbers differ and a reviewer comparing file
counts would otherwise think frames are missing.

Per-frame durations follow the adopted assembly rule (`duration` array, one
entry per delivered frame, last hold long enough to read the end state before
the reverse pass). Static-hero text rules still apply to frame 1: the hero
carries the exact title and subtitle copy, and the chaining keeps that copy
identical across the sequence.

## Placement constraints, measured

GitHub Markdown animates only `.gif` (`data-animated-image` marking; `.apng`,
`.png`, `.webp`, and `.jpg` render frozen — measured 2026-10-01, see
[`GITHUB_INLINE_MEDIA.md`](GITHUB_INLINE_MEDIA.md)). Two consequences:

1. The animated hero in README Markdown is a GIF.
2. The current hero rule in `schemas/asset-manifest.schema.json` requires a
   `hero` role path to end in `.png`, and issue #34 work made an SVG hero
   invalid. The proposal therefore ships the hero as a pair of records: the
   static PNG first frame keeps the existing `hero` role and the existing PNG
   gate untouched, and the animation is a companion sequence entry (working
   role `motion`) with `sequence.hero: true` marking it as the animated form of
   that hero. Adoption in Markdown points at the GIF; tools that cannot play
   GIFs still find the compliant PNG first frame in the manifest.

## Proposed validator rules

Beyond the frame-sequence rules:

1. A `motion` entry with `sequence.hero: true` MUST link to a static `hero` PNG
   entry (`hero_static_path`) whose first frame it is, and both entries MUST
   declare the same `sequence.id`.
2. `frame_order` MUST be recorded explicitly, MUST start and end on an outer
   frame (so a forward-then-reverse loop cannot hide a cut), and its length MUST
   equal the delivered duration array.
3. Both framings of a declared pair MUST reference one `concept` block, and
   their `changes` records MUST describe the same moving element.

## Boundaries

- The chaining proof comes from square 720x720 narrative GIFs at 5 frames. A
  ping-pong hero at other sizes repeats the mechanism, not a measured result;
  the first build must be reviewed like any hero (wide, tablet, narrow) before
  any adopter pins it.
- Animated social previews and og-images are out of scope: preview fetchers
  render a single image, so the static first frame stays the social asset.
- File weight is unmanaged here; proposal acceptance includes recording frames,
  colours (the 64-colour shared palette), and dimensions so size can be judged
  from records.

## Acceptance criteria for the eventual implementation

1. A wide and a portrait moving-hero pair is built once with the chained method
   and assembled ping-pong, and both pass frame-by-frame vision review for
   stray text.
2. The manifest records from this document exist in `schemas/` and the
   validator enforces the three rules above fail-closed.
3. `docs/IMAGE_GUIDE.md` and `modules/visual-direction/SKILL.md` describe the
   hero pair and the ping-pong rule at the point where a reader chooses hero
   roles.
