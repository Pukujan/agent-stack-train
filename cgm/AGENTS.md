# Agent Operating Contract

This repository is the reusable contract for human-oriented brand, content, visual, image, and HTML-demo work.

Before changing or using the system:

1. read `README.md`;
2. read `system-version.json`;
3. read only the module `SKILL.md` files relevant to the requested output;
4. inspect the target repository's `.content-system/` adapter and evidence before making claims;
5. run `python scripts/validate_content_system.py --root .` before handoff.

The helper system defines methods and constraints. It does not define product facts. Product facts, claims, audience, and project-specific visual identity belong in the target repository.

Do not treat model-generated scores as objective truth. Deterministic checks and human review remain authoritative for subjective quality.

## Versioning

Every target repository must pin a helper version or commit. Do not silently read the helper repository's moving `main` branch during a generation run.

## Safety

Never commit API keys, private source material, generated caches, or user data. Record image prompts and settings only when they are safe to publish.
