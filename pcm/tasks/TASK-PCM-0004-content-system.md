# TASK-PCM-0004 — Build and dogfood the reusable content-generation system

<!-- continuity:task {"acceptance":["content-generation-modules contains versioned modules for brand foundation, content context, writing direction, visual direction, image generation, and HTML demos","the helper repo has machine-readable project/asset/review schemas and a pinned release or commit reference","Eval Lab receives a non-destructive project adapter that points agents to the helper contract and preserves its existing research contracts","the Eval Lab adapter includes a durable project brief, brand-language rules, visual-style rules, and asset manifest","deterministic validation checks the adapter, claims/asset metadata, and required preview outputs","at least one rendered README/HTML/PDF review packet is produced for human inspection","the task records exact branch, PR, render, and validation evidence for a fresh Luna session","no target repository is merged without user review"],"depends_on":["PCM-0003"],"goal":"Create a reusable, versioned content-generation helper repository and apply it to Eval Lab as a preview-only dogfood integration with durable rendered review artifacts.","id":"PCM-0004","next_action":"Review PR #30 and the rendered preview; do not merge the target branch until the user approves promotion into README.md.","owner":"Codex current implementation session; GitHub assignee Pukujan","priority":"P0","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"The user needs multiple agents and ChatGPT sessions to produce human-oriented brand language, README content, visual direction, images, and HTML demos consistently without rebuilding the workflow from conversation history."} -->

- Status: awaiting user review
- Protocol status: active; human review state: awaiting user review
- Owner: Codex current implementation session; GitHub assignee Pukujan
- Priority: P0
- Depends on: PCM-0003
- Suggested branch: `task/PCM-0004-content-system`
- Helper repository: `Pukujan/content-generation-modules`
- Pilot repository: `Pukujan/Eval-lab`

## Goal

Create a versioned, agent-readable content-generation system and dogfood it in Eval Lab without merging any target-repository changes before user review.

The system covers:

- brand foundation and positioning;
- project evidence and content context;
- human-oriented writing and skimmability;
- visual direction and responsive asset roles;
- image-generation recipes and provenance;
- HTML demo structure, accessibility, and rendered review;
- deterministic checks plus advisory model/human rubrics.

## Allowed files and repositories

In `Pukujan/project-continuity-modules`:

- `.gitignore`;
- `tasks/TASK-PCM-0004-content-system.md`;
- `checkpoints/CURRENT.md`;
- `HANDOFF.md`.
- `artifacts/PCM-0004-content-system-review.md`.

In `Pukujan/content-generation-modules`:

- all files required to create the initial helper repository contract, modules, schemas, templates, examples, validation scripts, and tests;
- repository-level `AGENTS.md` and `README.md`.

In `Pukujan/Eval-lab` on a dedicated preview branch:

- a task file for this adoption;
- `.content-system/**` project adapter files;
- `AGENTS.md` pointer updates only if required to make the helper contract discoverable;
- preview/demo source and rendered review artifacts declared in the task file;
- no changes to research code, experiment data, or existing asset semantics outside the declared adapter/demo scope.

## Constraints

- Keep the helper method generic; keep product facts and claims in the target repository.
- Pin helper version/commit in every target adapter; never depend silently on helper `main`.
- Keep generated context packs and PDFs as review artifacts, not canonical project state.
- Treat model-generated scores as advisory; deterministic checks and human review decide acceptance.
- Do not commit API keys, private benchmark material, generated caches, or user data.
- Do not merge target preview branches without explicit user approval.

## Required evidence

Record:

- helper branch, commit, tag or release reference;
- target branch and exact helper pin;
- deterministic validator/test commands and results;
- README/HTML render paths and review URLs where available;
- PDF artifact path if produced;
- failures, rejected outputs, and decisions that changed the system;
- one exact next action for a fresh Luna/Codex session.

## Checkpoint log

### 2026-09-20 — Codex activation

Completed:

- activated PCM-0004 from the queued Eval Lab adoption slot;
- designated `content-generation-modules` as the reusable helper repository;
- designated Eval Lab as the first preview-only dogfood target.

Evidence:

- `project-continuity-modules` main contains completed PCM-0001 through PCM-0003 history;
- `content-generation-modules` is an empty public repository ready for the first versioned helper contract;
- Eval Lab main is clean at merged TASK-0013 commit `345e731`.

Decisions:

- use a versioned skill/module repository plus a target-repository adapter;
- use ChatGPT Project/GitHub context for read/review work and Codex branches/PRs for writes;
- produce rendered review artifacts before requesting any merge.

Blocked/uncertain:

- none; additional target repositories are not yet specified, so the first dogfood target is Eval Lab.

Next:

- create the helper repository contract and the Eval Lab preview task branch.

### 2026-09-20 — Codex implementation and review handoff

Completed:

- published `Pukujan/content-generation-modules` draft helper version `v0.1.1`;
- added six reusable agent modules, three JSON schemas, target templates, ChatGPT setup guidance, and dependency-free validation;
- applied a pinned project adapter to Eval Lab in preview-only PR #30;
- added story-first Markdown and responsive HTML previews using the existing accepted hero, wide, square, portrait, and SVG assets;
- generated and visually inspected desktop/tablet/mobile screenshots and a four-page A4 PDF review packet;
- corrected a stale-base CI failure and recorded the cause.

Evidence:

- helper release: commit `3e89100fed61da19bd3d3f17ad336f189b576c38`, tag `v0.1.1`;
- helper validation: `VALID: content-generation-modules contract`;
- target adapter validation: `VALID: content-generation-modules contract and target adapter`;
- Eval Lab local gate: repository contract OK, Ruff clean, `64 passed`;
- corrected Eval Lab CI run `35546202014`: Python 3.11 and 3.12 passed;
- Eval Lab PR #30: open, clean, all required checks passing;
- durable preview index: `artifacts/PCM-0004-content-system-review.md`.

Decisions:

- use the empty `content-generation-modules` repository as the generic helper, while keeping Eval Lab facts and claims in its local `.content-system/` adapter;
- pin the helper by tag and commit rather than reading moving `main`;
- keep canonical Eval Lab `README.md` unchanged until user review;
- retain historical CI failures as audit evidence; do not delete them.

Blocked/uncertain:

- no content-system blocker;
- additional target repositories for multi-repository dogfooding have not been supplied;
- promotion of the preview story into the canonical README awaits user approval.
- the existing Windows continuity test `test_minimal_end_to_end_dogfood_flow` currently fails because generated source paths use backslashes while the assertion expects `checkpoints/CURRENT.md`; fixing that protocol portability defect is outside PCM-0004 scope.

Next:

- open the durable preview links, review the PDF/screenshots, and decide whether to promote the system into Eval Lab's README before applying it to additional repositories; separately queue the Windows path assertion as a continuity maintenance task.
