# Writing routing

Soft router for choosing a writing module. CGM does not enforce a hard router;
agents still “load relevant modules.” Use this table so bold and voice rules do
not fight each other.

Machine-readable twin: [`docs/writing-routing.json`](writing-routing.json)
(`content-generation.writing-routing.v1`). ACS / hotload verify entrypoint:
`python scripts/validate_content_system.py --root <cgm-checkout> --mode writing`
(see [`docs/ACS_VERIFY.md`](ACS_VERIFY.md)).

| Situation | Load | Notes |
| --- | --- | --- |
| README / product entry | `writing-direction` (+ `brand-foundation` / `content-context` as needed) | Keep scan-first selective bold and the README scanability contract. |
| Pull request titles and bodies | `human-sounding-writing` (short name **hsw** / HSW) | Human-facing GitHub prose; plain titles, reader-first bodies. |
| Issue titles, issue bodies, issue-log titles | `human-sounding-writing` (short name **hsw** / HSW) | Same voice rules for tracker prose agents publish. |
| Non-README docs and changelog prose | `human-sounding-writing` (short name **hsw** / HSW) | Guides, ops notes, CHANGELOG narrative — not the root README. |
| Posts / blogs / social / general agent prose | `human-sounding-writing` (short name **hsw** / HSW) | Human voice, AI-tell scrub, restrained bold. Agents asked for "hsw" should load this module. |
| Papers / data writeups | `human-sounding-writing` (short name **hsw** / HSW) (+ chart rules in that module and guide) | Same voice rules; apply takeaway titles and plain-chart guidance. |

Commit messages are **not** in this soft router (not CI-enforced). Prefer a plain
human subject when you write one.

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
bold restraints. If the task is a PR, issue, issue-log title, non-README doc,
changelog prose, post, blog, social update, general prose, paper, or data
writeup, prefer `human-sounding-writing` over README scan/bold rules.

## References

- [`modules/writing-direction/SKILL.md`](../modules/writing-direction/SKILL.md)
- [`modules/human-sounding-writing/SKILL.md`](../modules/human-sounding-writing/SKILL.md)
- [`docs/HUMAN_SOUNDING_WRITING.md`](HUMAN_SOUNDING_WRITING.md)
- [`docs/human-sounding-rules.json`](human-sounding-rules.json)
- [`docs/writing-routing.json`](writing-routing.json)
- [`docs/ACS_VERIFY.md`](ACS_VERIFY.md)
