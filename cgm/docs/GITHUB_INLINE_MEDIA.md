# What GitHub's Markdown renderer keeps in the DOM

Measured on GitHub on 2026-10-01 by pushing a README to a throwaway public
repository and inspecting the rendered DOM after each change. These are
constraints, not preferences. Any adopter who wants inline media in a README
hits them, so they belong in the helper's documentation and not in one
project's commit notes.

The short version: a GIF animates, `user-attachments` is the only inline video
path, audio cannot play, and `<picture>` survives.

## Images and animation

- An `<img>` survives the sanitizer with an arbitrary `src`. GitHub keeps the
  element and rewrites the URL.
- GitHub attaches `data-animated-image` to a rendered `.gif` image. It does not
  attach it to `.apng`, `.png`, `.webp`, or `.jpg`. An APNG therefore renders as
  a single frozen frame, which is the whole reason the animated narrative assets
  in [`PROPOSAL_FRAME_SEQUENCE_ASSETS.md`](PROPOSAL_FRAME_SEQUENCE_ASSETS.md)
  are GIFs.
- A `<picture>` element with a `<source media="(max-width: 640px)" srcset="...">`
  and a fallback `<img>` survives. GitHub wraps it in
  `<themed-picture data-catalyst-inline="true">` and the browser still performs
  the media swap.
- The theme fragments `#gh-dark-mode-only` and `#gh-light-mode-only` appended to
  an image src select per reader theme. See
  [`PROPOSAL_DARK_MODE_VARIANTS.md`](PROPOSAL_DARK_MODE_VARIANTS.md) for the
  pairing contract built on this.

## Video

`<video src="...">` is stripped when the source is any of these:

- a `raw.githubusercontent.com` URL,
- a `github.com/.../raw/...` path,
- a GitHub Pages URL,
- a release-asset download URL.

In each case the rendered DOM contained 0 video elements. GitHub's own asset
hosting works: `<video src="https://github.com/user-attachments/assets/<uuid>">`
renders a real player. GitHub rewrites the element, wraps it in a `<details>`
element whose summary carries the original filename, and emits
`data-canonical-src`.

## Audio

`<audio src="...">` is stripped in every case tried, including when `src` is a
`user-attachments` asset URL — the same host that works for video. The rendered
DOM contained 0 audio elements. An `<img>` whose `src` is an mp3 survives the
sanitizer and renders as a broken image, not a player. There is no inline audio
path in GitHub Markdown.

## The upload path is not an API

Uploading to `github.com/user-attachments` needs a browser session cookie.
Measured responses:

- `POST https://github.com/upload/policies/assets` returns HTTP 422 for an
  OAuth token of the form `gho_`,
- `https://api.github.com/upload/policies/assets` returns 404,
- there is no supported API for this upload.

A `user-attachments` URL therefore cannot be produced by an automated build
script with a token. It is a manual, browser-session step, or a real browser
session driving the upload.

## What this means for adopters and for CGM

1. Plan animation as a GIF built on a shared palette. No other container
   animates in rendered Markdown.
2. If a page needs a video, budget for the manual browser upload and record the
   resulting asset URL in the manifest. Do not script it.
3. Do not promise inline audio. Offer a link to the file instead.
4. Responsive swaps and theme pairing can be done in the markup itself —
   `<picture>` and the theme fragments both survive — so a derived-asset pair
   needs no server support.
5. Any claim in a proposal about GitHub rendering must be re-measured before it
   becomes a rule. The DOM behaviour above is GitHub's, on one date, and GitHub
   can change it.
