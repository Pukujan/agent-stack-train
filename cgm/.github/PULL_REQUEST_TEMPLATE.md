## Tracking issue

Refs #<open issue with written acceptance criteria>

## Reader problem and outcome

What human or developer problem changes, and what will the reader be able to understand or do?

## Evidence and boundaries

- Evidence reviewed at exact revisions:
- What those sources support:
- What they do not establish:
- Record time and valid-time bounds, if this change makes time-sensitive claims:

## Brand and image contract

- [ ] Target-owned brand and market framing are preserved.
- [ ] Existing image-generation, exact-copy, raster, prompt, crop, alt-text, and review requirements are preserved or their change is explicitly accepted by the tracking issue.
- [ ] Generated assets have a role, prompt record, provenance, and human review where applicable.

## Acceptance and verification

- [ ] Tracking issue acceptance criteria are met.
- [ ] `python scripts/validate_content_system.py --root .` passes.
- [ ] `python -m unittest discover -s tests -v` passes.
- [ ] Reader, editorial, and visual checks are summarized.
- Hidden holdout status: `not_run` / `passed` / `inconclusive` (include evaluator record when run).
