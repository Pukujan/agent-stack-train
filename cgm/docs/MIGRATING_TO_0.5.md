# Migrating to Content Generation Modules 0.5

Version `0.5.0` adds the `human-sounding-writing` module and a soft writing
router. It does **not** change README scanability or `writing-direction` bold
rules.

## What changes

- New required module: `human-sounding-writing` (posts, blogs, social, general
  agent prose, papers/data writeups).
- New docs: `docs/WRITING_ROUTING.md`, `docs/HUMAN_SOUNDING_WRITING.md`,
  `docs/human-sounding-rules.json`.
- Helper version pin moves from `0.4.x` to `0.5.0`.

## Adapter steps

1. Pin the helper to `0.5.0` (version and commit) in the target
   `.content-system/system-version.json` (or equivalent adapter pin).
2. Add `human-sounding-writing` to the adapter `modules` list so it matches the
   helper contract.
3. **MUST load** writing modules with [`WRITING_ROUTING.md`](WRITING_ROUTING.md) /
   [`writing-routing.json`](writing-routing.json) (`required_load`):
   - README / product entry → `writing-direction` (keep scan/bold).
   - PR / issue titles and bodies, issue-log titles, **commit messages /
     commit subjects**, non-README docs, changelog prose → `human-sounding-writing`.
   - Posts / blogs / social / general prose → `human-sounding-writing`.
   - Papers / data writeups → `human-sounding-writing` (+ chart rules).
4. Run `python scripts/validate_content_system.py --root .` (and the target
   adapter check if you use one). ACS hotload may call `--mode writing` first;
   see [`ACS_VERIFY.md`](ACS_VERIFY.md).

## What stays the same

- README scanability_contract / selective bold anchors are unchanged.
- `writing-direction` remains the README and product-entry module.
- Claim-evidence v2 requirements from `0.4.x` remain in force for targets that
  pin `0.5.0`.

## Short name (0.5.1+)

**hsw** / **HSW** is a documentation short name for `human-sounding-writing`.
Adapters keep the module id `human-sounding-writing` in their modules list;
do not rename the folder or replace the id with `hsw`.

## Soft router + ACS verify (0.5.2+)

- Soft router surfaces now include PR/issue titles and bodies, issue-log titles,
  non-README docs, and changelog prose → `human-sounding-writing`.
- Machine-readable contract: `docs/writing-routing.json`.
- ACS entrypoint: `python scripts/validate_content_system.py --root <cgm> --mode writing`.
- Prefer full helper (and helper+adapter) for install completeness; pin **0.5.3+** (0.5.2+ for verify entrypoint without commit must-load).

## Apply + commits in router (0.5.3+)

- Commit messages and commit subjects are **in** the soft router → hsw (**MUST load**).
- `docs/writing-routing.json` declares `application: must_load`, per-route
  `required_load`, `apply_checklist`, and `acs_prompt_inject`.
- ACS must inject `acs_prompt_inject.instruction` into agent prompts after
  hotload verify (see [`ACS_VERIFY.md`](ACS_VERIFY.md)).
- Soft still means no NLP prose CI — pin **0.5.3+**.

## Adopter README product-only (0.5.4+)

- Adopter / target READMEs must be about the **target product** only (audience, problem, features, mechanism, evidence for product claims, next action).
- Do **not** cite/promote CGM, narrate image generation, or teach writing-style methodology in the target README.
- Drop any copied “Image generation and use” or “Templates and guides” sections from target READMEs; keep image provenance in `.content-system/asset-manifest.json`.
- Pin helper **0.5.4+**. With `--adapter` + `--project-root`, the validator rejects `CGM` / `content-generation-modules` and the exact `## Image generation and use` heading in the target README.
- The helper repository's own README may still document CGM workflow — that is unchanged.

## Human output naming (0.5.5+)

- New required module: `human-output-naming` (**hon**) for generated artifact filenames, asset-manifest paths, committed media basenames, and **per-feature filename legends**.
- Python API: `scripts/human_filename.py` — default **speakable** basenames (`Song Food – up 8.mp3`); optional `style="safe_twin"`; reject hashy junk and robot key=value stems.
- Soft router + ACS inject mention output filenames and legends (not titles only).
- Before / after: `song_food-p0-00e86d.mp3` (and rejected robot draft `song-food_pitch-plus-8st_speed-0pct.mp3`) → `Song Food – up 8.mp3`.
- Adapter steps:
  1. Pin helper **0.5.5+** (version and commit).
  2. Add `human-output-naming` to the adapter `modules` list (eight modules total).
  3. Use `build_basename` (speakable by default) for **new** asset paths; keep content hash as a separate asset field.
  4. Add `.content-system/filename-legends/<feature>.json` (glossary + file list) when claiming new generated assets for a feature.
  5. Do **not** rewrite published blob history unless a scoped migration requires it.
- Docs: [`HUMAN_OUTPUT_NAMING.md`](HUMAN_OUTPUT_NAMING.md), [`human-output-naming.json`](human-output-naming.json), [`filename-legends/`](filename-legends/).

## HSW default for human-facing HTML (0.5.6+)

- **HSW is ON by default** for every human-facing deliverable: GitHub prose, docs, posts, papers, **HTML reports**, **compare HTML / compare UIs**, appendable HTML, and other agent-produced human-readable HTML.
- `docs/writing-routing.json` adds `human_facing_default` and expands HSW surfaces; `acs_prompt_inject` forbids per-report / optional skip.
- Exceptions remain README/product entry (`writing-direction`) and filename-only surfaces (`human-output-naming` / **hon** for basenames).
- Adapter / ACS steps:
  1. Pin helper **0.5.6+** (version and commit).
  2. Keep the eight-module set (no new module).
  3. Inject `acs_prompt_inject` including `human_facing_default` so compare HTML / human-facing reports always load **hsw**.
  4. Run `python scripts/validate_content_system.py --root <cgm> --mode writing`.
- Soft still means no NLP prose CI — pin **0.5.6+**.

## Always-on HSW automation (0.5.7+)

- **Problem fixed:** pin ≠ enforcement. 0.5.6 documented MUST but adopters could
  skip loading HSW unless told mid-run.
- **Fix:** always-on `system_block` + `always_on` / `opt_in_forbidden` in
  `docs/writing-routing.json`; `scripts/verify_hsw_applied.py` fail-closed gate;
  validator needles; operational issue-log contract for this class of failure.
- Adapter / every-adopter steps:
  1. Pin helper **0.5.7+** (version and commit).
  2. Paste `acs_prompt_inject.system_block` into the agent system prompt at boot.
  3. Run `python scripts/validate_content_system.py --root <cgm> --mode writing`.
  4. Run `python scripts/verify_hsw_applied.py --root <cgm>` (and `--html` before
     publishing human-facing HTML / compare Pages).
- Soft still means no full NLP prose CI — automation = always-on inject +
  contract validate + optional HTML tell scan.
- Operational tickets for similar gaps: follow [`ISSUE_LOG.md`](ISSUE_LOG.md) /
  [`issue-log-contract.json`](issue-log-contract.json) (reproduce first; every
  adopter; never ACS-only).

## Adopter content freshness and asset verification gate (0.5.8+)

- **Problem fixed:** `validate_content_system.py` passed on stale bootstrap README (e.g. `Product implementation starts with... after that bootstrap is accepted`), assets declared in `asset-manifest.json` were never embedded in docs/README, and HON/HSW were not deterministically enforced on human-facing docs (CGM #33).
- **Fix:** new `scripts/verify_adopter_content.py` and `--check-adopter-docs` flag in `scripts/validate_content_system.py`.
- Adapter / every-adopter steps:
  1. Pin helper **0.5.8+** (version and commit).
  2. Run `python scripts/verify_adopter_content.py --adapter <project>/.content-system --project-root <project>` or `python scripts/validate_content_system.py --root <cgm> --adapter <project>/.content-system --project-root <project> --check-adopter-docs` in CI.
  3. Ensure `README.md` is updated beyond bootstrap placeholders and embeds declared visual assets.
  4. Ensure docs and filenames adhere to HON (no opaque hashes / robot stems) and HSW (no agent tool dumps or high-signal AI tells).

## PNG hero + adopter README structure + Antigravity bootstrap (0.5.9+)

- **Problem fixed:** an SVG layout sketch was registered and embedded as the public README hero (CGM #34), and Google Antigravity sessions generated shallow adopter READMEs that skipped the multi-image narrative and evidence structure (CGM #35).
- **Fix:** hero assets must be raster `.png` in the schema and both validators; a new `--check-adopter-readme` gate asserts the full adopter README structure; `docs/ANTIGRAVITY_INTEGRATION.md` and `agent_bootstrap.antigravity` in the router give coding agents a bootstrap that loads the full writing playbook.
- Adapter / every-adopter steps:
  1. Pin helper **0.5.9+** (version and commit).
  2. Register a PNG hero in `asset-manifest.json` and embed it as the README banner; an SVG wireframe is fine as a diagram, never as the hero.
  3. Give the README a problem narrative, a grounded status/evidence table, and a distinct boundaries section.
  4. Run `python scripts/validate_content_system.py --root <cgm> --adapter <project>/.content-system --project-root <project> --check-adopter-readme` in CI.
  5. Antigravity (or any coding agent) sessions: paste `acs_prompt_inject.system_block` at boot and follow [`ANTIGRAVITY_INTEGRATION.md`](ANTIGRAVITY_INTEGRATION.md).

## Reader-facing explanations route to writing-direction (0.5.10+)

- **Problem fixed:** a human-facing research plan, architecture explanation, or evidence brief is a reader-facing explanation, but nothing in the router named it, so agents could miss `writing-direction` and apply the wrong module (CGM #15).
- **Fix:** new `reader_facing_explanations` route in `docs/writing-routing.json` (`load: writing-direction`, `required_load: true`) with a 6-item `review_checklist`; it is an exception to `human_facing_default`, so these briefs do not default to hsw.
- Adapter / every-adopter steps:
  1. Pin helper **0.5.10+** (version and commit).
  2. When writing a human-facing research plan, architecture explanation, or evidence brief, **MUST load** `modules/writing-direction/SKILL.md` and apply the route's `review_checklist`.
  3. Keep a scholarly paper or raw data writeup on **hsw** (`human-sounding-writing`) — only reader-facing explanations route to `writing-direction`.
  4. Run `python scripts/validate_content_system.py --root <cgm> --mode writing`.

## Adopter merge gates — validation is not merge readiness (0.5.11+)

- **Problem fixed:** an adopter README pull request could pass the pinned CGM validator and target checks yet stay open, because the target repository added a manual reviewer gate or never enabled auto-merge, and the adopter guidance did not separate CGM validation from GitHub merge readiness (CGM #18).
- **Fix:** new [`ADOPTER_MERGE_GATES.md`](ADOPTER_MERGE_GATES.md) names four gates — (1) CGM contract validation, (2) target-side checks on the current head, (3) branch-protection readiness (required checks, up-to-date status, stale source claims), and (4) merge authorization (human approval vs auto-merge) — and documents an optional CI + auto-merge path.
- Adapter / every-adopter steps:
  1. Pin helper **0.5.11+** (version and commit).
  2. Read [`ADOPTER_MERGE_GATES.md`](ADOPTER_MERGE_GATES.md) before treating a validator pass as merge-ready.
  3. Confirm your target checks pass on the current head, and check whether your protection rules require a reviewer.
  4. If your own policy permits merging without a separate reviewer, run the pinned CGM validator and target checks as required CI checks and enable auto-merge; otherwise keep your review rule.
  5. Remember: CGM does not approve, push, or merge an adopter pull request, and a validator pass does not trigger or guarantee a merge.


