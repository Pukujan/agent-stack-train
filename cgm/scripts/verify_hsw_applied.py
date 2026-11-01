#!/usr/bin/env python3
"""Fail-closed HSW automation check for every CGM adopter.

Confirms the pinned helper declares always-on HSW inject + human-facing default
for prose. HTML pages are not routed to HSW (agent-stack-train#81), so this no
longer scans HTML.

This is NOT an NLP quality grader. Passing means the always-on contract is
present. Failing means automation is incomplete.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WRITING_ROUTER_CONTRACT = "docs/writing-routing.json"
WRITING_ROUTER_SCHEMA = "content-generation.writing-routing.v1"
HSW_SKILL = "modules/human-sounding-writing/SKILL.md"

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
        for needle in ("every human-facing", "github and docs prose"):
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
    for needle in ("pull request", "commit"):
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
            "opt-in is forbidden",
        ):
            if needle not in lowered:
                errors.append(f"acs_prompt_inject.system_block must mention {needle}")
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

    # The prose route covers GitHub prose and commits, and no longer HTML pages (agent-stack-train#81).
    routes = {r.get("id"): r for r in contract.get("routes", []) if isinstance(r, dict)}
    prose = routes.get("github_and_docs_prose") or {}
    route_surfaces = {str(s).lower() for s in prose.get("surfaces", [])}
    for needle in ("pull request", "commit message"):
        if not any(needle in surface for surface in route_surfaces):
            errors.append(f"github_and_docs_prose surfaces must mention {needle}")
    for surface in route_surfaces:
        if "html" in surface:
            errors.append(
                f"github_and_docs_prose must not route the HTML surface {surface!r} to hsw (agent-stack-train#81)"
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify HSW always-on automation for any CGM adopter (prose surfaces only)."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="CGM checkout root")
    parser.add_argument(
        "--mode",
        choices=("contract",),
        default="contract",
        help="contract=always-on inject + human_facing_default (the only mode; HTML scanning was retired in #81)",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()

    errors = check_always_on_contract(root)

    status = "OK" if not errors else "FAIL"
    print(
        f"HSW_VERIFY mode={args.mode} status={status} "
        f"always_on_inject={'present' if not any('always_on' in e and 'must be true' in e for e in errors) else 'missing'}"
    )
    if errors:
        print("INVALID: HSW automation check failed")
        for error in errors:
            print(f"- {error}")
        print(
            "Meaning: pin is missing the always-on inject contract. "
            "Soft = not a full NLP human-voice proof."
        )
        return 1

    print("VALID: HSW always-on contract OK")
    print(
        "Meaning: always-on inject + human_facing_default present. "
        "This does not prove the prose 'sounds human' — only that automation gates passed."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
