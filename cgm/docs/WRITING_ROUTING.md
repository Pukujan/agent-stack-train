# Writing routing

Soft router for choosing a writing module. **Soft** means CGM does not
NLP-grade prose in CI. It does **not** mean optional: agents **MUST load** the
routed module before writing the listed surfaces (APPLY / `required_load`).

Machine-readable twin: [`docs/writing-routing.json`](writing-routing.json)
(`content-generation.writing-routing.v1`). ACS / hotload verify entrypoint:
`python scripts/validate_content_system.py --root <cgm-checkout> --mode writing`
(see [`docs/ACS_VERIFY.md`](ACS_VERIFY.md)). ACS prompt inject path is
documented in `acs_prompt_inject` inside the JSON contract.

| Situation | Load | Notes |
| --- | --- | --- |
| README / product entry | `writing-direction` (+ `brand-foundation` / `content-context` as needed) | **MUST load.** Keep scan-first selective bold and the README scanability contract. |
| Pull request titles and bodies | `human-sounding-writing` (short name **hsw** / HSW) | **MUST load.** Human-facing GitHub prose; plain titles, reader-first bodies. |
| Issue titles, issue bodies, issue-log titles | `human-sounding-writing` (short name **hsw** / HSW) | **MUST load.** Same voice rules for tracker prose agents publish. |
| Commit messages and commit subjects | `human-sounding-writing` (short name **hsw** / HSW) | **MUST load.** Plain human subject; scrub AI-tell phrasing. In scope as of 0.5.3. |
| Non-README docs and changelog prose | `human-sounding-writing` (short name **hsw** / HSW) | **MUST load.** Guides, ops notes, CHANGELOG narrative — not the root README. |
| Posts / blogs / social / general agent prose | `human-sounding-writing` (short name **hsw** / HSW) | **MUST load.** Human voice, AI-tell scrub, restrained bold. Agents asked for "hsw" should load this module. |
| Papers / data writeups | `human-sounding-writing` (short name **hsw** / HSW) (+ chart rules in that module and guide) | **MUST load.** Same voice rules; apply takeaway titles and plain-chart guidance. |

## Apply checklist (agents)

1. Identify the writing surface (README, PR, issue, commit message/subject, doc, etc.).
2. Look up the surface in the table above or in `docs/writing-routing.json` `routes[].surfaces`.
3. **MUST** load `modules/<load>/SKILL.md` for that route before drafting (`required_load: true`).
4. Apply the module rules to the draft.
5. Do not skip load because the surface is short or "just a commit message."

## Short name

**hsw** (also **HSW**) is the official short name for `human-sounding-writing`.
Agents asked for "hsw" should load [`modules/human-sounding-writing/SKILL.md`](../modules/human-sounding-writing/SKILL.md).
The canonical module id and folder name remain `human-sounding-writing`.

## Conflict to avoid

`writing-direction` uses selective bold anchors so a heading-and-bold scan
tells a second story. `human-sounding-writing` treats heavy bold and bold
inline labels as AI tells. **Do not merge those policies.** Route by situation
instead.

If the task is a README or product entry, do not apply `human-sounding-writing`
bold restraints. If the task is a PR, issue, issue-log title, commit
message/subject, non-README doc, changelog prose, post, blog, social update,
general prose, paper, or data writeup, **MUST** use `human-sounding-writing`
over README scan/bold rules.

## ACS inject

After verify passes, ACS should inject the MUST-load contract into agent
prompts using `acs_prompt_inject` in [`writing-routing.json`](writing-routing.json)
(fields: `application`, `routes`, `apply_checklist`). See
[`ACS_VERIFY.md`](ACS_VERIFY.md).

## References

- [`modules/writing-direction/SKILL.md`](../modules/writing-direction/SKILL.md)
- [`modules/human-sounding-writing/SKILL.md`](../modules/human-sounding-writing/SKILL.md)
- [`docs/HUMAN_SOUNDING_WRITING.md`](HUMAN_SOUNDING_WRITING.md)
- [`docs/human-sounding-rules.json`](human-sounding-rules.json)
- [`docs/writing-routing.json`](writing-routing.json)
- [`docs/ACS_VERIFY.md`](ACS_VERIFY.md)
