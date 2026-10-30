#!/usr/bin/env python3
"""Fail-closed HSW automation check for every CGM adopter.

Confirms the pinned helper declares always-on HSW inject + human-facing default,
and optionally scans human-facing HTML for a short denylist of known AI-jargon /
tool-dump tells.

This is NOT an NLP quality grader. Passing means the always-on contract is
present and (if --html was given) obvious tell patterns were not found.
Failing means automation is incomplete or the HTML still looks tool/jargon-heavy.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

WRITING_ROUTER_CONTRACT = "docs/writing-routing.json"
WRITING_ROUTER_SCHEMA = "content-generation.writing-routing.v1"
HSW_SKILL = "modules/human-sounding-writing/SKILL.md"

# Conservative denylist: high-signal AI-jargon words (error severity in HSW rules)
# plus tool-dump / agent-internals patterns common in un-scrubbed compare HTML.
# False positives should stay few; absence of a hit does not prove human voice.
JARGON_WORDS = (
    r"delve",
    r"underscore(?:s|d|ing)?",
    r"showcase(?:s|d|ing)?",
    r"tapestry",
    r"intricate(?:s|ly)?",
    r"realm",
    r"pivotal",
    r"meticulous(?:ly)?",
    r"testament",
    r"multifaceted",
    r"groundbreaking",
    r"seamless(?:ly)?",
    r"holistic",
    r"leverag(?:e|es|ed|ing)",
    r"synerg(?:y|ies|istic)",
    r"paradigm",
    r"robust(?:ly|ness)?",
    r"cutting[- ]edge",
    r"game[- ]changer",
    r"unlock(?:s|ed|ing)?\s+(?:the\s+)?(?:power|potential|full)",
)

TOOL_DUMP_PATTERNS = (
    # Agent/tool narration dumps that should not ship in human-facing compare HTML
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

VISIBLE_TEXT_RE = re.compile(
    r"(?is)<(?:script|style|noscript)\b[^>]*>.*?</(?:script|style|noscript)>|"
    r"<!--.*?-->|"
    r"<[^>]+>"
)


def _load_contract(root: Path) -> tuple[dict | None, list[str]]:
    path = root / WRITING_ROUTER_CONTRACT
    errors: list[str] = []
    if not path.is_file():
        return None, [f"missing {WRITING_ROUTER_CONTRACT}"]
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"{WRITING_ROUTER_CONTRACT} is not valid JSON: {exc}"]
    if not isinstance(contract, dict):
        return None, [f"{WRITING_ROUTER_CONTRACT} must be a JSON object"]
    return contract, errors


def check_always_on_contract(root: Path) -> list[str]:
    """Require always-on inject + human_facing_default for every CGM adopter."""
    errors: list[str] = []
    if not (root / HSW_SKILL).is_file():
        errors.append(f"missing {HSW_SKILL}")

    contract, load_errors = _load_contract(root)
    errors.extend(load_errors)
    if contract is None:
        return errors

    if contract.get("schema_version") != WRITING_ROUTER_SCHEMA:
        errors.append(
            f"{WRITING_ROUTER_CONTRACT} schema_version must be {WRITING_ROUTER_SCHEMA}"
        )

    human_default = contract.get("human_facing_default")
    if not isinstance(human_default, dict):
        errors.append(f"{WRITING_ROUTER_CONTRACT} must declare human_facing_default")
    else:
        if human_default.get("load") != "human-sounding-writing":
            errors.append("human_facing_default.load must be human-sounding-writing")
        if human_default.get("required_load") is not True:
            errors.append("human_facing_default.required_load must be true")
        if human_default.get("default_on") is not True:
            errors.append("human_facing_default.default_on must be true")
        covers = {str(c).lower() for c in human_default.get("covers", [])}
        for needle in ("every human-facing", "html report", "compare"):
            if not any(needle in cover for cover in covers):
                errors.append(f"human_facing_default.covers must mention {needle}")

    inject = contract.get("acs_prompt_inject")
    if not isinstance(inject, dict):
        errors.append(f"{WRITING_ROUTER_CONTRACT} must declare acs_prompt_inject")
        return errors

    if inject.get("always_on") is not True:
        errors.append("acs_prompt_inject.always_on must be true")
    if inject.get("opt_in_forbidden") is not True:
        errors.append("acs_prompt_inject.opt_in_forbidden must be true")

    audience = str(inject.get("audience") or "").lower()
    if "every" not in audience and "adopter" not in audience and "all" not in audience:
        errors.append(
            "acs_prompt_inject.audience must name every CGM adopter (not ACS-only)"
        )

    surfaces = {str(s).lower() for s in inject.get("surfaces", [])}
    for needle in ("html report", "compare html", "compare ui"):
        if not any(needle in surface for surface in surfaces):
            errors.append(f"acs_prompt_inject.surfaces must mention {needle}")

    system_block = inject.get("system_block")
    if not isinstance(system_block, str) or len(system_block.strip()) < 80:
        errors.append("acs_prompt_inject.system_block must be a non-trivial always-on paste block")
    else:
        lowered = system_block.lower()
        for needle in (
            "always-on",
            "human-sounding-writing",
            "skill.md",
            "html",
            "opt-in is forbidden",
        ):
            if needle not in lowered:
                errors.append(f"acs_prompt_inject.system_block must mention {needle}")
        if "compare" not in lowered and "html report" not in lowered:
            errors.append("acs_prompt_inject.system_block must mention HTML/compare surfaces")
        if "marketing intro" not in lowered:
            errors.append(
                "acs_prompt_inject.system_block must say a marketing intro site "
                "is not the README exception"
            )

    instruction = str(inject.get("instruction") or "")
    if "MUST load" not in instruction:
        errors.append("acs_prompt_inject.instruction must mention MUST load")
    lowered_instruction = instruction.lower()
    if "always_on" not in lowered_instruction and "always-on" not in lowered_instruction:
        errors.append("acs_prompt_inject.instruction must mention always_on / always-on")
    if "every cgm adopter" not in lowered_instruction and "every adopter" not in lowered_instruction:
        # allow "every CGM adopter" phrasing variants
        if "every" not in lowered_instruction or "adopter" not in lowered_instruction:
            errors.append(
                "acs_prompt_inject.instruction must say the rule applies to every CGM adopter"
            )

    alias = contract.get("always_on_system_block")
    if not isinstance(alias, dict) or alias.get("always_on") is not True:
        errors.append(
            f"{WRITING_ROUTER_CONTRACT} must declare always_on_system_block with always_on true"
        )

    entry = contract.get("acs_verify_entrypoint")
    if not isinstance(entry, dict) or not entry.get("hsw_automation"):
        errors.append(
            f"{WRITING_ROUTER_CONTRACT} acs_verify_entrypoint must declare hsw_automation"
        )

    # HTML surfaces on the prose route
    routes = {r.get("id"): r for r in contract.get("routes", []) if isinstance(r, dict)}
    prose = routes.get("github_and_docs_prose") or {}
    route_surfaces = {str(s).lower() for s in prose.get("surfaces", [])}
    for needle in ("html report", "compare html", "compare ui"):
        if not any(needle in surface for surface in route_surfaces):
            errors.append(f"github_and_docs_prose surfaces must mention {needle}")

    return errors


def extract_visible_text(html: str) -> str:
    """Strip tags/scripts roughly; good enough for conservative tell scanning."""
    text = VISIBLE_TEXT_RE.sub(" ", html)
    text = re.sub(r"\s+", " ", text)
    return text


def scan_html_tells(html_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        raw = html_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [f"cannot read HTML: {exc}"]

    visible = extract_visible_text(raw)
    # Also scan raw for tool-dump markers that may live in attributes/comments
    haystacks = (("visible text", visible), ("raw html", raw))

    jargon_re = re.compile(r"\b(?:" + "|".join(JARGON_WORDS) + r")\b", re.I)
    for label, hay in haystacks:
        if label == "raw html":
            continue  # jargon only on visible text to reduce attribute FPs
        hits = sorted({m.group(0).lower() for m in jargon_re.finditer(hay)})
        if hits:
            preview = ", ".join(hits[:8])
            more = f" (+{len(hits) - 8} more)" if len(hits) > 8 else ""
            errors.append(
                f"HTML jargon tell(s) in {label} of {html_path.name}: {preview}{more}"
            )

    for pattern in TOOL_DUMP_PATTERNS:
        if re.search(pattern, raw, flags=re.I):
            errors.append(
                f"HTML tool-dump / agent-internals tell in {html_path.name}: /{pattern}/"
            )
            # One hit per pattern is enough; keep going to list distinct patterns
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify HSW always-on automation for any CGM adopter. "
            "Optionally scan human-facing HTML for known jargon/tool-dump tells."
        )
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="CGM checkout root")
    parser.add_argument(
        "--html",
        type=Path,
        action="append",
        default=[],
        help="Human-facing HTML artifact to scan (repeatable). Example: compare Pages HTML.",
    )
    parser.add_argument(
        "--mode",
        choices=("contract", "acs-html", "html"),
        default="contract",
        help=(
            "contract=always-on inject + human_facing_default only (default); "
            "acs-html/html=also require at least one --html path and scan it"
        ),
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()

    errors = check_always_on_contract(root)

    html_paths = [p.resolve() for p in (args.html or [])]
    if args.mode in {"acs-html", "html"} and not html_paths:
        errors.append("--mode acs-html/html requires at least one --html path")

    for html_path in html_paths:
        if not html_path.is_file():
            errors.append(f"HTML path does not exist: {html_path}")
            continue
        errors.extend(scan_html_tells(html_path))

    status = "OK" if not errors else "FAIL"
    html_note = f" html_files={len(html_paths)}" if html_paths or args.mode in {"acs-html", "html"} else ""
    print(
        f"HSW_VERIFY mode={args.mode} status={status} "
        f"always_on_inject={'present' if not any('always_on' in e and 'must be true' in e for e in errors) else 'missing'}"
        f"{html_note}"
    )
    if errors:
        print("INVALID: HSW automation check failed")
        for error in errors:
            print(f"- {error}")
        print(
            "Meaning: pin is missing the always-on inject contract, or given HTML still "
            "has known AI-jargon / tool-dump tells. Soft = not a full NLP human-voice proof."
        )
        return 1

    print("VALID: HSW always-on contract OK" + (" and HTML tell scan clean" if html_paths else ""))
    print(
        "Meaning: always-on inject + human_facing_default present"
        + ("; no denylist hits in given HTML" if html_paths else "")
        + ". This does not prove the prose 'sounds human' — only that automation gates passed."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
