#!/usr/bin/env python3
"""Dependency-free structural checks for the content-generation helper contract."""

from __future__ import annotations

import argparse
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

REQUIRED_HELPER_DOCS = (
    "docs/README_PLAYBOOK.md",
    "docs/IMAGE_GUIDE.md",
    "docs/PRIOR_WORK.md",
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
