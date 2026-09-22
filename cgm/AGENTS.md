# Agent Operating Contract

This repository is the reusable contract for human-oriented brand, content, visual, image, and HTML-demo work.

Before changing or using the system:

1. read `README.md`;
2. read `system-version.json`;
3. read only the module `SKILL.md` files relevant to the requested output;
4. inspect the target repository's `.content-system/` adapter and evidence before making claims;
5. for README or other human-facing work, read `docs/CONTENT_RESEARCH.md`, `docs/BRAND_DIRECTION.md`, `docs/README_PLAYBOOK.md`, `docs/IMAGE_GUIDE.md`, and `templates/readme-contract.json`;
6. inspect prior reviewed outputs in the target repository and the helper's prior-work references before inventing a new story or visual direction;
7. run `python scripts/validate_content_system.py --root .` before handoff.

The helper system defines methods and constraints. It does not define product facts. Product facts, claims, audience, and project-specific visual identity belong in the target repository.

Do not treat model-generated scores as objective truth. Deterministic checks and human review remain authoritative for subjective quality.

## Human-facing deliverable gate

README, product documentation, marketing copy, image briefs, and HTML demos are human-facing deliverables. Treat the reader's situation and reason to care as the primary output; put architecture and implementation details after the story has earned the reader's attention.

Every README deliverable must:

- explain why the project exists through a recognizable human situation and consequence;
- say what the project is, who it helps, and what it does not claim;
- show the mechanism in plain language before introducing internal names or architecture;
- connect important claims to repository evidence and label shipped, experimental, planned, or unknown work;
- give the reader a next action, example, or smallest useful path;
- use the target repository's visual contract when one exists;
- use descriptive headings, short sections, selective bold anchors, and the heading-and-bold scan test;
- include image role, prompt, text, dimensions, use, crop/accessibility, rejection, and review guidance for every committed raster asset;
- name relevant prior work or reviewed examples instead of pretending the pattern was invented in the current draft.

Do not hand off a README that is only a module index, setup checklist, architecture summary, or one-line product description. Use the [README contract](templates/readme-contract.json) and let the validator catch missing sections and visual evidence.

## Versioning

Every target repository must pin a helper version or commit. Do not silently read the helper repository's moving `main` branch during a generation run.

## Safety

Never commit API keys, private source material, generated caches, or user data. Record image prompts and settings only when they are safe to publish.
