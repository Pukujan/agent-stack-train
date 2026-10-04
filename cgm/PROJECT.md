# Content Generation Modules — Project Contract

## Main goal

Hold **one versioned contract for human-facing brand, content, visual, image, and HTML-demo work**, so that any project can turn its own repository evidence into something a person can understand and use — a story-first README, a grounded claim set, a purposeful visual, a responsive HTML demo — without every project reinventing the method.

## Why

**Technical completeness does not automatically create understanding.** A repository can have working code, careful tests, and valuable research while its README still leaves a new person reverse-engineering what matters: who it is for, what problem it changes, what is already real, which source supports each promise, and where to begin.

That failure is the reason this project exists. An agent sees a folder tree, produces confident copy, adds a generic hero, and moves on before checking whether the result tells a human why the project exists. CGM makes that work deliberate: it gives the writer a story order, the designer a visual role and a review record, the agent a pinned source contract, and the maintainer a clear point where human judgment still decides.

## What this project is

A **reusable, versioned helper contract** — modules, templates, schemas, guides, image records, and deterministic checks — that a target repository pins and applies. CGM supplies the method; the target repository owns its product facts, audience, evidence, visual identity, and boundaries.

When the evidence is missing, the output must say so. A citation proves traceability, not truth.

## Scope

- Eight module entry points under `modules/` — brand foundation, content context, writing direction, human-sounding writing (**hsw**), human-output naming (**hon**), visual direction, image generation, and HTML demo.
- The writing router: which module a writing surface must load before drafting (`docs/WRITING_ROUTING.md`, `docs/writing-routing.json`).
- Human-output rules for issue, pull request, receipt, and commit prose (`docs/NARRATIVE_AUTHORITY.md`).
- Templates, schemas, and the README contract (`templates/`, `schemas/`).
- Deterministic checks — the validator and the verify scripts (`scripts/validate_content_system.py`, `scripts/verify_hsw_applied.py`, `scripts/verify_adopter_content.py`).
- The version pin: each target repository pins a helper version or commit and never silently follows moving `main` (`system-version.json`).

## Non-goals

- **Does not define product facts.** Claims, audience, and project-specific visual identity belong in the target repository.
- **Does not invent a product story, provide a universal brand, or host images.**
- **Does not own issue governance.** The three-plane observational-issue form and triage live upstream in [Observational Issue Ops](https://github.com/Pukujan/observational-issue-ops); CGM links to that source and does not vendor it.
- **Does not own execution continuity.** Tasks, checkpoints, push receipts, and pull request gates belong to PCM.
- **Does not own the certified version set.** Compatible stack versions live in [`agent-stack-train`](https://github.com/Pukujan/agent-stack-train); CGM appears there as the narrative and styling authority, and no product repository certifies its own siblings.
- **Does not own the install surface.** Hot-loading and wiring belong to ACS.
- **Does not approve, push, or merge an adopter's pull request.** A validator pass is not merge readiness.
- **Does not grade prose in CI.** The writing router is soft — no NLP grade and no new lint step — but its module loads are required, not optional.

## How CGM separates from the rest of the stack

The stack is several repositories, each owning exactly one layer. CGM owns **narrative** and nothing else:

| Layer | Repo | Owns |
| --- | --- | --- |
| Ticket logging | OIO — `observational-issue-ops` | Writing issue tickets **only** — the form, the filer stamp, the triage, and how to handle/prioritize them. **Not coordination.** |
| Execution coordination | ACS — `agent-custom-setup` | **Running** the tickets: making them workable, breaking them down, coordinating the agents. The multi-agent hotload pack. Future DAG++ layer. |
| Continuity | PCM — `project-continuity-modules` | Tasks, checkpoints, push receipts, PR gates, and the `continuity` CLI. |
| **Narrative** | **CGM (this repository)** | **Writing routing, prose, naming, visual direction, image generation, HTML demos.** |
| Versions | train — `agent-stack-train` | The certified version set. |
| Decision-making | JEV — `jev-dump` | Aspirational arbiter / tie-breaker between agents — **parked**; not strong enough yet. |

CGM pins no layer above it and replaces none of them: an adopter pins the train once, consumes OIO's form once, and loads CGM's modules for the surface it is writing.

## Definition of success

- A target repository can pin CGM, add its `.content-system/` adapter, and turn its own evidence into a story-first, reviewable output without reading prior chat.
- Every important product claim is tied to a revision-pinned source that says what it supports and what it leaves unproven.
- Writing surfaces load the routed module before drafting; the README keeps its scan-first contract while every other human-facing surface uses human voice.
- Deterministic checks catch missing sections, files, paths, and version fields, and human review remains authoritative for subjective quality.
- The method lives in exactly one repository, and every adopter points at this source rather than hand-copying a rule.
