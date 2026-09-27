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
3. Route writing work with [`WRITING_ROUTING.md`](WRITING_ROUTING.md):
   - README / product entry → `writing-direction` (keep scan/bold).
   - Posts / blogs / social / general prose → `human-sounding-writing`.
   - Papers / data writeups → `human-sounding-writing` (+ chart rules).
4. Run `python scripts/validate_content_system.py --root .` (and the target
   adapter check if you use one).

## What stays the same

- README scanability_contract / selective bold anchors are unchanged.
- `writing-direction` remains the README and product-entry module.
- Claim-evidence v2 requirements from `0.4.x` remain in force for targets that
  pin `0.5.0`.
