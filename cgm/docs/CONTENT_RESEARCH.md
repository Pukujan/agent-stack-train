# Scan-first content research

This document is the durable research behind the helper's writing and README rules. It turns usability research into an operational content contract so a future draft does not have to rediscover why descriptive headings, short sections, bullets, and selective bolding matter.

Research reviewed: 2026-09-21.

## What the research says

### People scan before they commit to reading

Web readers often begin by scanning headings, the first lines of sections, and the left side of the page. The F-shaped pattern is a fallback behavior when text is dense, weakly structured, or not yet worth close attention. Stronger structure gives readers better places to stop and continue. [Nielsen Norman Group: F-shaped reading](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/)

### Descriptive headings create a usable outline

Meaningful headings let a reader move from section to section and identify the part that answers their question. This is sometimes called the layer-cake scanning pattern. A heading such as “How evidence becomes a usable story” carries more information than “Process” or “Details.” [Nielsen Norman Group: layer-cake scanning](https://www.nngroup.com/articles/layer-cake-pattern-scanning/)

### Bolding can create visual anchors

In a study of 51 web users, the more scannable version of a site used shorter sections, descriptive headings, bullets, bold keywords, and captions. It produced better measured usability than the promotional control. The study reported a 47% improvement for the scannable version and a 124% improvement when concise, scannable, and objective writing were combined. The study is older and small, so these numbers are directional evidence rather than a conversion guarantee. [Nielsen Norman Group: concise, scannable, and objective writing](https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/)

The result supports selective emphasis, not bolding as decoration. The bold phrase should let a skimming reader recover the paragraph's point: the problem, outcome, mechanism, proof, or boundary.

### Clear marketing is more useful than marketese

The same research found that objective copy performed better than promotional language. Marketing content can still be warm, memorable, and persuasive; it should earn attention with a recognizable situation, a concrete benefit, and evidence instead of adjective stacks.

### Formatting must remain accessible

Visual emphasis cannot carry the only meaning. Use real Markdown or HTML headings for structure, keep the heading hierarchy logical, and make sure the copy still makes sense if bold styling disappears. [W3C: headings](https://www.w3.org/WAI/tutorials/page-structure/headings/) [W3C: headings and labels](https://www.w3.org/WAI/WCAG21/Understanding/headings-and-labels)

GOV.UK also recommends highlighted keywords, subheadings, bullets, short sections, and clear paragraph organization while warning that over-highlighting can interrupt reading or make phrases look like links. [GOV.UK content research](https://www.gov.uk/government/publications/govuk-content-principles-conventions-and-research-background/govuk-content-principles-conventions-and-research-background)

## The content contract

Use these rules for README copy, product pages, marketing sections, UX explanations, and generated content examples:

1. **Lead with the human situation.** Name who is trying to do what, what becomes difficult, and why the reader should care.
2. **Make headings descriptive.** Write headings that tell the reader what they will learn or gain. Avoid vague labels such as “Overview,” “Details,” and “Other.”
3. **Put the point early.** The first sentence should orient the reader before the explanation expands.
4. **Keep one idea per paragraph.** Use short paragraphs and move parallel information into bullets.
5. **Use one meaningful bold anchor when it helps.** A practical heuristic is one short phrase per paragraph, often 2–8 words. This is a house rule, not a universal research threshold.
6. **Read the emphasis alone.** Read only the headings, bold phrases, and link text. They should form a useful second story about the product and the next action.
7. **Never use bold as a structural substitute.** Use semantic headings for sections and descriptive link text for actions.
8. **Prefer concrete outcomes to promotional adjectives.** Say what changes for the reader and how the project supports that change.
9. **Make the next step verb-first.** “Read the image guide,” “Validate a target adapter,” and “Start from the template” are easier to act on than “Learn more.”
10. **Keep claims bounded.** Label work as shipped, experimentally supported, planned, or unknown, and connect important claims to repository evidence.

## The twenty-second scan test

Before a human-facing document is accepted, ask:

- Can a new reader explain why the project exists after reading the title, lead, and first visual?
- Do the headings answer the questions a reader is likely to bring?
- Do the headings and bold anchors alone communicate the problem, promise, mechanism, and next action?
- Does removing bold styling leave the text accurate and understandable?
- Are the claims concrete and evidence-bounded rather than merely enthusiastic?
- Is the next action obvious without reading the technical appendix?

If the answer is no, improve the content structure before adding more implementation detail.

## How this changes this repository

The scan-first rules are part of the `0.3.0` helper contract. They are repeated in `modules/writing-direction/SKILL.md`, `docs/README_PLAYBOOK.md`, and `templates/README.template.md`. The README contract records the rule so future target repositories inherit it instead of treating scanability as optional polish.

## What prior repository work adds

The helper’s earlier reviewed outputs show how the writing and visual rules work together. [Harness on Steroids](https://github.com/Pukujan/harness-on-steroids/blob/main/README.md) opens with the failure a reader recognizes, then names the control problem and the measurable loop. [Eval Lab](https://github.com/Pukujan/Eval-lab/blob/main/README.md) opens with a trust question, follows with a short version, and uses problem, system, and evidence visuals to let a reader choose how deeply to continue.

Their README images also establish a useful continuity rule: keep a recognizable human and companion across the hero and supporting assets, then change the scene and diagram to answer a different question. That is why this repository’s new visuals use an original content designer and story-guide companion across the story, problem, and loop assets.
