#!/usr/bin/env python3
"""Make Claude Code load the stack's instructions in an adopter.

Codex, Cursor, Gemini and most other agent harnesses read ``AGENTS.md``. Claude
Code reads ``CLAUDE.md``. It loads ``AGENTS.md`` only through an optional,
remotely switchable fallback, and only when the project has no ``CLAUDE.md`` of
its own. So an adopter whose rules live in ``AGENTS.md`` gets no rules at all in
Claude on an older Claude Code, with the fallback off, or as soon as anyone adds
a ``CLAUDE.md`` that does not import it.

This module owns one delimited region in the adopter's ``CLAUDE.md``:

    <!-- acs:claude-bridge:start -->
    ... @AGENTS.md import, GitHub authority, boot rules ...
    <!-- acs:claude-bridge:end -->

The region imports ``AGENTS.md`` (``@AGENTS.md``, which every Claude Code version
honours), says GitHub is the authority, and carries the boot rules
``hotload_check`` otherwise asks a human to paste into the system prompt: CGM's
always-on writing rule, with its skill paths turned into GitHub links at the
stack commit, and ACS's dev root rule. ``CLAUDE.md`` is Claude's system prompt
at boot, so the paste happens by itself.

Text outside the region is never touched. A ``CLAUDE.md`` that is a symlink to
``AGENTS.md`` already bridges and is left alone; any other symlink is refused.

Stdlib only: ``acs_install.py`` and ``hotload_check.py`` both import it.

Usage (read-only check, as CI runs it):

    python claude_bridge.py --adopter-root .
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CLAUDE_REL = Path("CLAUDE.md")
AGENTS_NAME = "AGENTS.md"
START_MARKER = "<!-- acs:claude-bridge:start -->"
END_MARKER = "<!-- acs:claude-bridge:end -->"
# A line that is exactly the import, as Claude Code parses it.
IMPORT_RE = re.compile(r"^@(?:\./)?AGENTS\.md\s*$", re.MULTILINE)

REPOSITORY = "Pukujan/agent-stack-train"
# A CGM module or script path as the writing rule names it, relative to cgm/.
CGM_PATH_RE = re.compile(r"(?<![\w/.-])((?:modules/[\w-]+/SKILL\.md)|(?:scripts/human_filename(?:\.py)?))")

# ACS-owned boot rule: the region carries it, and PROMPT_INJECT.md appends it to
# the CGM system_block.
DEV_ROOT_RULE = (
    "Dev root hygiene (ACS): the dev root (ACS_DEV_ROOT; default D:\\development on "
    "Windows, ~/development elsewhere) holds exactly one main checkout per repo. Never "
    "create git worktrees, dependency or sibling clones, scratch folders, or caches "
    "there. Put them under the ACS cache instead: %LOCALAPPDATA%\\acs\\{deps,scratch,"
    "worktrees} on Windows, ~/.cache/acs/{deps,scratch,worktrees} on macOS/Linux "
    "(ACS_CACHE_DIR overrides). Check with scripts/dev_root_check.py."
)


class BridgeError(RuntimeError):
    """The adopter's CLAUDE.md cannot be bridged safely."""


def github_url(commit: str | None, rel: str) -> str:
    """The file at ``cgm/<rel>`` on GitHub, at the stack commit (``main`` when unknown)."""
    if rel == "scripts/human_filename":
        rel = "scripts/human_filename.py"
    return f"https://github.com/{REPOSITORY}/blob/{commit or 'main'}/cgm/{rel}"


def writing_rule(cgm_root: Path, commit: str | None) -> str | None:
    """CGM's always-on writing rule, its skill paths turned into GitHub links."""
    try:
        routing = json.loads((cgm_root / "docs" / "writing-routing.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    inject = routing.get("acs_prompt_inject") if isinstance(routing, dict) else None
    if not isinstance(inject, dict):
        return None
    block = str(inject.get("system_block") or inject.get("instruction") or "").strip()
    if not block:
        return None
    return CGM_PATH_RE.sub(lambda m: f"[{m.group(1)}]({github_url(commit, m.group(1))})", block)


def render_region(*, commit: str | None, cgm_root: Path | None) -> str:
    """The managed region, markers included, ending in a newline."""
    at = f"`{commit[:12]}`" if commit else "`main`"
    parts = [
        START_MARKER,
        "## Claude Code: load the stack's rules",
        "",
        "Other agents read `AGENTS.md` by themselves; Claude Code reads this file. "
        "The import below gives Claude the same rules every other agent follows. "
        "They bind here exactly as they do there.",
        "",
        "@AGENTS.md",
        "",
        "### GitHub is the authority",
        "",
        "Live GitHub state decides scope, status and what is accepted: the issues, pull "
        "requests, checks and merged default branch of this repository. Read them with "
        "`gh` before you plan, resume or report, and work through them: a branch and a "
        "pull request, never a push to the default branch. Local files are projections "
        "and caches (checkpoints, `HANDOFF.md`, `.oio/`, `.content-system/`, `.coord/`, "
        "any clone under `~/.cache`). When one disagrees with GitHub, GitHub wins; say "
        "so on the owning issue.",
        "",
        f"The stack's rules live in [`{REPOSITORY}`](https://github.com/{REPOSITORY}) at "
        f"commit {at}, recorded in `.coord/hotload.lock.json`. Read a stack file there, "
        "not from a local copy or one of the four frozen component repositories.",
    ]
    rule = writing_rule(cgm_root, commit) if cgm_root is not None else None
    if rule:
        parts += ["", "### Boot rules", "", rule, "", DEV_ROOT_RULE]
    else:
        parts += ["", "### Boot rules", "", DEV_ROOT_RULE]
    parts.append(END_MARKER)
    return "\n".join(parts) + "\n"


def _region_span(text: str) -> tuple[int, int] | None:
    starts, ends = text.count(START_MARKER), text.count(END_MARKER)
    if starts == 0 and ends == 0:
        return None
    if starts != 1 or ends != 1 or text.index(START_MARKER) > text.index(END_MARKER):
        raise BridgeError(
            f"{CLAUDE_REL}: unbalanced {START_MARKER} / {END_MARKER} markers; fix them by hand"
        )
    start = text.index(START_MARKER)
    end = text.index(END_MARKER) + len(END_MARKER)
    if text[end : end + 1] == "\n":
        end += 1
    return start, end


def is_symlink_bridge(adopter: Path) -> bool:
    """``CLAUDE.md`` is a symlink to this repository's ``AGENTS.md``."""
    path = adopter / CLAUDE_REL
    if not path.is_symlink():
        return False
    try:
        return path.resolve() == (adopter / AGENTS_NAME).resolve()
    except OSError:
        return False


def plan(adopter: Path, region: str) -> bytes | None:
    """The new ``CLAUDE.md`` bytes, or None when it already says exactly this.

    Raises BridgeError when the file cannot be changed safely.
    """
    path = adopter / CLAUDE_REL
    if is_symlink_bridge(adopter):
        return None
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise BridgeError(f"{CLAUDE_REL}: not a regular file (symlink or directory); refusing")
    if not path.exists():
        return ("# Claude Code\n\n" + region).encode("utf-8")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        raise BridgeError(f"{CLAUDE_REL}: unreadable: {exc}") from exc
    span = _region_span(text)
    if span is None:
        new = text.rstrip("\n") + "\n\n" + region if text.strip() else "# Claude Code\n\n" + region
    else:
        new = text[: span[0]] + region + text[span[1] :]
    return None if new == text else new.encode("utf-8")


def check(adopter: Path, *, require_agents: bool = True) -> list[str]:
    """Problems that keep Claude Code from loading the stack's rules (empty = OK).

    ``require_agents=False`` skips the AGENTS.md-exists check, for a caller that
    runs before OIO has written its AGENTS.md region.
    """
    path = adopter / CLAUDE_REL
    if is_symlink_bridge(adopter):
        return []
    if not path.is_file():
        return [
            f"{CLAUDE_REL} is missing, so Claude Code may load none of AGENTS.md; "
            "run acs_install.py to add the bridge"
        ]
    if require_agents and not (adopter / AGENTS_NAME).is_file():
        return [f"{CLAUDE_REL} has nothing to import: {AGENTS_NAME} is missing"]
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"{CLAUDE_REL}: unreadable: {exc}"]
    try:
        _region_span(text)
    except BridgeError as exc:
        return [str(exc)]
    if not IMPORT_RE.search(text):
        return [
            f"{CLAUDE_REL} does not import {AGENTS_NAME} (no '@AGENTS.md' line), so Claude "
            "Code skips the rules other agents follow; run acs_install.py to add the bridge"
        ]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check that Claude Code loads the adopter's AGENTS.md.")
    parser.add_argument("--adopter-root", type=Path, default=Path("."))
    parser.add_argument(
        "--warn-only", action="store_true", help="Report problems as warnings and exit 0."
    )
    args = parser.parse_args(argv)
    problems = check(args.adopter_root.resolve())
    if not problems:
        print("claude_bridge: OK (CLAUDE.md imports AGENTS.md)")
        return 0
    for item in problems:
        print(f"{'::warning::' if args.warn_only else ''}claude_bridge: {item}")
    return 0 if args.warn_only else 1


if __name__ == "__main__":
    sys.exit(main())
