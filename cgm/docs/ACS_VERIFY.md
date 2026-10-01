# ACS / hotload CGM verify entrypoint

**Audience:** Agent Custom Setup (`Pukujan/agent-custom-setup`) multi-agent-hotload
and adopters (for example Study-os) that must confirm full CGM + writing modules
are present before treating hotload install as complete.

**Enforcement:** soft for prose style (no NLP CI grade). The contract language
for agents is still **MUST load / APPLY** via `required_load` / `always_on` —
not "prefer." This entrypoint checks **presence** of the helper contract,
writing modules, soft router, and always-on inject — not whether a PR body or
commit subject "sounds human."

**Audience note:** Commands below say "ACS" because ACS asked for a verify
hook. The machine contract applies to **every CGM adopter**.

## What `validate_content_system.py` already does

| Call | Checks |
| --- | --- |
| `--root <cgm>` (default / `--mode helper`) | Full helper: `system-version.json`, all eight `EXPECTED_MODULES` (including `writing-direction` and `human-sounding-writing`), schemas, templates, helper docs (including `docs/WRITING_ROUTING.md` and `docs/writing-routing.json`), README contract. |
| `--root <cgm> --mode writing` | **ACS hotload entrypoint:** both writing modules’ `SKILL.md`, soft router markdown + JSON contract (`content-generation.writing-routing.v1`), commit surfaces routed to hsw, `required_load` / `apply_checklist` / `acs_prompt_inject`, and that `system-version.json` lists both writing modules. Prints a stable `CGM_VERIFY` line. |
| `--root <cgm> --adapter <project>/.content-system --project-root <project>` | Full helper **plus** target adapter: adapter `modules` must equal the full eight-module helper set (so HSW cannot be omitted on a 0.5.x pin). |

Alex direction: ACS + adopters need **full PCM + full CGM**. Prefer the helper
(or helper+adapter) path for install completeness; use `--mode writing` when
hotload only needs a fast writing-contract gate before calling the full check.

## Commands for `hotload_check`

From a pinned CGM checkout (do not vendor CGM into ACS):

```bash
# Fast writing-contract gate (HSW + writing-direction + soft router)
python scripts/validate_content_system.py --root /path/to/content-generation-modules --mode writing

# Full CGM helper contract
python scripts/validate_content_system.py --root /path/to/content-generation-modules

# Full CGM + adopter adapter (ACS / Study-os .content-system)
python scripts/validate_content_system.py \
  --root /path/to/content-generation-modules \
  --adapter /path/to/adopter/.content-system \
  --project-root /path/to/adopter

# Full CGM + adopter adapter + content freshness / asset reference enforcement (0.5.8+)
python scripts/validate_content_system.py \
  --root /path/to/content-generation-modules \
  --adapter /path/to/adopter/.content-system \
  --project-root /path/to/adopter \
  --check-adopter-docs

# Full CGM + adopter README structure + PNG hero gate (0.5.9+; includes --check-adopter-docs)
python scripts/validate_content_system.py \
  --root /path/to/content-generation-modules \
  --adapter /path/to/adopter/.content-system \
  --project-root /path/to/adopter \
  --check-adopter-readme

# Standalone adopter content freshness & asset reference check (0.5.8+)
python scripts/verify_adopter_content.py \
  --adapter /path/to/adopter/.content-system \
  --project-root /path/to/adopter
```

On success, `--mode writing` prints a line ACS can parse, for example:

```text
CGM_VERIFY mode=writing status=OK writing_direction=present human_sounding_writing=present writing_router=present
VALID: content-generation-modules writing contract
```

Non-zero exit + `CGM_VERIFY ... status=FAIL` means the pin is incomplete.


## Human-facing default (0.5.6+)

After verify, ACS must treat **hsw** as default ON for every human-facing
deliverable: GitHub prose, docs, posts, papers, **HTML reports**, **compare
HTML / compare UIs**, appendable HTML, and other agent-produced human-readable
HTML. Do not gate HSW behind a per-report flag. Exceptions remain
README/product entry (`writing-direction`) and filename-only surfaces (**hon**).

## Confirm HSW automation (0.5.7+ — every CGM adopter)

0.5.6 documented MUST / `human_facing_default` but agents could pin CGM and
still never load the skill. **0.5.7** forces automation with:

1. Always-on paste block: `acs_prompt_inject.system_block` in
   [`writing-routing.json`](writing-routing.json) (`always_on: true`,
   `opt_in_forbidden: true`, `audience: every_cgm_adopter`).
2. Fail-closed contract validate (needles for those keys).
3. Optional HTML tell scan (conservative denylist — not full NLP quality CI).

### Steps (any adopter; ACS example)

```bash
# 1) Pin CGM 0.5.7+ (version + commit SHA). Do not follow moving main.

# 2) Writing contract + always-on inject keys
python scripts/validate_content_system.py --root /path/to/content-generation-modules --mode writing

# 3) Confirm HSW always-on contract (fail closed if inject incomplete)
python scripts/verify_hsw_applied.py --root /path/to/content-generation-modules

# 4) Before publishing human-facing HTML / compare Pages, scan the artifact
python scripts/verify_hsw_applied.py --root /path/to/content-generation-modules \
  --mode acs-html --html /path/to/compare.html
```

| Result | Meaning |
| --- | --- |
| `HSW_VERIFY ... status=OK` + `VALID` | Always-on inject + `human_facing_default` present; if `--html` given, no denylist jargon/tool-dump hits. |
| Non-zero + `status=FAIL` | Hotload/inject contract incomplete, **or** given HTML still has known AI-jargon / tool-dump tells. |

Honest limit: pass does **not** prove the prose "sounds human." It proves the
automation gates ran. Soft still means no full NLP CI on every prose file.

### What every adopter must still wire

1. At **agent boot**, paste `acs_prompt_inject.system_block` into the system
   prompt (not per-report).
2. Run `verify_hsw_applied.py` (contract mode on install; `--html` before
   publishing compare / human-facing HTML).
3. Keep the eight-module pin on **0.5.9+**.
4. Run `verify_adopter_content.py` (or `--check-adopter-docs`) in CI to enforce
   README freshness, asset references, and HON/HSW doc compliance.
5. Run `validate_content_system.py --check-adopter-readme` (0.5.9+) to enforce
   the adopter README structure: PNG hero (SVG hero banned), problem narrative,
   grounded status/evidence table, and a boundaries section.

## Confirm adopter content freshness and asset references (0.5.8+ — every CGM adopter)

0.5.7 verified the presence and JSON validity of `.content-system` adapters and disk files,
but did not deterministically enforce that `README.md` was updated beyond a bootstrap stub
or that registered visual assets were embedded in docs (CGM #33).

**0.5.8** adds `scripts/verify_adopter_content.py` and `--check-adopter-docs`:

1. Fails CI if `README.md` matches known bootstrap stubs (e.g. `Product implementation starts with... after that bootstrap is accepted`, planning placeholders, or unfilled template placeholders).
2. Fails CI if visual assets declared in `asset-manifest.json` are never referenced in `README.md` or adopter docs.
3. Enforces basic HON checks (rejects opaque hex hashes and robot key=value basenames on human-facing files and media).
4. Enforces HSW checks across human-facing docs (rejects tool-dump/agent-internals and high-signal AI tells in markdown prose outside code blocks).

### Commands

```bash
# Standalone adopter check
python scripts/verify_adopter_content.py \
  --adapter /path/to/adopter/.content-system \
  --project-root /path/to/adopter

# Integrated with validate_content_system
python scripts/validate_content_system.py \
  --root /path/to/content-generation-modules \
  --adapter /path/to/adopter/.content-system \
  --project-root /path/to/adopter \
  --check-adopter-docs
```

## Adopter README structure + PNG hero (0.5.9+ — every CGM adopter)

0.5.8 checked freshness and asset references, but a registered SVG sketch could
still be embedded as the public README hero (CGM #34), and coding agents such as
Google Antigravity produced shallow adopter READMEs (CGM #35). **0.5.9** adds a
structure gate and a hero-format gate:

1. Rejects an SVG (or any non-PNG) asset registered with `role: hero` in
   `asset-manifest.json`.
2. Rejects a non-PNG image used as the adopter README hero banner.
3. Asserts the README has a problem narrative section, a grounded
   status/evidence table, and a distinct boundaries section.

```bash
# Adopter README structure gate (includes freshness + asset references)
python scripts/validate_content_system.py \
  --root /path/to/content-generation-modules \
  --adapter /path/to/adopter/.content-system \
  --project-root /path/to/adopter \
  --check-adopter-readme
```

Google Antigravity and other coding agents must additionally follow
[`ANTIGRAVITY_INTEGRATION.md`](ANTIGRAVITY_INTEGRATION.md) so they load the full
writing playbook (`writing-direction`, **hsw**, **hon**) and generate the
multi-image narrative, not a single SVG sketch.

## Adopter merge gates — validation is not merge readiness (0.5.11+ — every CGM adopter)

A green CGM validator run and a merged pull request are separate outcomes
(CGM #18). `validate_content_system.py` checks the helper contract and the
adapter; it never approves, pushes, or merges an adopter's pull request, and a
pass does not trigger or guarantee a merge. Four gates:

1. **CGM contract validation** — this repository's helper + adapter checks.
2. **Target-side checks on the current head** — the adopter's own factual,
   link, test, and structure checks on the exact commit under review.
3. **Branch-protection readiness** — required checks, up-to-date status, and
   stale source claims; all target-repository settings.
4. **Merge authorization** — a required human approval, or auto-merge armed.

When the adopter's own policy permits merging without a separate reviewer, run
the pinned CGM validator and the target checks as required CI checks and enable
GitHub auto-merge; otherwise keep the repository's review rule. Full guide:
[`ADOPTER_MERGE_GATES.md`](ADOPTER_MERGE_GATES.md).

## Output filenames (0.5.5+)

ACS prompt inject must mention **output filenames**, asset-manifest paths, and
**per-feature filename legends**, not titles only. After verify:

- Generated artifact filenames / asset-manifest paths / committed media basenames
  / filename legends → `human-output-naming` (**hon**) (`required_load: true`)
- Call `scripts/human_filename.build_basename` (speakable by default; optional
  `style="safe_twin"`) before writing new media
- Omit default pitch/speed from the basename (`Song Food – up 8.mp3`, not robot
  `song-food_pitch-plus-8st_speed-0pct.mp3`)
- Keep a per-feature legend under `docs/filename-legends/` (helper) or
  `.content-system/filename-legends/` (adapter): glossary + associated paths
- Do not emit classic `name-pN-<6hex>.ext` or robot key=value stems on helper
  pins ≥ 0.5.5
- Hash may remain a separate asset-manifest field

Full contract: [`HUMAN_OUTPUT_NAMING.md`](HUMAN_OUTPUT_NAMING.md). Soft router
row: [`WRITING_ROUTING.md`](WRITING_ROUTING.md).

## Soft router (MUST load after pin)

After verify passes, agents **MUST load** modules per
[`docs/WRITING_ROUTING.md`](WRITING_ROUTING.md) /
[`docs/writing-routing.json`](writing-routing.json):

- README / product entry → `writing-direction` (`required_load: true`)
- PR titles/bodies, issue titles/bodies, issue-log titles, **commit messages /
  commit subjects**, non-README docs, changelog prose, posts/blogs/social/
  general prose/papers, **HTML reports / compare HTML / compare UIs / appendable
  HTML / agent human-readable HTML** → `human-sounding-writing` (**hsw**)
  (`required_load: true`, `default_on: true`)
- Generated artifact filenames, asset-manifest paths, committed media basenames, filename legends
  → `human-output-naming` (**hon**) (`required_load: true`; speakable + per-feature legend)

**Human-facing default (0.5.6+):** HSW is ON for every human-facing task/output
unless the surface is README/product entry or filename-only. No per-report
opt-in. Soft = no NLP grader; still APPLY / default_on for agents.

## ACS prompt inject (required for application)

CGM does not rewrite agent prompts inside ACS. After `hotload_check` /
`CGM_VERIFY` succeeds, ACS **must inject** the writing-load contract into the
agent system or task prompt so adopters actually apply the modules.

**Source file:** `docs/writing-routing.json`  
**Fields to read:** `always_on`, `opt_in_forbidden`, `system_block`, `surfaces`,
`application`, `human_facing_default`, `routes`, `apply_checklist`
(paste **`system_block`** — that is the always-on boot inject for every adopter)  
**Canonical instruction text** (also in `acs_prompt_inject.instruction`):

> Inject into the agent system or task prompt: HSW (human-sounding-writing) is
> ON by default for EVERY human-facing task/output. For every route with
> `required_load` true, you MUST load `modules/<load>/SKILL.md` before writing
> any listed surface. README and product entry pages → `writing-direction`.
> Pull request titles/bodies, issue titles/bodies, issue-log titles, commit
> messages, commit subjects, non-README docs, changelog prose,
> posts/blogs/social/general prose, papers/data writeups, HTML reports, compare
> HTML, compare UIs, appendable HTML reports, and other agent-produced
> human-readable HTML → `human-sounding-writing` (hsw). Do NOT treat HSW as
> optional, per-report, or only-when-writing-posts. Soft enforcement means no
> NLP CI grade of prose; the contract language is MUST/APPLY/default_on, not
> prefer. Follow `apply_checklist` and `human_facing_default` in this file.

Suggested ACS wiring:

1. Subprocess `--mode writing` (fail install if non-zero).
2. Parse `docs/writing-routing.json` from the pinned CGM checkout.
3. Append `acs_prompt_inject.instruction` (or a rendered form of
   `routes` + `apply_checklist`) to the hotloaded agent prompt / HOTLOAD pack
   instructions so every writing surface — including commit messages — carries
   a mandatory module load.

## Adopter follow-up (ACS and every other pin)

1. Re-pin from CGM **0.5.6** to **0.5.7+** (eight modules; always-on HSW inject).
2. Call `--mode writing` and `scripts/verify_hsw_applied.py` from install /
   hotload checks (fail install if non-zero).
3. Paste `acs_prompt_inject.system_block` into the agent system prompt at
   **boot** (every adopter — not ACS-only, not per-report).
4. Before publishing compare / human-facing HTML, run
   `verify_hsw_applied.py --mode acs-html --html <path>`.
5. Keep adapter `system-version.json` on the full eight-module **0.5.7+** set.
