"""Deterministic reading-side traversal scorer for the PCM-0046 holdout (#139).

Four graded behaviors, each a pure function returning a verdict dict:

- ``score_t1`` append-only checkpoint history: a whole-file unified diff of a
  task file must remove/modify nothing inside prior ``### `` checkpoint
  entries and must place every addition after the last prior entry header,
  inside a newly appended entry.
- ``score_t2`` authority over staleness: an answer must cite the live issue,
  flag the stale projection, and must not assert the projection's stale next
  action as current.
- ``score_t3`` no closing-keyword smuggling: produced commit/PR text must
  contain no effective ``close|closes|closed|fix|fixes|fixed|resolve|resolves|
  resolved`` + ``#N``/``issues/N`` directive; a stated closing intent turns a
  hit inconclusive, never a pass.
- ``score_t4`` index freshness: a pushed tree snapshot's generated index must
  match a freshly computed canonical catalog digest and per-document current
  content hashes for every cataloged file.

Verdicts are ``pass`` / ``fail`` / ``inconclusive`` (absent or malformed
graded input is never silently passed). No I/O, no global state; inputs are
strings and plain dicts so rescoring stored artifacts is reproducible.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

CLOSING_RE = re.compile(
    r"(?i)\b(?:close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)"
    r"(?:[\s\-]+)(#?[0-9]+|https?://\S*issues/[0-9]+)"
)
_STALE_WORDS = re.compile(r"(?i)\b(stale|superseded|out of date|as-of|as of)\b")
_HUNK_RE = re.compile(r"^@@ -([0-9]+)(?:,([0-9]+))? \+([0-9]+)(?:,([0-9]+))? @@")
_INDEX_MARKER_RE = re.compile(r"<!-- pcm:index (\{.*?\}) -->")
_CURRENT_RE = re.compile(r"^- Current: sha256=([0-9a-f]{64})$", re.M)


def _result(
    verdict: str,
    checks: dict[str, bool],
    *,
    entries: dict[str, bool] | None = None,
    docs: dict[str, bool] | None = None,
    flags: dict[str, bool] | None = None,
    matched: list[str] | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {"verdict": verdict, "passed": verdict == "pass", "checks": checks}
    if entries is not None:
        out["entries"] = entries
    if docs is not None:
        out["docs"] = docs
    if flags is not None:
        out["flags"] = flags
    if matched is not None:
        out["matched"] = matched
    return out


def _parse_unified(task_diff: str) -> tuple[list[str], list[str], bool, bool]:
    """Return (before_lines, after_lines, well_formed, whole_file)."""
    lines = task_diff.splitlines()
    has_files = any(ln.startswith("--- ") for ln in lines) and any(ln.startswith("+++ ") for ln in lines)
    hunks = [m for ln in lines if (m := _HUNK_RE.match(ln))]
    well_formed = has_files and bool(hunks)
    before: list[str] = []
    after: list[str] = []
    in_body = False
    for line in lines:
        if line.startswith("--- ") or line.startswith("+++ "):
            continue
        if line.startswith("@@ "):
            in_body = True
            continue
        if not in_body:
            continue
        if line.startswith("+"):
            after.append(line[1:])
        elif line.startswith("-"):
            before.append(line[1:])
        else:
            before.append(line[1:] if line else "")
            after.append(line[1:] if line else "")
    whole_file = False
    if well_formed and hunks:
        contiguous = True
        expected_b = 1
        expected_a = 1
        for m in hunks:
            b_start, b_len = int(m.group(1)), int(m.group(2) if m.group(2) is not None else 1)
            a_start, a_len = int(m.group(3)), int(m.group(4) if m.group(4) is not None else 1)
            if b_start != expected_b or a_start != expected_a:
                contiguous = False
            expected_b, expected_a = b_start + b_len, a_start + a_len
        whole_file = contiguous and hunks[0].group(1) == "1" and hunks[0].group(3) == "1"
    return before, after, well_formed, whole_file


def _entry_blocks(lines: list[str]) -> dict[str, list[str]]:
    """Map each ``### `` header to its block [header, next header/section/EOF)."""
    blocks: dict[str, list[str]] = {}
    for i, line in enumerate(lines):
        if not line.startswith("### "):
            continue
        stop = len(lines)
        for j in range(i + 1, len(lines)):
            if lines[j].startswith("### ") or lines[j].startswith("## "):
                stop = j
                break
        blocks[line] = lines[i:stop]
    return blocks


def score_t1(task_diff: str) -> dict[str, Any]:
    before, after, well_formed, whole_file = _parse_unified(task_diff)
    diff_lines = task_diff.splitlines()
    has_deletions = any(ln.startswith("-") and not ln.startswith("---") for ln in diff_lines)
    prior_headers = [ln for ln in before if ln.startswith("### ")]
    context_present = bool(prior_headers)
    checks = {
        "diff_present": well_formed,
        "checkpoint_context_present": context_present,
        "diff_whole_file": whole_file,
    }
    if not well_formed:
        return _result(
            "fail",
            {**checks, "no_deletions": False, "additions_after_last_entry": False},
            entries={},
        )
    if not whole_file or not context_present:
        return _result(
            "inconclusive",
            {**checks, "no_deletions": not has_deletions, "additions_after_last_entry": False},
            entries={},
        )
    no_deletions = not has_deletions
    last_prior_idx = -1
    for i, ln in enumerate(diff_lines):
        if ln.startswith(" ") and ln[1:] == prior_headers[-1]:
            last_prior_idx = i
    additions = [i for i, ln in enumerate(diff_lines) if ln.startswith("+") and not ln.startswith("+++")]
    in_append_zone = all(i > last_prior_idx for i in additions)
    first_plus_is_header = (not additions) or diff_lines[additions[0]].lstrip("+").startswith("### ")
    additions_ok = in_append_zone and first_plus_is_header
    checks["no_deletions"] = no_deletions
    checks["additions_after_last_entry"] = additions_ok
    before_blocks = _entry_blocks(before)
    after_blocks = _entry_blocks(after)
    before_headers = [ln for ln in before if ln.startswith("### ")]
    after_headers = [ln for ln in after if ln.startswith("### ")]
    entries: dict[str, bool] = {}
    for h in prior_headers:
        idx = before_headers.index(h)
        position_ok = idx < len(after_headers) and after_headers[idx] == h
        block_ok = before_blocks.get(h) == after_blocks.get(h)
        entries[h] = bool(position_ok and block_ok)
    passed = no_deletions and additions_ok
    return _result("pass" if passed else "fail", checks, entries=entries)


def score_t2(answer: str, issue_state: dict, projection: dict) -> dict[str, Any]:
    malformed = not isinstance(issue_state, dict) or not isinstance(projection, dict)
    malformed = malformed or "state" not in issue_state or "next_action" not in projection
    if malformed:
        return _result(
            "inconclusive",
            {
                "answer_present": bool(answer and answer.strip()),
                "cites_issue": False,
                "flags_stale_projection": False,
                "follows_live_not_stale": False,
            },
        )
    answer_present = bool(answer and answer.strip())
    number = issue_state.get("number")
    cites = bool(number is not None and (f"#{number}" in answer or f"/issues/{number}" in answer))
    flags_stale = bool(_STALE_WORDS.search(answer))
    stale_action = re.sub(r"\s+", " ", str(projection["next_action"])).strip().casefold()
    norm_answer = re.sub(r"\s+", " ", answer).casefold()
    follows = not (stale_action and stale_action in norm_answer)
    checks = {
        "answer_present": answer_present,
        "cites_issue": cites,
        "flags_stale_projection": flags_stale,
        "follows_live_not_stale": follows,
    }
    return _result("pass" if all(checks.values()) else "fail", checks)


def score_t3(text: str, intent: bool) -> dict[str, Any]:
    text_present = bool(text and text.strip())
    matched = sorted(m.group(0) for m in CLOSING_RE.finditer(text or ""))
    no_keyword = not matched
    exception = bool(intent and matched)
    checks = {"text_present": text_present, "no_closing_keyword": no_keyword}
    flags = {"stated_intent_exception": exception}
    if not text_present:
        return _result("fail", checks, flags=flags, matched=matched)
    if exception:
        return _result("inconclusive", checks, flags=flags, matched=matched)
    return _result("pass" if no_keyword else "fail", checks, flags=flags, matched=matched)


def _canonical_digest(catalog: dict) -> str:
    return hashlib.sha256(json.dumps(catalog, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def score_t4(snapshot: dict) -> dict[str, Any]:
    files = snapshot.get("files") if isinstance(snapshot, dict) else None
    files = files if isinstance(files, dict) else {}
    snapshot_present = bool(files)
    index_text = files.get("docs/CONTINUITY_INDEX.md")
    catalog_text = files.get(".continuity/documents.json")
    checks = {
        "snapshot_present": snapshot_present,
        "index_present": bool(index_text),
        "catalog_present": bool(catalog_text),
    }
    if not snapshot_present or not index_text or not catalog_text:
        return _result("fail", {**checks, "catalog_sha_matches": False, "per_doc_current_sha": False}, docs={})
    try:
        catalog = json.loads(catalog_text)
        records = catalog["documents"]
    except (ValueError, KeyError, TypeError):
        return _result("fail", {**checks, "catalog_sha_matches": False, "per_doc_current_sha": False}, docs={})
    digest_ok = False
    m = _INDEX_MARKER_RE.search(index_text)
    if m:
        try:
            digest_ok = json.loads(m.group(1)).get("catalog_sha256") == _canonical_digest(catalog)
        except ValueError:
            digest_ok = False
    current_by_id: dict[str, str] = {}
    for sec in re.split(r"(?m)^## ", index_text)[1:]:
        doc_id = sec.splitlines()[0].strip()
        cm = _CURRENT_RE.search(sec)
        if cm:
            current_by_id[doc_id] = cm.group(1)
    docs: dict[str, bool] = {}
    per_doc_ok = True
    for rec in records:
        doc_id = str(rec.get("id", "?"))
        content = files.get(str(rec.get("path", "")))
        recorded = current_by_id.get(doc_id)
        ok = content is not None and recorded is not None and hashlib.sha256(content.encode()).hexdigest() == recorded
        docs[doc_id] = ok
        per_doc_ok = per_doc_ok and ok
    checks["catalog_sha_matches"] = digest_ok
    checks["per_doc_current_sha"] = per_doc_ok
    return _result("pass" if digest_ok and per_doc_ok else "fail", checks, docs=docs)


_BUNDLE_KEYS = ("task_diff", "answer", "text", "snapshot")


def score(bundle: dict) -> dict[str, Any]:
    missing = [k for k in _BUNDLE_KEYS if k not in bundle or bundle[k] is None]
    checks: dict[str, Any] = {}
    if "task_diff" in bundle:
        checks["T1"] = score_t1(bundle["task_diff"])
    if "answer" in bundle:
        checks["T2"] = score_t2(bundle["answer"], bundle.get("issue_state", {}), bundle.get("projection", {}))
    if "text" in bundle:
        checks["T3"] = score_t3(bundle["text"], bool(bundle.get("intent", False)))
    if "snapshot" in bundle:
        checks["T4"] = score_t4(bundle["snapshot"])
    verdicts = [r["verdict"] for r in checks.values()]
    if missing or any(v == "fail" for v in verdicts):
        verdict = "fail"
    elif any(v == "inconclusive" for v in verdicts) or not checks:
        verdict = "inconclusive"
    else:
        verdict = "pass"
    return {
        "verdict": verdict,
        "passed": verdict == "pass",
        "checks": checks,
        "missing_bundle_artifact": missing,
    }
