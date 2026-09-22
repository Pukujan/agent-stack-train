# README playbook

This playbook turns the helper contract into a working editorial process. It is for an agent or maintainer who needs to create or repair a repository README, product page, review packet, or related human-facing documentation.

The README is the first conversation a project has with a new reader. It should answer the human question before it asks the reader to understand the implementation.

## The first-screen test

After the title, lead sentence, and first visual, a first-time reader should be able to say:

> This project exists because ___, it helps ___ do ___, and I can learn or try it by ___.

If the reader can only repeat a category such as “an AI-powered framework,” the story is still too abstract. If the reader sees commands and folder names before understanding the reason to care, move the technical details down.

## Read the target repository first

Before drafting:

1. Read the target repository's `AGENTS.md`, `README.md`, current checkpoint, and relevant project contract.
2. Read `.content-system/system-version.json` and the relevant brief, brand, visual, asset, and review files.
3. Search for shipped behavior, tests, screenshots, examples, prompt records, and review artifacts.
4. Find earlier content-system previews or README promotions in the target repository. Preserve what was reviewed; change only what the new evidence requires.
5. Separate shipped facts, experiments, plans, and unknowns before writing a promise.

The helper method does not supply product facts. The target repository does.

## Write in this order

| Section | Reader job | What to include |
| --- | --- | --- |
| Why this exists | recognize the situation | a concrete human problem and consequence |
| What this project is | understand the promise | audience, scope, useful outcome, and explicit non-claims |
| What you can make or use | see the payoff | outputs, examples, decisions, or workflows |
| How it works | understand the mechanism | a few reader-sized steps before internal architecture |
| Evidence and boundaries | decide whether to trust it | sources, status labels, limitations, and open work |
| Image generation and use | understand the visual language | asset roles, prompt record, placement, crop, alt text, and reuse |
| Templates and guides | continue the work | links to the adapter, templates, schemas, and deeper docs |
| Prior work and references | see the lineage | reviewed examples, earlier decisions, and what was carried forward |
| Try it | take the next step | the smallest useful command, example, or review action |

Technical details belong in the mechanism, setup, and reference sections after the reader has a reason to continue. They should support the story, not replace it.

## Make the writing welcoming

- Use “you” when describing the reader's job and concrete nouns when describing the product.
- Name the frustration before naming the architecture.
- Explain a term the first time it appears; put the internal name in parentheses only when it helps the reader find the source.
- Use short paragraphs, descriptive headings, and selective bolding so a skimming reader can recover the story.
- Keep confidence proportional to evidence. “The repository records” is safer than “the system understands.”
- Say what is not yet built, measured, or proven where that boundary affects the reader's decision.
- Give the reader a path to a useful next action even when the project is research or architecture work.

## Make the writing skimmable

The research behind these rules is in [`CONTENT_RESEARCH.md`](CONTENT_RESEARCH.md). Apply it before polishing tone:

- write headings that describe the answer or outcome, not only the category;
- put the main point in the first sentence of a section;
- keep one idea per paragraph and use bullets for parallel information;
- bold one short, meaningful anchor when it helps a reader recover the point quickly;
- use bold for a problem, outcome, mechanism, proof, or boundary rather than for generic adjectives;
- read only the headings, bold phrases, and link text as a second-story test;
- keep the text understandable if bold styling disappears;
- use semantic headings and descriptive links so the visual treatment does not carry structure by itself.

There is no universal number of words to bold. The helper's practical house rule is one short phrase per paragraph, often 2–8 words, with restraint preferred over coverage.

## Use visuals as explanation

A hero should establish the human problem and promise. A supporting visual should explain one different mechanism or boundary. Do not fill the README with alternate hero banners.

Place each image beside the paragraph it clarifies. Give it useful alt text, preserve the declared responsive role, and link to the prompt record or [image guide](IMAGE_GUIDE.md). A visual without a role, usage note, or review decision is an orphaned asset.

Use the target repository's visual contract first. When the target inherits the helper's default direction, prefer the anime-inspired human-and-companion continuity documented in [`BRAND_DIRECTION.md`](BRAND_DIRECTION.md) and in the prior [Harness](https://github.com/Pukujan/harness-on-steroids) and [Eval Lab](https://github.com/Pukujan/Eval-lab) outputs.

## Preserve evidence and status

For each important claim, record:

- the claim in plain language;
- the source file, test, run, data artifact, or reviewed output;
- one status: `shipped`, `experimentally_supported`, `planned`, or `unknown`;
- the boundary that prevents the claim from becoming a promise it cannot support.

Model-assisted scores can help a person review a draft. They do not override deterministic checks, repository evidence, or human judgment.

## Final human review

Before opening a PR, ask:

1. Does the first screen explain why the project exists without requiring technical knowledge?
2. Can a reader name the audience, useful outcome, and main boundary after twenty seconds?
3. Does the mechanism appear before the deep architecture?
4. Are the visuals readable, purposeful, and useful when stacked on mobile?
5. Can another person regenerate or reuse every committed image from the recorded prompt and guide?
6. Can every strong claim be traced to evidence?
7. Is the next action obvious?

Run the deterministic validator after this human review. The validator catches missing contract structure; it cannot decide whether the story feels honest or welcoming.
