# Writing routing

Soft router for choosing a writing module. CGM does not enforce a hard router;
agents still “load relevant modules.” Use this table so bold and voice rules do
not fight each other.

| Situation | Load | Notes |
| --- | --- | --- |
| README / product entry | `writing-direction` (+ `brand-foundation` / `content-context` as needed) | Keep scan-first selective bold and the README scanability contract. |
| Posts / blogs / social / general agent prose | `human-sounding-writing` | Human voice, AI-tell scrub, restrained bold. |
| Papers / data writeups | `human-sounding-writing` (+ chart rules in that module and guide) | Same voice rules; apply takeaway titles and plain-chart guidance. |

## Conflict to avoid

`writing-direction` uses selective bold anchors so a heading-and-bold scan
tells a second story. `human-sounding-writing` treats heavy bold and bold
inline labels as AI tells. **Do not merge those policies.** Route by situation
instead.

If the task is a README, do not apply `human-sounding-writing` bold restraints.
If the task is a post, blog, social update, general prose, paper, or data
writeup, prefer `human-sounding-writing` over README scan/bold rules.

## References

- [`modules/writing-direction/SKILL.md`](../modules/writing-direction/SKILL.md)
- [`modules/human-sounding-writing/SKILL.md`](../modules/human-sounding-writing/SKILL.md)
- [`docs/HUMAN_SOUNDING_WRITING.md`](HUMAN_SOUNDING_WRITING.md)
- [`docs/human-sounding-rules.json`](human-sounding-rules.json)
