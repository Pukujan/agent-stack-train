# Migrating from 0.1.x to 0.2.0

Version `0.2.0` keeps the six existing modules and adapter file shapes, but it adds a stricter human-facing README contract. Existing target repositories pinned to `0.1.2` do not change automatically.

## What changed

- README work now has required human-facing sections and ordering guidance.
- README templates include visual placement, image generation/use, prior work, and next-action sections.
- Image records include placement, alt text, crop behavior, rejection conditions, and review decisions.
- The helper repository validator checks its own README for the contract, guides, and local visual assets.
- The README playbook and image guide are part of the helper contract.

## Migrate a target repository

1. Update `.content-system/system-version.json` to the `v0.2.0` tag and exact commit.
2. Read [`docs/README_PLAYBOOK.md`](README_PLAYBOOK.md), [`docs/IMAGE_GUIDE.md`](IMAGE_GUIDE.md), and [`templates/readme-contract.json`](../templates/readme-contract.json).
3. Add or update the target repository's `AGENTS.md` pointer so future agents load those files before human-facing work.
4. Compare the current README with [`templates/README.template.md`](../templates/README.template.md). Add the human situation, promise, mechanism, evidence, boundaries, image use, prior work, and next action in that order.
5. Review existing accepted visuals before generating replacements. Keep the target repository's visual identity and facts local to its adapter.
6. Update `asset-manifest.json` and the linked image prompt record for every accepted raster asset.
7. Run the helper and target adapter validators, render the README or HTML preview at the intended widths, and complete human review before merging.

## Existing 0.1.2 adopters

The first adopters—[Eval Lab](https://github.com/Pukujan/Eval-lab), [Harness on steroids](https://github.com/Pukujan/harness-on-steroids), [Custom Extensions](https://github.com/Pukujan/custom-extensions), and [Hades Product](https://github.com/Pukujan/hades-product)—remain valid at their pinned `0.1.2` commit. Their prior prompt records, adapters, images, and review artifacts are the migration references; update them only when the target repository deliberately adopts `0.2.0`.
