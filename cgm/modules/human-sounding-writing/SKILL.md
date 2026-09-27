---
name: human-sounding-writing
description: >
  Use for posts, blogs, social copy, general agent prose, and papers or data
  writeups that must sound human and avoid AI tells. Do not use for README or
  product-entry copy — load writing-direction and docs/WRITING_ROUTING.md instead.
---

# Human-sounding writing

Write so a careful reader hears a person with evidence, not a model averaging
safe phrases. Specifics beat synonyms. This module is for posts, blogs, social,
general agent prose, and papers or data writeups. It is **not** for README or
product-entry pages.

## When not to use this module

If the task is a **README or product entry**, stop. Load `writing-direction`
and follow [`docs/WRITING_ROUTING.md`](../../docs/WRITING_ROUTING.md) instead.
Do **not** apply this module’s bold restraints to READMEs. README scanability
and selective bold anchors stay under `writing-direction` and the README
scanability contract.

## Durable references (in this repository)

- Full guide: [`docs/HUMAN_SOUNDING_WRITING.md`](../../docs/HUMAN_SOUNDING_WRITING.md)
- Machine rules: [`docs/human-sounding-rules.json`](../../docs/human-sounding-rules.json)
- Soft router: [`docs/WRITING_ROUTING.md`](../../docs/WRITING_ROUTING.md)

Do not depend on box-only shared-ref paths. Prefer these vendored files.

If a target repository has a `tools/content-quality` (or equivalent) checker,
run it after drafting. That wiring is optional and out of scope for the helper
contract itself.

## Operational steps

1. **Read the guide once before writing.** Generic, abstract wording is the
   main tell. Prefer concrete nouns, named actors, and numbers you can verify.
2. **Open with something concrete.** Use a real record, question, case, or
   scene from the material, then zoom out to the broader point and numbers.
   Use a plain title that states what happened. Avoid colon-reveal titles and
   slogan formulas.
3. **Write as people.** Prefer “we” or a clear narrator, active verbs, and
   present tense for findings. Say what you did and what surprised you.
4. **Keep the main text short.** Numbered plain findings work well: each opens
   with a one-line takeaway, then a one-line “what to do.” Move jargon,
   internal IDs, stats methods, and per-run tables to a methods appendix or
   collapsed details.
5. **Scrub AI tells.** Cut overused words (delve, underscore, showcase,
   crucial, pivotal, realm, intricate, quietly, “serves as”), “-ing” tail
   clauses (“…, highlighting the need”), heavy nominalizations, “not X but Y”
   contrasts, rhythmic groups of three, “No X. No Y. Just Z.”, bold inline
   labels, em-dash stacks, and “despite these challenges” endings. Mix
   sentence lengths; include some short sentences.
6. **Restrain bold.** In this module’s outputs, bold at most one short phrase
   per section when it truly helps. Prefer prose over bullets with bold
   inline headers. This restraint does **not** apply to READMEs routed through
   `writing-direction`.
7. **Verify every number** against committed data or cited sources. Never
   invent a figure. When editing, keep every number, name, and link unless the
   source itself changed.
8. **Charts for papers and data writeups.** Use a takeaway title (a sentence
   stating the finding), no colon, no IDs/paths/version tags, and no stats
   jargon in the title. Prefer stacked or plain bars sorted by value with
   direct labels. Avoid dumbbell and whisker/CI charts in main text. Label
   reference lines in words; max one decimal; few series; plain source line.
9. **Check against the rules file** (`docs/human-sounding-rules.json`) or the
   target’s content-quality checker if present. Fix, then re-check.

## Final review

- Could a smart friend outside the project repeat the main finding after one
  read?
- Does the opening still look like a concrete case rather than a summary of
  averages?
- Did bold stay restrained (for non-README work)?
- Do headings and claims still match the verified numbers?
