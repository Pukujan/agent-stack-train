# TASK-PCM-0008 — Multi-repository content-system previews

<!-- continuity:task {"acceptance":["three recently updated public repositories receive separate non-destructive content-system preview branches","each preview pins content-generation-modules v0.1.2 by tag and commit and preserves the target repository's owner instructions","each preview has a repository-specific story, skimmable Markdown, responsive HTML, and a rendered review artifact","each preview records image/asset roles and provenance without committing caches or secrets","deterministic validation and repository-native checks are run where available","target README files remain unchanged until explicit user approval","the continuity task records exact branches, PRs, render paths, validation, failures, and next actions"],"depends_on":["PCM-0004"],"goal":"Apply the reusable content-generation system to a small, representative set of recently updated public repositories so the user can compare repository-specific marketing, human-language, visual, and responsive README previews before promotion.","id":"PCM-0008","next_action":"Review the three open preview PRs and local rendered packets; promote only after explicit user approval.","owner":"Codex current implementation session; GitHub assignee Pukujan","priority":"P0","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"The user wants the human-oriented content and visual workflow to be repeatable across multiple repositories while remaining inspectable and durable across future Codex/Luna sessions."} -->

- Status: active; human review state: three preview PRs open and local review packets complete
- Owner: Codex current implementation session; GitHub assignee Pukujan
- Priority: P0
- Depends on: PCM-0004
- Suggested branch: `task/PCM-0008-multi-repo-content-system-evidence`
- Helper repository: `Pukujan/content-generation-modules`
- Helper pin: tag `v0.1.2`, commit `cb8c18fa7789e4b651e1f963892bf056b0d3276d`
- Candidate repositories:
  - `Pukujan/harness-on-steroids` — research-led agent-harness behavior and mode specification
  - `Pukujan/custom-extensions` — install-first browser-extension collection with safety contracts
  - `Pukujan/hades-product` — product architecture for persistent identity, relationships, memory, and privacy

## Goal

Create separate, repository-specific previews that make each project easier for a human to understand and easier for future agents to continue. The previews will use the shared helper contract while keeping product facts, claims, examples, voice, and visual choices local to each repository.

## Guardrails

- Read and follow each target repository's owner instructions before editing.
- Use one branch and one review packet per target repository.
- Do not overwrite canonical `README.md` files during preview work.
- Pin the helper by tag and commit; never read moving helper `main` as an implicit dependency.
- Keep generated context packs, screenshots, PDFs, browser caches, and pycache files out of Git.
- Do not make unsupported product claims; distinguish repository evidence from positioning language.
- Use calm, low-noise visual direction with one clear subject per asset and responsive roles for wide, square, and portrait contexts.
- Do not touch private repositories in this task unless the user explicitly adds them.

## Planned target branches

| Repository | Branch | Preview scope |
|---|---|---|
| `Pukujan/harness-on-steroids` | `task/TASK-0015-content-system-preview` | story-first research explanation, agent-loop diagram, responsive README/HTML review |
| `Pukujan/custom-extensions` | `task/TASK-0016-content-system-preview` | install/use/safety story, extension collection visual system, responsive README/HTML review |
| `Pukujan/hades-product` | `task/TASK-0017-content-system-preview` | human explanation of persistent character runtime, privacy/relationship boundaries, responsive README/HTML review |

## Completed preview evidence

| Repository | Commit | Pull request | Local rendered packet |
|---|---|---|---|
| `Pukujan/harness-on-steroids` | `ee818c2` | https://github.com/Pukujan/harness-on-steroids/pull/1 | `D:\claude\harness-on-steroids-TASK-0015\review-output\harness-preview.pdf` |
| `Pukujan/custom-extensions` | `b941548` | https://github.com/Pukujan/custom-extensions/pull/9 | `D:\claude\custom-extensions-TASK-0016\review-output\extensions-preview.pdf` |
| `Pukujan/hades-product` | `326e13e` | https://github.com/Pukujan/hades-product/pull/2 | `D:\claude\hades-product-TASK-0017\review-output\hades-preview.pdf` |

Each preview also has `desktop-1440.png`, `tablet-900.png`, and `mobile-390.png` under its `review-output/` directory. The HTML review page and Markdown story are committed; generated screenshots and PDFs remain local review artifacts and are intentionally not committed.

### Shared visual contract now in force

- Every narrative raster asset (hero, problem, system, evidence, story, or social image) carries one exact short title and one short subtitle inside the image.
- Titles are kept to roughly 2–6 words; subtitles to roughly 6–16 words; the copy is supplied in the brief and recorded in the asset manifest.
- The composition reserves a quiet copy panel and protects the primary human/product subject from text and overlays.
- SVGs, logos, icons, and tiny helper graphics remain text-free unless their function specifically requires lettering.
- Low-noise, single-idea images are preferred; dense dashboard-like or competing-hero drafts are rejected.

## Required evidence

Record for each target:

- exact target branch and PR URL;
- helper tag and commit pin;
- files changed and files intentionally left unchanged;
- local deterministic checks and repository-native checks;
- rendered HTML screenshot paths and PDF path where produced;
- image prompts, selected assets, and provenance metadata;
- failures, revisions, and rejected visual/copy directions;
- one exact next action for a fresh session.

## Checkpoint log

### 2026-09-21 — Multi-repository scope selected

Completed:

- inventoried recently updated public repositories under `Pukujan`;
- selected three representative public targets after read-only inspection;
- read the owner contract for `harness-on-steroids` and `custom-extensions`, and the product README for `hades-product` (which has no root `AGENTS.md`);
- confirmed the shared helper release and commit remain available.

Evidence:

- `harness-on-steroids` — `AGENTS.md`, `PLAN.md`, `HANDOFF.md`, and README establish a research-first, transcript-grounded scope;
- `custom-extensions` — `AGENTS.md` and README establish per-extension deployability, safety policy, and evidence-state rules;
- `hades-product` — README establishes product-doc scope, source-tree separation, privacy constraints, and document read order;
- helper release `v0.1.1` was available at `3e89100fed61da19bd3d3f17ad336f189b576c38` when the task was scoped.

Decisions:

- start with public repositories only;
- keep all three previews separate so the user can compare distinct voices and visual systems;
- use a single story architecture but adapt wording, evidence, and visual metaphors to each project;
- leave canonical READMEs untouched until the user reviews rendered outputs.

Blocked/uncertain:

- the helper contract was later advanced from v0.1.1 to v0.1.2; the completed preview evidence below uses the newer release.

Next:

- create each target's dedicated worktree/branch, read the remaining required design documents, and build the first non-destructive preview packet.

### 2026-09-20 — Preview branches and rendered packets complete

Completed:

- read the required target contracts and created separate preview branches;
- added repository-specific `.content-system/` adapters, story-first Markdown, responsive HTML, prompt recipes, provenance manifests, and two raster assets per target;
- pinned every adapter to helper tag `v0.1.2` at `cb8c18fa7789e4b651e1f963892bf056b0d3276d`;
- applied the new repeatable text rule: narrative raster images have a small title and subtitle, while SVG/icon/helper assets remain text-free;
- rendered desktop, tablet, and mobile screenshots plus one PDF packet per target;
- opened PRs #1, #9, and #2 in the target repositories; canonical READMEs remain unchanged.

Evidence:

- helper adapter validation: all three targets returned `VALID: content-generation-modules contract`;
- `harness-on-steroids`: `python -m pytest -q` passed;
- `custom-extensions`: `node scripts/test-all.mjs` passed all 46 tests;
- all three responsive render checks passed with complete images and no horizontal overflow;
- `git diff --check` passed for all three target branches.

Decisions:

- keep the preview branches separate and non-destructive so the user can compare them before README promotion;
- use wide and square raster roles for device coverage, with the same calm visual language and exact embedded copy;
- keep generated screenshots and PDFs local while committing the inspectable HTML, Markdown, assets, prompts, and manifests.

Revisions:

- rejected the noisy, multi-dashboard visual direction because it covered the human/AI subject and competed with comprehension;
- retained only calm, single-idea wide and square assets with readable embedded copy;
- generated screenshots and PDFs remain outside Git as local review artifacts.

Blocked/uncertain:

- no merge or README promotion is authorized by this checkpoint;
- the user still needs to review the three PRs and rendered packets before promotion.

Next:

- user reviews the three open preview PRs and local PDF packets; after explicit approval, promote only the selected Markdown/image direction into each canonical README and merge the corresponding PR.
