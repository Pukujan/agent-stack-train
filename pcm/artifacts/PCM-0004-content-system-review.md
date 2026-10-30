# PCM-0004 content-system review index

This file is the durable map for a fresh Luna/Codex session. The canonical task and checkpoint remain the source of truth; these links are review conveniences.

## Helper repository

- Repository: https://github.com/Pukujan/content-generation-modules
- Release: `v0.1.1`
- Commit: `3e89100fed61da19bd3d3f17ad336f189b576c38`
- Contract: six modules covering brand, context, writing, visual direction, image generation, and HTML demos;
- Validation: `python scripts/validate_content_system.py --root .` -> valid;
- Tests: `python -m unittest discover -s tests -v` -> 3 tests passed.

## Eval Lab preview

- PR: https://github.com/Pukujan/Eval-lab/pull/30
- Branch: `task/TASK-0014-content-system-adoption`
- Head commit: `f7498a080cd30fc4c54812bad11a58f47ec8f43f`
- Preview Markdown: https://github.com/Pukujan/Eval-lab/blob/task/TASK-0014-content-system-adoption/docs/content-system-preview.md
- Preview HTML source: https://github.com/Pukujan/Eval-lab/blob/task/TASK-0014-content-system-adoption/docs/content-system-preview.html
- Adapter: https://github.com/Pukujan/Eval-lab/tree/task/TASK-0014-content-system-adoption/.content-system
- CI: run `35546202014` passed Python 3.11 and 3.12.
- Canonical README: intentionally unchanged.

## Local rendered packet

Generated from `docs/content-system-preview.html` with Playwright:

- `D:\\claude\\eval-lab-TASK-0014\\review-output\\desktop-1440.png`
- `D:\\claude\\eval-lab-TASK-0014\\review-output\\tablet-900.png`
- `D:\\claude\\eval-lab-TASK-0014\\review-output\\mobile-390.png`
- `D:\\claude\\eval-lab-TASK-0014\\review-output\\content-system-preview.pdf`

Render evidence:

- no horizontal overflow at 1440px, 900px, or 390px;
- all four images loaded at each viewport;
- PDF has four A4 pages and was rendered to page PNGs for visual inspection;
- accepted visual direction: one hero, one wide problem asset, one square system asset, one portrait evidence asset, and supporting SVG icons.

## Why the first CI run failed

The first preview branch was created from a stale local `origin/main` pointer at `345e731`, which did not contain the already-merged `PYTHONPATH=.:src` workflow fix. GitHub therefore failed during test collection with `ModuleNotFoundError: No module named 'scripts'`. Merging current Eval Lab `main` (`82047d9`) corrected the branch; the subsequent run passed.

## Next decision

Review the rendered packet and decide whether to:

1. promote the preview story into Eval Lab's canonical README;
2. keep the adapter as a reusable preview-only contract;
3. apply the pinned helper to another repository.

## Continuity-repository validation note

`PYTHONPATH=src python -S -m continuity validate --root .` is valid after keeping PCM-0004's machine status as `active`; the human review state is recorded separately. The existing `test_minimal_end_to_end_dogfood_flow` has a Windows-only separator mismatch (`checkpoints\\CURRENT.md` emitted versus `checkpoints/CURRENT.md` asserted). This was observed during PCM-0004 validation and is intentionally not changed here because it belongs to continuity protocol maintenance, not the content-system helper.
