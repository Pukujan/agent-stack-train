# Image generation and use guide

Images in a repository README should help a person understand one idea before they read the technical explanation. This guide covers the complete path from visual question to committed asset.

## Choose the job first

| Role | Reader question | Typical placement |
| --- | --- | --- |
| Hero | Why should I care about this project? | directly below the title and promise |
| Problem | What goes wrong without it? | beside the problem section |
| System | How does the main mechanism fit together? | beside the mechanism or workflow |
| Evidence | What makes the result inspectable? | beside proof, tests, or review state |
| Story | What human relationship or transition matters? | beside a narrative section |
| Social preview | What should a shared link communicate? | repository or social preview metadata |
| Icon/helper | What small action or state is this? | interface or documentation support |

Use one dominant idea per asset. A supporting visual should teach a different part of the story; it should not be a second hero with a new crop.

## The generation workflow

1. **Read the story.** Start from `project-brief.json`, `brand-language.json`, and `visual-style.json`. Identify the reader, the single message, and the boundary the image must preserve.
2. **Write the brief.** Declare the role, audience, subject relationship, scene, composition, palette, dimensions, crop, text policy, exact title/subtitle, and rejection conditions.
3. **Generate candidates.** Use the image-capable tool available in the current workflow. Keep the prompt and safe settings with the review record. If a provider does not expose a stable seed or model version, record reproducible intent instead of claiming exact reproduction.
4. **Inspect at use size.** Review the original and the rendered README/HTML at wide, tablet, and narrow widths. Check the subject, copy, crop, contrast, and alt-text meaning.
5. **Reject clearly.** Reject garbled or crowded text, competing focal points, covered subjects, wrong aspect ratios, dense fake UI, unsupported product claims, and any image that becomes decorative noise.
6. **Commit the accepted asset.** Use a stable path under the target repository, add it to `asset-manifest.json`, and give it useful alt text in the README or HTML.
7. **Record the decision.** Link the prompt record from the README or the project's visual documentation. Record accepted and rejected directions when they change the story.
8. **Review the human flow.** Ask whether the image makes the adjacent paragraph easier to understand. If it does not, change the image role or remove it.

## Prompt skeleton

Use this structure and replace every placeholder before generation:

```text
Use case: <ads-marketing | productivity-visual | illustration-story | other>
Asset type: <hero/problem/system/evidence/story/social/icon>
Reader question: <the one question this image helps answer>
Dominant message: <one sentence>
Audience: <who needs this orientation>
Scene/backdrop: <place and context>
Subject and relationship: <people, product, and how they relate>
Style/medium: <photo, editorial illustration, 3D, or other>
Composition/framing: <orientation, focal point, copy space, crop behavior>
Lighting/mood: <mood that supports the story>
Color palette: <reference colors and contrast>
Dimensions/aspect ratio: <declared role and size>
Text (verbatim): "<short title>" / "<short subtitle>"
Alt text: <what a non-visual reader should learn>
Constraints: <must keep, must show, must remain visible>
Avoid: <garbled text, extra labels, unsupported claims, clutter>
Use in README/HTML: <section and placement>
```

## Text-bearing raster rules

For hero, problem, system, evidence, story, and social-preview rasters:

- use one exact title, normally 2–6 words;
- use one exact subtitle, normally 6–16 words;
- keep both in a quiet panel or clear negative space;
- supply the copy verbatim and inspect its spelling;
- do not add fake metrics, dense interface labels, decorative pseudo-text, or extra slogans.

Keep icons, logos, SVGs, and tiny helper graphics text-free unless lettering is part of their function. If the generated copy is unreadable, regenerate with shorter exact text; do not silently remove the orientation copy.

## Use in Markdown

Use the role and alt text to place the asset next to the idea it explains:

```markdown
<p align="center">
  <img src="docs/content-system-assets/hero.png"
       alt="A human and a product move from a recognizable problem toward a clear, inspectable outcome"
       width="100%">
</p>
```

For a supporting asset:

```markdown
![A supporting visual showing the project's main boundary](docs/content-system-assets/supporting-square.png)
```

The alt text should communicate the image's job, not repeat its filename or embed the entire caption. Keep detailed interpretation in nearby Markdown so the story remains available to screen-reader users and people who cannot load images.

## Responsive and accessibility review

- Declare separate roles for wide, square, portrait, icon, and social-preview assets where the target needs them.
- Keep important subjects and copy inside the crop-safe area.
- Check wide, tablet, and narrow layouts after the image is placed in the document.
- Keep contrast calm but sufficient; do not make neon or dense panels do the explaining.
- Verify that the paragraph and alt text still convey the main idea if the image fails to load.
- Record the final dimensions, file hash, and review decision.

## Asset record

The asset manifest or linked prompt record should include:

```text
path
role
exact title and subtitle
dimensions and aspect ratio
prompt intent and negative constraints
provider/model and stable settings when available
reference assets and hashes when used
alt text
README/HTML placement and reuse rule
crop behavior
accepted/rejected review decision
final file hash
```

See the committed examples in [`assets/marketing/IMAGE_NOTES.md`](../assets/marketing/IMAGE_NOTES.md) and the prior repository records linked from [`PRIOR_WORK.md`](PRIOR_WORK.md).
