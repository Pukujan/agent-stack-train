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

    for name in ("project-brief.json", "brand-language.json", "visual-style.json", "asset-manifest.json", "review-rubric.json"):
        if not (root / "templates" / name).is_file():
            errors.append(f"missing template: templates/{name}")

    if not (root / "CHATGPT_SETUP.md").is_file():
        errors.append("missing CHATGPT_SETUP.md")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    errors = check(args.root.resolve())
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID: content-generation-modules contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
