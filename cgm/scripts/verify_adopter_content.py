#!/usr/bin/env python3
"""Deterministic structural checks for adopter repository content (CGM 0.5.8+).

Fails closed when:
1. README.md matches known bootstrap template stubs or unfilled placeholders.
2. Assets declared in asset-manifest.json are never referenced in README.md or docs.
3. Human-facing files or documentation assets violate Human-Output Naming (HON).
4. Human-facing documentation prose contains tool-dump / agent-internals tells
   or high-signal AI-jargon tells (Human-Sounding Writing / HSW).

Remedies the operational failure mode where CGM is installed and pinned, but
the agent leaves README.md as a stale bootstrap stub without referencing registered
assets or enforcing writing/naming contracts across docs (CGM #33).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from scripts.human_filename import (
        is_hashy_junk_basename,
        is_robot_key_value_basename,
    )
except ImportError:
    try:
        from human_filename import (
            is_hashy_junk_basename,
            is_robot_key_value_basename,
        )
    except ImportError:
        _HASHY_RE = re.compile(r"(?i)^.+-p\d+-[0-9a-f]{6}\.[a-z0-9]+$")
        _ROBOT_KV_RE = re.compile(r"(?i)_(?:pitch|speed|rate)-[a-z0-9.+-]+")

        def is_hashy_junk_basename(name: str) -> bool:
            base = str(name or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
            return bool(_HASHY_RE.fullmatch(base))

        def is_robot_key_value_basename(name: str) -> bool:
            base = str(name or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
            return bool(_ROBOT_KV_RE.search(base))

try:
    from scripts.validate_content_system import check_adopter_readme_product_only
except ImportError:
    try:
        from validate_content_system import check_adopter_readme_product_only
    except ImportError:
        def check_adopter_readme_product_only(readme_text: str) -> list[str]:
            errs: list[str] = []
            if "content-generation-modules" in readme_text:
                errs.append("adopter README must not cite content-generation-modules")
            if re.search(r"\bCGM\b", readme_text):
                errs.append("adopter README must not cite CGM")
            if re.search(r"(?im)^##\s+Image generation and use\s*$", readme_text):
                errs.append("adopter README must not include an 'Image generation and use' section")
            return errs


BOOTSTRAP_STUB_PATTERNS = (
    # Stale bootstrap progress statements (e.g. CGM #33 octo-database failure)
    (r"product implementation starts with .+ after (?:that )?bootstrap", "stale bootstrap milestone statement"),
    (r"after (?:that )?bootstrap is accepted", "stale bootstrap acceptance statement"),
    (r"after (?:the )?bootstrap pr is merged", "stale bootstrap merge statement"),
    (r"repository governance and planning are being initialized", "stale repository planning placeholder"),
    (r"\bbootstrap placeholder\b", "bootstrap placeholder marker"),
    (r"\bbootstrap stub\b", "bootstrap stub marker"),
    (r"\bminimal bootstrap\b", "minimal bootstrap marker"),
    # Unfilled template placeholders from templates/README.template.md
    (r"# Project name\b", "unfilled template title '# Project name'"),
    (r"One sentence that names the human situation and the concrete promise", "unfilled template hook text"),
    (r"\bpath/to/hero\.png\b", "unfilled template hero image path"),
    (r"\bpath/to/supporting-visual\.png\b", "unfilled template visual path"),
    (r"\[One material product claim\]", "unfilled template claim placeholder"),
    (r"\[A plain-language description\]", "unfilled template description placeholder"),
    (r"\[Its boundary\]", "unfilled template boundary placeholder"),
    (r"\[Direct citation\]", "unfilled template citation placeholder"),
    (r"Start with a situation the reader recognizes\.", "unfilled template instructions"),
    (r"Say who this is for, what the project helps them do, and what the project is not\.", "unfilled template instructions"),
    (r"Show the useful outputs, workflows, examples, or decisions a reader can reach\.", "unfilled template instructions"),
    (r"Explain the mechanism in reader-sized steps\.", "unfilled template instructions"),
    (r"Give the smallest useful path to a first result", "unfilled template instructions"),
)

TOOL_DUMP_PATTERNS = (
    r"\bI(?:'ll| will) (?:now )?(?:run|call|invoke|execute)\b",
    r"\bAs an AI\b",
    r"\bAs a language model\b",
    r"\btool[_ -]?call\b",
    r"\bfunction[_ -]?call\b",
    r"\b<tool_call\b",
    r"\bMCP\s+tool\b",
    r"\bhotload_check\b",
    r"\bCGM_VERIFY\b",
    r"\bSKILL\.md\b",
    r"\bmodules/human-sounding-writing\b",
    r"\bact\s+as\s+(?:an?\s+)?expert\b",
    r"\blet me (?:know if|break (?:this|it) down)\b",
)

HIGH_SIGNAL_JARGON_WORDS = (
    r"delve",
    r"tapestry",
    r"testament",
    r"game[- ]changer",
    r"groundbreaking",
    r"unlock(?:s|ed|ing)?\s+(?:the\s+)?(?:power|potential|full)",
)

EXCLUDED_DIR_NAMES = {
    ".git",
    ".content-system",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    ".idea",
    ".vscode",
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


def strip_markdown_code_and_comments(text: str) -> str:
    """Strip fenced code blocks, inline code, and HTML comments for prose analysis."""
    # Fenced code blocks
    cleaned = re.sub(r"(?s)```[^\n]*\n.*?\n```", " ", text)
    # Inline code
    cleaned = re.sub(r"`[^`\n]+`", " ", cleaned)
    # HTML comments
    cleaned = re.sub(r"(?s)<!--.*?-->", " ", cleaned)
    return cleaned


def collect_project_markdown_files(
    project_root: Path,
    docs_dir: Path | None = None,
    exclude_agent_contracts: bool = False,
) -> list[Path]:
    """Return all human-facing markdown files to scan for references and prose tells."""
    md_files: list[Path] = []
    readme = project_root / "README.md"
    if readme.is_file():
        md_files.append(readme)

    docs = docs_dir or (project_root / "docs")
    if docs.is_dir():
        for path in sorted(docs.rglob("*.md")):
            if not any(part in EXCLUDED_DIR_NAMES for part in path.parts):
                if exclude_agent_contracts and (path.name == "AGENTS.md" or ".agent" in path.parts):
                    continue
                if path not in md_files:
                    md_files.append(path)

    for path in sorted(project_root.glob("*.md")):
        if path.is_file():
            if exclude_agent_contracts and (path.name == "AGENTS.md" or ".agent" in path.parts):
                continue
            if path not in md_files:
                md_files.append(path)

    return md_files


def check_readme_freshness(project_root: Path) -> list[str]:
    """Check that README.md exists and is not a stale bootstrap stub or unfilled template."""
    errors: list[str] = []
    readme_path = project_root / "README.md"
    if not readme_path.is_file():
        return [f"missing README.md under project root: {project_root}"]

    try:
        readme_text = readme_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"cannot read {readme_path}: {exc}"]

    # 1. Check known bootstrap stubs and unfilled template placeholders
    for pattern, desc in BOOTSTRAP_STUB_PATTERNS:
        match = re.search(pattern, readme_text, re.IGNORECASE)
        if match:
            snippet = match.group(0).strip()
            errors.append(
                f"adopter README.md contains {desc}: matches pattern '{snippet}'"
            )

    # 2. Check minimum substantive content
    stripped = re.sub(r"\s+", " ", strip_markdown_code_and_comments(readme_text)).strip()
    if len(stripped) < 120:
        errors.append("adopter README.md is suspiciously short or empty (less than 120 prose characters)")

    # 3. Check product-only rules (forbids promoting CGM / Image generation heading)
    errors.extend(check_adopter_readme_product_only(readme_text))

    return errors


def check_manifest_assets_referenced(
    adapter: Path,
    project_root: Path,
    docs_dir: Path | None = None,
) -> list[str]:
    """Ensure all declared non-rejected assets in asset-manifest.json are referenced in docs."""
    errors: list[str] = []
    manifest_path = adapter / "asset-manifest.json"
    if not manifest_path.is_file():
        return [f"missing {manifest_path}"]

    try:
        manifest = load_json(manifest_path)
    except ValueError as exc:
        return [str(exc)]

    assets = manifest.get("assets", [])
    if not isinstance(assets, list) or not assets:
        return errors

    md_files = collect_project_markdown_files(project_root, docs_dir)
    doc_texts = {}
    for md_path in md_files:
        try:
            raw = md_path.read_text(encoding="utf-8", errors="replace")
            # Strip HTML comments so commented-out assets aren't considered rendered/referenced
            uncommented = re.sub(r"(?s)<!--.*?-->", " ", raw)
            doc_texts[md_path] = uncommented
        except OSError:
            continue

    combined_text = "\n".join(doc_texts.values())

    for index, asset in enumerate(assets, start=1):
        if not isinstance(asset, dict):
            continue
        decision = str(asset.get("review") or asset.get("review_decision") or "").lower()
        if decision == "rejected":
            continue

        raw_path = str(asset.get("path") or "").strip()
        if not raw_path:
            continue

        normalized_path = raw_path.replace("\\", "/")
        basename = normalized_path.rsplit("/", 1)[-1]

        # Forms to search for:
        # 1. Exact declared path (e.g. docs/assets/workspace-dashboard.svg)
        # 2. Relative inside docs/ (e.g. assets/workspace-dashboard.svg)
        # 3. Basename in link/img syntax or plain reference (e.g. workspace-dashboard.svg)
        referenced = False
        if normalized_path in combined_text:
            referenced = True
        elif normalized_path.startswith("docs/") and normalized_path[5:] in combined_text:
            referenced = True
        elif basename:
            # Check if basename appears in a markdown link/image or html src/href
            pattern = re.compile(
                r"(?:\]\([^)]*" + re.escape(basename) + r"[^)]*\)|"
                r"src=[\"'][^\"']*" + re.escape(basename) + r"[^\"']*|"
                r"href=[\"'][^\"']*" + re.escape(basename) + r"[^\"']*|"
                r"\b" + re.escape(basename) + r"\b)",
                re.IGNORECASE,
            )
            if pattern.search(combined_text):
                referenced = True

        if not referenced:
            errors.append(
                f"asset declared in asset-manifest.json (entry {index}) is never "
                f"referenced in README.md or docs: '{raw_path}'"
            )

    return errors


def check_human_output_naming(project_root: Path, docs_dir: Path | None = None) -> list[str]:
    """Reject hashy junk, robot key=value, and opaque hex basenames on human-facing files."""
    errors: list[str] = []
    candidate_dirs: list[Path] = []

    docs = docs_dir or (project_root / "docs")
    if docs.is_dir():
        candidate_dirs.append(docs)

    assets = project_root / "assets"
    if assets.is_dir():
        candidate_dirs.append(assets)

    scanned_files: set[Path] = set()
    for root_dir in candidate_dirs:
        for file_path in root_dir.rglob("*"):
            if not file_path.is_file():
                continue
            if any(part in EXCLUDED_DIR_NAMES for part in file_path.parts):
                continue
            if file_path.name.startswith("."):
                continue
            scanned_files.add(file_path)

    for file_path in sorted(scanned_files):
        rel = file_path.relative_to(project_root)
        name = file_path.name
        if is_hashy_junk_basename(name):
            errors.append(
                f"human-facing file '{rel}' uses hashy junk basename (stem-pN-<6hex>.ext): '{name}'; "
                "use speakable or safe-twin style from scripts/human_filename"
            )
            continue
        if is_robot_key_value_basename(name):
            errors.append(
                f"human-facing file '{rel}' uses robot key=value basename: '{name}'; "
                "use speakable or safe-twin style from scripts/human_filename"
            )
            continue

        stem = name.rsplit(".", 1)[0]
        if re.fullmatch(r"[0-9a-f]{8,}", stem) or re.fullmatch(r"[0-9a-f]{32,}", stem):
            errors.append(
                f"human-facing file '{rel}' uses opaque hex hash basename: '{name}'; "
                "use speakable or safe-twin style from scripts/human_filename"
            )

    return errors


def check_docs_hsw_tells(project_root: Path, docs_dir: Path | None = None) -> list[str]:
    """Reject tool-dump / agent-internals tells and high-signal AI tells in markdown prose."""
    errors: list[str] = []
    md_files = collect_project_markdown_files(project_root, docs_dir, exclude_agent_contracts=True)

    for md_path in md_files:
        try:
            raw_text = md_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        rel = md_path.relative_to(project_root)
        prose = strip_markdown_code_and_comments(raw_text)

        # 1. Tool dump / agent internals
        for pattern in TOOL_DUMP_PATTERNS:
            match = re.search(pattern, prose, re.IGNORECASE)
            if match:
                errors.append(
                    f"documentation prose in '{rel}' contains agent/tool-dump tell: /{pattern}/"
                )

        # 2. High signal jargon tells
        for pattern in HIGH_SIGNAL_JARGON_WORDS:
            match = re.search(r"\b" + pattern + r"\b", prose, re.IGNORECASE)
            if match:
                snippet = match.group(0)
                errors.append(
                    f"documentation prose in '{rel}' contains high-signal AI jargon tell: '{snippet}'"
                )

    return errors


def check_manifest_hero_asset_format(adapter: Path) -> list[str]:
    """Enforce that hero assets declared in asset-manifest.json are PNGs and not SVGs."""
    errors: list[str] = []
    manifest_path = adapter / "asset-manifest.json"
    if not manifest_path.is_file():
        return errors

    try:
        manifest = load_json(manifest_path)
    except ValueError as exc:
        return [str(exc)]

    assets = manifest.get("assets", [])
    if not isinstance(assets, list):
        return errors

    for asset in assets:
        if not isinstance(asset, dict):
            continue
        role = str(asset.get("role") or "").strip().lower()
        orientation = str(asset.get("orientation") or "").strip().lower()
        raw_path = str(asset.get("path") or "").strip()
        path_lower = raw_path.lower()

        if "hero" in role:
            if orientation == "svg" or path_lower.endswith(".svg"):
                errors.append(
                    f"hero asset '{raw_path}' in asset-manifest.json must be a PNG image, "
                    "not an SVG (SVGs are for layout reference or diagrams, not public hero banners)"
                )
            elif not path_lower.endswith(".png"):
                errors.append(
                    f"hero asset '{raw_path}' in asset-manifest.json must have a .png extension (got '{raw_path}')"
                )

    return errors


_README_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]+)?\)")
_README_HTML_IMG_RE = re.compile(r"""<img\b[^>]*?\bsrc=["']([^"']+)["']""", re.IGNORECASE)
_RASTER_SUFFIXES = (".png", ".webp", ".jpg", ".jpeg")
_HERO_PNG_SUFFIX = ".png"


def _strip_html_comments(text: str) -> str:
    return re.sub(r"(?s)<!--.*?-->", " ", text)


def _readme_image_urls(text: str) -> list[str]:
    return _README_IMAGE_RE.findall(text) + _README_HTML_IMG_RE.findall(text)


def _readme_hero_image_url(clean_readme: str) -> str | None:
    """Return the first image in the intro section, falling back to the first in the doc."""
    intro = re.split(r"(?m)^##\s+", clean_readme, maxsplit=1)[0]
    images = _readme_image_urls(intro) or _readme_image_urls(clean_readme)
    if not images:
        return None
    return images[0].split("?")[0].split("#")[0].strip("<>")


def _registered_hero_paths(adapter: Path | None) -> list[str]:
    if adapter is None:
        return []
    manifest_path = adapter / "asset-manifest.json"
    if not manifest_path.is_file():
        return []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    paths: list[str] = []
    for asset in manifest.get("assets", []):
        if isinstance(asset, dict) and "hero" in str(asset.get("role", "")).lower():
            raw_path = str(asset.get("path", "")).strip()
            if raw_path:
                paths.append(raw_path)
    return paths


def _hero_visual_errors(hero_url: str) -> list[str]:
    lowered = hero_url.lower()
    if lowered.endswith(".svg"):
        return [
            f"adopter README.md hero visual must be a PNG image, not an SVG (found '{hero_url}'); "
            "SVGs are meant for UI layout wireframes or flow diagrams, never as the public README hero banner"
        ]
    if not lowered.endswith(_HERO_PNG_SUFFIX):
        return [f"adopter README.md hero visual must be a PNG image (found '{hero_url}')"]
    return []


def _registered_hero_reference_errors(clean_readme: str, adapter: Path | None) -> list[str]:
    errors: list[str] = []
    for hero_path in _registered_hero_paths(adapter):
        hero_base = hero_path.replace("\\", "/").rsplit("/", 1)[-1]
        if hero_base not in clean_readme and hero_path not in clean_readme:
            errors.append(f"adopter README.md must reference registered PNG hero asset '{hero_path}'")
    return errors


def check_readme_hero_format(project_root: Path, adapter: Path | None = None) -> list[str]:
    """Reject non-PNG (especially SVG) hero visuals and require registered hero references."""
    errors: list[str] = []
    readme_path = project_root / "README.md"
    if not readme_path.is_file():
        return errors

    try:
        readme_text = readme_path.read_text(encoding="utf-8")
    except OSError:
        return errors

    clean_readme = _strip_html_comments(readme_text)
    hero_url = _readme_hero_image_url(clean_readme)
    if hero_url:
        errors.extend(_hero_visual_errors(hero_url))
    errors.extend(_registered_hero_reference_errors(clean_readme, adapter))
    return errors


def check_adopter_readme_structure(project_root: Path, adapter: Path | None = None) -> list[str]:
    """Lint adopter README.md structure: PNG hero image, problem narrative, table, and boundaries."""
    errors: list[str] = []
    readme_path = project_root / "README.md"
    if not readme_path.is_file():
        return [f"missing README.md under project root: {project_root}"]

    try:
        readme_text = readme_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"cannot read {readme_path}: {exc}"]

    clean_readme = _strip_html_comments(readme_text)

    # 1. Hero banner visual must exist and be a PNG (SVGs are banned as the hero).
    hero_url = _readme_hero_image_url(clean_readme)
    if not hero_url:
        errors.append(
            "adopter README.md is missing a hero banner visual; every adopter README must include a narrative hero illustration (PNG)"
        )
    else:
        errors.extend(_hero_visual_errors(hero_url))
    errors.extend(_registered_hero_reference_errors(clean_readme, adapter))

    # 2. Problem narrative section check
    problem_match = re.search(
        r"(?im)^##\s+.*(?:\bwhy\b.*(?:\bexists\b|\bbuilt\b|\bhere\b|\bnow\b|\bcreated\b)|\bproblem\b|\btension\b|\bsituation\b).*$",
        clean_readme,
    )
    if not problem_match:
        errors.append(
            "adopter README.md is missing a problem narrative section (e.g. '## Why this exists' or '## Problem')"
        )

    # 3. Structured status / evidence / capabilities table check
    table_match = re.search(r"(?m)^\|[^\n]+\|\s*\n\|[- :|]+\|\s*\n\|[^\n]+\|", clean_readme)
    if not table_match:
        errors.append(
            "adopter README.md is missing a structured status/evidence table (markdown table mapping delivered capabilities/slices or claims and boundaries)"
        )

    # 4. Distinct boundaries section check
    boundaries_match = re.search(
        r"(?im)^##\s+.*(?:\bboundar|\bwhat\s+(?:is\s+implemented|this\s+project\s+|it\s+)?does\s+not\s+claim|\blimitations?\b|\bnon-goals?\b|\bscope\b).*$",
        clean_readme,
    )
    if not boundaries_match:
        errors.append(
            "adopter README.md is missing a distinct boundaries section (e.g. '## Boundaries' or '## What it does not claim')"
        )

    return errors


def check_adopter_content(
    adapter: Path,
    project_root: Path | None = None,
    docs_dir: Path | None = None,
    check_readme_structure_enabled: bool = False,
) -> list[str]:
    """Run all adopter content freshness, asset reference, and HON/HSW checks."""
    errors: list[str] = []
    root = project_root if project_root is not None else adapter.parent

    errors.extend(check_readme_freshness(root))
    errors.extend(check_readme_hero_format(root, adapter))
    if check_readme_structure_enabled:
        errors.extend(check_adopter_readme_structure(root, adapter=adapter))
    errors.extend(check_manifest_assets_referenced(adapter, root, docs_dir))
    errors.extend(check_manifest_hero_asset_format(adapter))
    errors.extend(check_human_output_naming(root, docs_dir))
    errors.extend(check_docs_hsw_tells(root, docs_dir))

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify adopter content freshness, asset references, and HON/HSW compliance."
    )
    parser.add_argument(
        "--adapter",
        type=Path,
        default=None,
        help="Path to .content-system adapter directory (defaults to <project-root>/.content-system)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Adopter project root directory (defaults to adapter parent or cwd)",
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=None,
        help="Adopter documentation directory (defaults to <project-root>/docs)",
    )
    parser.add_argument(
        "--check-adopter-readme",
        "--check-readme-structure",
        action="store_true",
        dest="check_readme_structure",
        help="Lint adopter README structure (PNG hero, problem section, status table, boundaries)",
    )

    args = parser.parse_args(argv)

    if args.project_root:
        project_root = args.project_root.resolve()
    elif args.adapter:
        project_root = args.adapter.resolve().parent
    else:
        project_root = Path.cwd().resolve()

    if args.adapter:
        adapter = args.adapter.resolve()
    else:
        adapter = project_root / ".content-system"

    docs_dir = args.docs_dir.resolve() if args.docs_dir else None

    errors = check_adopter_content(
        adapter,
        project_root,
        docs_dir,
        check_readme_structure_enabled=args.check_readme_structure,
    )
    status = "OK" if not errors else "FAIL"

    print(
        f"ADOPTER_VERIFY status={status} "
        f"project_root={project_root.name} "
        f"adapter={adapter.name}"
    )

    if errors:
        print("INVALID: adopter content check failed")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALID: adopter content contract OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
