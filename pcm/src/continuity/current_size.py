"""Keep checkpoints/CURRENT.md short enough to read at the start of every session.

CURRENT is the second file a new session reads, so every superseded paragraph
left in it costs every later session context. `validate` fails a CURRENT over
the limits, and `continuity current archive` moves superseded state into
`checkpoints/history/YYYY-MM.md` (#48). Nothing is lost: the archive is
checked in next to CURRENT, and Git keeps every earlier version.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

CURRENT_MAX_LINES = 60
CURRENT_MAX_BYTES = 8000
# Sections that describe the present. Every other section (Completed, history,
# superseded notes) is archived whole.
KEEP_PREFIXES = (
    "current projection",
    "program state",
    "main objective",
    "active",
    "queued",
    "blockers",
    "next atomic action",
    "next action",
)
HISTORY_LINK_RE = re.compile(r"^Older state: .*$", re.MULTILINE)


def current_size_errors(path: Path, text: str | None = None) -> list[str]:
    text = path.read_text(encoding="utf-8") if text is None else text
    lines = len(text.splitlines())
    size = len(text.encode("utf-8"))
    if lines <= CURRENT_MAX_LINES and size <= CURRENT_MAX_BYTES:
        return []
    message = (
        f"{path}: CURRENT is {lines} lines and {size} bytes; the limit is {CURRENT_MAX_LINES} lines and "
        f"{CURRENT_MAX_BYTES} bytes, because every new session reads it. Run `continuity current archive` to move "
        "superseded state into checkpoints/history/, then shorten what is left by hand if it is still over"
    )
    return [message]


def _split(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Return the preamble (title, marker, intro) and the `## ` sections as (heading, body)."""
    parts = re.split(r"(?m)^(?=## )", text)
    preamble = parts[0]
    sections = []
    for part in parts[1:]:
        heading, _, body = part.partition("\n")
        sections.append((heading[3:].strip(), body))
    return preamble, sections


def _keeps(heading: str) -> bool:
    lowered = heading.lower()
    if "superseded" in lowered or "historical" in lowered or "prior" in lowered:
        return False
    return lowered.startswith(KEEP_PREFIXES)


def _first_paragraph(body: str) -> tuple[str, str]:
    stripped = body.strip("\n")
    first, sep, rest = stripped.partition("\n\n")
    return first, rest.strip("\n") if sep else ""


def archive_current(current: Path, today: date) -> tuple[Path | None, int]:
    """Move superseded sections of CURRENT into checkpoints/history/YYYY-MM.md.

    Sections that describe the present are kept; if CURRENT is still over the
    limits, each kept section is cut to its first paragraph and the rest is
    archived too. Returns the history file (None when nothing moved) and the
    number of sections or section tails moved.
    """
    text = current.read_text(encoding="utf-8")
    preamble, sections = _split(text)
    kept: list[tuple[str, str]] = []
    moved: list[tuple[str, str]] = []
    for heading, body in sections:
        (kept if _keeps(heading) else moved).append((heading, body))

    def render(parts: list[tuple[str, str]], link: str) -> str:
        head = HISTORY_LINK_RE.sub("", preamble).rstrip("\n")
        out = head + "\n\n" + (link + "\n\n" if link else "")
        out += "".join(f"## {heading}\n\n{body.strip(chr(10))}\n\n" for heading, body in parts)
        return out.rstrip("\n") + "\n"

    history = current.parent / "history" / f"{today:%Y-%m}.md"
    link = f"Older state: [`history/{history.name}`](history/{history.name}) and earlier months in `history/`."
    if current_size_errors(current, render(kept, link)):
        trimmed: list[tuple[str, str]] = []
        for heading, body in kept:
            first, rest = _first_paragraph(body)
            trimmed.append((heading, first + "\n"))
            if rest:
                moved.append((f"{heading} (continued)", rest + "\n"))
        kept = trimmed
    if not moved:
        return None, 0

    history.parent.mkdir(parents=True, exist_ok=True)
    title = f"# Archived checkpoint state, {today:%Y-%m}\n"
    existing = history.read_text(encoding="utf-8") if history.exists() else title
    block = f"\n## Archived from CURRENT.md on {today.isoformat()}\n\n"
    block += "".join(f"### {heading}\n\n{body.strip(chr(10))}\n\n" for heading, body in moved)
    history.write_text(existing.rstrip("\n") + "\n" + block.rstrip("\n") + "\n", encoding="utf-8")
    current.write_text(render(kept, link), encoding="utf-8")
    return history, len(moved)
