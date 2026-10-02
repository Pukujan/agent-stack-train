# Changelog

## 0.5.12 — draft

- **Issue, pull request, and receipt prose (issue #45):** new [`docs/NARRATIVE_AUTHORITY.md`](docs/NARRATIVE_AUTHORITY.md) states the human-output rules adopters apply to issue logs, pull request titles and bodies, receipts, and commit subjects, and routes them through `human-sounding-writing` (**hsw**) and `human-output-naming` (**hon**);
- it encodes the two rules #45 names: a title is one complete, understandable human sentence with no leading prefix code (`feat:`, `fix:`, `chore:`) and no internal task number, and every commit SHA, pull request number, flag, or file path gets a plain-English meaning in the same sentence before it carries weight;
- `docs/writing-routing.json` adds a `receipts` surface and a `title_contract` to the `github_and_docs_prose` route, and `docs/human-sounding-rules.json` adds the matching title patterns (`title_prefix_code`, `title_internal_task_number`, `title_reference_only`);
- README and AGENTS point at [Observational Issue Ops](https://github.com/Pukujan/observational-issue-ops) as the single upstream for the three-plane issue template and triage, and at the stack release train [`stack-releases.json`](https://github.com/Pukujan/agent-stack-train/blob/main/stack-releases.json); CGM links to those sources and does not vendor their files;
- the release train moved out of Observational Issue Ops into its own repository, [agent-stack-train](https://github.com/Pukujan/agent-stack-train), so that no product repository certifies its own siblings; every CGM link to `stack-releases.json` now points there;
- the new doc joins `REQUIRED_HELPER_DOCS` and `system-version.json` `helper_contract_files` (presence only — no CI prose grade and no new lint step);
- version bump to 0.5.12 across `system-version.json`, README, CHANGELOG, and the writing rules file.

## 0.5.11 — draft

- **Adopter merge gates (issue #18):** new [`docs/ADOPTER_MERGE_GATES.md`](docs/ADOPTER_MERGE_GATES.md) separates four gates in plain language — (1) CGM contract validation, (2) target-side factual/link/test checks on the current head, (3) branch-protection readiness including up-to-date status and stale source claims, and (4) merge authorization (human approval vs auto-merge);
- documents an optional CI + auto-merge path for adopters whose own policy permits merging without a separate reviewer, and states plainly that a validator pass does not trigger or guarantee a merge and that CGM cannot approve, push, or merge an adopter's pull request;
- validator: new `check_adopter_merge_gates` fails closed if the guide is missing, drops one of the four gate concepts, or omits the boundary that CGM does not approve, push, or merge an adopter PR; the guide joins `REQUIRED_HELPER_DOCS` and `system-version.json` `helper_contract_files`;
- README, AGENTS, and `docs/ACS_VERIFY.md` cross-reference the guide; unit tests cover presence, a missing guide, and a missing CGM-merge boundary;
- version bump to 0.5.11 across `system-version.json`, README, and CHANGELOG.

## 0.5.10 — draft

- **Reader-facing explanations route to `writing-direction` (issue #15):** new `reader_facing_explanations` route in `docs/writing-routing.json` for human-facing research plans, architecture explanations, and evidence briefs — `load: writing-direction`, `required_load: true`, with a 6-item `review_checklist`;
- the route is listed as an exception to `human_facing_default`, so those reader-facing briefs do **not** silently default to hsw; a scholarly paper or raw data writeup still routes to `human-sounding-writing` (hsw);
- validator: `reader_facing_explanations` joins `REQUIRED_ROUTER_ROUTE_IDS`, and `check_writing_contract` asserts its load, `required_load`, surfaces (research plan / architecture / evidence brief), hsw distinction note, and review checklist;
- `docs/WRITING_ROUTING.md` gains a "Reader-facing explanations" section with the checklist; README and the always-on inject name the new exception;
- unit tests cover the route shape and reject a missing route;
- version bump to 0.5.10 across `system-version.json`, README, CHANGELOG, and the router contract.

## 0.5.9 — draft

- **PNG hero enforcement (issue #34):** `schemas/asset-manifest.schema.json` now rejects an SVG assigned to the `hero` role — a hero asset must be a raster `.png` with a non-`svg` orientation;
- `scripts/verify_adopter_content.py` adds `check_manifest_hero_asset_format` and `check_readme_hero_format`, rejecting an SVG or non-PNG hero in the manifest or the README banner;
- **Adopter README linter (issue #35):** new `scripts/validate_content_system.py --check-adopter-readme` (and `verify_adopter_content.py --check-readme-structure`) asserts the required adopter README structure — narrative PNG hero, problem narrative section, grounded status/evidence table, and a distinct boundaries section;
- **Antigravity bootstrap (issue #35):** new [`docs/ANTIGRAVITY_INTEGRATION.md`](docs/ANTIGRAVITY_INTEGRATION.md) plus `agent_bootstrap.antigravity` in `docs/writing-routing.json`, so Google Antigravity sessions load the full writing playbook (writing-direction, hsw, hon) and generate the multi-image narrative instead of a single SVG sketch;
- validator `check_antigravity_bootstrap_contract` fails closed if the guide or the bootstrap contract keys are missing;
- unit + integration tests cover acceptance and rejection for hero PNG enforcement, SVG hero ban, adopter README structure, and the Antigravity bootstrap contract;
- version bump to 0.5.9 across `system-version.json`, README, AGENTS, ACS_VERIFY, MIGRATING_TO_0.5, and the router contract.

## 0.5.8 — draft

- **Adopter content freshness and asset verification gate:** ship `scripts/verify_adopter_content.py` to deterministically prevent the failure mode reported in #33 (install ≠ enforcement);
- fails CI if adopter `README.md` still contains known bootstrap stubs (e.g. `Product implementation starts with... after that bootstrap is accepted`, planning placeholders, or unfilled template placeholders);
- fails CI if visual assets declared in `asset-manifest.json` are never referenced in `README.md` or docs;
- enforces basic HON checks (rejects opaque hex hashes, hashy junk, and robot key=value basenames on human-facing files and media);
- enforces HSW checks across human-facing docs (rejects tool-dump/agent-internals and high-signal AI tells in markdown prose outside code blocks);
- added `--check-adopter-docs` flag to `scripts/validate_content_system.py` to run these checks alongside adapter validation;
- updated validator, ACS_VERIFY, MIGRATING_TO_0.5, AGENTS, system-version.json, and tests.

## 0.5.7 — draft

- **Force HSW for every CGM adopter:** always-on inject is no longer ACS-only documentation — any repo that pins CGM must paste the always-on system block at agent start;
- `acs_prompt_inject` gains `always_on`, `opt_in_forbidden`, `audience: every_cgm_adopter`, `surfaces` (incl. HTML/compare), and a single copy-paste `system_block`; alias `always_on_system_block` points at it;
- new `scripts/verify_hsw_applied.py` fail-closed gate: contract mode checks always-on inject + `human_facing_default`; `--html` / `--mode acs-html` optionally scans human-facing HTML for a short AI-jargon / tool-dump denylist (not full NLP quality CI);
- validator + tests require the new contract keys and the verify script; EXPECTED_MODULES stays eight;
- docs (ACS_VERIFY “Confirm HSW automation”, WRITING_ROUTING, README, AGENTS, MIGRATING, CHANGELOG) state the rule for **all adopters**; ACS remains one example consumer;
- **operational issue-log contract:** `docs/issue-log-contract.json` + `docs/ISSUE_LOG.md` + `.github/ISSUE_TEMPLATE/operational.yml` — reproduce first, every-adopter framing, fix pin/contract/validate, never ACS-only tickets; validator asserts required keys.

## 0.5.6 — draft

- **HSW default ON for every human-facing deliverable:** HTML reports, compare HTML/UIs, appendable HTML, and other agent-produced human-readable HTML join the soft router → `human-sounding-writing` (**hsw**) with `required_load` / `default_on`;
- added `human_facing_default` to `docs/writing-routing.json` (HSW by default; exceptions only README/product entry and filename-only surfaces); no per-report or per-HTML opt-in;
- strengthened `acs_prompt_inject.when` / `instruction` so ACS hotload cannot treat HSW as optional for compare HTML or human-facing reports;
- validator + tests assert HTML report / compare surfaces, `human_facing_default`, and inject needles; still no prose-style NLP CI gate;
- docs (WRITING_ROUTING, ACS_VERIFY, SKILL, README, AGENTS, HUMAN_SOUNDING_WRITING, MIGRATING) updated; EXPECTED_MODULES remains eight; **hon** still owns basenames only.

## 0.5.5 — draft

- added `human-output-naming` (**hon**) module + `scripts/human_filename.py` with **speakable** default basenames (e.g. `Song Food – up 8.mp3`; omit defaults) and optional kebab-safe twin (`song-food--up-8.mp3`); rejects hashy junk (`song_food-p0-00e86d.mp3`) and robot key=value stems (`song-food_pitch-plus-8st_speed-0pct.mp3`);
- required **per-feature filename legends** (`docs/filename-legends/<feature>.{md,json}` helper; `.content-system/filename-legends/<feature>.json` adapter) — glossary of human terms → meaning, then associated file paths (not one global dump);
- extended soft writing router + `acs_prompt_inject` with filename + legend surfaces; sibling contract `docs/HUMAN_OUTPUT_NAMING.md` / `docs/human-output-naming.json`;
- validator: `EXPECTED_MODULES` is now eight; fail closed if the filename helper API or sample legend is missing when claimed; adapter smoke (helper ≥ 0.5.5) rejects hashy and robot basenames and checks feature↔legend membership when `feature` is claimed (hash may remain an asset field);
- ACS / full adapters must re-pin to **0.5.5** and include the 8th module; do not rewrite published blob history; HTML explorer UI is out of scope for CGM (markdown/JSON legend contracts only).

## 0.5.4 — draft

- **adopter README product-only contract:** target READMEs must cover audience, problem, features, how it works, evidence for *their* claims, and a next action — not CGM, image-gen pipeline narration, or writing-methodology teaching;
- removed `image_generation_and_use` and `templates_and_guides` (and prior-work) from required README sections; added `adopter_readme_policy` anti-rules to `templates/readme-contract.json` + schema;
- updated playbook, writing-direction, README template, AGENTS human-facing gate, and IMAGE_GUIDE audience note so image provenance stays in `.content-system/asset-manifest` (or linked records);
- optional deterministic adapter guard (helper ≥ 0.5.4): forbid `content-generation-modules` / `CGM` and the exact `## Image generation and use` heading in adopter README when `--adapter` is used;
- helper README may still document CGM, images, and templates (that is this product). Soft/docs+contract only — no prose NLP CI gate.


## 0.5.3 — draft

- soft writing router now **includes commit messages and commit subjects** → `human-sounding-writing` (**hsw**); README/product entry stays on `writing-direction`;
- contract language strengthened to **MUST load / APPLY** (`application: must_load`, per-route `required_load: true`, `apply_checklist`); no longer "prefer" or "outside the soft router" for commits;
- added machine-readable `acs_prompt_inject` so ACS can inject the MUST-load contract into agent prompts on hotload (documented in `docs/ACS_VERIFY.md`);
- validator checks commit surfaces, `required_load`, `apply_checklist`, and `acs_prompt_inject`; still no prose-style NLP CI gate.


## 0.5.2 — draft

- expanded soft writing router so PR titles/bodies, issue titles/bodies, issue-log titles, non-README docs, and changelog prose load `human-sounding-writing` (**hsw**); README/product entry stays on `writing-direction`;
- added machine-readable soft router `docs/writing-routing.json` (`content-generation.writing-routing.v1`) checked by the validator;
- added ACS hotload verify entrypoint: `python scripts/validate_content_system.py --root <cgm> --mode writing` emits a stable `CGM_VERIFY` line; documented for ACS in `docs/ACS_VERIFY.md`;
- no prose-style CI gate — presence + agent discipline only.

## 0.5.1 — draft

- documented official short name **hsw** (also HSW) for the `human-sounding-writing` module in the skill frontmatter/body, soft writing router, AGENTS, README, and human-sounding guide;
- canonical module id, folder name, and `EXPECTED_MODULES` entry remain `human-sounding-writing` (adapters keep that id);
- rebuilt root README for ACS / Study-os pin path: current version near the top, seven-module catalog with paths and when-to-load, writing-router summary + hsw alias, adapter pin instructions (version/SHA, `.content-system/`, validator), tightened story while keeping required sections and marketing assets;
- docs/alias + README contract refresh — no module rename or router behavior change beyond naming the short alias.

## 0.5.0 — draft

- added the `human-sounding-writing` module for posts, blogs, social copy, general agent prose, and papers or data writeups;
- vendored `docs/HUMAN_SOUNDING_WRITING.md` and `docs/human-sounding-rules.json` so adapters do not depend on box-only shared refs;
- added soft writing router `docs/WRITING_ROUTING.md` so README/product entry keeps `writing-direction` scan/bold rules while other prose uses human-sounding guidance;
- updated `AGENTS.md` and README module-selection guidance to point at the router;
- treated the new required module as a breaking helper contract and versioned the helper from `0.4.0` to `0.5.0`;
- added `docs/MIGRATING_TO_0.5.md` so adapters add `human-sounding-writing` to their modules list and bump the pin.


## 0.3.1 — draft

- added a deterministic `0.3.x` narrative-image gate that rejects SVG substitutions, missing built-in image-generation provenance, missing exact title/subtitle records, missing prompt records, and stale file hashes;
- added `docs/HOLDOUT_EVALUATION.md` with a private three-run protocol for testing whether an agent repeats the contract on unseen target repositories;
- updated the visual template, README contract, migration guide, and helper version to make the generation workflow and holdout path durable.

## 0.3.0 — draft

- recorded the UX, accessibility, and marketing research behind descriptive headings, short sections, bullets, and selective bolding in `docs/CONTENT_RESEARCH.md`;
- made the heading-and-bold second-story scan test part of the README template, playbook, writing module, machine-readable contract, and validator;
- added `docs/BRAND_DIRECTION.md` with the Story Loop direction and analysis of prior anime-inspired README work in Harness on Steroids and Eval Lab;
- replaced the paper-study marketing visuals with original anime-inspired content UX assets showing a content designer, story-guide companion, and research-to-review loop;
- recorded the new image prompts, exact copy, alt text, crop behavior, rejection conditions, and review decisions;
- added migration guidance for existing `0.2.x` target repositories;
- versioned the helper contract from `0.2.0` to `0.3.0`.

## 0.2.0 — draft

- made the README a human-facing product entry point with a required situation, consequence, product promise, mechanism, evidence, boundaries, and next action;
- added a machine-readable README contract and deterministic checks for required sections, local visual assets, image guides, templates, and prior-work references;
- replaced the minimal README starter with a welcoming, visual, evidence-bounded template;
- added the README playbook, image generation and use guide, and prior-work record from Eval Lab, Harness on steroids, Custom Extensions, and Hades Product;
- added migration guidance for existing `0.1.x` target repositories;
- added an operational handoff gate so technical-only README drafts cannot pass as complete human-facing work;
- versioned the helper contract from `0.1.2` to `0.2.0`.

## 0.1.0 — draft

- established the six-module helper contract;
- added project, asset, and review schemas;
- added target-repository templates;
- added dependency-free structural validation;
- added ChatGPT Project/custom-GPT setup guidance;
- documented human-first writing, visual continuity, and image-generation metadata.

## 0.1.1 — draft

- added deterministic validation for a target repository adapter;
- added project-root asset existence checks when validating an adapter.

## 0.1.2 — draft

- made a short, exact title plus subtitle the default for narrative raster assets;
- kept icons, SVGs, logos, and tiny helper graphics text-free by default;
- added rejection guidance for garbled, crowded, or overlong generated copy;
- updated image-brief and visual-style templates so future adapters inherit the rule.
