#!/usr/bin/env python3
"""Dependency-free structural checks for the content-generation helper contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


EXPECTED_MODULES = {
    "brand-foundation",
    "content-context",
    "writing-direction",
    "visual-direction",
    "image-generation",
    "html-demo",
}

NARRATIVE_ROLE_MARKERS = ("hero", "problem", "supporting", "evidence", "story", "social")
NARRATIVE_RASTER_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
REQUIRED_NARRATIVE_ASSET_FIELDS = (
    "path",
    "role",
    "orientation",
    "dimensions",
    "text_policy",
    "prompt_recipe",
    "exact_title",
    "exact_subtitle",
    "alt_text",
    "usage",
    "crop_behavior",
    "rejection_conditions",
    "review_decision",
    "provider",
    "prompt_record",
    "hash",
)

REQUIRED_HELPER_DOCS = (
    "docs/CONTENT_RESEARCH.md",
    "docs/BRAND_DIRECTION.md",
    "docs/README_PLAYBOOK.md",
    "docs/IMAGE_GUIDE.md",
    "docs/PRIOR_WORK.md",
    "docs/HOLDOUT_EVALUATION.md",
    "docs/MIGRATING_TO_0.3.md",
    "docs/MIGRATING_TO_0.2.md",
)


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected object in {path}")
    return value


def _version_tuple(value: object) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", str(value or ""))
    if not match:
        return (0, 0, 0)
    return tuple(int(part) for part in match.groups())


def check_narrative_assets(
    visual: dict, manifest: dict, project_root: Path | None = None
) -> list[str]:
    """Enforce the 0.3.x narrative-image provenance contract for target adapters."""
    errors: list[str] = []
    if visual.get("generation_workflow") != "built-in image_gen":
        errors.append("adapter visual-style.json must declare generation_workflow: built-in image_gen")

    roles = visual.get("narrative_roles")
    if not isinstance(roles, list) or not roles:
        errors.append("adapter visual-style.json must declare narrative_roles")
        role_markers = NARRATIVE_ROLE_MARKERS
    else:
        role_markers = tuple(str(role).lower() for role in roles)

    for asset in manifest.get("assets", []):
        role = str(asset.get("role", "")).lower()
        if not any(role == marker or role.startswith(f"{marker} ") for marker in role_markers):
            continue

        for field in REQUIRED_NARRATIVE_ASSET_FIELDS:
            if not asset.get(field):
                errors.append(f"narrative asset {asset.get('path', '<unknown>')} missing {field}")

        asset_path = str(asset.get("path", ""))
        if Path(asset_path).suffix.lower() not in NARRATIVE_RASTER_SUFFIXES:
            errors.append(f"narrative asset must be a raster image, not SVG: {asset_path}")

        if str(asset.get("provider", "")).lower() != "built-in image_gen":
            errors.append(f"narrative asset must record provider built-in image_gen: {asset_path}")

        prompt_recipe = str(asset.get("prompt_recipe", ""))
        if str(asset.get("exact_title", "")) not in prompt_recipe:
            errors.append(f"narrative asset prompt must include exact_title: {asset_path}")
        if str(asset.get("exact_subtitle", "")) not in prompt_recipe:
            errors.append(f"narrative asset prompt must include exact_subtitle: {asset_path}")

        digest = str(asset.get("hash", ""))
        if not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            errors.append(f"narrative asset hash must be a SHA-256 digest: {asset_path}")

        if project_root:
            image_path = project_root / asset_path
            prompt_record = project_root / str(asset.get("prompt_record", ""))
            if not prompt_record.is_file():
                errors.append(f"narrative asset prompt record does not exist: {asset.get('prompt_record')}")
            if image_path.is_file() and re.fullmatch(r"[0-9a-fA-F]{64}", digest):
                actual_digest = hashlib.sha256(image_path.read_bytes()).hexdigest()
                if actual_digest.lower() != digest.lower():
                    errors.append(f"narrative asset hash does not match file: {asset_path}")

    return errors


def check_readme(root: Path) -> list[str]:
    errors: list[str] = []
    readme_path = root / "README.md"
    if not readme_path.is_file():
        return ["missing README.md"]

    try:
        contract = load_json(root / "templates" / "readme-contract.json")
    except ValueError as exc:
        return [str(exc)]

    text = readme_path.read_text(encoding="utf-8")
    for section in contract.get("required_sections", []):
        heading = section.get("heading")
        if heading and f"## {heading}" not in text:
            errors.append(f"README missing required section: {heading}")

    story_heading = "## Why this exists"
    mechanism_heading = "## How it works"
    story_position = text.find(story_heading)
    mechanism_position = text.find(mechanism_heading)
    if story_position == -1 or mechanism_position == -1:
        pass
    elif story_position > mechanism_position:
        errors.append("README must explain why the project exists before how it works")
    first_code_block = text.find("```")
    if first_code_block != -1 and story_position != -1 and first_code_block < story_position:
        errors.append("README must place technical code after the human situation")

    for reference in contract.get("required_references", []):
        if reference not in text:
            errors.append(f"README missing required reference: {reference}")

    if contract.get("scanability_policy"):
        if not re.search(r"\*\*[^*\n]+\*\*", text):
            errors.append("README must include at least one meaningful bold scan anchor")
        if not re.search(r"^## .+", text, flags=re.MULTILINE):
            errors.append("README must use semantic level-two headings for scan structure")

    visual_policy = contract.get("visual_policy", {})
    image_refs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    image_refs.extend(re.findall(r"<img[^>]+src=[\"']([^\"']+)[\"']", text, flags=re.IGNORECASE))
    local_image_refs = [ref for ref in image_refs if not ref.startswith(("http://", "https://", "#"))]
    minimum_images = int(visual_policy.get("minimum_narrative_images_for_this_helper", 0))
    if len(local_image_refs) < minimum_images:
        errors.append(
            "README must reference at least "
            f"{minimum_images} local narrative image(s); found {len(local_image_refs)}"
        )
    for reference in local_image_refs:
        image_path = reference.split("#", 1)[0].strip("<>")
        if not (root / image_path).is_file():
            errors.append(f"README image does not exist: {image_path}")

    for guide in visual_policy.get("required_guides", []):
        if not (root / guide).is_file():
            errors.append(f"missing required image guide or record: {guide}")

    return errors


def check(root: Path) -> list[str]:
    errors: list[str] = []
    version_path = root / "system-version.json"
    try:
        version = load_json(version_path)
    except ValueError as exc:
        return [str(exc)]

    if not re.fullmatch(r"\d+\.\d+\.\d+", str(version.get("version", ""))):
        errors.append("system-version.json version must use semantic-version form")
    modules = set(version.get("modules", []))
    if modules != EXPECTED_MODULES:
        errors.append(f"system modules must be exactly {sorted(EXPECTED_MODULES)}")
    human_output = version.get("human_output_contract", {})
    if human_output.get("version") != "content-generation.readme-contract.v1":
        errors.append("system-version.json must declare content-generation.readme-contract.v1")
    for field in ("template", "playbook", "image_guide", "prior_work"):
        if not human_output.get(field):
            errors.append(f"system-version.json human_output_contract missing {field}")
    if not human_output.get("research"):
        errors.append("system-version.json human_output_contract missing research")
    if not human_output.get("brand_direction"):
        errors.append("system-version.json human_output_contract missing brand_direction")
    scanability = version.get("scanability_contract", {})
    if scanability.get("version") != "content-generation.scanability.v1":
        errors.append("system-version.json must declare content-generation.scanability.v1")
    for field in ("heading_rule", "bolding_rule", "scan_test", "accessibility_rule"):
        if not scanability.get(field):
            errors.append(f"system-version.json scanability_contract missing {field}")
    for module in EXPECTED_MODULES:
        path = root / "modules" / module / "SKILL.md"
        if not path.is_file():
            errors.append(f"missing module entry point: {path.relative_to(root)}")
        elif len(path.read_text(encoding="utf-8").splitlines()) > 500:
            errors.append(f"module entry point is over 500 lines: {path.relative_to(root)}")

    required_schemas = {
        "project-brief.schema.json",
        "asset-manifest.schema.json",
        "review-rubric.schema.json",
        "readme-contract.schema.json",
    }
    for name in required_schemas:
        path = root / "schemas" / name
        try:
            schema = load_json(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if "$schema" not in schema or "$id" not in schema:
            errors.append(f"schema missing $schema or $id: {path.relative_to(root)}")

    for name in (
        "project-brief.json",
        "brand-language.json",
        "visual-style.json",
        "asset-manifest.json",
        "review-rubric.json",
        "readme-contract.json",
    ):
        if not (root / "templates" / name).is_file():
            errors.append(f"missing template: templates/{name}")

    if not (root / "CHATGPT_SETUP.md").is_file():
        errors.append("missing CHATGPT_SETUP.md")
    for path in REQUIRED_HELPER_DOCS:
        if not (root / path).is_file():
            errors.append(f"missing helper guide: {path}")
    errors.extend(check_readme(root))
    return errors


def check_adapter(adapter: Path, project_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "system-version.json": "content-generation.adapter.v1",
        "project-brief.json": "content-generation.project-brief.v1",
        "brand-language.json": "content-generation.brand-language.v1",
        "visual-style.json": "content-generation.visual-style.v1",
        "asset-manifest.json": "content-generation.asset-manifest.v1",
        "review-rubric.json": "content-generation.review-rubric.v1",
    }
    values: dict[str, dict] = {}
    for name, schema_version in required.items():
        path = adapter / name
        try:
            values[name] = load_json(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if values[name].get("schema_version") != schema_version:
            errors.append(f"{name} must declare {schema_version}")

    system = values.get("system-version.json", {})
    for field in ("helper_repository", "helper_version", "helper_commit"):
        if not system.get(field):
            errors.append(f"adapter system-version.json missing {field}")
    if not system.get("modules") or set(system["modules"]) != EXPECTED_MODULES:
        errors.append("adapter system-version.json modules do not match the helper contract")

    project = values.get("project-brief.json", {})
    for field in ("project", "audience", "problem", "solution", "evidence", "boundaries"):
        if not project.get(field):
            errors.append(f"adapter project-brief.json missing {field}")

    brand = values.get("brand-language.json", {})
    for field in ("name", "personality", "promise", "avoid"):
        if not brand.get(field):
            errors.append(f"adapter brand-language.json missing {field}")

    visual = values.get("visual-style.json", {})
    for field in ("reference_asset", "palette", "roles", "reject_when"):
        if not visual.get(field):
            errors.append(f"adapter visual-style.json missing {field}")

    manifest = values.get("asset-manifest.json", {})
    assets = manifest.get("assets", [])
    if not assets:
        errors.append("adapter asset-manifest.json must contain at least one asset")
    if project_root:
        for asset in assets:
            asset_path = asset.get("path")
            if asset_path and not (project_root / asset_path).is_file():
                errors.append(f"asset does not exist under project root: {asset_path}")
    if _version_tuple(system.get("helper_version")) >= (0, 3, 0):
        errors.extend(check_narrative_assets(visual, manifest, project_root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--adapter", type=Path)
    parser.add_argument("--project-root", type=Path)
    args = parser.parse_args()
    errors = check(args.root.resolve())
    if args.adapter:
        errors.extend(check_adapter(args.adapter.resolve(), args.project_root.resolve() if args.project_root else None))
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID: content-generation-modules contract" + (" and target adapter" if args.adapter else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
