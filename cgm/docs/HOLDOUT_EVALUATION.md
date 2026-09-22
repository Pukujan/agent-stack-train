# Holdout evaluation for repeatable human-facing output

The public validator proves that a target adapter contains the expected files and records. It cannot prove that an agent will make the same judgment on a repository it has never seen. That question needs a holdout: an unseen target, an unseen failure pattern, and an evaluation record that the agent cannot optimize against by reading the fixture.

## What the holdout should measure

Run the same content-generation task against target repositories that are excluded from the public examples. The task should ask for a story-first README and its narrative visuals using the target adapter. The evaluator should score two layers:

- **Contract layer:** the README leads with the human situation; headings and bold anchors pass the scan test; narrative assets are PNG, JPEG, or WebP; each has exact title and subtitle fields, a prompt record, provider provenance, a review decision, and a matching SHA-256 hash; the README does not substitute hand-authored SVGs for requested narrative images.
- **Quality layer:** an independent reviewer or vision-capable evaluator checks that the image explains the target repository, keeps the required visual identity, uses readable copy, survives wide and narrow crops, and avoids generic cyberpunk, dashboard, route-signal, or decorative imagery that does not answer the reader’s question.

The contract layer is deterministic. The quality layer must remain independent because a file can satisfy metadata checks while still being the wrong visual.

## Keep the real holdout private

Do not commit the expected holdout fixtures, answer key, hidden rejection examples, or scoring prompts to this public repository. Store them in a private evaluator repository or private CI environment. The public helper can be pinned by commit; the holdout’s target adapters, expected role decisions, and visual review rubric stay outside the agent’s working tree.

A useful private fixture includes:

1. a target whose visual contract requires a human and friendly robot in an anime-inspired editorial scene;
2. a target whose story requires a different palette and subject relationship, proving that the agent reads the adapter instead of copying the helper’s characters;
3. a deliberately misleading legacy adapter that mentions SVG diagrams but also declares narrative hero and supporting roles;
4. a fixture with a stale image hash, a missing prompt record, or title/subtitle text that differs from the accepted copy;
5. a target with prior README work that must be preserved and cited rather than overwritten by generic marketing language.

The fixture should not reveal which failure class is being tested. Give the agent the same task prompt and repository access it receives in normal work.

## Repeat the run

Run each unseen fixture at least three times from a clean checkout. Record the helper commit, model, task prompt, target fixture identifier, generated asset hashes, deterministic validator result, and independent quality result. Report:

```text
contract pass rate = runs passing every deterministic gate / total runs
quality pass rate  = runs accepted by the independent visual and editorial rubric / total runs
repeatability      = fixtures passing both rates on every run / total fixtures
```

Treat a single successful run as evidence of possibility, not repeatability. A release candidate should have zero contract failures and no repeated quality failure on the same fixture. Any failure should be classified before changing the helper: wrong source contract, wrong asset type, missing provenance, unreadable copy, visual mismatch, crop failure, or unsupported claim.

## Suggested private evaluator flow

```text
private holdout fixture
        |
        v
clean agent run x3
        |
        +--> public validator with the fixture's adapter
        |
        +--> independent visual/editorial review
        |
        v
failure-class report and release decision
```

The public helper now provides the structural gate used by that flow. For `0.3.x` adapters it rejects narrative SVGs, missing built-in image-generation provenance, missing exact title or subtitle records, missing prompt records, and hashes that do not match the committed image. It does not claim to replace human review of taste, clarity, or brand fit.

## What this catches from the previous failure

The earlier target could pass while producing the wrong result because its adapter explicitly asked for text-free SVG diagrams and its old helper version did not require image-generation provenance or exact narrative copy. A private holdout containing that legacy shape tests whether a future agent follows the current target contract and upgrades the adapter instead of repeating the old instruction literally.

