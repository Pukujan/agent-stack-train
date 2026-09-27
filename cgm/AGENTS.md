# Agent Operating Contract

This repository is the reusable contract for human-oriented brand, content, visual, image, and HTML-demo work.

Before changing or using the system:

1. read `README.md`;
2. read `system-version.json`;
3. read only the module `SKILL.md` files relevant to the requested output; for writing work, **MUST load** the routed module per [`docs/WRITING_ROUTING.md`](docs/WRITING_ROUTING.md) / [`docs/writing-routing.json`](docs/writing-routing.json) (`required_load`): README/product entry → `writing-direction`; PR/issue titles and bodies, issue-log titles, **commit messages/subjects**, non-README docs, changelog prose, posts, blogs, social, general prose, and papers/data writeups → `human-sounding-writing`; generated artifact filenames / asset-manifest paths / committed media basenames / filename legends → `human-output-naming`;
4. inspect the target repository's `.content-system/` adapter and evidence before making claims;
5. for README or other human-facing work, read `docs/CONTENT_RESEARCH.md`, `docs/BRAND_DIRECTION.md`, `docs/README_PLAYBOOK.md`, `docs/IMAGE_GUIDE.md`, `docs/PROVENANCE_AND_CITATION.md`, `docs/README_QUALITY_PDD.md`, `docs/README_QUALITY_SDD.md`, `docs/README_QUALITY_TDD.md`, and `templates/readme-contract.json`;
6. inspect prior reviewed outputs in the target repository and the helper's prior-work references before inventing a new story or visual direction;
7. run `python scripts/validate_content_system.py --root .` before handoff (ACS hotload may call `--mode writing` first; see [`docs/ACS_VERIFY.md`](docs/ACS_VERIFY.md)).

The helper system defines methods and constraints. It does not define product facts. Product facts, claims, audience, and project-specific visual identity belong in the target repository.

Do not treat model-generated scores as objective truth. Deterministic checks and human review remain authoritative for subjective quality.

## Human-facing deliverable gate

README, product documentation, marketing copy, image briefs, and HTML demos are human-facing deliverables. Treat the reader's situation and reason to care as the primary output; put architecture and implementation details after the story has earned the reader's attention.

Every **adopter / target** README deliverable must:

- explain why the project exists through a recognizable human situation and consequence;
- develop that situation with a concrete, repository-grounded example before architecture;
- say what the project is, who it helps, and what it does not claim;
- show the mechanism in plain language before introducing internal names or architecture;
- connect important **product** claims to revision-pinned evidence, explain what each source supports and leaves unproven, and label shipped, experimental, planned, or unknown work;
- give the reader a next action, example, or smallest useful path;
- use the target repository's visual contract when one exists (place images with useful alt text; do not narrate the generation pipeline in the README);
- use descriptive headings, short sections, selective bold anchors, and the heading-and-bold scan test as craft — do not teach that methodology in the README;
- record image role, prompt, text, dimensions, use, crop/accessibility, rejection, and review for every committed raster asset in `.content-system/asset-manifest.json` (or linked prompt records), **not** as README story;
- when naming prior work, name the **target product's** lineage — do not cite or promote CGM.

**Adopter README anti-rules (0.5.4+):** do not cite/promote CGM or `content-generation-modules`; do not narrate how images were generated; do not narrate writing-style methodology; do not add “Image generation and use” or “Templates and guides” helper sections. The helper repository's own README may document CGM, image workflow, and templates because that is its product.

Do not hand off a README that is only a module index, setup checklist, architecture summary, one-line product description, or a CGM/image/writing-method defense. Use the [README contract](templates/readme-contract.json) (`adopter_readme_policy`), the PDD/SDD/TDD acceptance documents, and the validator. A citation proves traceability, not truth. Keep the target's visual identity and adapter image-generation records intact.

## Writing modules

**MUST load** the soft router in [`docs/WRITING_ROUTING.md`](docs/WRITING_ROUTING.md) (JSON: [`docs/writing-routing.json`](docs/writing-routing.json); each route has `required_load: true`):

- README / product entry → `writing-direction` (keep scan-first selective bold);
- PR titles/bodies, issue titles/bodies, issue-log titles, **commit messages and commit subjects**, non-README docs, changelog prose → `human-sounding-writing` (**hsw** / HSW);
- posts / blogs / social / general agent prose → `human-sounding-writing` (**hsw** / HSW);
- papers / data writeups → `human-sounding-writing` (including chart rules; short name **hsw**);
- generated artifact filenames / asset-manifest paths / committed media basenames / filename legends → `human-output-naming` (**hon** / HON).

Soft means no NLP CI grade of prose — not optional load. Follow `apply_checklist` in the JSON. Agents asked for "hsw" must load `human-sounding-writing`. Agents asked for "hon" must load `human-output-naming`, call `scripts/human_filename` (speakable by default; optional safe_twin), and keep a per-feature filename legend. Canonical module ids remain the folder names.

Do not apply `human-sounding-writing` bold restraints to READMEs. Do not weaken the README scanability contract.

ACS / multi-agent-hotload verify entrypoint: `python scripts/validate_content_system.py --root <cgm> --mode writing` (full helper or helper+adapter as needed). After verify, ACS must inject `acs_prompt_inject` from the JSON into agent prompts. Details: [`docs/ACS_VERIFY.md`](docs/ACS_VERIFY.md).

## Versioning

Every target repository must pin a helper version or commit. Do not silently read the helper repository's moving `main` branch during a generation run.

Changes to this helper must be owned by an open issue created by or assigned to `Pukujan`, with written acceptance or delivery criteria. The pull request must reference that issue; CI verifies the owner and criteria before branch protection permits a merge. Keep corrections and decisions in the issue/PR/commit history so record time and source lineage remain inspectable.

## Safety

Never commit API keys, private source material, generated caches, or user data. Record image prompts and settings only when they are safe to publish.

## Repository ownership and remote writes

This agent may make remote changes only in GitHub repositories owned by the user, whose GitHub account is `Pukujan`.

Before any GitHub write—including creating or editing issues, pull requests, comments, branches, releases, or repository settings—verify the exact repository with `gh repo view OWNER/REPO --json nameWithOwner` and confirm the returned owner is `Pukujan`. Also confirm the active GitHub CLI account with `gh api user --jq .login`. Do not infer ownership from a local folder name, a repository description, a link in a conversation, or a Git remote alone.

Only write to the exact Pukujan-owned repository that the user selected or explicitly authorized for that change. A request to inspect or compare another repository authorizes read-only inspection, not edits there. All repositories owned by other accounts are read-only, even when they are cloned locally or the user has access to them. If ownership or the intended target is uncertain, stop before writing and report what could not be verified.
