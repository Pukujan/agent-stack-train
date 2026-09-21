# TASK-PCM-0008 — Multi-repository content-system previews

<!-- continuity:task {"acceptance":["three recently updated public repositories receive separate non-destructive content-system preview branches","each preview pins content-generation-modules v0.1.1 by tag and commit and preserves the target repository's owner instructions","each preview has a repository-specific story, skimmable Markdown, responsive HTML, and a rendered review artifact","each preview records image/asset roles and provenance without committing caches or secrets","deterministic validation and repository-native checks are run where available","target README files remain unchanged until explicit user approval","the continuity task records exact branches, PRs, render paths, validation, failures, and next actions"],"depends_on":["PCM-0004"],"goal":"Apply the reusable content-generation system to a small, representative set of recently updated public repositories so the user can compare repository-specific marketing, human-language, visual, and responsive README previews before promotion.","id":"PCM-0008","next_action":"Create the three preview branches after reading each target repository contract; render the first review packets without changing canonical README files.","owner":"Codex current implementation session; GitHub assignee Pukujan","priority":"P0","protocol_version":"0.1.0-draft","schema":"project-continuity.task.v1","status":"active","why":"The user wants the human-oriented content and visual workflow to be repeatable across multiple repositories while remaining inspectable and durable across future Codex/Luna sessions."} -->

- Status: active; human review state: preview branches planned
- Owner: Codex current implementation session; GitHub assignee Pukujan
- Priority: P0
- Depends on: PCM-0004
- Suggested branch: `task/PCM-0008-multi-repo-content-system`
- Helper repository: `Pukujan/content-generation-modules`
- Helper pin: tag `v0.1.1`, commit `3e89100fed61da19bd3d3f17ad336f189b576c38`
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
- helper release `v0.1.1` is available at `3e89100fed61da19bd3d3f17ad336f189b576c38`.

Decisions:

- start with public repositories only;
- keep all three previews separate so the user can compare distinct voices and visual systems;
- use a single story architecture but adapt wording, evidence, and visual metaphors to each project;
- leave canonical READMEs untouched until the user reviews rendered outputs.

Blocked/uncertain:

- target repositories have not yet received preview branches;
- whether each target needs new generated raster assets will be decided after inspecting existing assets and visual constraints;
- no merge or README promotion is authorized by this checkpoint.

Next:

- create each target's dedicated worktree/branch, read the remaining required design documents, and build the first non-destructive preview packet.
