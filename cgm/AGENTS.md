# Agent Operating Contract

This repository is the reusable contract for human-oriented brand, content, visual, image, and HTML-demo work.

Before changing or using the system:

1. read `README.md`;
2. read `system-version.json`;
3. read only the module `SKILL.md` files relevant to the requested output;
4. inspect the target repository's `.content-system/` adapter and evidence before making claims;
5. for README or other human-facing work, read `docs/CONTENT_RESEARCH.md`, `docs/BRAND_DIRECTION.md`, `docs/README_PLAYBOOK.md`, `docs/IMAGE_GUIDE.md`, `docs/PROVENANCE_AND_CITATION.md`, `docs/README_QUALITY_PDD.md`, `docs/README_QUALITY_SDD.md`, `docs/README_QUALITY_TDD.md`, and `templates/readme-contract.json`;
6. inspect prior reviewed outputs in the target repository and the helper's prior-work references before inventing a new story or visual direction;
7. run `python scripts/validate_content_system.py --root .` before handoff.

The helper system defines methods and constraints. It does not define product facts. Product facts, claims, audience, and project-specific visual identity belong in the target repository.

Do not treat model-generated scores as objective truth. Deterministic checks and human review remain authoritative for subjective quality.

## Human-facing deliverable gate

README, product documentation, marketing copy, image briefs, and HTML demos are human-facing deliverables. Treat the reader's situation and reason to care as the primary output; put architecture and implementation details after the story has earned the reader's attention.

Every README deliverable must:

- explain why the project exists through a recognizable human situation and consequence;
- develop that situation with a concrete, repository-grounded example before architecture;
- say what the project is, who it helps, and what it does not claim;
- show the mechanism in plain language before introducing internal names or architecture;
- connect important claims to revision-pinned evidence, explain what each source supports and leaves unproven, and label shipped, experimental, planned, or unknown work;
- give the reader a next action, example, or smallest useful path;
- use the target repository's visual contract when one exists;
- use descriptive headings, short sections, selective bold anchors, and the heading-and-bold scan test;
- include image role, prompt, text, dimensions, use, crop/accessibility, rejection, and review guidance for every committed raster asset;
- name relevant prior work or reviewed examples instead of pretending the pattern was invented in the current draft.

Do not hand off a README that is only a module index, setup checklist, architecture summary, or one-line product description. Use the [README contract](templates/readme-contract.json), the PDD/SDD/TDD acceptance documents, and the validator. A citation proves traceability, not truth. Keep the target's visual identity and image-generation contract intact.

## Versioning

Every target repository must pin a helper version or commit. Do not silently read the helper repository's moving `main` branch during a generation run.

Changes to this helper must be owned by an open issue created by or assigned to `Pukujan`, with written acceptance or delivery criteria. The pull request must reference that issue; CI verifies the owner and criteria before branch protection permits a merge. Keep corrections and decisions in the issue/PR/commit history so record time and source lineage remain inspectable.

## Safety

Never commit API keys, private source material, generated caches, or user data. Record image prompts and settings only when they are safe to publish.

## Repository ownership and remote writes

This agent may make remote changes only in GitHub repositories owned by the user, whose GitHub account is `Pukujan`.

Before any GitHub write—including creating or editing issues, pull requests, comments, branches, releases, or repository settings—verify the exact repository with `gh repo view OWNER/REPO --json nameWithOwner` and confirm the returned owner is `Pukujan`. Also confirm the active GitHub CLI account with `gh api user --jq .login`. Do not infer ownership from a local folder name, a repository description, a link in a conversation, or a Git remote alone.

Only write to the exact Pukujan-owned repository that the user selected or explicitly authorized for that change. A request to inspect or compare another repository authorizes read-only inspection, not edits there. All repositories owned by other accounts are read-only, even when they are cloned locally or the user has access to them. If ownership or the intended target is uncertain, stop before writing and report what could not be verified.
