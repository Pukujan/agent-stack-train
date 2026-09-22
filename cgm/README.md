# Content Generation Modules

> **Give every project a clearer story.** A versioned content UX system for turning repository evidence into welcoming, skimmable, reviewable human-facing output.

<p align="center">
  <img src="assets/marketing/hero-story-loop.png" alt="An anime-inspired content designer and friendly story-guide companion review a research, writing, visual, and review loop for a clearer project story." width="100%">
</p>

**A full repository can still leave readers guessing.** The useful truth may be spread across code, tests, screenshots, research notes, prompts, and unfinished drafts. Content Generation Modules helps an agent or maintainer find the human situation, shape the story, create supporting visuals, and keep every important claim tied to evidence.

If you are trying to make a project understandable, this repository gives you a repeatable starting point:

- **Start with the reader’s problem.**
- **Write the point so it can be skimmed.**
- **Use visuals to explain the work.**
- **Review the story before trusting the polish.**

## Why this exists

**Technical completeness does not automatically create understanding.** A project can have working code, careful tests, and valuable research while its README still makes a new person reverse-engineer what matters.

The failure is familiar: an agent sees a folder tree, produces confident copy, adds a generic hero, and moves on before checking whether the result tells a human why the project exists. The output may be grammatically correct while the product story remains invisible.

This repository exists to make that work deliberate. It gives the writer a story order, the visual designer a role and review record, the agent a pinned source contract, and the maintainer a clear point at which human judgment still matters.

<p align="center">
  <img src="assets/marketing/problem-scattered-story.png" alt="An anime-inspired content designer and story-guide companion sort research notes, screenshots, prompts, and test results into a clearer story for a waiting reader." width="100%">
</p>

## What this project is

Content Generation Modules is a **versioned contract for human-facing brand, content, visual, image, and HTML-demo work**. It helps maintainers, agents, designers, researchers, product people, and engineers turn project evidence into something another person can understand and use.

The target repository owns its product facts, audience, evidence, visual identity, and boundaries. This helper supplies the reusable method: modules, templates, schemas, guides, image records, and deterministic checks.

It does not invent a product story, provide a universal brand, host images, or replace the target repository’s research. **When the evidence is missing, the output should say so.**

## What you can make or use

- **A brand foundation** that names the audience, promise, personality, preferred language, and claim boundaries.
- **A project brief** that maps the user, problem, solution, mechanism, evidence, terminology, and limitations.
- **A story-first README or product document** that earns attention before it introduces architecture.
- **A visual direction** with palette, composition, responsive roles, text policy, and rejection conditions.
- **Generated image briefs and asset records** that explain how to create, review, place, and reuse visuals.
- **An accessible responsive HTML demo** that lets a person inspect the story at desktop, tablet, and mobile widths.

<p align="center">
  <img src="assets/marketing/story-loop-square.png" alt="An anime-inspired content designer and story-guide companion review a four-step research, writing, visual, and review loop." width="520">
</p>

## How it works

**Every output has one job.** A README explains the project. A hero introduces the promise. A problem image makes the reader’s tension visible. A supporting image explains one mechanism or boundary.

```text
target repository situation and evidence
                    |
                    v
          pinned .content-system adapter
                    |
                    v
brief -> brand -> writing / visual / image / HTML direction
                    |
                    v
        draft -> scan test -> deterministic checks
                    |
                    v
             human review -> useful output
```

1. **Read the repository first.** Find the user, situation, evidence, prior work, and boundaries.
2. **Build the source map.** Record supported claims, status, terminology, and limitations.
3. **Choose the modules.** Load only the brand, context, writing, visual, image, or HTML guidance the requested output needs.
4. **Write for the scan.** Use descriptive headings, short sections, bullets, and selective bold anchors that let a reader recover the point quickly.
5. **Make the visual explain something.** Generate a role-specific asset, inspect it at its actual use size, and record its prompt, alt text, crop, and review decision.
6. **Review before handoff.** Check the evidence, human flow, accessibility, and next action before treating the output as complete.

## Evidence and boundaries

The helper contract is **shipped as repository structure and guidance**: six module entry points, templates, schemas, a validator, image records, README rules, and a version pin. The contract does not prove that a target project’s product claims are true; those claims must come from the target repository.

The scan-first rules are grounded in usability and accessibility research. Nielsen Norman Group’s study of 51 users found better measured usability when content was concise, scannable, and objective, including descriptive headings, bullets, bold keywords, captions, and shorter sections. The study is useful directional evidence, not a universal conversion promise. The full sources and operational rules are in [`docs/CONTENT_RESEARCH.md`](docs/CONTENT_RESEARCH.md).

**Human review remains authoritative for subjective quality.** Deterministic checks can catch missing sections, files, paths, and version fields. They cannot decide whether a visual feels appropriate, a claim is persuasive, or a story is honest.

## Image generation and use

The README visuals use the repository’s current default brand direction: anime-inspired editorial scenes, a recurring content designer and friendly story-guide companion, deep blue-violet light, warm accents, and one clear workflow per asset.

The [image guide](docs/IMAGE_GUIDE.md) explains how to choose a role, write a prompt, supply exact title and subtitle copy, generate candidates, inspect wide and narrow crops, write alt text, place the asset in Markdown or HTML, and record the final decision. The committed prompt records are in [`assets/marketing/IMAGE_NOTES.md`](assets/marketing/IMAGE_NOTES.md) and [`assets/marketing/asset-manifest.json`](assets/marketing/asset-manifest.json).

For a new target repository, **copy the method, not the characters or scene**. Start from the target’s own visual contract, then keep one dominant idea, one human question, one responsive role, and one review decision per image.

## Templates and guides

Start with the [README template](templates/README.template.md) and its [machine-readable contract](templates/readme-contract.json). The template puts the human situation, promise, usefulness, mechanism, evidence, images, prior work, scan test, and next action in a deliberate order.

- [`docs/CONTENT_RESEARCH.md`](docs/CONTENT_RESEARCH.md) records the UX, accessibility, and marketing research behind scan-first writing.
- [`docs/BRAND_DIRECTION.md`](docs/BRAND_DIRECTION.md) defines the Story Loop brand direction and prior-work visual analysis.
- [`docs/README_PLAYBOOK.md`](docs/README_PLAYBOOK.md) explains the twenty-second test, welcoming language, selective emphasis, evidence status, and human review.
- [`docs/IMAGE_GUIDE.md`](docs/IMAGE_GUIDE.md) explains image roles, prompt structure, exact in-image copy, responsive crops, alt text, manifests, and rejection rules.
- [`docs/MIGRATING_TO_0.2.md`](docs/MIGRATING_TO_0.2.md) explains how existing `0.1.x` target repositories adopted the human-facing contract.
- [`docs/MIGRATING_TO_0.3.md`](docs/MIGRATING_TO_0.3.md) explains how existing `0.2.x` target repositories adopt the scan-first and anime-inspired visual direction.
- [`templates/`](templates/) contains starter project, brand, visual, image, asset, review, and README files.
- [`schemas/`](schemas/) defines the project brief, asset manifest, review rubric, and README contract shapes.

## Prior work and references

This helper is extracted from repository-specific work. It keeps the story and visual lessons from prior reviewed examples instead of pretending they were invented in this README:

| Repository | What the work contributed |
| --- | --- |
| [Eval Lab](https://github.com/Pukujan/Eval-lab) | Opens with a trust question, then uses problem, system, and evidence visuals to make the research path easy to enter. |
| [Harness on Steroids](https://github.com/Pukujan/harness-on-steroids) | Uses a human and friendly companion to make a research-act-verify loop feel concrete and memorable. |
| [Custom Extensions](https://github.com/Pukujan/custom-extensions) | Shows how to explain an everyday problem before installation, permissions, risk, and implementation. |
| [Hades Product](https://github.com/Pukujan/hades-product) | Keeps privacy, continuity, and product boundaries legible in a human relationship story. |
| [Peeps case study](https://www.linamakesnoise.com/peeps) | Demonstrates audience-led personality, onboarding, user flow, motion, and a visual metaphor that supports the product story. |

The cross-repository adoption record is [Project Continuity Modules task PCM-0008](https://github.com/Pukujan/project-continuity-modules/blob/main/tasks/TASK-PCM-0008-multi-repo-content-system.md).

The detailed evidence map is [`docs/PRIOR_WORK.md`](docs/PRIOR_WORK.md).

## Try it

**The smallest useful path is one target adapter and one reviewed README.** From this repository root:

```powershell
python scripts/validate_content_system.py --root .
python -m unittest discover -s tests -v
```

For a target project, add this adapter:

```text
.content-system/
├── system-version.json
├── project-brief.json
├── brand-language.json
├── visual-style.json
├── asset-manifest.json
└── review-rubric.json
```

Then pin the helper release or commit, read the playbook and image guide, inspect prior reviewed outputs, fill the templates from repository evidence, run the validator, and complete the twenty-second scan test.

## Current version

The current helper contract is `0.3.0` (`v0.3.0`). It adds the durable scan-first content research, the Story Loop brand direction, the prior-work visual analysis, and anime-inspired README assets with documented generation and use. Existing target repositories pinned to `v0.2.0` remain on that earlier contract until they deliberately migrate.
