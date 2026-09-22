---
name: writing-direction
description: Produce human-oriented README, marketing, UX, and product language from a project brief and brand foundation with concrete narrative structure and selective emphasis.
---

# Writing direction

## Story order

Use this sequence unless the format has a strong reason not to:

1. recognizable human situation;
2. problem and consequence;
3. what the project is;
4. how it works;
5. evidence and examples;
6. limitations and trust boundaries;
7. next action.

## README deliverable contract

Treat a repository README as a welcoming product entry point before treating it as a technical manual. Use the repository's `templates/readme-contract.json` and `docs/README_PLAYBOOK.md` as the acceptance source.

The README must make these questions easy to answer in order:

1. What human situation brings the reader here?
2. What becomes difficult, costly, risky, or confusing?
3. Why does this project exist, and who is it for?
4. What can the reader make, use, or understand with it?
5. How does it work at the reader's altitude?
6. What evidence supports the story, and where does the project stop?
7. What should the reader do next?

Place architecture, commands, schemas, and implementation vocabulary after the first human explanation. When the target repository has a visual contract or committed assets, the README should use a meaningful hero or lead visual and link to the image-generation/use guide and asset record.

## Paragraph recipe

Each important paragraph should contain:

- a concrete situation or claim;
- an interpretation that explains why it matters;
- evidence, example, or boundary.

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

Use [`docs/CONTENT_RESEARCH.md`](../../docs/CONTENT_RESEARCH.md) as the research source for this contract.

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

Also ask: can the reader find why the project exists, see one visual idea, understand how that visual was generated and should be used, find prior reviewed examples, and reach a useful next action without reading the technical appendix?
