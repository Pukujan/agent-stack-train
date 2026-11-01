# PROMPT_INJECT — acs_prompt_inject (CGM 0.5.13)

Generated / refreshed by `hotload_check` after full adapter `VALID`.
Source: CGM `docs/writing-routing.json` → `acs_prompt_inject`, from the `cgm/` folder of the same agent-stack-train checkout as this pack.

Also see: CGM [`docs/ACS_VERIFY.md`](../../../../../cgm/docs/ACS_VERIFY.md) and [`docs/writing-routing.json`](../../../../../cgm/docs/writing-routing.json).

**Version:** CGM `0.5.13`. It moves with the stack: re-run `hotload_check` after updating the agent-stack-train checkout.

## application

`must_load` — agents MUST load the listed module before writing each surface.

## When

At agent start / session boot for EVERY repo that pins CGM — not per-task and not ACS-only. Paste system_block into the agent system prompt before the agent writes ANY human-facing prose: GitHub or docs prose, commits, posts, papers — and before naming generated artifact / asset-manifest / media paths.

## human_facing_default

- **load:** `human-sounding-writing` (**hsw**) — `required_load: true`, `default_on: true`
- **covers:** `every human-facing prose task`, `GitHub and docs prose`, `commit messages and subjects`, `posts blogs social`, `papers and data writeups`
- **exceptions:** `readme_product_entry`, `reader_facing_explanations`, `generated_artifact_filenames`, `html_pages` (README/product → writing-direction; basenames → **hon**)
- **rule:** HSW is ON by default for EVERY human-facing prose task. Not optional. Not per-task opt-in. HTML pages (reports, compare HTML/UIs, appendable HTML) need no writing module (agent-stack-train#81); filesystem basenames → **hon**.

## Boot paste — acs_prompt_inject.system_block (ALWAYS-ON)

- **always_on:** `true`
- **opt_in_forbidden:** `true`
- **rule:** Paste the block below into the agent **system prompt at session boot** (every CGM adopter). Not per-task. Not ACS-only.

```
CGM ALWAYS-ON WRITING RULE (every adopter that pins this helper)

Before you write ANY human-facing prose — PR/issue/commit prose, issue-log titles, receipts, docs, changelog prose, posts, papers — you MUST load and apply modules/human-sounding-writing/SKILL.md (hsw).

This rule is always on. Opt-in is forbidden. Do not wait for a per-task flag.

Exceptions (only these):
- README.md / product entry pages → load modules/writing-direction/SKILL.md instead
- Human-facing research plans, architecture explanations, and evidence briefs → load modules/writing-direction/SKILL.md (reader-facing explanation, not a manuscript or data writeup)
- Generated artifact filenames / asset-manifest paths / media basenames / filename legends → load modules/human-output-naming/SKILL.md (hon)
- HTML pages (HTML reports, compare HTML/UIs, appendable HTML, other agent-produced HTML) → no writing module is required

Marketing intro sites, sales sites, and technical demo pages are not the README exception. Load modules/writing-direction/SKILL.md, plus modules/visual-direction/SKILL.md, modules/brand-foundation/SKILL.md, and modules/html-demo/SKILL.md, and follow the marketing_intro_site review checklist. Product-entry bold stays one short scan anchor. The verified-number rule still applies. Words and pictures come from the brand feeling.

If you cannot load a required skill file from the pinned CGM checkout, stop and report that.

Filenames: use scripts/human_filename (speakable basenames; optional safe_twin) and keep a per-feature legend. Hash may stay a separate manifest field.
```

## ACS addendum — dev root hygiene (paste with the block above)

Owned by ACS, not CGM. Paste it at boot together with the system_block.

```
Dev root hygiene (ACS): the dev root (ACS_DEV_ROOT; default D:\development on Windows, ~/development elsewhere) holds one entry per repo: its main checkout, or a PCM project folder with the checkout at <project>/main and task worktrees at <project>/worktrees/<TASK-ID>, made with `continuity worktree`. Never create any other worktree there, inside a checkout, or anywhere else, and no dependency or sibling clones, scratch folders, or caches. Put those under the ACS cache: %LOCALAPPDATA%\acs\{deps,scratch} on Windows, ~/.cache/acs/{deps,scratch} on macOS/Linux (ACS_CACHE_DIR overrides). Check with scripts/dev_root_check.py.
```

## Instruction (MUST paste/apply into system or task prompts)

ALWAYS-ON for every CGM adopter (ACS is one consumer, not the only one). Paste acs_prompt_inject.system_block into the agent system prompt at start. HSW (human-sounding-writing) is ON by default for every human-facing prose task. Before writing ANY human-facing prose, MUST load modules/human-sounding-writing/SKILL.md. Opt-in is forbidden; always_on is true; HSW is not optional for prose. README and product entry pages → writing-direction. Human-facing research plans, architecture explanations, and evidence briefs → writing-direction (reader_facing_explanations; a scholarly paper or raw data writeup stays on hsw). Pull request titles/bodies, issue titles/bodies, issue-log titles, commit messages, commit subjects, non-README docs, changelog prose, posts/blogs/social/general prose, and papers/data writeups → human-sounding-writing (hsw). HTML pages (HTML reports, compare HTML/UIs, appendable HTML, other agent-produced HTML) need no writing module (not_routed html_pages, agent-stack-train#81). Soft enforcement means no NLP CI grade of prose; the contract language is MUST/APPLY/default_on/always_on, not prefer. Follow apply_checklist and human_facing_default in this file. Generated artifact filenames, asset-manifest paths, committed media basenames, and filename legends → human-output-naming (hon): MUST load that skill and use scripts/human_filename with speakable basenames (omit defaults; optional safe_twin); keep a per-feature legend (glossary + file list); never opaque p0/hex stems or robot key=value stems. Marketing intro sites, sales sites, and technical demo pages load writing-direction (route marketing_intro_site, also visual-direction, brand-foundation, and html-demo). That surface is not the README exception.

## apply_checklist

1. Identify the writing surface (README, product entry, human-facing research plan / architecture explanation / evidence brief, PR title/body, issue title/body, issue-log title, commit message/subject, non-README doc, changelog prose, post/blog/social, paper/data writeup, marketing intro site, HTML page, or generated filename).
2. Look up the surface in routes[].surfaces in docs/writing-routing.json (or the table in docs/WRITING_ROUTING.md). If it is a reader-facing research plan, architecture explanation, or evidence brief, route to writing-direction (see the reader_facing_explanations route and its review_checklist) — a scholarly paper or raw data writeup still routes to human-sounding-writing (hsw). If it is human-facing prose and not README/product entry, not a reader-facing explanation, not an HTML page, and not a filename-only surface, default to human-sounding-writing (human_facing_default).
3. HTML pages (HTML reports, compare HTML/UIs, appendable HTML, other agent-produced HTML) are in not_routed: no writing module is required before writing them (agent-stack-train#81).
4. MUST load modules/<load>/SKILL.md for that route before drafting — required_load is true; do not skip because the surface is short or 'just a commit'.
5. Apply the module rules to the draft (voice, AI-tell scrub, bold policy as the module states).
6. README / product entry stays on writing-direction; do not apply hsw bold restraints there.
7. A marketing intro site, sales site, or technical demo page is route marketing_intro_site. MUST load writing-direction plus visual-direction, brand-foundation, and html-demo. Follow that route's review checklist. It is not the README exception.
8. Human-facing research plans, architecture explanations, and evidence briefs route to writing-direction (reader_facing_explanations); apply its review_checklist. A scholarly paper or raw data writeup still routes to hsw.
9. If the surface is a generated artifact filename, asset-manifest path, committed media basename, or filename legend, MUST load modules/human-output-naming/SKILL.md (hon), call scripts/human_filename (speakable by default; optional safe_twin), and keep a per-feature legend.
10. Never treat HSW as optional, soft-skip, or per-task opt-in for GitHub and docs prose, commits, posts, or papers.

## routes (Surface → module MUST load)

| Surfaces (sample) | MUST load |
| --- | --- |
| README.md; product entry pages | `writing-direction` |
| human-facing research plans; reader-facing research briefs; architecture explanations; evidence briefs; human-facing project explanations | `writing-direction` |
| marketing intro sites; sales sites; technical demo pages; big-tech intro websites; product demo pages | `writing-direction` |
| pull request titles; pull request bodies; issue titles; issue bodies; issue log titles; receipts; push receipts; commit messages; ... | `human-sounding-writing` (hsw/HSW) |
| generated artifact filenames; asset-manifest paths; committed media basenames; filename legends | `human-output-naming` (hon/HON) |

Contract language is **MUST / APPLY / default_on**, not prefer. Soft enforcement = no NLP CI grade of prose.
