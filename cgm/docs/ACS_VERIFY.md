# ACS / hotload CGM verify entrypoint

**Audience:** Agent Custom Setup (`Pukujan/agent-custom-setup`) multi-agent-hotload
and adopters (for example Study-os) that must confirm full CGM + writing modules
are present before treating hotload install as complete.

**Enforcement:** soft for prose style (no NLP CI grade). The contract language
for agents is still **MUST load / APPLY** via `required_load` — not "prefer."
This entrypoint checks **presence** of the helper contract, writing modules,
and soft router (including commit surfaces + inject metadata) — not whether a
PR body or commit subject "sounds human."

## What `validate_content_system.py` already does

| Call | Checks |
| --- | --- |
| `--root <cgm>` (default / `--mode helper`) | Full helper: `system-version.json`, all seven `EXPECTED_MODULES` (including `writing-direction` and `human-sounding-writing`), schemas, templates, helper docs (including `docs/WRITING_ROUTING.md` and `docs/writing-routing.json`), README contract. |
| `--root <cgm> --mode writing` | **ACS hotload entrypoint:** both writing modules’ `SKILL.md`, soft router markdown + JSON contract (`content-generation.writing-routing.v1`), commit surfaces routed to hsw, `required_load` / `apply_checklist` / `acs_prompt_inject`, and that `system-version.json` lists both writing modules. Prints a stable `CGM_VERIFY` line. |
| `--root <cgm> --adapter <project>/.content-system --project-root <project>` | Full helper **plus** target adapter: adapter `modules` must equal the full seven-module helper set (so HSW cannot be omitted on a 0.5.x pin). |

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
```

On success, `--mode writing` prints a line ACS can parse, for example:

```text
CGM_VERIFY mode=writing status=OK writing_direction=present human_sounding_writing=present writing_router=present
VALID: content-generation-modules writing contract
```

Non-zero exit + `CGM_VERIFY ... status=FAIL` means the pin is incomplete.

## Soft router (MUST load after pin)

After verify passes, agents **MUST load** modules per
[`docs/WRITING_ROUTING.md`](WRITING_ROUTING.md) /
[`docs/writing-routing.json`](writing-routing.json):

- README / product entry → `writing-direction` (`required_load: true`)
- PR titles/bodies, issue titles/bodies, issue-log titles, **commit messages /
  commit subjects**, non-README docs, changelog prose, posts/blogs/social/
  general prose/papers → `human-sounding-writing` (**hsw**) (`required_load: true`)

No prose-style CI gate is implied. Soft = no NLP grader; still APPLY for agents.

## ACS prompt inject (required for application)

CGM does not rewrite agent prompts inside ACS. After `hotload_check` /
`CGM_VERIFY` succeeds, ACS **must inject** the writing-load contract into the
agent system or task prompt so adopters actually apply the modules.

**Source file:** `docs/writing-routing.json`  
**Fields to read:** `application`, `routes` (each with `surfaces`, `load`,
`required_load`), `apply_checklist`  
**Canonical instruction text** (also in `acs_prompt_inject.instruction`):

> Inject into the agent system or task prompt: For every route with
> `required_load` true, you MUST load `modules/<load>/SKILL.md` before writing
> any listed surface. README and product entry pages → `writing-direction`.
> Pull request titles/bodies, issue titles/bodies, issue-log titles, commit
> messages, commit subjects, non-README docs, changelog prose,
> posts/blogs/social/general prose, and papers/data writeups →
> `human-sounding-writing` (hsw). Soft enforcement means no NLP CI grade of
> prose; the contract language is MUST/APPLY, not prefer. Follow
> `apply_checklist` in this file.

Suggested ACS wiring:

1. Subprocess `--mode writing` (fail install if non-zero).
2. Parse `docs/writing-routing.json` from the pinned CGM checkout.
3. Append `acs_prompt_inject.instruction` (or a rendered form of
   `routes` + `apply_checklist`) to the hotloaded agent prompt / HOTLOAD pack
   instructions so every writing surface — including commit messages — carries
   a mandatory module load.

## ACS follow-up (owning repo)

1. Re-pin hotload docs from CGM **0.5.3** to this release (**0.5.4+**)
   after merge.
2. Call the entrypoint above from `hotload_check.py` (subprocess; fail install
   if non-zero).
3. Inject `acs_prompt_inject` into agent prompts (see above).
4. Bump adopter `.content-system/system-version.json` to the full seven-module
   0.5.4+ set (ACS main was observed still on 0.4.0 without HSW).
