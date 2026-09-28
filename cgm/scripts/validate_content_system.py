#!/usr/bin/env python3
"""Dependency-free structural checks for the content-generation helper contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.parse import unquote, urlparse


EXPECTED_MODULES = {
    "brand-foundation",
    "content-context",
    "writing-direction",
    "human-sounding-writing",
    "human-output-naming",
    "visual-direction",
    "image-generation",
    "html-demo",
}

WRITING_MODULES = (
    "writing-direction",
    "human-sounding-writing",
)

WRITING_ROUTER_DOC = "docs/WRITING_ROUTING.md"
WRITING_ROUTER_CONTRACT = "docs/writing-routing.json"
WRITING_ROUTER_SCHEMA = "content-generation.writing-routing.v1"
FILENAME_CONTRACT_DOC = "docs/HUMAN_OUTPUT_NAMING.md"
FILENAME_CONTRACT = "docs/human-output-naming.json"
FILENAME_CONTRACT_SCHEMA = "content-generation.human-output-naming.v1"
FILENAME_HELPER_PATH = "scripts/human_filename.py"
HSW_VERIFY_HELPER_PATH = "scripts/verify_hsw_applied.py"
ISSUE_LOG_DOC = "docs/ISSUE_LOG.md"
ISSUE_LOG_CONTRACT = "docs/issue-log-contract.json"
ISSUE_LOG_SCHEMA = "content-generation.issue-log.v1"
ISSUE_LOG_REQUIRED_STEP_IDS = (
    "reproduce_first",
    "classify_product_defect_all_adopters",
    "fix_pin_contract_validate",
    "never_single_adopter_ticket",
)
FILENAME_HELPER_SYMBOLS = (
    "build_basename",
    "build_basename_from_dimensions",
    "build_relative_path",
    "is_accepted_basename",
    "is_hashy_junk_basename",
    "is_robot_key_value_basename",
    "pitch_phrase",
    "sanitize_label",
    "speed_phrase",
)
HASHY_BASENAME_RE = re.compile(
    r"(?i)^.+-p\d+-[0-9a-f]{6}\.[a-z0-9]+$"
)
ROBOT_KV_BASENAME_RE = re.compile(r"(?i)_(?:pitch|speed|rate)-[a-z0-9.+-]+")
FILENAME_LEGEND_DIR = "docs/filename-legends"
FILENAME_LEGEND_SCHEMA = "content-generation.filename-legend.v1"
ADAPTER_FILENAME_LEGEND_DIR = ".content-system/filename-legends"
REQUIRED_ROUTER_ROUTE_IDS = ("readme_product_entry", "github_and_docs_prose", "generated_artifact_filenames")

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
    "docs/MIGRATING_TO_0.4.md",
    "docs/README_QUALITY_PDD.md",
    "docs/README_QUALITY_SDD.md",
    "docs/README_QUALITY_TDD.md",
    "docs/PROVENANCE_AND_CITATION.md",
    "docs/REVERSE_ANALYSIS_PCM_AND_ADOPTERS.md",
    "docs/WRITING_ROUTING.md",
    "docs/writing-routing.json",
    "docs/ACS_VERIFY.md",
    "docs/ISSUE_LOG.md",
    "docs/issue-log-contract.json",
    "docs/HUMAN_SOUNDING_WRITING.md",
    "docs/human-sounding-rules.json",
    "docs/MIGRATING_TO_0.5.md",
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


def _valid_date(value: object) -> bool:
    try:
        date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return False
    return True


def _parse_aware_datetime(value: object) -> datetime | None:
    if not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})",
        str(value or ""),
    ):
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return parsed if parsed.utcoffset() is not None else None


def _valid_web_uri(value: object) -> bool:
    try:
        parsed = urlparse(str(value or ""))
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _valid_repository_permalink(uri: object, repository: str, commit: str, source_path: str) -> bool:
    try:
        parsed = urlparse(str(uri or ""))
    except ValueError:
        return False
    if parsed.scheme != "https" or not parsed.netloc:
        return False
    parts = [unquote(part) for part in parsed.path.split("/") if part]
    repository_parts = repository.split("/")
    repo_index = next(
        (index for index in range(len(parts) - len(repository_parts) + 1)
         if parts[index:index + len(repository_parts)] == repository_parts),
        None,
    )
    if repo_index is None:
        return False
    commit_index = next(
        (index for index in range(repo_index + len(repository_parts), len(parts))
         if parts[index].lower() == commit.lower()),
        None,
    )
    if commit_index is None:
        return False
    linked_path = "/".join(parts[commit_index + 1:])
    return linked_path == source_path or linked_path.startswith(f"{source_path}/")


def check_project_brief_v2(project: dict, readme_text: str | None = None) -> list[str]:
    """Check claim explanations and the source identity needed to reproduce them."""
    errors: list[str] = []
    if project.get("schema_version") != "content-generation.project-brief.v2":
        errors.append("project brief must declare content-generation.project-brief.v2")
    evidence = project.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("project-brief v2 must contain at least one evidence item")
        return errors

    allowed_statuses = {"shipped", "experimentally_supported", "planned", "unknown"}
    allowed_kinds = {
        "repository_artifact",
        "external_source",
        "user_observation",
        "owner_decision",
        "experiment_result",
        "unknown_search",
    }
    repo_kinds = {"repository_artifact"}

    for index, item in enumerate(evidence, start=1):
        label = f"project-brief evidence item {index}"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue

        for field in ("claim", "source", "supports", "limits"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"{label} missing non-empty {field}")
        if item.get("supports") == item.get("limits") and item.get("supports"):
            errors.append(f"{label} supports and limits must explain different things")
        if _parse_aware_datetime(item.get("recorded_at")) is None:
            errors.append(f"{label} recorded_at must be an RFC 3339 timestamp with a timezone")

        valid_time = item.get("valid_time")
        if valid_time is not None:
            if not isinstance(valid_time, dict) or set(valid_time) != {"start", "end"}:
                errors.append(f"{label} valid_time must contain start and end")
            else:
                start_value, end_value = valid_time["start"], valid_time["end"]
                start = _parse_aware_datetime(start_value) if start_value is not None else None
                end = _parse_aware_datetime(end_value) if end_value is not None else None
                if start_value is not None and start is None:
                    errors.append(f"{label} valid_time.start must be a timezone-aware RFC 3339 timestamp")
                if end_value is not None and end is None:
                    errors.append(f"{label} valid_time.end must be a timezone-aware RFC 3339 timestamp")
                if start_value is None and end_value is None:
                    errors.append(f"{label} valid_time must have at least one bounded endpoint")
                if start is not None and end is not None and start > end:
                    errors.append(f"{label} valid_time.start must not follow valid_time.end")

        status = item.get("status")
        if not isinstance(status, str) or status not in allowed_statuses:
            errors.append(f"{label} has invalid status: {status}")
        cite_in_readme = item.get("cite_in_readme")
        if not isinstance(cite_in_readme, bool):
            errors.append(f"{label} cite_in_readme must be a boolean")

        revision = item.get("source_revision")
        if not isinstance(revision, dict):
            errors.append(f"{label} missing source_revision object")
            continue

        kind = revision.get("kind")
        if not isinstance(kind, str) or kind not in allowed_kinds:
            errors.append(f"{label} has unsupported source_revision kind: {kind}")
            continue

        if not isinstance(revision.get("reference"), str) or not revision["reference"].strip():
            errors.append(f"{label} source_revision missing reference")

        if kind in repo_kinds:
            repository = str(revision.get("repository", ""))
            if not re.fullmatch(r"[^/\s]+/[^/\s]+", repository):
                errors.append(f"{label} repository source needs owner/repository")
            commit = str(revision.get("commit", ""))
            if not re.fullmatch(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", commit):
                errors.append(f"{label} repository source needs a full commit ID")
            source_path = str(revision.get("path", ""))
            if (
                not source_path
                or "\\" in source_path
                or Path(source_path).is_absolute()
                or ".." in Path(source_path).parts
            ):
                errors.append(f"{label} repository source needs a repository-relative path")
            if not isinstance(revision.get("locator"), str) or not revision["locator"].strip():
                errors.append(f"{label} repository source needs a line, heading, or record locator")
            if not _valid_repository_permalink(revision.get("uri"), repository, commit, source_path):
                errors.append(
                    f"{label} repository source needs an immutable web permalink containing its repository, full commit ID, and path"
                )
        elif kind in {"external_source", "experiment_result"}:
            if not _valid_web_uri(revision.get("uri")):
                errors.append(f"{label} {kind} source needs a direct HTTP(S) URI")
            if not _valid_date(revision.get("accessed_at")):
                errors.append(f"{label} {kind} source needs accessed_at in YYYY-MM-DD form")
            if kind == "experiment_result" and not revision.get("locator"):
                errors.append(f"{label} experiment source needs a run or artifact locator")
        elif kind in {"user_observation", "owner_decision", "unknown_search"}:
            if not _valid_date(revision.get("observed_at")):
                errors.append(f"{label} {kind} source needs observed_at in YYYY-MM-DD form")
        if revision.get("uri") and not _valid_web_uri(revision["uri"]):
            errors.append(f"{label} source_revision URI must use HTTP(S)")
        if revision.get("observed_at") and not _valid_date(revision["observed_at"]):
            errors.append(f"{label} observed_at must use YYYY-MM-DD form")
        if revision.get("published_at") and not _valid_date(revision["published_at"]):
            errors.append(f"{label} published_at must use YYYY-MM-DD form")
        if revision.get("accessed_at") and not _valid_date(revision["accessed_at"]):
            errors.append(f"{label} accessed_at must use YYYY-MM-DD form")
        if revision.get("sha256") and not re.fullmatch(r"[0-9a-fA-F]{64}", str(revision["sha256"])):
            errors.append(f"{label} sha256 must be a SHA-256 digest")

        if status != "unknown" and kind == "unknown_search":
            errors.append(f"{label} cannot label a claim {status} when its only source is an unknown search")
        if cite_in_readme:
            uri = revision.get("uri")
            if not _valid_web_uri(uri):
                errors.append(f"{label} requires a public citation URI")
            elif readme_text is None:
                errors.append(f"{label} citation check requires the target README")
            elif str(uri) not in readme_text:
                errors.append(f"{label} citation URI is not linked in the target README")

    return errors


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

    expected_claim_fields = ["claim", "source", "status", "supports", "limits", "source_revision", "recorded_at"]
    if contract.get("schema_version") != "content-generation.readme-contract.v2":
        errors.append("README contract must declare content-generation.readme-contract.v2")
    adopter_policy = contract.get("adopter_readme_policy") or {}
    if not adopter_policy.get("must_not") or not adopter_policy.get("image_provenance"):
        errors.append("README contract must declare adopter_readme_policy with must_not and image_provenance")
    story_policy = contract.get("story_policy", {})
    if not story_policy.get("sequence") or not story_policy.get("worked_example") or not story_policy.get("reader_paths"):
        errors.append("README contract must define its story sequence, worked example, and reader paths")
    evidence_policy = contract.get("evidence_policy", {})
    if evidence_policy.get("claim_fields") != expected_claim_fields:
        errors.append("README contract must require the v2 claim fields in order")

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



def check_human_output_naming_contract(root: Path) -> list[str]:
    """Fail closed if the filename contract claims a helper that is missing."""
    errors: list[str] = []
    skill = root / "modules" / "human-output-naming" / "SKILL.md"
    if not skill.is_file():
        errors.append("missing module entry point: modules/human-output-naming/SKILL.md")
    elif len(skill.read_text(encoding="utf-8").splitlines()) > 500:
        errors.append("module entry point is over 500 lines: modules/human-output-naming/SKILL.md")

    helper_path = root / FILENAME_HELPER_PATH
    if not helper_path.is_file():
        errors.append(
            f"filename contract claims {FILENAME_HELPER_PATH} but the helper module/API is missing"
        )
    else:
        # Structural symbol check without importing (keeps validate dependency-free
        # beyond stdlib and avoids package-path surprises in adapters).
        source = helper_path.read_text(encoding="utf-8")
        for symbol in FILENAME_HELPER_SYMBOLS:
            if f"def {symbol}(" not in source:
                errors.append(
                    f"{FILENAME_HELPER_PATH} missing required API symbol: {symbol}"
                )

    doc = root / FILENAME_CONTRACT_DOC
    if not doc.is_file():
        errors.append(f"missing filename contract guide: {FILENAME_CONTRACT_DOC}")

    contract_path = root / FILENAME_CONTRACT
    try:
        contract = load_json(contract_path)
    except ValueError as exc:
        errors.append(str(exc))
        return errors

    if contract.get("schema_version") != FILENAME_CONTRACT_SCHEMA:
        errors.append(f"{FILENAME_CONTRACT} must declare {FILENAME_CONTRACT_SCHEMA}")
    if contract.get("module") != "human-output-naming":
        errors.append(f"{FILENAME_CONTRACT} module must be human-output-naming")
    if contract.get("application") != "must_load":
        errors.append(f"{FILENAME_CONTRACT} application must be must_load")
    surfaces = {str(s).lower() for s in (contract.get("surfaces") or [])}
    for needle in ("generated artifact", "asset-manifest", "committed media", "filename legend"):
        if not any(needle in surface for surface in surfaces):
            errors.append(f"{FILENAME_CONTRACT} surfaces must mention {needle}")
    styles = contract.get("basename_styles") or {}
    if styles.get("default") != "speakable":
        errors.append(f"{FILENAME_CONTRACT} basename_styles.default must be speakable")
    if "safe_twin" not in str(styles.get("optional") or ""):
        errors.append(f"{FILENAME_CONTRACT} basename_styles.optional must mention safe_twin")
    legends = contract.get("filename_legends") or {}
    if legends.get("schema_version") != FILENAME_LEGEND_SCHEMA:
        errors.append(f"{FILENAME_CONTRACT} filename_legends.schema_version must be {FILENAME_LEGEND_SCHEMA}")
    api = contract.get("python_api") or {}
    if api.get("path") != FILENAME_HELPER_PATH:
        errors.append(f"{FILENAME_CONTRACT} python_api.path must be {FILENAME_HELPER_PATH}")
    required_syms = list(api.get("required_symbols") or [])
    for symbol in FILENAME_HELPER_SYMBOLS:
        if symbol not in required_syms:
            errors.append(f"{FILENAME_CONTRACT} python_api.required_symbols must include {symbol}")
    checklist = contract.get("apply_checklist")
    if not isinstance(checklist, list) or len(checklist) < 3:
        errors.append(f"{FILENAME_CONTRACT} apply_checklist must be a list with at least 3 steps")

    errors.extend(check_filename_legends(root, adapter=False))
    return errors


def is_hashy_junk_basename(name: str) -> bool:
    """Detect classic stem-pN-<6hex>.ext basenames in asset-manifest paths."""
    base = str(name or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
    return bool(HASHY_BASENAME_RE.fullmatch(base))


def is_robot_key_value_basename(name: str) -> bool:
    """Detect rejected robot key=value stems like pitch-plus-8st_speed-0pct."""
    base = str(name or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
    if not base or is_hashy_junk_basename(base):
        return False
    return bool(ROBOT_KV_BASENAME_RE.search(base))


def check_filename_legends(root: Path, *, adapter: bool = False) -> list[str]:
    """Require per-feature legends with glossary + files; paths must be speakable/safe-twin."""
    errors: list[str] = []
    if adapter:
        base = root / "filename-legends"
        label = ADAPTER_FILENAME_LEGEND_DIR
    else:
        base = root / FILENAME_LEGEND_DIR
        label = FILENAME_LEGEND_DIR

    if not base.is_dir():
        if not adapter:
            errors.append(f"missing filename legends directory: {label}")
        return errors

    json_files = sorted(base.glob("*.json"))
    if not adapter and not json_files:
        errors.append(f"{label} must contain at least one per-feature legend JSON")
        return errors

    for legend_path in json_files:
        try:
            legend = load_json(legend_path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        rel = f"{label}/{legend_path.name}"
        if legend.get("schema_version") != FILENAME_LEGEND_SCHEMA:
            errors.append(f"{rel} must declare {FILENAME_LEGEND_SCHEMA}")
        if not legend.get("feature"):
            errors.append(f"{rel} missing feature id")
        glossary = legend.get("glossary")
        if not isinstance(glossary, list) or len(glossary) < 1:
            errors.append(f"{rel} glossary must be a non-empty list")
        else:
            for index, entry in enumerate(glossary, start=1):
                if not isinstance(entry, dict) or not entry.get("token") or not entry.get("meaning"):
                    errors.append(f"{rel} glossary entry {index} needs token and meaning")
        files = legend.get("files")
        if not isinstance(files, list) or len(files) < 1:
            errors.append(f"{rel} files must be a non-empty list")
            continue
        for index, entry in enumerate(files, start=1):
            if not isinstance(entry, dict):
                errors.append(f"{rel} files entry {index} must be an object")
                continue
            file_path = str(entry.get("path") or "")
            if not file_path:
                errors.append(f"{rel} files entry {index} missing path")
                continue
            if is_hashy_junk_basename(file_path):
                errors.append(
                    f"{rel} files entry {index} uses hashy junk basename: {file_path}"
                )
            if is_robot_key_value_basename(file_path):
                errors.append(
                    f"{rel} files entry {index} uses robot key=value basename: {file_path}"
                )
            identity = entry.get("identity")
            style = str(entry.get("style") or "speakable")
            if identity is not None:
                # Import lazily so validate stays usable when scripts/ is on sys.path.
                try:
                    from scripts.human_filename import build_basename as _build
                except Exception:
                    # Structural-only fallback already covered hashy/robot above.
                    continue
                expected = _build(
                    str(identity),
                    file_path.rsplit(".", 1)[-1] if "." in file_path else "mp3",
                    pitch=entry.get("pitch"),
                    speed_pct=entry.get("speed_pct"),
                    style="safe_twin" if style == "safe_twin" else "speakable",
                )
                basename = file_path.replace("\\", "/").rsplit("/", 1)[-1]
                if basename != expected:
                    errors.append(
                        f"{rel} files entry {index} path {file_path!r} does not match "
                        f"helper output {expected!r}"
                    )
        md_twin = legend_path.with_suffix(".md")
        if not adapter and not md_twin.is_file():
            errors.append(f"missing markdown twin for legend: {label}/{md_twin.name}")
    return errors


def check_asset_manifest_human_paths(
    manifest: dict,
    helper_version: tuple[int, int, int],
    *,
    adapter_root: Path | None = None,
) -> list[str]:
    """For helper >= 0.5.5, reject hashy/robot basenames; enforce feature legends when claimed.

    Historical published blobs are not rewritten; adopters pin 0.5.5+ only when
    new (and migrated) path entries use speakable or safe-twin names. Hash may
    remain as a separate asset field.
    """
    errors: list[str] = []
    if helper_version < (0, 5, 5):
        return errors
    assets = manifest.get("assets") or []
    if not isinstance(assets, list):
        return errors

    legend_index: dict[str, set[str]] = {}
    if adapter_root is not None:
        legend_dir = adapter_root / "filename-legends"
        if legend_dir.is_dir():
            for legend_path in sorted(legend_dir.glob("*.json")):
                try:
                    legend = load_json(legend_path)
                except ValueError:
                    continue
                feature = str(legend.get("feature") or legend_path.stem)
                paths = set()
                for entry in legend.get("files") or []:
                    if isinstance(entry, dict) and entry.get("path"):
                        paths.add(str(entry["path"]).replace("\\", "/"))
                legend_index[feature] = paths

    for index, asset in enumerate(assets, start=1):
        if not isinstance(asset, dict):
            continue
        asset_path = str(asset.get("path") or "")
        if not asset_path:
            continue
        if is_hashy_junk_basename(asset_path):
            errors.append(
                f"asset-manifest path entry {index} uses a hashy junk basename "
                f"(stem-pN-<6hex>.ext): {asset_path}; "
                "use scripts/human_filename.build_basename (hash may remain an asset field)"
            )
        elif is_robot_key_value_basename(asset_path):
            errors.append(
                f"asset-manifest path entry {index} uses a robot key=value basename: "
                f"{asset_path}; use speakable or safe_twin style from scripts/human_filename"
            )
        feature = asset.get("feature")
        if feature and adapter_root is not None:
            feature_id = str(feature)
            if feature_id not in legend_index:
                errors.append(
                    f"asset-manifest path entry {index} claims feature {feature_id!r} "
                    f"but {ADAPTER_FILENAME_LEGEND_DIR}/{feature_id}.json is missing"
                )
            else:
                normalized = asset_path.replace("\\", "/")
                basename = normalized.rsplit("/", 1)[-1]
                allowed = legend_index[feature_id]
                if normalized not in allowed and basename not in allowed:
                    errors.append(
                        f"asset-manifest path entry {index} path {asset_path!r} is not listed "
                        f"in filename legend for feature {feature_id!r}"
                    )
    if adapter_root is not None:
        errors.extend(check_filename_legends(adapter_root, adapter=True))
    return errors



def check_issue_log_contract(root: Path) -> list[str]:
    """Operational issue intake contract for every CGM adopter (not ACS-only)."""
    errors: list[str] = []
    doc = root / ISSUE_LOG_DOC
    if not doc.is_file():
        errors.append(f"missing {ISSUE_LOG_DOC}")
    path = root / ISSUE_LOG_CONTRACT
    try:
        contract = load_json(path)
    except ValueError as exc:
        return errors + [str(exc)]

    if contract.get("schema_version") != ISSUE_LOG_SCHEMA:
        errors.append(f"{ISSUE_LOG_CONTRACT} schema_version must be {ISSUE_LOG_SCHEMA}")
    audience = str(contract.get("audience") or "").lower()
    if "every" not in audience and "adopter" not in audience:
        errors.append(f"{ISSUE_LOG_CONTRACT} audience must name every CGM adopter")

    steps = contract.get("intake_steps")
    if not isinstance(steps, list) or len(steps) < 4:
        errors.append(f"{ISSUE_LOG_CONTRACT} intake_steps must list at least 4 steps")
    else:
        by_id = {str(s.get("id")): s for s in steps if isinstance(s, dict)}
        for step_id in ISSUE_LOG_REQUIRED_STEP_IDS:
            step = by_id.get(step_id)
            if not isinstance(step, dict):
                errors.append(f"{ISSUE_LOG_CONTRACT} missing intake step id {step_id}")
            elif step.get("required") is not True:
                errors.append(f"{ISSUE_LOG_CONTRACT} intake step {step_id} must be required")

    forbidden = contract.get("forbidden_ticket_shapes")
    if not isinstance(forbidden, list) or len(forbidden) < 2:
        errors.append(f"{ISSUE_LOG_CONTRACT} forbidden_ticket_shapes must list ACS-only / single-adopter bans")
    else:
        joined = " ".join(str(x).lower() for x in forbidden)
        if "acs-only" not in joined and "acs only" not in joined:
            errors.append(f"{ISSUE_LOG_CONTRACT} forbidden_ticket_shapes must ban ACS-only tickets")
        if "single-adopter" not in joined and "single adopter" not in joined:
            errors.append(f"{ISSUE_LOG_CONTRACT} forbidden_ticket_shapes must ban single-adopter tickets")

    done_when = contract.get("done_when")
    if not isinstance(done_when, list) or len(done_when) < 3:
        errors.append(f"{ISSUE_LOG_CONTRACT} done_when must be a list with at least 3 items")

    must_include = {str(x) for x in contract.get("done_when_must_include", [])}
    for needle in ("validate_needles", "adopter_facing_docs"):
        if needle not in must_include:
            errors.append(f"{ISSUE_LOG_CONTRACT} done_when_must_include must contain {needle}")

    needles = contract.get("validate_needles")
    if not isinstance(needles, list) or "intake_steps" not in needles:
        errors.append(f"{ISSUE_LOG_CONTRACT} validate_needles must include intake_steps")

    template = root / ".github" / "ISSUE_TEMPLATE" / "operational.yml"
    if not template.is_file():
        errors.append("missing .github/ISSUE_TEMPLATE/operational.yml")
    else:
        body = template.read_text(encoding="utf-8").lower()
        for needle in ("reproduce", "every cgm adopter", "acs-only", "validate"):
            if needle not in body:
                errors.append(f"operational issue template must mention {needle}")

    return errors


def check_writing_contract(root: Path) -> list[str]:
    """Presence check for writing modules + soft router + always-on HSW inject (every adopter)."""
    errors: list[str] = []
    if not (root / HSW_VERIFY_HELPER_PATH).is_file():
        errors.append(f"missing {HSW_VERIFY_HELPER_PATH}")
    version_path = root / "system-version.json"
    try:
        version = load_json(version_path)
    except ValueError as exc:
        return [str(exc)]

    modules = set(version.get("modules", []))
    for module in WRITING_MODULES:
        if module not in modules:
            errors.append(f"system-version.json modules missing required writing module: {module}")
        skill = root / "modules" / module / "SKILL.md"
        if not skill.is_file():
            errors.append(f"missing writing module entry point: {skill.relative_to(root)}")
        elif len(skill.read_text(encoding="utf-8").splitlines()) > 500:
            errors.append(f"writing module entry point is over 500 lines: {skill.relative_to(root)}")

    router_doc = root / WRITING_ROUTER_DOC
    if not router_doc.is_file():
        errors.append(f"missing soft writing router: {WRITING_ROUTER_DOC}")

    contract_path = root / WRITING_ROUTER_CONTRACT
    try:
        contract = load_json(contract_path)
    except ValueError as exc:
        errors.append(str(exc))
        return errors

    if contract.get("schema_version") != WRITING_ROUTER_SCHEMA:
        errors.append(f"{WRITING_ROUTER_CONTRACT} must declare {WRITING_ROUTER_SCHEMA}")
    if contract.get("enforcement") != "soft":
        errors.append(f"{WRITING_ROUTER_CONTRACT} enforcement must be soft")
    required_modules = contract.get("required_writing_modules")
    if list(required_modules or []) != list(WRITING_MODULES):
        errors.append(
            f"{WRITING_ROUTER_CONTRACT} required_writing_modules must be exactly {list(WRITING_MODULES)}"
        )

    routes = contract.get("routes")
    if not isinstance(routes, list):
        errors.append(f"{WRITING_ROUTER_CONTRACT} routes must be a list")
        return errors
    by_id = {route.get("id"): route for route in routes if isinstance(route, dict)}
    for route_id in REQUIRED_ROUTER_ROUTE_IDS:
        route = by_id.get(route_id)
        if not route:
            errors.append(f"{WRITING_ROUTER_CONTRACT} missing route id: {route_id}")
            continue
        if not isinstance(route.get("surfaces"), list) or not route.get("surfaces"):
            errors.append(f"{WRITING_ROUTER_CONTRACT} route {route_id} needs non-empty surfaces")
        if not route.get("load"):
            errors.append(f"{WRITING_ROUTER_CONTRACT} route {route_id} missing load")

    readme_route = by_id.get("readme_product_entry") or {}
    if readme_route.get("load") != "writing-direction":
        errors.append(f"{WRITING_ROUTER_CONTRACT} readme_product_entry must load writing-direction")
    if readme_route.get("required_load") is not True:
        errors.append(f"{WRITING_ROUTER_CONTRACT} readme_product_entry required_load must be true")
    prose_route = by_id.get("github_and_docs_prose") or {}
    if prose_route.get("load") != "human-sounding-writing":
        errors.append(f"{WRITING_ROUTER_CONTRACT} github_and_docs_prose must load human-sounding-writing")
    if prose_route.get("required_load") is not True:
        errors.append(f"{WRITING_ROUTER_CONTRACT} github_and_docs_prose required_load must be true")

    filename_route = by_id.get("generated_artifact_filenames") or {}
    if filename_route.get("load") != "human-output-naming":
        errors.append(
            f"{WRITING_ROUTER_CONTRACT} generated_artifact_filenames must load human-output-naming"
        )
    if filename_route.get("required_load") is not True:
        errors.append(
            f"{WRITING_ROUTER_CONTRACT} generated_artifact_filenames required_load must be true"
        )
    filename_surfaces = {str(s).lower() for s in filename_route.get("surfaces", [])}
    for needle in ("generated artifact", "asset-manifest", "committed media", "filename legend"):
        if not any(needle in surface for surface in filename_surfaces):
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} generated_artifact_filenames surfaces must mention {needle}"
            )
    surfaces = {str(s).lower() for s in prose_route.get("surfaces", [])}
    for needle in (
        "pull request",
        "issue title",
        "issue log",
        "commit message",
        "commit subject",
        "non-readme",
        "changelog",
        "html report",
        "compare html",
        "compare ui",
        "human-readable html",
    ):
        if not any(needle in surface for surface in surfaces):
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} github_and_docs_prose surfaces must mention {needle}"
            )
    if prose_route.get("default_on") is not True:
        errors.append(
            f"{WRITING_ROUTER_CONTRACT} github_and_docs_prose default_on must be true"
        )

    human_default = contract.get("human_facing_default")
    if not isinstance(human_default, dict):
        errors.append(f"{WRITING_ROUTER_CONTRACT} must declare human_facing_default object")
    else:
        if human_default.get("load") != "human-sounding-writing":
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} human_facing_default.load must be human-sounding-writing"
            )
        if human_default.get("required_load") is not True:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} human_facing_default.required_load must be true"
            )
        if human_default.get("default_on") is not True:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} human_facing_default.default_on must be true"
            )
        covers = {str(c).lower() for c in human_default.get("covers", [])}
        for needle in ("every human-facing", "html report", "compare"):
            if not any(needle in cover for cover in covers):
                errors.append(
                    f"{WRITING_ROUTER_CONTRACT} human_facing_default.covers must mention {needle}"
                )

    if contract.get("application") != "must_load":
        errors.append(f"{WRITING_ROUTER_CONTRACT} application must be must_load")

    checklist = contract.get("apply_checklist")
    if not isinstance(checklist, list) or len(checklist) < 3:
        errors.append(f"{WRITING_ROUTER_CONTRACT} apply_checklist must be a list with at least 3 steps")

    not_routed = contract.get("not_routed")
    if not isinstance(not_routed, list):
        errors.append(f"{WRITING_ROUTER_CONTRACT} not_routed must be a list")
    else:
        for item in not_routed:
            surface = str((item or {}).get("surface", "")).lower() if isinstance(item, dict) else str(item).lower()
            if "commit" in surface:
                errors.append(
                    f"{WRITING_ROUTER_CONTRACT} commit surfaces must be routed to human-sounding-writing, not not_routed"
                )

    entry = contract.get("acs_verify_entrypoint")
    if not isinstance(entry, dict) or not entry.get("writing") or not entry.get("full_helper"):
        errors.append(f"{WRITING_ROUTER_CONTRACT} must declare acs_verify_entrypoint.writing and full_helper")

    inject = contract.get("acs_prompt_inject")
    if not isinstance(inject, dict):
        errors.append(f"{WRITING_ROUTER_CONTRACT} must declare acs_prompt_inject object")
    else:
        instruction = inject.get("instruction")
        if not isinstance(instruction, str) or "MUST load" not in instruction:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.instruction must mention MUST load"
            )
        if "commit" not in str(instruction).lower():
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.instruction must mention commit surfaces"
            )
        lowered_instruction = str(instruction).lower()
        if "filename" not in lowered_instruction and "human-output-naming" not in lowered_instruction:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.instruction must mention output filenames"
            )
        if "legend" not in lowered_instruction and "speakable" not in lowered_instruction:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.instruction must mention speakable names or filename legends"
            )
        if "html report" not in lowered_instruction and "compare html" not in lowered_instruction:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.instruction must mention HTML reports or compare HTML"
            )
        if "every human-facing" not in lowered_instruction and "default" not in lowered_instruction:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.instruction must mention every human-facing default"
            )
        if "per-report" not in lowered_instruction and "optional" not in lowered_instruction:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.instruction must forbid per-report/optional HSW skip"
            )
        fields = inject.get("fields")
        if not isinstance(fields, list) or "routes" not in fields:
            errors.append(f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.fields must include routes")
        if not isinstance(fields, list) or "human_facing_default" not in fields:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.fields must include human_facing_default"
            )
        when = str(inject.get("when") or "").lower()
        if "html" not in when and "compare" not in when:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.when must mention HTML or compare deliverables"
            )
        if inject.get("always_on") is not True:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.always_on must be true"
            )
        if inject.get("opt_in_forbidden") is not True:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.opt_in_forbidden must be true"
            )
        audience = str(inject.get("audience") or "").lower()
        if "every" not in audience and "adopter" not in audience and "all" not in audience:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.audience must name every CGM adopter"
            )
        inject_surfaces = {str(s).lower() for s in inject.get("surfaces", [])}
        for needle in ("html report", "compare html", "compare ui"):
            if not any(needle in surface for surface in inject_surfaces):
                errors.append(
                    f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.surfaces must mention {needle}"
                )
        system_block = inject.get("system_block")
        if not isinstance(system_block, str) or len(system_block.strip()) < 80:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.system_block must be a non-trivial always-on paste block"
            )
        else:
            lowered_block = system_block.lower()
            for needle in ("always-on", "human-sounding-writing", "skill.md", "opt-in is forbidden"):
                if needle not in lowered_block:
                    errors.append(
                        f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.system_block must mention {needle}"
                    )
            if "html" not in lowered_block:
                errors.append(
                    f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.system_block must mention HTML surfaces"
                )
        if "system_block" not in (fields or []):
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.fields must include system_block"
            )
        if "always_on" not in (fields or []):
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.fields must include always_on"
            )
        lowered_instruction = str(instruction).lower() if isinstance(instruction, str) else ""
        if "always_on" not in lowered_instruction and "always-on" not in lowered_instruction:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.instruction must mention always_on / always-on"
            )
        if "adopter" not in lowered_instruction:
            errors.append(
                f"{WRITING_ROUTER_CONTRACT} acs_prompt_inject.instruction must mention every CGM adopter"
            )

    alias = contract.get("always_on_system_block")
    if not isinstance(alias, dict) or alias.get("always_on") is not True:
        errors.append(
            f"{WRITING_ROUTER_CONTRACT} must declare always_on_system_block with always_on true"
        )

    if isinstance(entry, dict) and not entry.get("hsw_automation"):
        errors.append(
            f"{WRITING_ROUTER_CONTRACT} acs_verify_entrypoint must declare hsw_automation"
        )

    errors.extend(check_human_output_naming_contract(root))
    return errors


def _writing_verify_line(root: Path, errors: list[str], mode: str) -> str:
    wd = (root / "modules" / "writing-direction" / "SKILL.md").is_file()
    hsw = (root / "modules" / "human-sounding-writing" / "SKILL.md").is_file()
    hon = (root / "modules" / "human-output-naming" / "SKILL.md").is_file()
    router = (root / WRITING_ROUTER_CONTRACT).is_file() and (root / WRITING_ROUTER_DOC).is_file()
    status = "OK" if not errors else "FAIL"
    return (
        f"CGM_VERIFY mode={mode} status={status} "
        f"writing_direction={'present' if wd else 'missing'} "
        f"human_sounding_writing={'present' if hsw else 'missing'} "
        f"human_output_naming={'present' if hon else 'missing'} "
        f"writing_router={'present' if router else 'missing'}"
    )


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
    if human_output.get("version") != "content-generation.readme-contract.v2":
        errors.append("system-version.json must declare content-generation.readme-contract.v2")
    for field in ("template", "playbook", "image_guide", "prior_work"):
        if not human_output.get(field):
            errors.append(f"system-version.json human_output_contract missing {field}")
    if not human_output.get("research"):
        errors.append("system-version.json human_output_contract missing research")
    if not human_output.get("brand_direction"):
        errors.append("system-version.json human_output_contract missing brand_direction")
    for field in ("product_definition", "system_design", "test_design", "provenance", "reverse_analysis"):
        if not human_output.get(field):
            errors.append(f"system-version.json human_output_contract missing {field}")
    claim_contract = version.get("claim_explanation_contract", {})
    if claim_contract.get("version") != "content-generation.claim-evidence.v2":
        errors.append("system-version.json must declare content-generation.claim-evidence.v2")
    expected_claim_fields = ["claim", "source", "status", "supports", "limits", "source_revision", "recorded_at"]
    if claim_contract.get("fields") != expected_claim_fields:
        errors.append("system-version.json claim_explanation_contract fields do not match the v2 contract")
    if claim_contract.get("truth_boundary") != "citation establishes traceability, not truth":
        errors.append("system-version.json claim_explanation_contract must preserve the citation truth boundary")
    if claim_contract.get("required_for_helper_version") != "0.4.0":
        errors.append("system-version.json claim_explanation_contract must be required from 0.4.0")
    if claim_contract.get("optional_fields") != ["valid_time"] or not claim_contract.get("temporal_model"):
        errors.append("system-version.json claim_explanation_contract must define the valid-time model")
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
        "project-brief.v2.schema.json",
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

    for relative_path in version.get("helper_contract_files", []):
        if not (root / relative_path).is_file():
            errors.append(f"missing versioned helper contract file: {relative_path}")

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
    errors.extend(check_writing_contract(root))
    errors.extend(check_issue_log_contract(root))
    # Filename contract is also required on full helper (fail closed if claimed/missing).
    # check_writing_contract already extends it; keep an explicit call only if writing skipped.
    return errors



ADOPTER_README_FORBIDDEN_SUBSTRINGS = (
    "content-generation-modules",
)
ADOPTER_README_FORBIDDEN_CGM = re.compile(r"\bCGM\b")
ADOPTER_README_FORBIDDEN_HEADINGS = re.compile(
    r"(?im)^##\s+Image generation and use\s*$"
)


def check_adopter_readme_product_only(readme_text: str) -> list[str]:
    """Soft-contract deterministic guard for target README leakage (0.5.4+).

    Forbids promoting CGM / content-generation-modules and the exact helper
    heading that narrates image generation. Does not grade writing style.
    """
    errors: list[str] = []
    lowered_hits = []
    for needle in ADOPTER_README_FORBIDDEN_SUBSTRINGS:
        if needle in readme_text:
            lowered_hits.append(needle)
    if lowered_hits:
        errors.append(
            "adopter README must not cite or promote the helper ("
            + ", ".join(lowered_hits)
            + "); keep the README about the target product"
        )
    if ADOPTER_README_FORBIDDEN_CGM.search(readme_text):
        errors.append(
            "adopter README must not cite or promote CGM; keep the README about the target product"
        )
    if ADOPTER_README_FORBIDDEN_HEADINGS.search(readme_text):
        errors.append(
            "adopter README must not include an 'Image generation and use' section; "
            "put image provenance in .content-system/asset-manifest instead"
        )
    return errors


def check_adapter(adapter: Path, project_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    required = {
        "system-version.json": "content-generation.adapter.v1",
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
    project_path = adapter / "project-brief.json"
    try:
        project = load_json(project_path)
    except ValueError as exc:
        errors.append(str(exc))
    helper_version = _version_tuple(system.get("helper_version"))
    brief_version = project.get("schema_version")
    if brief_version not in {"content-generation.project-brief.v1", "content-generation.project-brief.v2"}:
        errors.append("project-brief.json must declare content-generation.project-brief.v1 or v2")
    if helper_version >= (0, 4, 0) and brief_version != "content-generation.project-brief.v2":
        errors.append("helper versions 0.4.0 and later require project-brief.v2")
    for field in ("project", "audience", "problem", "solution", "evidence", "boundaries"):
        if not project.get(field):
            errors.append(f"adapter project-brief.json missing {field}")
    if brief_version == "content-generation.project-brief.v2":
        readme_text = None
        if project_root and (project_root / "README.md").is_file():
            readme_text = (project_root / "README.md").read_text(encoding="utf-8")
        errors.extend(check_project_brief_v2(project, readme_text))

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
    if helper_version >= (0, 3, 0):
        errors.extend(check_narrative_assets(visual, manifest, project_root))
    errors.extend(check_asset_manifest_human_paths(manifest, helper_version, adapter_root=adapter))
    if project_root and (project_root / "README.md").is_file():
        adopter_readme = (project_root / "README.md").read_text(encoding="utf-8")
        if helper_version >= (0, 5, 4):
            errors.extend(check_adopter_readme_product_only(adopter_readme))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the content-generation helper contract. "
            "Adopter/hotload: --mode writing checks writing-direction + human-sounding-writing + soft router + always-on inject."
        )
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--adapter", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument(
        "--mode",
        choices=("helper", "writing"),
        default="helper",
        help="helper=full CGM contract (default); writing=adopter entrypoint for writing modules + soft router + always-on inject",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.mode == "writing":
        errors = check_writing_contract(root)
        print(_writing_verify_line(root, errors, "writing"))
        if errors:
            print("INVALID")
            for error in errors:
                print(f"- {error}")
            return 1
        print("VALID: content-generation-modules writing contract")
        return 0

    errors = check(root)
    if args.adapter:
        errors.extend(
            check_adapter(
                args.adapter.resolve(),
                args.project_root.resolve() if args.project_root else None,
            )
        )
    # Always emit CGM_VERIFY for ACS parsers on helper runs too.
    print(_writing_verify_line(root, errors, "helper"))
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID: content-generation-modules contract" + (" and target adapter" if args.adapter else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
