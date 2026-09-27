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
3. Route writing work with [`WRITING_ROUTING.md`](WRITING_ROUTING.md) /
   [`writing-routing.json`](writing-routing.json):
   - README / product entry → `writing-direction` (keep scan/bold).
   - PR / issue titles and bodies, issue-log titles, non-README docs,
     changelog prose → `human-sounding-writing`.
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
- Prefer full helper (and helper+adapter) for install completeness; pin **0.5.2+**.

