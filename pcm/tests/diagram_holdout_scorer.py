"""Pure scoring functions for the PCM-0039 hidden diagram-guidance holdout.

``tests/fixtures/pcm0039_diagram_holdout/scenario.md`` is the prompt given to
participants; their submitted record text is scored here. The rubric
(``rubric.json``) is hidden from participants, so every check is computed
mechanically from the record text alone: no network access, no file reads at
score time, and identical input always produces an identical result.
"""

from __future__ import annotations

import re

CHECKS = (
    "diagram_present",
    "direction_ok",
    "size_ok",
    "text_alternative",
    "details_when_wide",
    "no_renderer_link",
    "syntax_shape_ok",
)

RENDERER_LINK_HOST = "viewscreen.githubusercontent.com"

MAX_NODES = 8
MAX_LABEL_WORDS = 6
MAX_LR_NODES = 4

_FENCE_RE = re.compile(r"(?m)^[ \t]*(`{3,}|~{3,})[ \t]*mermaid[ \t]*\r?\n(.*?)\r?\n[ \t]*\1[ \t]*$", re.DOTALL)
_DETAILS_SPAN_RE = re.compile(r"<details\b[^>]*>.*?</details\s*>", re.IGNORECASE | re.DOTALL)

_STATEMENT_RE = re.compile(r"^(?:graph|flowchart)[ \t]+(TD|TB|LR|RL|BT)\b[ \t]*;?[ \t]*$")
_NODE_ID_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*)\s*(?:\[|\{|\(|-->)")
_EDGE_TARGET_RE = re.compile(r"-->[ \t]*(?:\|[^|\n]*\|)?[ \t]*([A-Za-z][A-Za-z0-9_]*)")
_LABEL_RE = re.compile(r"\[([^\]\n]*)\]|\{([^}\n]*)\}")

_STEP_LINE_RE = re.compile(r"^\s*(\d+[.)]|-|\*)\s+")
_TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
_TABLE_SEP_RE = re.compile(r"^\s*\|[ \t:|-]*-[ \t:|-]*\|\s*$")

_KEYWORD_IDS = frozenset(
    {"graph", "flowchart", "subgraph", "end", "style", "classDef", "direction", "class", "click"}
)

_LABEL_BODY = r"[^|\n]*"
_NODE = r"[A-Za-z][A-Za-z0-9_]*(?:\[" + _LABEL_BODY + r"\]|\{" + _LABEL_BODY + r"\})?"
_EDGE_FORMS = (
    "^" + _NODE + r" *--> *" + _NODE + "$",
    "^" + _NODE + r" *--> *\|[^|\n]+\| *" + _NODE + "$",
    "^" + _NODE + r" *-- *[^|>]*--> *" + _NODE + "$",
)
_LONE_FORMS = ("^" + _NODE + "$",)
_OTHER_FORMS = (
    r"^style [^#]*$",
    r"^classDef [^#]*$",
    r"^subgraph [^#]+$",
    r"^end$",
    r"^direction +(TD|TB|LR|RL|BT)$",
)
_LINE_FORMS = tuple(re.compile(form) for form in (_EDGE_FORMS + _LONE_FORMS + _OTHER_FORMS))

_BALANCE_PAIRS = (("[", "]"), ("{", "}"), ("(", ")"))


def extract_fences(text: str) -> list[str]:
    """Return the bodies of mermaid fenced blocks (including fences inside <details>)."""
    return [match.group(2) for match in _FENCE_RE.finditer(text)]


def outside_fences(text: str) -> str:
    """Return the text with every fenced code block body removed."""
    return _FENCE_RE.sub("", text)


def fence_lines(fence: str) -> list[str]:
    """Return the non-empty lines of a fence body."""
    return [line.strip("\r") for line in fence.splitlines() if line.strip()]


def first_statement(fence: str) -> str:
    """Return the first non-empty line of a fence body ('' when the fence is empty)."""
    lines = fence_lines(fence)
    return lines[0].strip() if lines else ""


def is_wide(fence: str) -> bool:
    """True when the fence declares a left-to-right layout on its first line."""
    return bool(re.match(r"^(?:flowchart|graph)[ \t]+LR\b", first_statement(fence)))


def node_count(fence: str) -> int:
    """Count unique node identifiers conservatively (source tokens plus edge targets)."""
    ids: set[str] = set()
    for line in fence_lines(fence):
        for match in _NODE_ID_RE.finditer(line):
            if match.group(1) not in _KEYWORD_IDS:
                ids.add(match.group(1))
        for match in _EDGE_TARGET_RE.finditer(line):
            if match.group(1) not in _KEYWORD_IDS:
                ids.add(match.group(1))
    return len(ids)


def label_words(fence: str) -> int:
    """Return the maximum word count across bracketed/braced labels in the fence."""
    longest = 0
    for match in _LABEL_RE.finditer(fence):
        longest = max(longest, len((match.group(1) or match.group(2)).split()))
    return longest


def _details_spans(text: str) -> list[tuple[int, int]]:
    return [(match.start(), match.end()) for match in _DETAILS_SPAN_RE.finditer(text)]


def _step_lines(outside: str) -> int:
    return sum(1 for line in outside.splitlines() if _STEP_LINE_RE.match(line))


def _has_table_with_rows(outside: str, minimum: int) -> bool:
    rows = outside.splitlines()
    index = 0
    while index < len(rows) - 1:
        if _TABLE_ROW_RE.match(rows[index]) and _TABLE_SEP_RE.match(rows[index + 1]):
            body = 0
            index += 2
            while index < len(rows) and _TABLE_ROW_RE.match(rows[index]):
                body += 1
                index += 1
            if body >= minimum:
                return True
        else:
            index += 1
    return False


def _line_shape_ok(line: str) -> bool:
    if line.rstrip().endswith("-->") or line.lstrip().startswith("-->"):
        return False
    for opener, closer in _BALANCE_PAIRS:
        if line.count(opener) != line.count(closer):
            return False
    if line.count('"') % 2 != 0:
        return False
    return any(form.match(line.strip()) for form in _LINE_FORMS)


def _syntax_shape_ok(fence: str) -> bool:
    lines = fence_lines(fence)
    if not lines:
        return False
    if not _STATEMENT_RE.match(lines[0].strip()):
        return False
    return all(_line_shape_ok(line) for line in lines[1:])


def _direction_ok(fence: str) -> bool:
    match = _STATEMENT_RE.match(first_statement(fence))
    if not match:
        return False
    direction = match.group(1)
    if direction in ("TD", "TB"):
        return True
    return direction == "LR" and node_count(fence) <= MAX_LR_NODES


def _size_ok(fence: str) -> bool:
    return node_count(fence) <= MAX_NODES and label_words(fence) <= MAX_LABEL_WORDS


def score(text: str) -> dict[str, bool]:
    """Score a participant record against all seven holdout checks."""
    matches = list(_FENCE_RE.finditer(text))
    fences = [match.group(2) for match in matches]
    outside = outside_fences(text)
    details = _details_spans(text)
    wide_needing_details = [
        (match.start(), match.end())
        for match in matches
        if is_wide(match.group(2)) and node_count(match.group(2)) > MAX_LR_NODES
    ]
    return {
        "diagram_present": bool(fences),
        "direction_ok": all(_direction_ok(fence) for fence in fences),
        "size_ok": all(_size_ok(fence) for fence in fences),
        "text_alternative": _step_lines(outside) >= 4 or _has_table_with_rows(outside, 4),
        "details_when_wide": all(
            any(outer[0] <= start and end <= outer[1] for outer in details)
            for start, end in wide_needing_details
        ),
        "no_renderer_link": RENDERER_LINK_HOST not in text,
        "syntax_shape_ok": all(_syntax_shape_ok(fence) for fence in fences),
    }


def applicable(text: str) -> list[str]:
    """Every check applies to a record describing a >=4-step flow (which the scenario does)."""
    return list(CHECKS)
