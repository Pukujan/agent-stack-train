# Migrating to 0.3.0

Version `0.3.0` adds a durable scan-first writing contract and a brand direction for human-facing content and visuals.

## What changed

- `docs/CONTENT_RESEARCH.md` records the UX and accessibility research behind selective bolding, descriptive headings, short sections, and objective marketing language.
- `docs/BRAND_DIRECTION.md` defines the Story Loop direction and explains how Harness on Steroids, Eval Lab, and the Peeps reference informed the method without becoming a copy.
- `modules/writing-direction/SKILL.md`, the README playbook, and the README template now require a heading-and-bold scan test.
- `templates/readme-contract.json` records the scanability policy and requires the durable research and brand references.
- the helper README and committed marketing assets now use the bright editorial content-UX identity.

## Migration steps

1. Update the target adapter's `helper_version` to `0.3.0` and set `helper_commit` to the commit you reviewed.
2. Read `docs/CONTENT_RESEARCH.md` and add the scanability rules to the target repository's content instructions.
3. Review the target repository's brand and visual adapter against `docs/BRAND_DIRECTION.md`; preserve its own product identity when it has one.
4. Update README sections so the headings and bold phrases form a useful second story.
5. Replace any hero or supporting image that does not have a role, alt text, prompt record, crop rule, and review decision.
6. Run the validator and complete the twenty-second scan test before opening a PR.

Existing `0.2.x` adapters remain valid until they migrate. New human-facing work should use `0.3.0`.
