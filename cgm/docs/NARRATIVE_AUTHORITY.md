# Issue, pull request, and receipt prose

**Audience:** anyone who pins Content Generation Modules (CGM) and publishes
issue logs, pull request titles and bodies, receipts, or commit subjects in a
repository that consumes this stack.

CGM owns the prose on those surfaces. The three-plane protocol that decides what
an observation means lives upstream in
[Observational Issue Ops](https://github.com/Pukujan/observational-issue-ops)
(OIO). CGM owns how the sentence reads.

## What routes where

| Surface | Load | Notes |
| --- | --- | --- |
| Issue titles and bodies, issue-log titles | `human-sounding-writing` (**hsw**) | **MUST load.** Plain title, reader-first body. |
| Pull request titles and bodies | `human-sounding-writing` (**hsw**) | **MUST load.** Same rules as an issue. |
| Receipts (push, checkpoint, and release receipts) | `human-sounding-writing` (**hsw**) | **MUST load.** A receipt is a human sentence, not a tool dump. |
| Commit messages and commit subjects | `human-sounding-writing` (**hsw**) | **MUST load.** One plain human subject line. |
| Generated filenames and asset paths inside those texts | `human-output-naming` (**hon**) | **MUST load** before naming a generated artifact. |

The machine twin is the `github_and_docs_prose` route in
[`writing-routing.json`](writing-routing.json), which carries the `title_contract`
and the `receipts` surface. Soft enforcement means CGM does not NLP-grade prose
in CI. It does not make the load optional.

## Rule 1: the title is one human sentence

An issue title and a pull request title are one complete, understandable human
sentence. The sentence states what is wrong or what the reader gets. A reader who
sees only the title should know what the change is about.

Do not open a title with a prefix code. `feat:`, `fix:`, `chore:`, `docs:`, and
the rest of the conventional-commit tags are internal shorthand, not a sentence.
Do not open with an internal task number either. A bare `CGM-45`, `#45`, or
`TASK-0045` as the first token tells a reader nothing until they open the ticket.

| Instead of | Write |
| --- | --- |
| `feat: add issue prose rules` | `Adopters get one plain sentence for issue and pull request titles` |
| `fix: hsw skipped on compare html` | `Compare HTML still reads like a tool dump after the 0.5.7 pin` |
| `CGM-45: narrative authority` | `CGM states the prose rules adopters apply to issues and receipts` |

Colon-reveal slogans such as `Reading receipts: what the hashes hide` fail the
same test. The title is a sentence, not a label with a subtitle.

## Rule 2: explain the reference before it carries weight

A commit SHA, a pull request number, a flag, or a file path is a reference, not a
meaning. Give each one a plain-English meaning in the same sentence before it
does any work. The reader should not have to resolve an identifier to follow the
point.

| Instead of | Write |
| --- | --- |
| `Pinned at c069613` | `The pin now points at CGM 0.5.7, commit c069613` |
| `See PR #43` | `The motion-frame change in pull request 43 adds the moving hero` |
| `run with --check-adopter-readme` | `Run the validator with --check-adopter-readme, the flag that checks the adopter README` |

Numbers, SHAs, and paths are welcome. They earn their place when the sentence
around them says what they are.

## Upstream protocol and the release train

OIO is the single upstream for the three-plane observational issue template and
its triage workflow. CGM does not copy that template. Point at it:

- Issue protocol and template:
  [`observational-issue-ops`](https://github.com/Pukujan/observational-issue-ops)
  and its
  [`observational-issue.yml`](https://github.com/Pukujan/observational-issue-ops/blob/main/.github/ISSUE_TEMPLATE/observational-issue.yml)
- Release train:
  [`stack-releases.json`](https://github.com/Pukujan/observational-issue-ops/blob/main/stack-releases.json)

The release train is the single source of certified versions. CGM appears in the
2026-10-01 train as version 0.5.7 at commit `c069613`, certified for the
narrative and styling authority role: writing routing, human-sounding writing,
output naming, visual direction, and image generation. An adopter pins the train
and references CGM by that version instead of hand-copying a pin into several
files.

## Boundaries

- CGM owns prose on issue, pull request, receipt, and commit surfaces. OIO owns
  the issue template and the three-plane triage. Neither owns the other's files.
- Receipts are produced by Project Continuity Modules (PCM). CGM owns how a
  receipt reads, not what it records.
- This page states rules. It adds no CI prose grade and no new lint step. The
  load is carried by the writing router and the always-on block, as before.

## Related contracts

- Soft router: [`WRITING_ROUTING.md`](WRITING_ROUTING.md) /
  [`writing-routing.json`](writing-routing.json)
- Writing guide: [`HUMAN_SOUNDING_WRITING.md`](HUMAN_SOUNDING_WRITING.md) /
  [`human-sounding-rules.json`](human-sounding-rules.json)
- Filename contract: [`HUMAN_OUTPUT_NAMING.md`](HUMAN_OUTPUT_NAMING.md) /
  [`human-output-naming.json`](human-output-naming.json)
- Operational issue intake: [`ISSUE_LOG.md`](ISSUE_LOG.md) /
  [`issue-log-contract.json`](issue-log-contract.json)
