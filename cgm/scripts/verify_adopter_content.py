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


def collect_project_markdown_files(project_root: Path, docs_dir: Path | None = None) -> list[Path]:
    """Return all human-facing markdown files to scan for references and prose tells."""
    md_files: list[Path] = []
    readme = project_root / "README.md"
    if readme.is_file():
        md_files.append(readme)

    docs = docs_dir or (project_root / "docs")
    if docs.is_dir():
        for path in sorted(docs.rglob("*.md")):
            if not any(part in EXCLUDED_DIR_NAMES for part in path.parts):
                if path not in md_files:
                    md_files.append(path)

    for path in sorted(project_root.glob("*.md")):
        if path.is_file() and path not in md_files:
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
            doc_texts[md_path] = md_path.read_text(encoding="utf-8", errors="replace")
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
    md_files = collect_project_markdown_files(project_root, docs_dir)

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


def check_adopter_content(
    adapter: Path,
    project_root: Path | None = None,
    docs_dir: Path | None = None,
) -> list[str]:
    """Run all adopter content freshness, asset reference, and HON/HSW checks."""
    errors: list[str] = []
    root = project_root or (adapter.parent if (adapter.parent / "README.md").is_file() else Path.cwd())

    errors.extend(check_readme_freshness(root))
    errors.extend(check_manifest_assets_referenced(adapter, root, docs_dir))
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

    args = parser.parse_args(argv)

    if args.project_root:
        project_root = args.project_root.resolve()
    elif args.adapter:
        adapter_res = args.adapter.resolve()
        project_root = adapter_res.parent if (adapter_res.parent / "README.md").is_file() else Path.cwd().resolve()
    else:
        project_root = Path.cwd().resolve()

    if args.adapter:
        adapter = args.adapter.resolve()
    else:
        adapter = project_root / ".content-system"

    docs_dir = args.docs_dir.resolve() if args.docs_dir else None

    errors = check_adopter_content(adapter, project_root, docs_dir)
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
