When a GitHub issue reference appears in a pull-request description or commit message, use a supported issue-closing keyword only when merging should complete that issue. GitHub treats `close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves`, and `resolved` followed by an issue reference as a close directive; negation does not cancel it. For progress-only work, link with `Refs #<number>` or the GitHub sidebar. After each merge, verify the live issue state before changing task status. See [GitHub's issue-linking rules](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue).

## Human outcome

What changed for the person or project?

## Change and scope

Summarize the change and important boundaries.

## Verification

List focused commands and observed results. Link the CI run; do not paste full logs.

## Evidence and provenance (when relevant)

- Task ID and issue:
- Starting revision, inputs, or source:
- Direct citations or reproducible artifact:
- What remains unknown:

<details>
<summary>Reproduction details or extended technical notes (only when useful)</summary>

Add exact commands, configuration, inputs, results, and limitations here when they are needed to verify the claim.

</details>

## Continuity closeout

- Task checkpoint updated:
- One next action or explicit completion:

This template records context; it does not automatically synchronize this pull request with issues or checkpoints.
