# Writing routing

Soft router for choosing a writing module. **Soft** means CGM does not
NLP-grade prose in CI. It does **not** mean optional: agents **MUST load** the
routed module before writing the listed surfaces (APPLY / `required_load`).
**HSW is ON by default** for every human-facing deliverable except README /
product entry (`writing-direction`) and filename-only surfaces
(`human-output-naming`). No per-report or per-HTML opt-in.

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
| HTML reports / compare HTML / compare UIs / appendable HTML / agent human-readable HTML | `human-sounding-writing` (short name **hsw** / HSW) | **MUST load (default ON).** Visible prose and labels in human-facing HTML — including ACS compare reports. No per-report opt-in. Basenames still use **hon**. |
| Generated artifact filenames / asset-manifest paths / committed media basenames / filename legends | `human-output-naming` (short name **hon** / HON) | **MUST load.** Speakable basenames (omit defaults) via `scripts/human_filename`; optional safe twin; per-feature legend required. Never opaque `p0`/hex or robot key=value stems. See [`docs/HUMAN_OUTPUT_NAMING.md`](HUMAN_OUTPUT_NAMING.md). |


## Human-facing default (0.5.6+)

`human_facing_default` in [`writing-routing.json`](writing-routing.json) sets
**hsw** as the default load for every human-facing deliverable. Exceptions:

- README / product entry → `writing-direction`
- Generated artifact filenames / legends → `human-output-naming` (**hon**) for
  *basenames*; visible prose inside HTML still uses **hsw**

ACS and sibling adapters must not treat HSW as optional or per-report.

## Filename surfaces (0.5.5+)

Generated artifact filenames, asset-manifest paths, committed media basenames,
and **per-feature filename legends** **MUST** load `human-output-naming`
(**hon**). Use HSW voice for *what* you call dimensions; the filesystem shape
and legend companion are owned by **hon** and
[`scripts/human_filename.py`](../scripts/human_filename.py).

Before / after: `song_food-p0-00e86d.mp3` (and the rejected robot draft
`song-food_pitch-plus-8st_speed-0pct.mp3`) → `Song Food – up 8.mp3`. Optional
safe twin: `song-food--up-8.mp3`. Full contract:
[`docs/HUMAN_OUTPUT_NAMING.md`](HUMAN_OUTPUT_NAMING.md) /
[`docs/human-output-naming.json`](human-output-naming.json). Sample legend:
[`docs/filename-legends/`](filename-legends/).

## Apply checklist (agents)

1. Identify the writing surface (README, PR, issue, commit message/subject, doc, HTML report, compare UI, etc.).
2. Look up the surface in the table above or in `docs/writing-routing.json` `routes[].surfaces`. If it is human-facing and not README/product entry and not filename-only, default to **hsw** (`human_facing_default`).
3. **MUST** load `modules/<load>/SKILL.md` for that route before drafting (`required_load: true`).
4. Apply the module rules to the draft.
5. Do not skip load because the surface is short or "just a commit message."
6. If naming a generated artifact, asset-manifest path, committed media file, or filename legend, MUST load `human-output-naming` (**hon**), call `scripts/human_filename` (speakable by default), and keep a per-feature legend.
7. Never treat HSW as optional, soft-skip, or per-report opt-in for HTML reports, compare UIs, or other human-facing HTML.

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
general prose, paper, data writeup, HTML report, compare HTML/UI, or other
human-facing HTML, **MUST** use `human-sounding-writing` over README scan/bold
rules. Default is ON — do not wait for a per-report flag.

## ACS inject

After verify passes, ACS should inject the MUST-load contract into agent
prompts using `acs_prompt_inject` in [`writing-routing.json`](writing-routing.json)
(fields: `application`, `human_facing_default`, `routes`, `apply_checklist`). The
inject text must say HSW is **default ON for every human-facing task/output**,
including **HTML reports / compare HTML**, and must mention **output filenames** /
asset-manifest paths / filename legends (hon, speakable), not titles only. See
[`ACS_VERIFY.md`](ACS_VERIFY.md).

## References

- [`modules/writing-direction/SKILL.md`](../modules/writing-direction/SKILL.md)
- [`modules/human-sounding-writing/SKILL.md`](../modules/human-sounding-writing/SKILL.md)
- [`docs/HUMAN_SOUNDING_WRITING.md`](HUMAN_SOUNDING_WRITING.md)
- [`docs/human-sounding-rules.json`](human-sounding-rules.json)
- [`docs/writing-routing.json`](writing-routing.json)
- [`docs/ACS_VERIFY.md`](ACS_VERIFY.md)
- [`modules/human-output-naming/SKILL.md`](../modules/human-output-naming/SKILL.md)
- [`docs/HUMAN_OUTPUT_NAMING.md`](HUMAN_OUTPUT_NAMING.md)
- [`docs/human-output-naming.json`](human-output-naming.json)
