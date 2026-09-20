# TASK-PCM-0004 — Build and dogfood the reusable content-generation system

<!-- continuity:task {"acceptance":["content-generation-modules contains versioned modules for brand foundation, content context, writing direction, visual direction, image generation, and HTML demos","the helper repo has machine-readable project/asset/review schemas and a pinned release or commit reference","Eval Lab receives a non-destructive project adapter that points agents to the helper contract and preserves its existing research contracts","the Eval Lab adapter includes a durable project brief, brand-language rules, visual-style rules, and asset manifest","deterministic validation checks the adapter, claims/asset metadata, and required preview outputs","at least one rendered README/HTML/PDF review packet is produced for human inspection","the task records exact branch, PR, render, and validation evidence for a fresh Luna session","no target repository is merged without user review"],"depends_on":["PCM-0003"],"goal":"Create a reusable, versioned content-generation helper repository and apply it to Eval Lab as a preview-only dogfood integration with durable rendered review artifacts.","id":"PCM-0004","next_action":"Create the helper repository contract and the Eval Lab preview task branches.","owner":"Codex current implementation session; GitHub assignee Pukujan","priority":"P0","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"The user needs multiple agents and ChatGPT sessions to produce human-oriented brand language, README content, visual direction, images, and HTML demos consistently without rebuilding the workflow from conversation history."} -->

- Status: active
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

- `tasks/TASK-PCM-0004-content-system.md`;
- `checkpoints/CURRENT.md`;
- `HANDOFF.md`.

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
