# PROMPT_INJECT — acs_prompt_inject (CGM 0.5.13)

Generated / refreshed by `hotload_check` after full adapter `VALID`.
Source: CGM `docs/writing-routing.json` → `acs_prompt_inject`, from the `cgm/` folder of the same agent-stack-train checkout as this pack.

Also see: CGM [`docs/ACS_VERIFY.md`](../../../../../cgm/docs/ACS_VERIFY.md) and [`docs/writing-routing.json`](../../../../../cgm/docs/writing-routing.json).

**Version:** CGM `0.5.13`. It moves with the stack: re-run `hotload_check` after updating the agent-stack-train checkout.

## application

`must_load` — agents MUST load the listed module before writing each surface.

## When

At agent start / session boot for EVERY repo that pins CGM — not per-task and not ACS-only. Paste system_block into the agent system prompt before the agent writes GitHub prose (PRs, issues, issue logs, comments, commits, receipts) — and before naming files the stack itself writes.

## human_facing_default

- **load:** `human-sounding-writing` (**hsw**) — `required_load: true`, `default_on: true`
- **covers:** `GitHub prose`, `commit messages and subjects`, `changelog prose`
- **exceptions:** `reader_facing_explanations`, `generated_artifact_filenames`, `product_pages_and_sites`, `html_pages` (README and product pages are not routed, #117; basenames → **hon**)
- **rule:** HSW is ON by default for GitHub prose. Not optional. Not per-task opt-in. HTML pages (reports, compare HTML/UIs, appendable HTML) need no writing module (agent-stack-train#81); filesystem basenames → **hon**.

## Boot paste — acs_prompt_inject.system_block (ALWAYS-ON)

- **always_on:** `true`
- **opt_in_forbidden:** `true`
- **rule:** Paste the block below into the agent **system prompt at session boot** (every CGM adopter). Not per-task. Not ACS-only.

```
CGM ALWAYS-ON WRITING RULE (every adopter that pins this helper)

Before you write GitHub prose — PR and issue titles and bodies, issue-log titles, comments, commit messages, receipts, changelog prose — you MUST load and apply modules/human-sounding-writing/SKILL.md (hsw).

This rule is always on for that prose. Opt-in is forbidden. Do not wait for a per-task flag.

This rule does not cover the project's own product. READMEs, product pages, marketing or sales sites, demo pages and HTML pages follow the owner's direction; no writing module is required, and writing-direction is loaded only when the owner asks. HTML pages need no writing module.

Exceptions (only these):
- Human-facing research plans, architecture explanations, and evidence briefs → load modules/writing-direction/SKILL.md (reader-facing explanation, not a manuscript or data writeup)
- Filenames the stack itself writes (generated artifacts, asset-manifest paths, media basenames, filename legends) → load modules/human-output-naming/SKILL.md (hon)

If you cannot load a required skill file from the pinned CGM checkout, stop and report that.

Filenames the stack writes: use scripts/human_filename (speakable basenames; optional safe_twin) and keep a per-feature legend. Hash may stay a separate manifest field.
```

## ACS addendum — dev root hygiene (paste with the block above)

Owned by ACS, not CGM. Paste it at boot together with the system_block.

```
Dev root hygiene (ACS): the dev root (ACS_DEV_ROOT; default D:\development on Windows, ~/development elsewhere) holds one entry per repo: its main checkout, or a PCM project folder with the checkout at <project>/main and task worktrees at <project>/worktrees/<TASK-ID>, made with `continuity worktree`. Never create any other worktree there, inside a checkout, or anywhere else, and no dependency or sibling clones, scratch folders, or caches. Put those under the ACS cache: %LOCALAPPDATA%\acs\{deps,scratch} on Windows, ~/.cache/acs/{deps,scratch} on macOS/Linux (ACS_CACHE_DIR overrides). Check with scripts/dev_root_check.py.
```

## Instruction (MUST paste/apply into system or task prompts)

ALWAYS-ON for every CGM adopter (ACS is one consumer, not the only one). Paste acs_prompt_inject.system_block into the agent system prompt at start. HSW (human-sounding-writing) is ON by default for GitHub prose. Before writing it, MUST load modules/human-sounding-writing/SKILL.md. Opt-in is forbidden; always_on is true; HSW is not optional for GitHub prose. HTML pages need no writing module. Pull request titles/bodies, issue titles/bodies, issue-log titles, comments, commit messages, receipts and changelog prose → human-sounding-writing (hsw). README, product pages, marketing and sales sites, demo pages and HTML pages are not routed (agent-stack-train#117, #81): follow the owner's direction. Human-facing research plans, architecture explanations, and evidence briefs → writing-direction (reader_facing_explanations). Soft enforcement means no NLP CI grade of prose; the contract language is MUST/APPLY/default_on/always_on. Follow apply_checklist and human_facing_default in this file. Filenames the stack itself writes → human-output-naming (hon): MUST load that skill and use scripts/human_filename with speakable basenames; keep a per-feature legend; never opaque p0/hex stems.

## apply_checklist

1. Identify the writing surface. If it is GitHub prose (PR title/body, issue title/body, issue-log title, comment, commit message/subject, receipt, changelog prose), MUST load modules/human-sounding-writing/SKILL.md before drafting; do not skip because it is short or 'just a commit'.
2. Apply the module rules to the draft (voice, AI-tell scrub, bold policy as the module states).
3. A README, product page, marketing or sales site, demo page or HTML page is NOT governed by CGM: follow the owner's direction. Load writing-direction only when the owner asks for it (agent-stack-train#117).
4. Human-facing research plans, architecture explanations, and evidence briefs route to writing-direction (reader_facing_explanations); apply its review_checklist. A scholarly paper or raw data writeup still routes to hsw.
5. If the surface is a filename the stack itself writes (generated artifact, asset-manifest path, committed media basename, filename legend), MUST load modules/human-output-naming/SKILL.md (hon), call scripts/human_filename (speakable by default; optional safe_twin), and keep a per-feature legend.
6. Never treat HSW as optional or per-task opt-in for GitHub prose.

## routes (Surface → module MUST load)

| Surfaces (sample) | MUST load |
| --- | --- |
| human-facing research plans; reader-facing research briefs; architecture explanations; evidence briefs; human-facing project explanations | `writing-direction` |
| pull request titles; pull request bodies; issue titles; issue bodies; issue log titles; receipts; push receipts; commit messages; ... | `human-sounding-writing` (hsw/HSW) |
| generated artifact filenames; asset-manifest paths; committed media basenames; filename legends | `human-output-naming` (hon/HON) |

Contract language is **MUST / APPLY / default_on**, not prefer. Soft enforcement = no NLP CI grade of prose.
