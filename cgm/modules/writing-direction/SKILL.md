---
name: writing-direction
description: >
  MUST load for human-oriented README and product-entry language from a project
  brief and brand foundation with concrete narrative structure and selective
  emphasis. For PR/issue titles and bodies, issue-log titles, commit
  messages/subjects, non-README docs, and general prose, MUST load
  human-sounding-writing per docs/WRITING_ROUTING.md instead.
---

# Writing direction

**MUST load** this module for README / product-entry work. For route selection
(README vs PR/issue/commit/docs prose), follow
[`docs/WRITING_ROUTING.md`](../../docs/WRITING_ROUTING.md)
(`required_load: true` on each route). Soft = no NLP CI grade; not optional load.

## Story order

Use this sequence unless the format has a strong reason not to:

1. recognizable human situation;
2. concrete example of the problem and consequence;
3. what the project is;
4. how it works;
5. evidence and examples;
6. limitations and trust boundaries;
7. next action.

## README deliverable contract

Treat a repository README as a welcoming product entry point before treating it as a technical manual. Use the repository's `templates/readme-contract.json` and `docs/README_PLAYBOOK.md` as the acceptance source.

### Adopter README scope (0.5.4+)

An **adopter / target** README must be about the **target repository only**:

- audience and situation;
- problem and consequence;
- what the product is / is not;
- features, outputs, or workflows;
- how it works at reader altitude;
- provenance and citations for **that product's** claims;
- a next action.

**Anti-rules — do not put these in an adopter README:**

- cite, promote, justify, or defend CGM / `content-generation-modules`;
- narrate how images were generated (provider, prompt pipeline, seed, model);
- narrate writing-style methodology (this module, hsw, scan-first recipes, bold heuristics) as story;
- “Image generation and use” or “Templates and guides” sections that surface helper docs as product features.

Image provenance (role, prompt, dimensions, review) belongs in
`.content-system/asset-manifest.json` or linked prompt records. Place images with
useful alt text beside the product idea they explain.

The **helper** README (content-generation-modules itself) may document CGM,
image workflow, and templates — that is its product.

The README must make these questions easy to answer in order:

1. What human situation brings the reader here?
2. What becomes difficult, costly, risky, or confusing?
3. Why does this project exist, and who is it for?
4. What can the reader make, use, or understand with it?
5. How does it work at the reader's altitude?
6. What evidence supports the **product** story, and where does the project stop?
7. What should the reader do next?

Place architecture, commands, schemas, and implementation vocabulary after the first human explanation. When the target repository has a visual contract or committed assets, the README should use a meaningful hero or lead visual with useful alt text. Do **not** link the image-generation guide or prompt record from adopter README prose; keep those in the adapter.

## Paragraph recipe

Each important paragraph should contain:

- a concrete situation or claim;
- an interpretation that explains why it matters;
- evidence, example, or boundary.

At least one early example should show the problem unfolding for the target reader. Ground it in target-repository evidence or label it clearly as hypothetical. A section heading and a list of capabilities do not replace the explanation.

## Human-language rules

- prefer active verbs and concrete nouns;
- vary sentence length naturally;
- remove filler introductions and abstract adjective stacks;
- explain technical terms at the moment they matter;
- use one main idea per paragraph;
- bold the phrase a skimming reader should retain;
- italicize a short qualification, contrast, or human note;
- do not bold entire paragraphs;
- do not claim that a system “understands,” “guarantees,” or “solves” something without evidence.

## Scan-first formatting

Use [`docs/CONTENT_RESEARCH.md`](../../docs/CONTENT_RESEARCH.md) as the research source for this contract. Apply these as craft rules; **do not teach them inside an adopter README.**

- Make the heading tell the reader what they will learn or gain.
- Put the main point early in the section and keep one idea per paragraph.
- Use bullets for parallel benefits, steps, options, and requirements.
- Bold one short phrase when it gives a skimming reader a useful anchor. Prefer a problem, outcome, mechanism, proof, or boundary.
- Treat one short bold phrase per paragraph, often 2–8 words, as a practical heuristic rather than a universal rule.
- Read headings and bold phrases alone. They should form a useful second story about the project.
- Do not use bold as a replacement for semantic headings or descriptive links.
- If the sentence becomes inaccurate or unclear when bold is removed, fix the sentence instead of depending on styling.

## Final review

Ask what a first-time reader can repeat after twenty seconds. If the answer is only a category (“an AI-powered evaluation platform”), the copy needs a more concrete situation and mechanism.

For helper `0.4.x`+, also ask: does each material **product** claim explain what its cited source supports, what remains unproven, which exact revision was inspected, and when this evidence record was recorded? Keep valid-time bounds separate for claims that only apply during a known period. Put direct citations beside important public claims. A citation provides traceability, not a truth guarantee. Do not cite CGM to prop up the product story.

Also ask: can the reader find why the project exists, see one visual idea that clarifies the product, find evidence for product claims, and reach a useful next action — without being taught CGM, image-gen process, or writing methodology?
