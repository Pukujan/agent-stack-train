#!/usr/bin/env python3
"""Fail-closed drift check for component pins restated in stack prose.

A stack document -- ``README.md``, ``AGENTS.md``, ``PROJECT.md`` -- sometimes
restates a sibling component's version or commit as if it were current. No
validator reads prose: ``check_manifest.py`` reads ``stack-manifest.json``,
``mesh.py`` reads ``stack-mesh.json``, and ACS's ``check_pins.py`` reads only
the projections ``pins.json`` declares. A reader who follows the prose installs
the wrong versions, and every check stays green. That is the 2026-10-13 defect
in agent-stack-train#16.

This script is the missing reader. The rule it enforces is the one the train's
own README already practices: a stack document points at ``stack-releases.json``
(or ``stack-mesh.json``) instead of restating a current value, because a
hand-copied pin was correct for eleven hours on 2026-10-10 and stale ever since
(OIO PR #44 vs train commits 83379c6 and bc212fa).

Usage (pure, offline -- the certified set is passed as a file):

    python scripts/check_prose_pins.py --root /path/to/a/checkout
    python scripts/check_prose_pins.py --root . --train /path/stack-releases.json

An adopter calls it with ``--train <path>`` pointing at a checkout of
``agent-stack-train/stack-releases.json``; with no ``--train`` it reads this
repository's own copy. With no ``--root`` it checks ``.``. A bare call from any
checkout therefore checks that checkout against the train it ships with.

Exit codes: 0 no stale prose pins, 1 a document states a value the certified
set does not name, 2 unreadable input.

The check is a pure function over ``(document_text, certified_set)``:
``prose_pin_problems(document, certified)`` needs no filesystem, network, or
git, so the same rule runs in this repository's CI and against any checkout.

The match rule
--------------

Prose names commits for reasons other than pinning: a SHA cited as evidence, a
permalink to a frozen revision, a policy marker's own schema version, a module's
versioned directory. A naive SHA matcher flags all of them; noise gets a check
disabled, and a disabled check is today's failure with extra steps (issue #16,
"Risk Introduced by a Proposed Change"). The rule below is deliberately
conservative: a false negative -- a stale pin that slips through -- silently
reproduces the defect, so the *positive* signal is the gate and every other
construct exists to keep a legitimate reference out of the report.

1. **Blanked before scanning** (length-preserving, so line and column numbers
   stay true):
   - URLs -- a SHA inside a permalink freezes a revision on purpose, so it is a
     historical reference whatever the sentence around it says (OIO AGENTS.md
     line 19).
   - Whole-line machine markers -- ``<!-- pcm:policy ... -->`` and
     ``<!-- continuity:project ... -->`` carry their own schema versions, not
     component pins.
   - Path segments -- ``modules/coordination/multi-agent-hotload/v0.1.0/`` is
     the ACS module's own versioned directory, not a component version.
2. **Commit pins.** A line is a *pin line* when it carries a positive signal: a
   component name (``project-continuity-modules``, its spaced form, or an alias
   ``PCM``/``CGM``/``ACS``/``OIO``), or pin context (``pinned at``, ``@ ` ``,
   ``checkout at``). On a pin line every remaining SHA token must be a prefix
   of one of the four certified commits; 7 hex characters is the floor, because
   a short SHA names the full commit it shortened. A SHA with no component name
   and no pin context -- "the mesh advanced in commit 83379c6" -- is evidence,
   not a pin, and passes.
3. **Version pins.** A version-shaped token (``x.y.z``, optional leading ``v``)
   is a pin only when it is *paired* with a component: a cue word introduces it
   (``CLI``, ``contract``, ``version``, ``pins``), or a component mention sits
   immediately before it, or ``@`` follows it, or a component shares its
   markdown table cell. It is attributed to the nearest component mention
   before it, and must equal that component's certified ``version`` or ``cli``.
   An unpaired version -- a ``v0.1.0`` directory, ``lease 30m``, ``eight
   modules``, a ``protocol_version`` field -- is not a pin.
4. **Historical suppression, the narrow exception.** A line that carries a
   calendar date (``2026-10-01``, ``2026-10``, ``October 2026``) or an
   unambiguous past construction (``snapshot``, ``frozen``, ``previously``,
   ``former``, ``superseded``, ``no longer``, ``used to``, ``at the time``,
   ``historical``) is narrating history, and history may name old values. This
   is what keeps the train's own README clean -- "a copied table is how the
   2026-10-01 snapshot stayed on PCM 0.6.0 after 0.7.0 had shipped". The list
   is deliberately short: a generic word like ``was`` or ``example`` would
   silence the ``--cgm-root <checkout at 6831f91e...>`` command this check
   exists to catch, and a silent false negative is the defect recurring.

The rule is line-scoped because that is the shape of every real stale pin in
the stack (OIO AGENTS.md 15-17; ACS README 52, 54, 122, 159) and not the shape
of a historical citation.

Deliberate non-goals: it does not check that a stated commit belongs to the
component named beside it (a line may legitimately list two components), and it
does not scan ``docs/``, ``HANDOFF.md``, checkpoints, or the ACS pack's own
``NOTES.md``/``SPEC.md``. Those are other surfaces; this check owns the three
document names the issue names, and ``--file`` adds more.

Stdlib only, and Windows-safe: no POSIX-only shell, no fcntl, no symlinks, and
console output is ASCII-folded so it cannot crash a cp1252 console.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_TRAIN = Path(__file__).resolve().parent.parent / "stack-releases.json"
DOCUMENT_NAMES = ("README.md", "AGENTS.md", "PROJECT.md")

# Any URL: a SHA inside one is a reference to a revision, not a restated pin.
URL_RE = re.compile(r"https?://\S+")

# Whole-line machine markers (pcm:policy, continuity:project, continuity:*) --
# schema metadata with its own version fields, not component pins.
MARKER_LINE_RE = re.compile(r"^\s*<!--\s*(?:pcm|continuity):[a-z-]+")

# Versioned path segments: modules/.../multi-agent-hotload/v0.1.0/HOTLOAD.md is
# the ACS module's own versioned directory, not a sibling component version.
PATH_SEGMENT_RE = re.compile(r"[\w./~-]*/[\w./~-]*[vV]?\d+\.\d+\.\d+[\w./~-]*")

# A SHA-shaped token: 7-40 hex characters, not embedded in a longer word. 7 is
# the floor GitHub itself uses for an unambiguous short SHA, and accepting a
# prefix is what lets `776b468...` name the full commit it shortened. A bare
# digit run can be a SHA too (`264117398...`), so no letter is required.
SHA_TOKEN_RE = re.compile(r"(?<![0-9a-zA-Z])[0-9a-f]{7,40}(?![0-9a-zA-Z])")

# A version-shaped token: 1.2.3 or v1.2.3. Does not match x.y or plain
# integers, so lease minutes, module counts, and schema generations stay out.
VERSION_TOKEN_RE = re.compile(r"(?<![0-9a-zA-Z])v?(\d+\.\d+\.\d+)(?![0-9a-zA-Z])")

# Component names, long form (hyphenated and spaced) and aliases, as prose
# writes them. The spaced forms matter: ACS README line 54 says "Content
# Generation Modules contract 0.5.12".
COMPONENT_ALIASES: dict[str, tuple[str, ...]] = {
    "project-continuity-modules": (
        "project-continuity-modules", "project continuity modules", "pcm",
    ),
    "content-generation-modules": (
        "content-generation-modules", "content generation modules", "cgm",
    ),
    "agent-custom-setup": (
        "agent-custom-setup", "agent custom setup", "acs",
    ),
    "observational-issue-ops": (
        "observational-issue-ops", "observational issue ops", "oio",
    ),
}
_ALIAS_TO_COMPONENT: dict[str, str] = {
    alias.lower(): name for name, aliases in COMPONENT_ALIASES.items() for alias in aliases
}
COMPONENT_WORD_RE = re.compile(
    r"\b(" + "|".join(sorted(_ALIAS_TO_COMPONENT, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)

# Pin context words that pair a value with a component on one line.
PIN_CONTEXT_RE = re.compile(
    r"(?:pinned?\s+at|pinned\s+to|checked?\s*out\s+at|checkout\s+at|@\s*`|@\s*[0-9a-f]{7})",
    re.IGNORECASE,
)

# A version is paired when a cue word introduces it ("CLI 0.6.0") or a commit
# follows it ("0.5.12 @ 6831f91e").
VERSION_CUE_BEFORE_RE = re.compile(
    r"(?:\bCLI\b|\bcontract\b|\bversion\b|\bpins?\b|\bpinned\b)[\s:=\[(`'\"]*$",
    re.IGNORECASE,
)
VERSION_CUE_AFTER_RE = re.compile(r"\s*@")

# Historical suppression: a calendar date, or one of these past constructions.
# Generic words ("was", "old", "example", "evidence", "before") are
# deliberately absent -- they would silence a live stale command.
DATE_RE = re.compile(
    r"\b\d{4}-\d{2}(?:-\d{2})?\b"
    r"|\b(?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b"
    r"|\b(?:January|February|March|April|May|June|July|August|September|October"
    r"|November|December)\s+\d{4}\b",
    re.IGNORECASE,
)
HISTORICAL_RE = re.compile(
    r"\b(?:snapshot|frozen|previously|previous|former|formerly|superseded|"
    r"no\s+longer|used\s+to|at\s+the\s+time|historical)\b",
    re.IGNORECASE,
)

# Fields of a certified entry that a version pin may legitimately state.
VERSION_FIELDS = ("version", "cli")


def _blank(match: re.Match) -> str:
    """Replace a matched span with spaces, keeping the line's length."""
    return " " * len(match.group(0))


def strip_non_prose(line: str) -> str:
    """Blank URLs and versioned path segments, preserving every position."""
    return PATH_SEGMENT_RE.sub(_blank, URL_RE.sub(_blank, line))


def certified_shas(certified: dict) -> dict[str, str]:
    """Map lowercase full-SHA -> component name, for prefix comparison."""
    names: dict[str, str] = {}
    for name, entry in certified.items():
        commit = entry.get("commit") if isinstance(entry, dict) else None
        if isinstance(commit, str) and re.fullmatch(r"[0-9a-fA-F]{40}", commit):
            names[commit.lower()] = name
    return names


def certified_versions(certified: dict) -> dict[str, set[str]]:
    """Map component name -> the versions that component certifies."""
    out: dict[str, set[str]] = {}
    for name, entry in certified.items():
        if not isinstance(entry, dict):
            continue
        values = {entry[field] for field in VERSION_FIELDS if isinstance(entry.get(field), str)}
        if values:
            out[name] = values
    return out


def sha_names_component(token: str, shas: dict[str, str]) -> str | None:
    """The component a SHA token names, by prefix, or None if it names none."""
    token = token.lower()
    if token in shas:
        return shas[token]
    for full, name in shas.items():
        if full.startswith(token):
            return name
    return None


def components_on_line(line: str) -> list[tuple[int, int, str]]:
    """Every component mention as (start, end, component-name), in order."""
    return [
        (match.start(), match.end(), _ALIAS_TO_COMPONENT[match.group(1).lower()])
        for match in COMPONENT_WORD_RE.finditer(line)
    ]


def component_for(line: str, at: int) -> str | None:
    """The component a value at position ``at`` belongs to.

    The nearest mention *before* it wins, because a line may list several
    components ("pins PCM CLI 0.6.0 and Content Generation Modules 0.5.12");
    a value with no mention before it belongs to the first mention on the line.
    """
    mentions = components_on_line(line)
    before = [mention for mention in mentions if mention[1] <= at]
    if before:
        return before[-1][2]
    return mentions[0][2] if mentions else None


def cell_of(line: str, at: int) -> str:
    """The pipe-delimited cell containing position ``at`` ("" outside a table)."""
    left = line.rfind("|", 0, at)
    right = line.find("|", at)
    if left == -1 or right == -1:
        return ""
    return line[left + 1: right]


def is_historical(line: str) -> bool:
    """True when the line narrates the past, so old values in it are history."""
    return bool(DATE_RE.search(line) or HISTORICAL_RE.search(line))


def is_pin_line(line: str) -> bool:
    """A positive signal that this line offers a value as current."""
    return bool(COMPONENT_WORD_RE.search(line) or PIN_CONTEXT_RE.search(line))


def version_is_paired(line: str, match: re.Match) -> bool:
    """Whether a version token is offered as a component's current version."""
    if VERSION_CUE_BEFORE_RE.search(line[: match.start()]):
        return True
    if VERSION_CUE_AFTER_RE.match(line[match.end():]):
        return True
    # A component mention immediately before it ("CGM 0.5.12").
    if any(0 <= match.start() - end <= 2 for _, end, _ in components_on_line(line)):
        return True
    # A component and the version sharing one markdown table cell.
    cell = cell_of(line, match.start())
    return bool(cell) and bool(COMPONENT_WORD_RE.search(cell))


def prose_pin_problems(document: str, certified: dict) -> list[str]:
    """Return a problem string for every stale pin in one document.

    Pure over ``(document_text, certified_set)``. The certified set is the
    ``certified`` object of stack-releases.json: component name -> entry with
    at least ``version`` and ``commit``. An empty or malformed certified set
    yields no problems: an unreadable rule must not invent drift.
    """
    if not isinstance(certified, dict) or not certified:
        return []
    shas = certified_shas(certified)
    versions = certified_versions(certified)

    problems: list[str] = []
    for lineno, raw_line in enumerate(document.splitlines(), start=1):
        if MARKER_LINE_RE.search(raw_line):
            continue
        line = strip_non_prose(raw_line)
        if is_historical(line):
            continue

        # Commit pins: every SHA on a pin line must name a certified commit.
        if is_pin_line(line):
            for match in SHA_TOKEN_RE.finditer(line):
                if sha_names_component(match.group(0), shas) is None:
                    problems.append(
                        _problem(lineno, raw_line, "commit",
                                 f"states {match.group(0)}, which is no certified "
                                 f"component commit")
                    )

        # Version pins: a paired version must equal the certified version of
        # the component it is attributed to.
        for match in VERSION_TOKEN_RE.finditer(line):
            if not version_is_paired(line, match):
                continue
            version = match.group(1)
            named = component_for(line, match.start())
            allowed = versions.get(named) if named else None
            if allowed and version not in allowed:
                problems.append(
                    _problem(lineno, raw_line, "version",
                             f"states {version} for {named}; certified is "
                             f"{', '.join(sorted(allowed))}")
                )
    return problems


def _problem(lineno: int, line: str, kind: str, detail: str) -> str:
    excerpt = line.strip()
    if len(excerpt) > 100:
        excerpt = excerpt[:97] + "..."
    return f"line {lineno}: a {kind} pin the certified set does not name: {detail} -- {excerpt}"


def find_documents(root: Path, extra: list[str] | None = None) -> list[Path]:
    """The three stack document names at the repository root, plus ``extra``."""
    names = list(DOCUMENT_NAMES) + [name for name in (extra or []) if name not in DOCUMENT_NAMES]
    found = [root / name for name in names]
    return sorted({path for path in found if path.is_file()})


def check_root(root: Path, train_path: Path, extra: list[str] | None = None) -> tuple[list[str], list[Path]]:
    """Check every stack document under root against the certified set."""
    try:
        train = json.loads(train_path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        raise SystemExit(f"FAIL: {train_path} is missing") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"FAIL: {train_path} is not valid JSON: {exc}") from None
    certified = train.get("certified") if isinstance(train, dict) else None
    if not isinstance(certified, dict) or not certified:
        raise SystemExit(f"FAIL: {train_path} has no certified object to check against")

    errors: list[str] = []
    documents = find_documents(root, extra)
    for path in documents:
        try:
            text = path.read_text(encoding="utf-8-sig")
        except OSError as exc:
            errors.append(f"{path}: unreadable ({exc})")
            continue
        try:
            rel = path.relative_to(root)
        except ValueError:
            rel = path
        for problem in prose_pin_problems(text, certified):
            errors.append(f"{rel.as_posix()}: {problem}")
    return errors, documents


def console_safe(text: str) -> str:
    """ASCII-fold for Windows cp1252 consoles (unicode punctuation crashes print)."""
    for fancy, plain in (("—", "-"), ("–", "-"), ("…", "..."),
                         ("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"')):
        text = text.replace(fancy, plain)
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."),
                        help="repository root to scan (default: current directory)")
    parser.add_argument("--train", type=Path, default=DEFAULT_TRAIN,
                        help="path to the train's stack-releases.json "
                             "(default: this repository's copy)")
    parser.add_argument("--file", action="append", default=[], dest="files",
                        help="extra document name, relative to --root (repeatable)")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        print(f"FAIL: {root} is not a directory", file=sys.stderr)
        return 2
    train_path = args.train.resolve()

    errors, documents = check_root(root, train_path, args.files)
    if errors:
        print(f"FAIL: prose pins disagree with the certified train at {train_path}")
        for error in errors:
            print(f"  - {console_safe(error)}", file=sys.stderr)
        return 1
    print(f"OK: {len(documents)} stack document(s) state no component pin "
          f"the certified set does not name")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
