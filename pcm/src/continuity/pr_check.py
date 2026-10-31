"""Check a pull-request description against PCM's reader-first shape.

The shape is the one the generated pull-request template asks for: one
problem sentence before any heading, the required sections, a before-and-after
picture, and an issue reference. The check reads the text only; it cannot
judge whether the prose is good, so it reports what is missing, not quality.
"""

from __future__ import annotations

import re

REQUIRED_SECTIONS = ("Human outcome", "Before and after", "Change and scope", "What stays unchanged", "Verification")
# Prompts from the generated template. A body that still holds one was not filled in.
TEMPLATE_PROMPTS = (
    "What changed for the person or project?",
    "**Before:** what happened, step by step.",
    "Summarize the change and important boundaries.",
    "List focused commands and observed results.",
)
ISSUE_REF = r"(?:[\w.-]+/[\w.-]+)?#(?P<number>\d+)"
CLOSING_RE = re.compile(rf"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\b:?\s+{ISSUE_REF}", re.IGNORECASE)
REFS_RE = re.compile(rf"\b(?:refs?|part of)\b:?\s+{ISSUE_REF}", re.IGNORECASE)
REFERENCE_LINE_RE = re.compile(r"^(?:refs?|part of|close[sd]?|fix(?:e[sd])?|resolve[sd]?)\b", re.IGNORECASE)
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
MERMAID_RE = re.compile(r"```mermaid\s*\n(?P<body>.*?)```", re.DOTALL)
NODE_RE = re.compile(r"(?<![\w-])([A-Za-z][\w]*)\s*(?:\[|\(|\{|>)")
BRANCH_ISSUE_RE = re.compile(r"(?:^|/)(?:[a-z]+-)?(\d+)(?:-|$)")


def branch_issue(branch: str) -> int | None:
    """The issue number a branch name carries, as in `fix/47-pr-shape`."""
    match = BRANCH_ISSUE_RE.search(branch or "")
    return int(match.group(1)) if match else None


def opening_line(body: str) -> str:
    for line in COMMENT_RE.sub("", body).splitlines():
        if line.strip():
            return line.strip()
    return ""


def check_pr_body(body: str, owning_issue: int | None = None) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for one pull-request description."""
    errors: list[str] = []
    warnings: list[str] = []
    visible = COMMENT_RE.sub("", body)

    first = opening_line(body)
    if not first:
        errors.append("the description is empty; open with one problem sentence a newcomer can follow")
    elif first.startswith("#") or first.startswith("<details") or first.startswith("|"):
        errors.append(
            f"open with one problem sentence before any heading, table or details block (found: {first[:60]!r})"
        )
    elif REFERENCE_LINE_RE.match(first):
        errors.append(
            f"open with the problem, not an issue reference (found: {first[:60]!r}); "
            "put `Closes #N` or `Refs #N` at the end"
        )

    headings = {m.group(1).strip().lower() for m in re.finditer(r"^#{2,3}\s+(.+?)\s*$", visible, re.MULTILINE)}
    for section in REQUIRED_SECTIONS:
        if not any(heading.startswith(section.lower()) for heading in headings):
            errors.append(f"missing section `## {section}`")
    for prompt in TEMPLATE_PROMPTS:
        if prompt in visible:
            errors.append(f"template text left unfilled: {prompt!r}")

    closing = {int(m.group("number")) for m in CLOSING_RE.finditer(visible)}
    refs = {int(m.group("number")) for m in REFS_RE.finditer(visible)}
    if not closing and not refs:
        errors.append("name the issue this work belongs to: `Closes #N` when merging finishes it, else `Refs #N`")
    if owning_issue is not None and owning_issue not in closing:
        if owning_issue in refs:
            warnings.append(
                f"the branch's issue #{owning_issue} is named only with `Refs`; if this pull request finishes it, "
                f"say `Closes #{owning_issue}` so close-on-merge closes it"
            )
        else:
            warnings.append(f"the branch's issue #{owning_issue} is not named in the description")

    for match in MERMAID_RE.finditer(visible):
        diagram = match.group("body")
        nodes = set(NODE_RE.findall(diagram)) - {"graph", "flowchart", "subgraph", "end"}
        wide = re.match(r"\s*(?:graph|flowchart)\s+(?:LR|RL)\b", diagram)
        if wide and len(nodes) > 4:
            warnings.append(f"a left-to-right diagram with {len(nodes)} nodes is unreadable on phones; use `graph TD`")
        if len(nodes) > 8:
            warnings.append(f"a diagram has {len(nodes)} nodes; keep it to 8 or fewer")
        if "<details" not in visible[: match.start()].rsplit("</details>", 1)[-1]:
            warnings.append("wrap each mermaid diagram in `<details>` and keep a text version next to it")
    return errors, warnings
