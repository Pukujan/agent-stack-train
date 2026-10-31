#!/usr/bin/env python3
"""Validate multi-agent hotload pack: files, pins, FULL CGM validate_content_system, failover."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None  # type: ignore

MODULE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import claude_bridge  # noqa: E402  (sibling script; stdlib only)
import dev_root_check  # noqa: E402  (sibling script; stdlib only)
import stack_checkout  # noqa: E402  (sibling script; stdlib only)

REQUIRED_FILES = (
    "README.md",
    "ROLES.md",
    "PROPOSALS.md",
    "HOTLOAD.md",
    "BEHAVIOR.md",
    "NOTES.md",
    "module.json",
    "schema/assignment.schema.json",
    "examples/assignment.example.json",
    "scripts/acs_install.py",
    "scripts/hotload_check.py",
    "scripts/watchdog_check.py",
    "scripts/seat_protocol.py",
    "scripts/dev_root_check.py",
    "scripts/stack_checkout.py",
    "scripts/claude_bridge.py",
    "scripts/claude_guard.py",
    "workflow-stubs/watchdog.yml",
)

# ACS-owned boot rule; claude_bridge.py owns it so the CLAUDE.md region and
# PROMPT_INJECT.md carry the same text.
DEV_ROOT_RULE = claude_bridge.DEV_ROOT_RULE


def check_required_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).is_file()]


def console_safe(text: str) -> str:
    """ASCII-safe for Windows cp1252 consoles (Unicode arrows crash print)."""
    return (
        text.replace("→", "->")
        .replace("←", "<-")
        .replace("⇒", "=>")
        .replace("—", "--")
        .replace("–", "-")
        .replace(" ", " ")
    )


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8-sig") as fh:
        return json.load(fh)


def validate_failover_watchdog(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["assignment must be an object"]
    bf = data.get("boss_failover")
    ttl = None
    if not isinstance(bf, dict):
        errors.append("boss_failover: required object missing")
    else:
        ttl = bf.get("lease_ttl_minutes")
        if not isinstance(ttl, (int, float)) or ttl < 15 or ttl > 120:
            errors.append(
                "boss_failover.lease_ttl_minutes: must be a number in 15..120 "
                "(default 30; short leases OK)"
            )
        if "lease_ttl_hours" in bf:
            errors.append(
                "boss_failover.lease_ttl_hours: removed — use lease_ttl_minutes "
                "(default 30; range 15–120)"
            )
        check_in = bf.get("check_in")
        if not isinstance(check_in, dict) or "mechanism" not in check_in:
            errors.append("boss_failover.check_in.mechanism: required")
        elif check_in.get("mechanism") not in ("issue_comment", "claim_file"):
            errors.append("boss_failover.check_in.mechanism: must be issue_comment or claim_file")
        if "standby" in bf and not isinstance(bf.get("standby"), list):
            errors.append("boss_failover.standby: must be an array when present")
        if "claim_queue" in bf and not isinstance(bf.get("claim_queue"), list):
            errors.append("boss_failover.claim_queue: must be an array when present (FIFO)")
        elif isinstance(bf.get("claim_queue"), list):
            for i, item in enumerate(bf["claim_queue"]):
                if not isinstance(item, str) or not item.strip():
                    errors.append(f"boss_failover.claim_queue[{i}]: must be non-empty string agent_id")
    wd = data.get("watchdog")
    if not isinstance(wd, dict):
        errors.append("watchdog: required object missing (agent-less liveness)")
    else:
        interval = wd.get("watchdog_interval_minutes")
        if not isinstance(interval, (int, float)) or interval < 5 or interval > 30:
            errors.append("watchdog.watchdog_interval_minutes: must be 5..30 (~10m typical)")
        idle = wd.get("idle_window")
        if not isinstance(idle, dict) or not isinstance(idle.get("minutes"), (int, float)):
            errors.append("watchdog.idle_window.minutes: required number")
        runner = wd.get("runner")
        if runner not in ("cron", "github_action", "script"):
            errors.append("watchdog.runner: must be cron|github_action|script (agent-less; no LLM)")
        if isinstance(ttl, (int, float)) and isinstance(interval, (int, float)):
            if interval >= ttl:
                errors.append(
                    "watchdog.watchdog_interval_minutes must stay below lease_ttl_minutes "
                    "(watchdog != failover; ~10m liveness only)"
                )
    return errors


REQUIRED_CGM_MODULES = (
    "brand-foundation",
    "content-context",
    "writing-direction",
    "human-sounding-writing",
    "human-output-naming",
    "visual-direction",
    "image-generation",
    "html-demo",
)

REQUIRED_PCM_FEATURES = (
    "checkout_continuity_checkpoints",
    "github_issues_own_task_progression",
    "pr_only_to_default_branch",
    "required_ci_gates",
    "branch_protection_preference",
    "github_auto_merge_preference",
    "fail_closed_on_missing_gates",
    "leaf_parent_dependency_receipts",
)

def load_requires(stack_root: Path | None = None) -> dict:
    """Each component's version, all at the stack checkout's one commit."""
    return stack_checkout.requires(stack_root)


def stack_component(name: str, stack_root: Path | None = None) -> dict:
    return load_requires(stack_root)[name]


def commits_match(head: str, expected: str) -> bool:
    head, expected = head.lower(), expected.lower()
    return bool(head) and bool(expected) and (
        head == expected or head.startswith(expected) or expected.startswith(head)
    )


def dependency_location_problem(path: Path, dev_root: Path | None = None) -> str | None:
    """Refuse a pinned dependency checkout that sits inside the dev root.

    The only things allowed inside the dev root are its top-level main checkouts.
    A pinned dependency clone (``_deps/cgm``, ``.scratch/cgm``, a nested copy...)
    must live under the ACS cache instead.
    """
    root = dev_root if dev_root is not None else dev_root_check.default_dev_root()
    if not dev_root_check.is_inside(path, root):
        return None
    if dev_root_check.is_primary_checkout_path(path, root):
        return None
    return (
        f"dependency checkout {path} is inside the dev root {root} but is not one of its "
        f"main checkouts; move it under {dev_root_check.cache_subdir('deps')} "
        "(see dev_root_check.py)"
    )


def stack_cgm_root(stack_root: Path | None = None) -> Path:
    """The stack checkout's own cgm/ folder."""
    root = (stack_root or stack_checkout.DEFAULT_ROOT).expanduser().resolve()
    return stack_checkout.folder(root, "content-generation-modules")


def discover_cgm_root(explicit: Path | None = None, *, stack_root: Path | None = None) -> Path | None:
    """Resolve CGM: --cgm-root, CGM_ROOT, else the stack checkout's own cgm/ folder.

    An explicit path is returned as-is and checked by ``dependency_location_problem``
    in ``run`` so the operator sees why it was refused. The stack's own folder is
    part of the main checkout, never a dependency clone, so the dev root rule does
    not apply to it.
    """
    for cand in (explicit, os.environ.get("CGM_ROOT")):
        if cand:
            return Path(cand).expanduser().resolve()
    root = stack_cgm_root(stack_root)
    if (root / "scripts" / "validate_content_system.py").is_file() and (root / "system-version.json").is_file():
        return root
    return None


def discover_adopter_root(explicit: Path | None = None) -> Path:
    if explicit is not None:
        return explicit.expanduser().resolve()
    env = os.environ.get("ADOPTER_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    # Default: ACS repository root containing this pack
    return MODULE_ROOT.parents[3].resolve()


def cgm_checkout_sha(cgm_root: Path) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(cgm_root), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return (proc.stdout or "").strip()


def validate_cgm_live(
    cgm_root: Path | None,
    adopter_root: Path,
    *,
    require: bool = True,
    stack_root: Path | None = None,
) -> list[str]:
    """Fail install unless CGM is at the stack commit and validate_content_system prints VALID."""
    errors: list[str] = []
    expected = stack_component("content-generation-modules", stack_root)
    if cgm_root is None:
        if require:
            errors.append(
                f"CGM not found: {stack_cgm_root(stack_root)} is missing; install from a "
                f"complete {stack_checkout.REPOSITORY} checkout"
            )
        return errors

    sha = cgm_checkout_sha(cgm_root)
    if not sha:
        errors.append(f"CGM_ROOT={cgm_root} is not a git checkout (rev-parse HEAD failed)")
        return errors
    if not commits_match(sha, expected["commit"]):
        errors.append(
            f"CGM checkout HEAD={sha} must be the stack commit {expected['commit']}; "
            "use the stack checkout's own cgm/ folder"
        )
        return errors

    # Confirm helper system-version.json reports the stack's version + eight modules
    try:
        version = load_json(cgm_root / "system-version.json")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"CGM system-version.json unreadable: {exc}")
        return errors
    if not isinstance(version, dict) or str(version.get("version")) != expected["version"]:
        errors.append(f"CGM system-version.json version must be {expected['version']}")
    mods = version.get("modules") if isinstance(version, dict) else None
    if not isinstance(mods, list) or set(mods) != set(REQUIRED_CGM_MODULES):
        errors.append(
            "CGM system-version.json modules must be exactly the eight FULL modules "
            "(slim HSW+WD-only fails)"
        )

    adapter = adopter_root / ".content-system"
    if not adapter.is_dir():
        errors.append(
            f"adopter missing .content-system adapter at {adapter} "
            "(FULL CGM install requires target adapter)"
        )
        return errors

    script = cgm_root / "scripts" / "validate_content_system.py"
    if not script.is_file():
        errors.append(f"missing {script}")
        return errors

    try:
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "--root",
                str(cgm_root),
                "--adapter",
                str(adapter),
                "--project-root",
                str(adopter_root),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        errors.append(f"failed to run validate_content_system.py: {exc}")
        return errors

    out = (proc.stdout or "") + (proc.stderr or "")
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    first = lines[0] if lines else ""
    # CGM 0.5.2+ may print CGM_VERIFY before VALID; accept any VALID line.
    valid_line = next((ln for ln in lines if ln.startswith("VALID")), "")
    if proc.returncode != 0 or not valid_line:
        detail = (
            f"(exit={proc.returncode}, first_line={first!r}, valid_line={valid_line!r}). "
            f"Output:\n{out.strip()}"
        )
        errors.append("validate_content_system.py did not return VALID " + detail)
    return errors





def load_writing_routing(cgm_root: Path) -> dict | None:
    path = cgm_root / "docs" / "writing-routing.json"
    if not path.is_file():
        return None
    try:
        data = load_json(path)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


# From PROMPT_INJECT.md in this pack up to the stack root, then into cgm/.
CGM_DOCS_FROM_PACK = "../../../../../cgm/docs"


def render_prompt_inject_md(routing: dict, *, pin_version: str) -> str:
    """Render PROMPT_INJECT.md from CGM writing-routing acs_prompt_inject fields.

    Injects application, human_facing_default, routes, apply_checklist, and
    always-on system_block (see acs_prompt_inject.fields). Paste system_block
    into agent system prompt at session boot — not per-report. HSW is ON by
    default for every human-facing deliverable including HTML reports/compare/
    appendable; basenames -> hon. Opt-in forbidden.
    """
    inject = routing.get("acs_prompt_inject") if isinstance(routing.get("acs_prompt_inject"), dict) else {}
    instruction = str(inject.get("instruction") or "").strip()
    system_block = str(inject.get("system_block") or "").strip()
    when = str(inject.get("when") or "").strip()
    always_on = inject.get("always_on") is True
    opt_in_forbidden = inject.get("opt_in_forbidden") is True
    application = str(routing.get("application") or "must_load").strip()
    checklist = routing.get("apply_checklist") if isinstance(routing.get("apply_checklist"), list) else []
    checklist_md = "\n".join(f"{i+1}. {c}" for i, c in enumerate(checklist))
    hfd = routing.get("human_facing_default") if isinstance(routing.get("human_facing_default"), dict) else {}
    hfd_load = str(hfd.get("load") or "human-sounding-writing")
    hfd_covers = hfd.get("covers") if isinstance(hfd.get("covers"), list) else []
    hfd_exc = hfd.get("exceptions") if isinstance(hfd.get("exceptions"), list) else []
    covers_md = ", ".join(f"`{c}`" for c in hfd_covers) if hfd_covers else "(see CGM writing-routing.json)"
    exc_md = ", ".join(f"`{e}`" for e in hfd_exc) if hfd_exc else "`readme_product_entry`, `generated_artifact_filenames`"
    routes = routing.get("routes") if isinstance(routing.get("routes"), list) else []
    route_rows = []
    for r in routes:
        if not isinstance(r, dict):
            continue
        surfaces = r.get("surfaces") if isinstance(r.get("surfaces"), list) else []
        load = str(r.get("load") or "")
        short = r.get("short_name") if isinstance(r.get("short_name"), list) else []
        short_s = f" ({'/'.join(str(s) for s in short)})" if short else ""
        surf = "; ".join(str(s) for s in surfaces[:8])
        if len(surfaces) > 8:
            surf += "; ..."
        route_rows.append(f"| {surf} | `{load}`{short_s} |")
    routes_table = "\n".join(route_rows) if route_rows else (
        "| README / product entry | `writing-direction` |\n"
        "| Human-facing prose + HTML reports/compare/appendable | `human-sounding-writing` (**hsw**) |\n"
        "| Generated artifact basenames / legends | `human-output-naming` (**hon**) |"
    )
    when_block = when or (
        "After `hotload_check` / CGM_VERIFY succeeds, before writing ANY human-facing "
        "deliverable (GitHub/docs prose, HTML reports, compare HTML/UIs, appendable HTML, "
        "posts, papers) — and before naming generated artifact / media paths."
    )
    return (
        f"# PROMPT_INJECT — acs_prompt_inject (CGM {pin_version})\n\n"
        f"Generated / refreshed by `hotload_check` after full adapter `VALID`.\n"
        f"Source: CGM `docs/writing-routing.json` → `acs_prompt_inject`, from the `cgm/` folder "
        f"of the same agent-stack-train checkout as this pack.\n\n"
        f"Also see: CGM [`docs/ACS_VERIFY.md`]({CGM_DOCS_FROM_PACK}/ACS_VERIFY.md) "
        f"and [`docs/writing-routing.json`]({CGM_DOCS_FROM_PACK}/writing-routing.json).\n\n"
        f"**Version:** CGM `{pin_version}`. It moves with the stack: re-run `hotload_check` "
        f"after updating the agent-stack-train checkout.\n\n"
        f"## application\n\n`{application}` — agents MUST load the listed module before writing each surface.\n\n"
        "## When\n\n"
        f"{when_block}\n\n"
        "## human_facing_default\n\n"
        f"- **load:** `{hfd_load}` (**hsw**) — `required_load: true`, `default_on: true`\n"
        f"- **covers:** {covers_md}\n"
        f"- **exceptions:** {exc_md} (README/product → writing-direction; basenames → **hon**)\n"
        "- **rule:** HSW is ON by default for EVERY human-facing task/output including HTML "
        "reports, compare HTML/UIs, and appendable HTML. Not optional. Not per-report opt-in. "
        "Visible HTML prose → **hsw**; filesystem basenames → **hon**.\n\n"
        "## Boot paste — acs_prompt_inject.system_block (ALWAYS-ON)\n\n"
        f"- **always_on:** `{str(always_on).lower()}`\n"
        f"- **opt_in_forbidden:** `{str(opt_in_forbidden).lower()}`\n"
        "- **rule:** Paste the block below into the agent **system prompt at session boot** "
        "(every CGM adopter). Not per-report. Not per-HTML. Not ACS-only.\n\n"
        "```\n"
        f"{system_block or instruction}\n"
        "```\n\n"
        "## ACS addendum — dev root hygiene (paste with the block above)\n\n"
        "Owned by ACS, not CGM. Paste it at boot together with the system_block.\n\n"
        "```\n"
        f"{DEV_ROOT_RULE}\n"
        "```\n\n"
        "## Instruction (MUST paste/apply into system or task prompts)\n\n"
        f"{instruction}\n\n"
        "## apply_checklist\n\n"
        f"{checklist_md}\n\n"
        "## routes (Surface → module MUST load)\n\n"
        "| Surfaces (sample) | MUST load |\n"
        "| --- | --- |\n"
        f"{routes_table}\n\n"
        "Contract language is **MUST / APPLY / default_on**, not prefer. Soft enforcement = no NLP CI grade of prose.\n"
    )

def apply_acs_prompt_inject(
    cgm_root: Path, pack_root: Path, *, stack_root: Path | None = None
) -> tuple[str | None, list[str]]:
    """After VALID: load writing-routing.json, write PROMPT_INJECT.md, return instruction text."""
    notes: list[str] = []
    routing = load_writing_routing(cgm_root)
    if routing is None:
        notes.append(
            "acs_prompt_inject: missing or unreadable docs/writing-routing.json in CGM pin "
            f"(expected at {cgm_root / 'docs' / 'writing-routing.json'})"
        )
        return None, notes
    inject = routing.get("acs_prompt_inject")
    if not isinstance(inject, dict) or not str(inject.get("instruction") or "").strip():
        notes.append("acs_prompt_inject: writing-routing.json missing acs_prompt_inject.instruction")
        return None, notes
    instruction = str(inject["instruction"]).strip()
    out = pack_root / "PROMPT_INJECT.md"
    try:
        cgm_req = stack_component("content-generation-modules", stack_root)
        out.write_text(
            render_prompt_inject_md(routing, pin_version=cgm_req["version"]),
            encoding="utf-8",
        )
        notes.append(f"acs_prompt_inject: wrote {out} (system_block boot paste)")
    except OSError as exc:
        notes.append(f"acs_prompt_inject: failed to write PROMPT_INJECT.md: {exc}")
    system_block = ""
    if isinstance(inject, dict):
        system_block = str(inject.get("system_block") or "").strip()
        if inject.get("always_on") is not True:
            notes.append("acs_prompt_inject: WARN always_on is not true on pinned writing-routing")
        if inject.get("opt_in_forbidden") is not True:
            notes.append("acs_prompt_inject: WARN opt_in_forbidden is not true on pinned writing-routing")
    return (system_block or instruction), notes


def validate_pins(
    data: object, *, against_stack: bool = True, stack_root: Path | None = None
) -> list[str]:
    """Require FULL PCM + FULL CGM pins (Alex binding: no slim subsets).

    ``against_stack`` compares the pinned revision and version with the stack
    checkout (``stack_checkout.py``). The pack's own example is checked with it
    off: that file is a template whose pin-bearing fields
    ``acs_install.build_assignment`` rebuilds from ``pins.json`` and the
    checkout before an adopter sees them, so its revision is a placeholder.
    Comparing a placeholder with the live commit would fail every pull request.
    The shape checks (FULL PCM features, all eight CGM modules, the
    human-output contract) run either way.
    """
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["assignment must be an object"]
    pins = data.get("pins")
    if not isinstance(pins, dict):
        errors.append("pins: required object missing (FULL PCM + FULL CGM)")
        return errors

    pcm = pins.get("pcm")
    if not isinstance(pcm, dict):
        errors.append("pins.pcm: required (FULL PCM stack)")
    else:
        if against_stack:
            pcm_req = stack_component("project-continuity-modules", stack_root)
            rev = str(pcm.get("revision") or "")
            if not commits_match(rev, pcm_req["commit"]):
                errors.append(
                    f"pins.pcm.revision: must be the stack commit {pcm_req['commit']}; "
                    f"got {rev or '(none)'}; re-run acs_install.py --force from this checkout"
                )
        feats = pcm.get("required_features")
        if not isinstance(feats, list):
            errors.append("pins.pcm.required_features: required list of FULL PCM features")
        else:
            missing = [f for f in REQUIRED_PCM_FEATURES if f not in feats]
            if missing:
                errors.append(
                    "pins.pcm.required_features: missing FULL PCM features: "
                    + ", ".join(missing)
                )

    cgm = pins.get("cgm")
    if not isinstance(cgm, dict):
        errors.append("pins.cgm: required (FULL CGM stack)")
    else:
        if against_stack:
            cgm_req = stack_component("content-generation-modules", stack_root)
            ver = str(cgm.get("version") or "")
            if ver != cgm_req["version"]:
                errors.append(
                    f"pins.cgm.version: must be {cgm_req['version']}, the stack checkout's CGM"
                )
            rev = str(cgm.get("revision") or "")
            if not commits_match(rev, cgm_req["commit"]):
                errors.append(
                    f"pins.cgm.revision: must be the stack commit {cgm_req['commit']}; "
                    f"got {rev or '(none)'}; re-run acs_install.py --force from this checkout"
                )
        mods = cgm.get("modules")
        if not isinstance(mods, list):
            errors.append("pins.cgm.modules: required list of all eight CGM module ids")
        else:
            # accept either bare ids or modules/<id> paths
            normalized = []
            for m in mods:
                s = str(m).strip().rstrip("/")
                if s.startswith("modules/"):
                    s = s[len("modules/") :]
                normalized.append(s)
            missing = [m for m in REQUIRED_CGM_MODULES if m not in normalized]
            if missing:
                errors.append(
                    "pins.cgm.modules: FULL CGM requires all eight modules; missing: "
                    + ", ".join(missing)
                )
            if len(normalized) < len(REQUIRED_CGM_MODULES):
                errors.append(
                    "pins.cgm.modules: slim subset incomplete — need all eight CGM modules"
                )
        hoc = cgm.get("human_output_contract")
        if not isinstance(hoc, list) or len(hoc) < 5:
            errors.append(
                "pins.cgm.human_output_contract: required list (playbook/template/contract/"
                "quality/provenance/routing) — README contract is part of FULL CGM"
            )
    return errors


def validate_assignment(
    schema_path: Path,
    assignment_path: Path,
    *,
    against_stack: bool = True,
    stack_root: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    schema = load_json(schema_path)
    data = load_json(assignment_path)
    if jsonschema is None:
        errors.append("jsonschema is not installed; pip install jsonschema")
        return errors
    validator = jsonschema.Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        loc = ".".join(str(p) for p in err.path) or "<root>"
        errors.append(f"{loc}: {err.message}")
    errors.extend(validate_failover_watchdog(data))
    errors.extend(validate_pins(data, against_stack=against_stack, stack_root=stack_root))
    return errors



# Binding doc gate: section heading presence only (no phrase laundry list).
EXTERNAL_RESEARCH_GATE_HEADING = "External research gate"
EXTERNAL_RESEARCH_GATE_FILES = (
    "BEHAVIOR.md",
    "HOTLOAD.md",
)


def check_external_research_gate(root: Path, *, policy_path: Path | None = None) -> list[str]:
    """Assert External research gate heading exists in pack BEHAVIOR/HOTLOAD + root POLICY."""
    errors: list[str] = []
    targets: list[tuple[str, Path]] = [(rel, root / rel) for rel in EXTERNAL_RESEARCH_GATE_FILES]
    if policy_path is None:
        policy_path = root.parents[3] / "POLICY.md"
    targets.append(("POLICY.md", policy_path))
    for label, path in targets:
        if not path.is_file():
            errors.append(f"external research gate: missing {label} at {path}")
            continue
        try:
            body = path.read_text(encoding="utf-8-sig")
        except OSError as exc:
            errors.append(f"external research gate: unreadable {label}: {exc}")
            continue
        if EXTERNAL_RESEARCH_GATE_HEADING not in body:
            errors.append(
                f"external research gate: {label} missing heading '{EXTERNAL_RESEARCH_GATE_HEADING}'"
            )
    return errors


def check_dev_root_layout(dev_root: Path) -> list[str]:
    """Run dev_root_check.scan and turn findings into one-line messages."""
    if not dev_root.is_dir():
        return []
    try:
        report = dev_root_check.scan(dev_root)
    except OSError as exc:
        return [f"dev_root: could not scan {dev_root}: {exc}"]
    msgs = [
        f"dev_root: {f['kind']}: {f['path']} ({f['detail']})" for f in report["findings"]
    ]
    if msgs:
        msgs.append(
            f"dev_root: {len(report['findings'])} entr{'y' if len(report['findings']) == 1 else 'ies'} "
            f"in {dev_root} are not single main checkouts; run "
            "scripts/dev_root_check.py --clean to plan a fix"
        )
    return msgs


def run(
    root: Path,
    assignment: Path | None = None,
    *,
    cgm_root: Path | None = None,
    adopter_root: Path | None = None,
    skip_cgm_validate: bool = False,
    dev_root: Path | None = None,
    check_dev_root: bool = True,
    strict_dev_root: bool = False,
    stack_root: Path | None = None,
) -> int:
    problems: list[str] = []
    warnings: list[str] = []
    resolved_dev_root = (dev_root or dev_root_check.default_dev_root()).expanduser()
    try:
        requires = load_requires(stack_root)
    except stack_checkout.StackError as exc:
        print("hotload_check: FAIL")
        print(f"  - {exc}")
        return 1
    missing = check_required_files(root)
    if missing:
        problems.extend(f"missing file: {m}" for m in missing)
    problems.extend(check_external_research_gate(root))
    schema_path = root / "schema" / "assignment.schema.json"
    example_path = assignment or (root / "examples" / "assignment.example.json")
    if schema_path.is_file() and example_path.is_file():
        # A real assignment (--assignment) must pin the stack commit. The pack's
        # own example is a template whose pins build_assignment rebuilds; see
        # validate_pins.
        problems.extend(
            validate_assignment(
                schema_path,
                example_path,
                against_stack=assignment is not None,
                stack_root=stack_root,
            )
        )
    elif not example_path.is_file():
        problems.append(f"assignment not found: {example_path}")

    resolved_adopter = discover_adopter_root(adopter_root)
    resolved_cgm = discover_cgm_root(cgm_root, stack_root=stack_root)
    if resolved_cgm is not None and resolved_cgm != stack_cgm_root(stack_root):
        where = dependency_location_problem(resolved_cgm, resolved_dev_root)
        if where:
            problems.append(where)
    if check_dev_root:
        dev_msgs = check_dev_root_layout(resolved_dev_root)
        (problems if strict_dev_root else warnings).extend(dev_msgs)
    # Claude Code reads CLAUDE.md, not AGENTS.md: without the import, Claude
    # sessions run with none of the rules every other agent follows.
    problems.extend(claude_bridge.check(resolved_adopter, require_agents=False))
    problems.extend(claude_bridge.check_guard(resolved_adopter))
    if skip_cgm_validate:
        # Explicit opt-out for isolated schema unit tests only — not a successful install.
        print("hotload_check: WARN skip_cgm_validate=1 (schema-only; install incomplete)")
    else:
        problems.extend(
            validate_cgm_live(resolved_cgm, resolved_adopter, require=True, stack_root=stack_root)
        )

    for item in warnings:
        print(f"hotload_check: WARN {item}")
    if problems:
        print("hotload_check: FAIL")
        for item in problems:
            for line in str(item).splitlines() or [str(item)]:
                print(f"  - {line}")
        return 1
    # After full adapter VALID: wire acs_prompt_inject (primary done-when remains VALID)
    inject_text = None
    inject_notes: list[str] = []
    if resolved_cgm is not None and not skip_cgm_validate:
        inject_text, inject_notes = apply_acs_prompt_inject(resolved_cgm, root, stack_root=stack_root)

    print("hotload_check: OK")
    print(f"  module_root={root}")
    print(f"  assignment={example_path}")
    print(f"  cgm_root={resolved_cgm}")
    print(f"  adopter_root={resolved_adopter}")
    cgm_req = requires["content-generation-modules"]
    print(f"  stack_commit={cgm_req['commit']}")
    print(f"  install_surface=FULL PCM + FULL CGM {cgm_req['version']} + this runtime")
    print("  cgm_validate=VALID (validate_content_system.py)")
    print("  claude_bridge=OK (CLAUDE.md imports AGENTS.md; boot rules ride in its region; guard hooks installed)")
    print("  watchdog=agent-less ~10m; lease_ttl=minutes (default 30)")
    print("  claim_queue=FIFO after vacancy; zombie re-reads the claim file")
    for note in inject_notes:
        print(f"  {note}")
    print(
        "  next: MUST paste acs_prompt_inject.system_block into agent system prompt at BOOT "
        "(always_on; opt_in_forbidden; Claude Code already gets it from CLAUDE.md's "
        "acs:claude-bridge region). Then MUST load CGM modules per docs/writing-routing.json "
        "/ docs/ACS_VERIFY.md (README/product -> writing-direction; human-facing prose/HTML/"
        "compare/appendable -> hsw; basenames -> hon). Not per-report."
    )
    print(
        "  hsw_verify: before publishing compare/Pages HTML run "
        "python <cgm>/scripts/verify_hsw_applied.py --root <cgm> --mode acs-html "
        "--html <path-to-published-report.html>"
    )
    if inject_text:
        print("  --- acs_prompt_inject.system_block (BOOT PASTE) ---")
        print(console_safe(inject_text))
        print("  --- end acs_prompt_inject.system_block ---")
    print("  --- ACS dev root rule (BOOT PASTE) ---")
    print(console_safe(DEV_ROOT_RULE))
    print("  --- end ACS dev root rule ---")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=MODULE_ROOT)
    parser.add_argument("--assignment", type=Path, default=None)
    parser.add_argument(
        "--stack-root",
        type=Path,
        default=None,
        help="agent-stack-train checkout (default: the one this script is in)",
    )
    parser.add_argument(
        "--cgm-root",
        type=Path,
        default=None,
        help="CGM at the stack commit (else CGM_ROOT, else the stack checkout's cgm/)",
    )
    parser.add_argument(
        "--adopter-root",
        type=Path,
        default=None,
        help="Adopter repo root with .content-system (else ADOPTER_ROOT / ACS root)",
    )
    parser.add_argument(
        "--skip-cgm-validate",
        action="store_true",
        help="Schema-only (tests). A real install must NOT use this flag.",
    )
    parser.add_argument(
        "--dev-root",
        type=Path,
        default=None,
        help="Dev root to check for stray worktrees/clones/scratch (else ACS_DEV_ROOT / OS default)",
    )
    parser.add_argument(
        "--strict-dev-root",
        action="store_true",
        help="Fail (not just warn) when the dev root holds anything but main checkouts",
    )
    parser.add_argument(
        "--no-dev-root-check",
        action="store_true",
        help="Skip the dev root layout check",
    )
    args = parser.parse_args(argv)
    strict = bool(args.strict_dev_root) or os.environ.get("ACS_DEV_ROOT_STRICT") == "1"
    skip = bool(args.skip_cgm_validate) or os.environ.get("HOTLOAD_SKIP_CGM_VALIDATE") == "1"
    return run(
        args.root.resolve(),
        args.assignment,
        cgm_root=args.cgm_root,
        adopter_root=args.adopter_root,
        skip_cgm_validate=skip,
        dev_root=args.dev_root,
        check_dev_root=not args.no_dev_root_check,
        strict_dev_root=strict,
        stack_root=args.stack_root,
    )


if __name__ == "__main__":
    sys.exit(main())
