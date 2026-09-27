# ACS / hotload CGM verify entrypoint

**Audience:** Agent Custom Setup (`Pukujan/agent-custom-setup`) multi-agent-hotload
and adopters (for example Study-os) that must confirm full CGM + writing modules
are present before treating hotload install as complete.

**Enforcement:** soft for prose style. This entrypoint checks **presence** of the
helper contract, writing modules, and soft router — not whether a PR body
“sounds human.”

## What `validate_content_system.py` already does

| Call | Checks |
| --- | --- |
| `--root <cgm>` (default / `--mode helper`) | Full helper: `system-version.json`, all seven `EXPECTED_MODULES` (including `writing-direction` and `human-sounding-writing`), schemas, templates, helper docs (including `docs/WRITING_ROUTING.md` and `docs/writing-routing.json`), README contract. |
| `--root <cgm> --mode writing` | **ACS hotload entrypoint:** both writing modules’ `SKILL.md`, soft router markdown + JSON contract (`content-generation.writing-routing.v1`), and that `system-version.json` lists both writing modules. Prints a stable `CGM_VERIFY` line. |
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

## Soft router (agent discipline after pin)

After verify passes, agents still load modules per
[`docs/WRITING_ROUTING.md`](WRITING_ROUTING.md) /
[`docs/writing-routing.json`](writing-routing.json):

- README / product entry → `writing-direction`
- PR titles/bodies, issue titles/bodies, issue-log titles, non-README docs,
  changelog prose, posts/blogs/social/general prose/papers → `human-sounding-writing` (**hsw**)

Commit messages stay outside the soft router. No prose-style CI gate is implied.

## ACS follow-up (owning repo)

1. Re-pin hotload docs from CGM **0.5.0 / 0.5.1** to this release (**0.5.2+**)
   after merge.
2. Call the entrypoint above from `hotload_check.py` (subprocess; fail install
   if non-zero).
3. Bump adopter `.content-system/system-version.json` to the full seven-module
   0.5.2+ set (ACS main was observed still on 0.4.0 without HSW).
